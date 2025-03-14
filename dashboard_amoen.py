# /dashboard_amoen.py

import os
import datetime
import pandas as pd
import streamlit as st
import matplotlib

matplotlib.use("Agg")

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import time
from bson import ObjectId

import streamlit_authenticator as stauth

# import yaml
# from yaml.loader import SafeLoader

from sections.helpers.validation_saisie import (
    validate_input_float,
    validate_energie_input,
    validate_percentage_sum,
)

from sections.helpers.calcul_dj import (
    get_meteo_data,
)

from sections.helpers.graphique_bars_exploitation import (
    graphique_bars_objectif_exploitation,
)

from sections.helpers.rapport import (
    generate_pdf,
)

from sections.helpers.query_IDC import (
    make_request,
    convert_geometry_for_streamlit,
    show_map,
    show_dataframe,
    get_adresses_egid,
    create_barplot,
)

from sections.helpers.amoen_historique import create_barplot_historique_amoen

from sections.helpers.avusy import (
    avusy_consommation_energie_dashboard,
    update_existing_data_avusy,
    display_counter_indices,
)

from sections.helpers.affectations_sre import display_affectations

from sections.helpers.agents_energetiques import (
    display_energy_agents,
)

from sections.helpers.note_calcul_main import (
    fonction_note_calcul,
    validate_required_data_for_note_calcul,
)

from sections.helpers.sidebar import add_sidebar_links

from sections.helpers.admin.admin_chiffre_cle import display_admin_dashboard

from sections.helpers.admin.admin_db_mgmt import display_database_management

from sections.helpers.sanitize_mongo import sanitize_db

from sections.helpers.utils import get_rounded_float

from sections.helpers.save_excel_streamlit import (
    display_dataframe_with_excel_download,
)

st.set_page_config(page_title="AMOEN Dashboard", page_icon=":bar_chart:", layout="wide")
os.environ["USE_ARROW_extension"] = "0"

# Variable pour la mise a jour de la météo
last_update_time_meteo = datetime.datetime(2021, 1, 1)

# IDC query
FIELDS = "*"
URL_INDICE_MOYENNES_3_ANS = "https://vector.sitg.ge.ch/arcgis/rest/services/Hosted/SCANE_INDICE_MOYENNES_3_ANS/FeatureServer/0/query"

MONGODB_URI = st.secrets["MONGODB_URI"]

# BD mongodb
def connect_with_retry(uri, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            client = MongoClient(
                uri, 
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                retryWrites=True,
                retryReads=True
            )
            # Test connection
            client.admin.command('ping')
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            if attempt < max_retries - 1:
                st.warning(f"MongoDB connection attempt {attempt+1} failed. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                st.error(f"Failed to connect to MongoDB after {max_retries} attempts. Error: {str(e)}")
                raise

client = connect_with_retry(MONGODB_URI)
# client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db_sites = client["amoen_ancienne_methodo"]
mycol_historique_sites = db_sites["historique"]
mycol_authentification_site = db_sites["authentification"]
mycol_historique_index_avusy = db_sites["avusy"]

if "data_site" not in st.session_state:
    st.session_state["data_site"] = {}


@st.cache_data
def load_project_data(project_name):
    """Load project data from the database."""
    data = mycol_historique_sites.find_one({"nom_projet": project_name})
    if data is not None:
        data_cleaned = sanitize_db(data)
    return data_cleaned


@st.cache_data
def load_projets_liste(project_name):
    """
    Retrieves a list of distinct project names from the 'mycol_historique_sites' collection.

    If the logged-in user is 'admin', it returns all distinct project names.
    Otherwise, it returns distinct project names filtered by the user's 'amoen_id'.

    Args:
        project_name (str): The name of the project to load (not used in the current implementation).

    Returns:
        list: A list of distinct project names.
    """
    if username_login == "admin":
        nom_projets_liste = mycol_historique_sites.distinct("nom_projet")
    else:
        nom_projets_liste = mycol_historique_sites.distinct(
            "nom_projet", {"amoen_id": username}
        )
    return nom_projets_liste


def load_projets_admin():
    """
    Retrieve all documents from the 'mycol_historique_sites' collection.

    This function connects to the MongoDB collection 'mycol_historique_sites' and retrieves all documents
    present in the collection. The documents are returned as a list.

    Returns:
        list: A list of documents retrieved from the 'mycol_historique_sites' collection.
    """
    data = list(mycol_historique_sites.find({}))
    return data


# Mise à jour météo
now = datetime.datetime.now()
if (now - last_update_time_meteo).days > 1:
    last_update_time_meteo = now
    st.session_state["df_meteo_tre200d0"] = get_meteo_data()


# Authentification
# with open('sections/secrets/secrets.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)

# Retrieve the config in mongodb
config = mycol_authentification_site.find_one(
    {"_id": ObjectId("66ad0b102f5cc6cb3c64e1d1")}
)

# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["pre-authorized"],
)

username, authentication_status, username_login = authenticator.login(
    location="sidebar"
)

if st.session_state["authentication_status"]:
    # st.write(config['credentials']['usernames'][st.session_state['username']]['password'])
    add_sidebar_links()
    with st.sidebar.popover("Changer mot de passe"):
        try:
            if authenticator.reset_password(
                username=st.session_state["username"],
                fields={
                    "Form name": "Remplacer mot de passe",
                    "Current password": "Mot de passe actuel",
                    "New password": "Nouveau mot de passe (Critères minimaux: 8 caractères[8-20], une majuscule[A-Z], un chiffre[0-9], un caractère spécial[@$!%*?&] Exemple: Patate1234!)",
                    "Repeat password": "Répéter nouveau mot de passe",
                    "Reset": "Reset",
                },
            ):
                st.success("Mot de passe modifié.")
                # update a specific field in mongodb
                mycol_authentification_site.update_one(
                    {"_id": ObjectId("66ad0b102f5cc6cb3c64e1d1")}, {"$set": config}
                )
        except Exception as e:
            st.error(e)
    authenticator.logout(button_name="Déconnexion", location="sidebar")
    st.sidebar.write("Connecté(e) en tant que: ", st.session_state["username"])

    # dashboard
    st.title("Calcul de l'atteinte des objectifs AMOén selon méthodologie")

    # Define the default tabs
    tabs = [
        "0 Readme",
        "1 Données site",
        "2 Note de calcul",
        "3 Résultats",
        "4 Historique",
        "5 Générer Rapport",
    ]

    # Add an extra tab for admin
    if username_login == "admin":
        tabs.append("6 Admin - Chiffres-clés")
        tabs.append("7 Admin - Base de données")
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(tabs)
    else:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tabs)

    # Calcul des index selon dates
    with tab1:
        st.subheader("Différences entre méthodologie et calcul IDC")
        st.write(
            "Selon la méthodologie AMOén, l'énergie finale pondérée après travaux (Ef,après,corr) représente la quantité d'énergie finale pondérée et climatiquement corrigée consommée par le bâtiment."
        )
        st.write(
            "L'IDC est utilisé à Genève pour mesurer la performance des bâtiments de plus de 5 preneurs de chaleur, l'IDC est aussi pondéré et corrigé climatiquement."
        )
        st.write(
            "l'IDC et l'Ef,après,corr ont le même but, c'est à dire de mesurer les performances des bâtiments, mais ils ne sont pas calculés de la même manière.\
             Les pincipales différences sont détaillées ci-dessous:"
        )
        tab1_col1, tab1_col2 = st.columns(2)
        with tab1_col1:
            st.write("Méthodologie")
            st.write(
                "- PAC: Dans la méthodologie on applique un facteur de pondération de 2 sur l'électricité consommée par les PAC."
            )
            st.write(
                "- CAD: Tous les CAD sont identiques dans la méthodologie. Il n'y a pas de différence entre CAD réparti ou tarifé"
            )
            st.write(
                "- Météo: utilisation des données MétéoSuisse station Cointrin, mesure tre200d0."
            )
            st.write(
                "- Répartition ECS/chauffage: la méthodologie se base sur la répartition théorique des besoins ECS/chauffage \
                    selon rénové/neuf ou les compteurs si disponible (ECS/Chauffage). Ces chiffres sont indiqueés dans le tableau Excel\
                    de fixation d'objectif de performances"
            )

        with tab1_col2:
            st.write("Règlement IDC")
            st.write(
                "- PAC: Dans le règlement IDC on doit appliquer un COP de 3.25 sur l'électricité consommée par les PAC après 2010."
            )
            st.write(
                "- CAD: Dans le cas du CAD tarifé, on doit appliquer des pertes → 1kWh utile = 3.6/0.925 MJ = 3.892 MJ normalisés"
            )
            st.write(
                "- Météo: Le tableau Excel IDC ne précise pas les données météo exactes utilisées."
            )
            st.write(
                "- Répartition ECS/chauffage: Le règlement IDC se base sur consommation normalisé de ECS (Eww), par exemple 128 MJ/m²\
                     pour du logement collectif. Tout le reste de l'énergie est pour le chauffage donc soumis a correction climatique."
            )

        st.subheader("Limitations du calcul")
        st.write("La période minimale recommandée de calcul est de 6 mois de données.")

    with tab2:

        @st.fragment
        def tab2_fragment():
            # projet
            st.subheader("Chargement données de base du projet")
            # in the database search unique values of the field 'nom_projet' in the documents mongodb
            nom_projets_liste = load_projets_liste(username)
            nom_projet_db = st.selectbox("Sélectionner projet", nom_projets_liste)

            data_sites_db = load_project_data(nom_projet_db)
            tab2_col01, tab2_col02 = st.columns(2)

            with tab2_col01:
                st.session_state["data_site"]["nom_projet"] = st.text_input(
                    "Nom du projet", value=data_sites_db["nom_projet"]
                )
                # SRE rénovée
                sre_renovation_m2 = st.text_input(
                    "SRE rénovée (m²):",
                    value=get_rounded_float(data_sites_db, "sre_renovation_m2"),
                    help="La SRE rénovée est la partie du batiment qui a été rénovée, la surélévation/extension n'est pas incluse",
                )
                st.session_state["data_site"]["sre_renovation_m2"] = (
                    validate_input_float(
                        name="SRE rénovée:",
                        variable=sre_renovation_m2,
                        unit="m²",
                        text=False,
                    )
                )

            with tab2_col02:
                st.session_state["data_site"]["adresse_projet"] = st.text_input(
                    "Adresse(s) du projet", value=data_sites_db["adresse_projet"]
                )
                st.session_state["data_site"]["amoen_id"] = st.text_input(
                    "AMOen", value=data_sites_db["amoen_id"]
                )

            st.markdown(
                '<span style="font-size:1.2em;">**IDC moyen avant travaux et objectif en énergie finale**</span>',
                unsafe_allow_html=True,
            )
            # st.text("Ces données se trouvent dans le tableau Excel de fixation d'objectif de performances:\n\
            # - Surélévation: C92/C94\n\
            # - Rénovation: C61/C63")
            tab2_col5, tab2_col6 = st.columns(2)
            with tab2_col5:
                # Autres données
                # st.write('IDC moyen 3 ans avant travaux (Ef,avant,corr [kWh/m²/an])')
                ef_avant_corr_kwh_m2 = st.text_input(
                    "IDC moyen 3 ans avant travaux (Ef,avant,corr [kWh/m²/an]):",
                    value=get_rounded_float(data_sites_db, "ef_avant_corr_kwh_m2"),
                    help="Surélévation: C92 / Rénovation: C61",
                )
                st.session_state["data_site"]["ef_avant_corr_kwh_m2"] = (
                    validate_energie_input(
                        name="Ef,avant,corr",
                        variable=ef_avant_corr_kwh_m2,
                        unit1="kWh/m²/an",
                        unit2="MJ/m²/an",
                    )
                )
            with tab2_col6:
                ef_objectif_pondere_kwh_m2 = st.text_input(
                    "Ef,obj * fp [kWh/m²/an]:",
                    value=get_rounded_float(
                        data_sites_db, "ef_objectif_pondere_kwh_m2"
                    ),
                    help="Surélévation: C94 / Rénovation: C63",
                )
                st.session_state["data_site"]["ef_objectif_pondere_kwh_m2"] = (
                    validate_energie_input(
                        name="Ef,obj * fp",
                        variable=ef_objectif_pondere_kwh_m2,
                        unit1="kWh/m²/an",
                        unit2="MJ/m²/an",
                    )
                )
            st.markdown(
                '<span style="font-size:1.2em;">**Répartition énergie finale ECS/Chauffage**</span>',
                unsafe_allow_html=True,
            )

            tab2_col7, tab2_col8 = st.columns(2)
            with tab2_col7:
                # Répartition énergie finale
                # rénovation - chauffage
                repartition_energie_finale_partie_renovee_chauffage = st.text_input(
                    "Chauffage partie rénovée [%]",
                    value=get_rounded_float(
                        data_sites_db,
                        "repartition_energie_finale_partie_renovee_chauffage",
                    ),
                    help="Surélévation: C77 / Rénovation: C49",
                )
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_chauffage"
                ] = validate_input_float(
                    name="Répartition EF - Chauffage partie rénovée:",
                    variable=repartition_energie_finale_partie_renovee_chauffage,
                    unit="%",
                    text=True,
                    zero=True,
                )

                # surélévation - chauffage
                repartition_energie_finale_partie_surelevee_chauffage = st.text_input(
                    "Chauffage partie surélévée [%]",
                    value=get_rounded_float(
                        data_sites_db,
                        "repartition_energie_finale_partie_surelevee_chauffage",
                    ),
                    help="C79",
                )
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_surelevee_chauffage"
                ] = validate_input_float(
                    name="Répartition EF - Chauffage partie surélévée:",
                    variable=repartition_energie_finale_partie_surelevee_chauffage,
                    unit="%",
                    text=True,
                    zero=True,
                )
            with tab2_col8:
                # rénovation - ECS
                repartition_energie_finale_partie_renovee_ecs = st.text_input(
                    "ECS partie rénovée [%]",
                    value=get_rounded_float(
                        data_sites_db,
                        "repartition_energie_finale_partie_renovee_ecs",
                    ),
                    help="Surélévation: C78 / Rénovation: C50",
                )
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_ecs"
                ] = validate_input_float(
                    name="Répartition EF - ECS partie rénovée:",
                    variable=repartition_energie_finale_partie_renovee_ecs,
                    unit="%",
                    text=True,
                    zero=True,
                )

                # surélévation - ECS
                repartition_energie_finale_partie_surelevee_ecs = st.text_input(
                    "ECS partie surélévée [%]",
                    value=get_rounded_float(
                        data_sites_db,
                        "repartition_energie_finale_partie_surelevee_ecs",
                    ),
                    help="C80",
                )
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_surelevee_ecs"
                ] = validate_input_float(
                    name="Répartition EF - ECS partie surélevée:",
                    variable=repartition_energie_finale_partie_surelevee_ecs,
                    unit="%",
                    text=True,
                    zero=True,
                )

            # Validation somme des pourcentages
            fields_to_validate_sum_repartition_energie_finale = [
                "repartition_energie_finale_partie_renovee_chauffage",
                "repartition_energie_finale_partie_renovee_ecs",
                "repartition_energie_finale_partie_surelevee_chauffage",
                "repartition_energie_finale_partie_surelevee_ecs",
            ]

            st.session_state["data_site"]["somme_repartition_energie_finale"] = (
                validate_percentage_sum(
                    st.session_state["data_site"],
                    fields_to_validate_sum_repartition_energie_finale,
                )
            )

            st.subheader("Eléments à renseigner", divider="rainbow")

            st.markdown(
                '<span style="font-size:1.2em;">**Sélectionner les dates de début et fin de période**</span>',
                unsafe_allow_html=True,
            )
            tab2_col3, tab2_col4 = st.columns(2)
            # dates
            with tab2_col3:
                last_year = pd.to_datetime(
                    st.session_state["df_meteo_tre200d0"]["time"].max()
                ) - pd.DateOffset(days=365)
                periode_start = st.date_input(
                    "Début de la période",
                    datetime.date(last_year.year, last_year.month, last_year.day),
                )

            with tab2_col4:
                max_date_texte = (
                    st.session_state["df_meteo_tre200d0"]["time"]
                    .max()
                    .strftime("%Y-%m-%d")
                )
                fin_periode_txt = (
                    f"Fin de la période (météo disponible jusqu'au: {max_date_texte})"
                )
                max_date = pd.to_datetime(
                    st.session_state["df_meteo_tre200d0"]["time"].max()
                )
                periode_end = st.date_input(
                    fin_periode_txt,
                    datetime.date(max_date.year, max_date.month, max_date.day),
                )

            periode_nb_jours = (periode_end - periode_start).days + 1
            st.session_state["data_site"]["periode_nb_jours"] = float(periode_nb_jours)

            st.session_state["data_site"]["periode_start"] = pd.to_datetime(
                periode_start
            )
            st.session_state["data_site"]["periode_end"] = pd.to_datetime(periode_end)

            try:
                if st.session_state["data_site"]["periode_nb_jours"] <= 180:
                    st.warning(
                        "La période de mesure doit être supérieure à 3 mois (minimum recommandé 6 mois)"
                    )
            except ValueError:
                st.warning("Problème de date de début et de fin de période")
            st.write(
                f"Période du {st.session_state['data_site']['periode_start'].strftime('%Y-%m-%d')} au {st.session_state['data_site']['periode_end'].strftime('%Y-%m-%d')} soit {int(st.session_state['data_site']['periode_nb_jours'])} jours"
            )

            tab2_col1, tab2_col2 = st.columns(2)
            with tab2_col1:
                # Affectations SRE
                st.session_state["data_site"]["somme_pourcentage_affectations"] = (
                    display_affectations(data_sites_db, sre_renovation_m2)
                )

            with tab2_col2:
                # Agents énergétiques
                st.session_state["data_site"]["somme_agents_energetiques_mj"] = (
                    display_energy_agents(
                        st.session_state["data_site"],
                        data_sites_db,
                    )
                )

            # Bug travaux_start serialization fix
            st.session_state["data_site"]["travaux_start"] = data_sites_db["travaux_start"]

            # Autres données
            # st.session_state["data_site"]["travaux_start"] = data_sites_db["travaux_start"]
            st.session_state["data_site"]["travaux_end"] = data_sites_db["travaux_end"]
            st.session_state["data_site"]["annees_calcul_idc_avant_travaux"] = (
                data_sites_db["annees_calcul_idc_avant_travaux"]
            )
            st.session_state["data_site"]["sre_extension_surelevation_m2"] = float(
                data_sites_db["sre_extension_surelevation_m2"]
            )

        tab2_fragment()

        if st.button("Sauvegarder", use_container_width=True, type="primary"):
            st.success("Données validées")
            st.rerun()

        # Avusy spécifique
        if st.session_state["data_site"]["nom_projet"] == "Avusy 10-10A":
            st.divider()
            st.subheader("Informations spécifiques Avusy 10-10A")

            # Create tabs for different views
            avusy_tab1, avusy_tab2, avusy_tab3 = st.tabs(
                ["Dashboard", "Index des compteurs", "Mise à jour des données"]
            )

            with avusy_tab1:
                # Use the session state dates for the dashboard
                avusy_consommation_energie_dashboard(
                    st.session_state["data_site"]["periode_start"],
                    st.session_state["data_site"]["periode_end"],
                    mycol_historique_index_avusy,
                )

            with avusy_tab2:
                display_counter_indices(mycol_historique_index_avusy)

            with avusy_tab3:
                update_existing_data_avusy(mycol_historique_index_avusy)

    with tab3:
        st.subheader("Note de calcul")

        if "data_site" in st.session_state and "df_meteo_tre200d0" in st.session_state:
            # vérifier que toutes les données sont présentes pour la note de calcul
            is_valid, missing_fields = validate_required_data_for_note_calcul(
                st.session_state["data_site"]
            )

            if is_valid:
                (
                    df_periode_list,
                    df_list,
                    df_agent_energetique,
                    df_meteo_note_calcul,
                    df_results,
                    formula_facteur_ponderation_moyen_texte,
                    formula_facteur_ponderation_moyen,
                ) = fonction_note_calcul(
                    st.session_state["data_site"], st.session_state["df_meteo_tre200d0"]
                )
            else:
                st.warning("Missing required data:")
                for field in missing_fields:
                    st.warning(f"- {field}")
                # Initialize empty returns if needed
                df_periode_list = pd.DataFrame()
                df_list = pd.DataFrame()
                df_agent_energetique = pd.DataFrame()
                df_meteo_note_calcul = pd.DataFrame()
                df_results = pd.DataFrame()
                formula_facteur_ponderation_moyen_texte = ""
                formula_facteur_ponderation_moyen = ""
        else:
            st.warning("Données pas complètes pour la note de calcul")

        # Hide the index
        hide_index_style = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

        # Display the DataFrame in Streamlit without the index
        st.markdown(hide_index_style, unsafe_allow_html=True)

        # Display the dataframes
        st.write("Période sélectionnée")
        display_dataframe_with_excel_download(df_periode_list, "periode_liste.xlsx")

        st.write("Calculs effectués pour la période sélectionnée")
        display_dataframe_with_excel_download(df_list, "calculs_periode.xlsx")

        st.write("Agents énergétiques")
        display_dataframe_with_excel_download(
            df_agent_energetique, "agents_energetiques.xlsx"
        )

        # Render the text in LaTeX
        st.latex(formula_facteur_ponderation_moyen_texte)

        # Render the formula in LaTeX
        st.latex(formula_facteur_ponderation_moyen)

        # Display the meteo data
        st.write("Données météo station Genève-Cointrin pour la période sélectionnée")
        display_dataframe_with_excel_download(
            df_meteo_note_calcul, "meteo_note_calcul.xlsx"
        )

        # display a hidden dataframe with all the data
        st.write("Données complètes")
        show_debug_data = st.checkbox("Afficher les données complètes")
        if show_debug_data:
            display_dataframe_with_excel_download(
                st.session_state["data_site"], "data_site.xlsx"
            )
            display_dataframe_with_excel_download(
                st.session_state["df_meteo_tre200d0"], "df_meteo_tre200d0.xlsx"
            )

    with tab4:
        st.subheader("Synthèse des résultats")
        if df_results is not None:
            st.table(df_results)
        else:
            st.warning(
                "Veuillez compléter les informations dans '1 Données site' pour voir les résultats"
            )

        # résultats en latex

        if (
            st.session_state["data_site"].get("facteur_ponderation_moyen") is not None
            and st.session_state["data_site"].get("facteur_ponderation_moyen") > 0
            and st.session_state["data_site"].get("ef_avant_corr_kwh_m2") > 0
            and st.session_state["data_site"].get(
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2",
                0,
            )
            > 0
            and st.session_state["data_site"].get("ef_objectif_pondere_kwh_m2") > 0
            and st.session_state["data_site"].get("atteinte_objectif") > 0
            and st.session_state["data_site"].get("somme_repartition_energie_finale")
            == 100
            and st.session_state["data_site"].get("somme_pourcentage_affectations")
            == 100
            and st.session_state["data_site"].get("somme_agents_energetiques_mj", 0) > 0
        ):
            formula_atteinte_objectif = r"Atteinte\ objectif \ [\%]= \frac{{\Delta E_{{f,réel}}}}{{\Delta E_{{f,visée}}}} = \frac{{E_{{f,avant,corr}} - E_{{f,après,corr,rénové}}*f_{{p}}}}{{E_{{f,avant,corr}} - E_{{f,obj}}*f_{{p}}}}"

            formula_atteinte_objectif_num = r"Atteinte\ objectif \ [\%]= \frac{{{} - {}*{}}}{{{} - {}*{}}} = {}".format(
                round(st.session_state["data_site"]["ef_avant_corr_kwh_m2"], 4),
                round(
                    st.session_state["data_site"][
                        "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
                    ],
                    4,
                )
                / round(st.session_state["data_site"]["facteur_ponderation_moyen"], 4),
                round(st.session_state["data_site"]["facteur_ponderation_moyen"], 4),
                round(st.session_state["data_site"]["ef_avant_corr_kwh_m2"], 4),
                round(st.session_state["data_site"]["ef_objectif_pondere_kwh_m2"], 4)
                / round(st.session_state["data_site"]["facteur_ponderation_moyen"], 4),
                round(st.session_state["data_site"]["facteur_ponderation_moyen"], 4),
                round(st.session_state["data_site"]["atteinte_objectif"], 3),
            )

            formula_atteinte_objectifs_pourcent = (
                r"Atteinte\ objectif\ [\%]= {} \%".format(
                    round(st.session_state["data_site"]["atteinte_objectif"] * 100, 2)
                )
            )

            # latex color
            if st.session_state["data_site"]["atteinte_objectif"] >= 0.85:
                formula_atteinte_objectifs_pourcent = (
                    r"\textcolor{green}{" + formula_atteinte_objectifs_pourcent + "}"
                )
            else:
                formula_atteinte_objectifs_pourcent = (
                    r"\textcolor{red}{" + formula_atteinte_objectifs_pourcent + "}"
                )

            # Render the formula in LaTeX
            st.latex(formula_atteinte_objectif)
            st.latex(formula_atteinte_objectif_num)
            st.latex(formula_atteinte_objectifs_pourcent)

        st.subheader("Graphiques")

        # Graphique 1
        if (
            st.session_state["data_site"].get("amoen_id")
            and st.session_state["data_site"].get("ef_avant_corr_kwh_m2")
            and st.session_state["data_site"].get(
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
            )
            and st.session_state["data_site"].get("ef_objectif_pondere_kwh_m2")
        ):
            graphique_bars_objectif_exploitation(
                st.session_state["data_site"]["nom_projet"],
                st.session_state["data_site"]["ef_avant_corr_kwh_m2"],
                st.session_state["data_site"][
                    "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
                ],
                st.session_state["data_site"]["ef_objectif_pondere_kwh_m2"],
                st.session_state["data_site"]["atteinte_objectif"],
                st.session_state["data_site"]["amoen_id"],
            )
        else:
            st.warning(
                "Veuillez compléter les informations dans '1 Données site' pour générer le graphique"
            )

    with tab5:
        # IDC
        # mulitselect adresses
        df_adresses_egid = get_adresses_egid()

        # Create a multiselect for addresses
        selected_addresses = st.session_state["data_site"]["adresse_projet"].split(";")

        if selected_addresses:
            # get egids that are selected
            filtered_df = df_adresses_egid[
                df_adresses_egid["adresse"].isin(selected_addresses)
            ]
            egids = filtered_df["egid"].tolist()

            # get data
            data_geometry = make_request(
                0,
                FIELDS,
                URL_INDICE_MOYENNES_3_ANS,
                1000,
                "SCANE_INDICE_MOYENNES_3_ANS",
                True,
                egids,
            )
            data_df = make_request(
                0,
                FIELDS,
                URL_INDICE_MOYENNES_3_ANS,
                1000,
                "SCANE_INDICE_MOYENNES_3_ANS",
                False,
                egids,
            )

            if data_geometry and data_df:
                # show map
                if st.checkbox("Afficher la carte"):
                    geojson_data, centroid = convert_geometry_for_streamlit(
                        data_geometry
                    )
                    show_map(geojson_data, centroid)

                st.subheader("Historique IDC")
                # create barplot
                create_barplot(data_df, st.session_state["data_site"]["nom_projet"])

                # show dataframe in something hidden like a
                if st.checkbox("Afficher les données IDC"):
                    show_dataframe(data_df)
            else:
                st.error(
                    "Pas de données disponibles pour le(s) EGID associé(s) à ce site."
                )
        else:
            st.write("Pas d'adresse sélectionnée.")

        st.subheader("Historique résultats méthodologie AMOen")
        # get data from mongodb
        pipeline_historique_graphique = [
            {
                "$match": {
                    "nom_projet": st.session_state["data_site"]["nom_projet"],
                    "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2": {
                        "$ne": 0.0
                    },
                }
            },
            {
                "$group": {
                    "_id": {
                        "periode_start": "$periode_start",
                        "periode_end": "$periode_end",
                    },
                    "doc": {"$first": "$$ROOT"},
                }
            },
            {"$replaceRoot": {"newRoot": "$doc"}},
        ]
        # Execute the aggregation pipeline
        data_db_historique = mycol_historique_sites.aggregate(
            pipeline_historique_graphique
        )

        # Process the results
        if data_db_historique:
            data_list = list(data_db_historique)

            # Convert to DataFrame
            df_historique_complet = pd.DataFrame(data_list)

            # Ensure required columns are present
            required_columns = [
                "nom_projet",
                "periode_start",
                "periode_end",
                "atteinte_objectif",
            ]

            # Proceed only if all required columns are present
            if all([col in df_historique_complet.columns for col in required_columns]):
                create_barplot_historique_amoen(df_historique_complet)

                # Show DataFrame in a hidden section
                if st.checkbox("Afficher les données historiques"):
                    display_dataframe_with_excel_download(
                        df_historique_complet, "historique_amoen.xlsx"
                    )
            else:
                st.error("Pas de données historiques disponibles")

    with tab6:
        st.subheader("Générer rapport")

        # Check if all fields are valid
        def is_valid(var):
            """
            Check if a variable is valid.

            A variable is considered valid if it is not None and not an empty string.

            Args:
                var: The variable to check.

            Returns:
                bool: True if the variable is valid, False otherwise.
            """
            return var is not None and var != ""

        def check_validity():
            """
            Checks the validity of various fields in the session state data.

            This function iterates over a predefined list of fields and checks if each field
            in the session state data is valid. If a field is found to be invalid, it is added
            to a list of invalid fields.

            Returns:
                list: A list of field names that are invalid.
            """
            invalid_fields = []
            fields_to_check = [
                "nom_projet",
                "adresse_projet",
                "amoen_id",
                "sre_renovation_m2",
                "sre_pourcentage_habitat_collectif",
                "sre_pourcentage_habitat_individuel",
                "sre_pourcentage_administration",
                "sre_pourcentage_ecoles",
                "sre_pourcentage_commerce",
                "sre_pourcentage_restauration",
                "sre_pourcentage_lieux_de_rassemblement",
                "sre_pourcentage_hopitaux",
                "sre_pourcentage_industrie",
                "sre_pourcentage_depots",
                "sre_pourcentage_installations_sportives",
                "sre_pourcentage_piscines_couvertes",
                "agent_energetique_ef_mazout_kg",
                "agent_energetique_ef_mazout_litres",
                "agent_energetique_ef_mazout_kwh",
                "agent_energetique_ef_gaz_naturel_m3",
                "agent_energetique_ef_gaz_naturel_kwh",
                "agent_energetique_ef_bois_buches_dur_stere",
                "agent_energetique_ef_bois_buches_tendre_stere",
                "agent_energetique_ef_bois_buches_tendre_kwh",
                "agent_energetique_ef_pellets_m3",
                "agent_energetique_ef_pellets_kg",
                "agent_energetique_ef_pellets_kwh",
                "agent_energetique_ef_plaquettes_m3",
                "agent_energetique_ef_plaquettes_kwh",
                "agent_energetique_ef_cad_kwh",
                "agent_energetique_ef_electricite_pac_kwh",
                "agent_energetique_ef_electricite_directe_kwh",
                "agent_energetique_ef_autre_kwh",
                "periode_start",
                "periode_end",
                "ef_avant_corr_kwh_m2",
                "ef_objectif_pondere_kwh_m2",
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2",
                "delta_ef_visee_kwh_m2",
                "facteur_ponderation_moyen",
                "atteinte_objectif",
                "repartition_energie_finale_partie_renovee_chauffage",
                "repartition_energie_finale_partie_renovee_ecs",
                "repartition_energie_finale_partie_surelevee_chauffage",
                "repartition_energie_finale_partie_surelevee_ecs",
            ]

            for field in fields_to_check:
                if not is_valid(st.session_state["data_site"].get(field)):
                    invalid_fields.append(field)

            return invalid_fields

        # Generate the PDF report
        invalid_fields = check_validity()
        if (
            invalid_fields is not None
            and st.session_state["data_site"].get("facteur_ponderation_moyen")
            is not None
            and st.session_state["data_site"].get("facteur_ponderation_moyen") > 0
            and st.session_state["data_site"].get("ef_avant_corr_kwh_m2") > 0
            and st.session_state["data_site"].get(
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2",
                0,
            )
            > 0
            and st.session_state["data_site"].get("ef_objectif_pondere_kwh_m2") > 0
            and st.session_state["data_site"].get("atteinte_objectif") > 0
            and st.session_state["data_site"].get("somme_repartition_energie_finale")
            == 100
            and st.session_state["data_site"].get("somme_pourcentage_affectations")
            == 100
            and st.session_state["data_site"].get("somme_agents_energetiques_mj", 0) > 0
        ):
            if st.button("Générer le rapport PDF"):
                pdf_data, file_name = generate_pdf(st.session_state["data_site"])
                st.download_button(
                    label="Cliquez ici pour télécharger le PDF",
                    data=pdf_data,
                    file_name=file_name,
                    mime="application/pdf",
                )
                st.success(
                    f"Rapport PDF '{file_name}' généré avec succès! Cliquez sur le bouton ci-dessus pour le télécharger."
                )

                # add date to data_rapport
                st.session_state["data_site"][
                    "date_rapport"
                ] = datetime.datetime.now()

                # Remove the _id field if it exists to ensure MongoDB generates a new one
                if "_id" in st.session_state["data_site"]:
                    del st.session_state["data_site"]["_id"]

                # Send data_site to MongoDB
                x = mycol_historique_sites.insert_one(st.session_state["data_site"])
        else:
            st.warning(
                "Toutes les informations nécessaires ne sont pas disponibles pour générer le PDF."
            )
            invalid_fields_list = "\n".join([f"- {field}" for field in invalid_fields])
            if len(invalid_fields_list) > 0:
                st.warning(f"Les champs suivants sont invalides ou manquants:\n\n{invalid_fields_list}")
            
            # Check and display which conditions are not met
            conditions_not_met = []
            
            if invalid_fields is None:
                conditions_not_met.append("Des champs sont invalides")
                
            if not st.session_state["data_site"].get("facteur_ponderation_moyen"):
                conditions_not_met.append("Facteur de pondération moyen manquant ou égal à 0")
                
            if not st.session_state["data_site"].get("ef_avant_corr_kwh_m2", 0) > 0:
                conditions_not_met.append("Énergie finale avant correction ≤ 0")
                
            if not st.session_state["data_site"].get("energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2", 0) > 0:
                conditions_not_met.append("Énergie finale après travaux ≤ 0")
                
            if not st.session_state["data_site"].get("ef_objectif_pondere_kwh_m2", 0) > 0:
                conditions_not_met.append("Objectif d'énergie finale pondéré ≤ 0")
                
            if not st.session_state["data_site"].get("atteinte_objectif", 0) > 0:
                conditions_not_met.append("Atteinte de l'objectif ≤ 0")
                
            if st.session_state["data_site"].get("somme_repartition_energie_finale") != 100:
                conditions_not_met.append("La somme des répartitions d'énergie finale n'est pas égale à 100%")
                
            if st.session_state["data_site"].get("somme_pourcentage_affectations") != 100:
                conditions_not_met.append("La somme des pourcentages d'affectations n'est pas égale à 100%")
                
            if not st.session_state["data_site"].get("somme_agents_energetiques_mj", 0) > 0:
                conditions_not_met.append("La somme des agents énergétiques ≤ 0")
            
            if conditions_not_met:
                st.text("Conditions non respectées:")
                for condition in conditions_not_met:
                    st.text(f"• {condition}")

    if username_login == "admin":
        with tab7:
            data_admin = load_projets_admin()
            df = pd.DataFrame(data_admin)
            display_admin_dashboard(df)
        with tab8:
            # Admin - Base de données
            display_database_management(mycol_historique_sites, load_projets_admin())


elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
