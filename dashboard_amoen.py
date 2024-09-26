"""
TODO
- renseigner les consommations ECS séparées du total
- déplacer les valeurs fixes tel que DJ_TEMPERATURE_REFERENCE vers le helper 
"""

import os
import datetime
import time
import io
from io import BytesIO
import numpy as np
import pandas as pd
import smtplib
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

st.set_page_config(page_title="AMOEN Dashboard", page_icon=":bar_chart:", layout="wide")
import seaborn as sns
import tempfile
from datetime import date

import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib

matplotlib.use("Agg")
import plotly.express as px
import altair as alt

from pymongo import MongoClient
from bson import ObjectId

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from sections.helpers.validation_saisie import (
    validate_input,
    validate_input_affectation,
    validate_agent_energetique_input,
    validate_energie_input,
)
from sections.helpers.calcul_dj import get_meteo_data, calcul_dj_periode
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
    avusy_consommation_energie_elec_periode,
    update_existing_data_avusy,
)

os.environ["USE_ARROW_extension"] = "1"

## Météo
DJ_REF_ANNUELS = 3260.539010836340
DJ_TEMPERATURE_REFERENCE = 20

## Agents énergétiques conversion
CONVERSION_MAZOUT_KG_MJ = 44.8
CONVERSION_MAZOUT_LITRES_MJ = 44.8 * 0.84
CONVERSION_MAZOUT_KWH_MJ = 3.6
CONVERSION_GAZ_NATUREL_M3_MJ = 38.5
CONVERSION_GAZ_NATUREL_KWH_MJ = 3.6
CONVERSION_BOIS_BUCHES_DUR_STERE_MJ = 7960
CONVERSION_BOIS_BUCHES_TENDRE_STERE_MJ = 5572
CONVERSION_BOIS_BUCHES_TENDRE_KWH_MJ = 3.6
CONVERSION_PELLETS_M3_MJ = 13332
CONVERSION_PELLETS_KG_MJ = 20.2
CONVERSION_PELLETS_KWH_MJ = 3.6
CONVERSION_PLAQUETTES_M3_MJ = 200 * 20
CONVERSION_PLAQUETTES_KWH_MJ = 3.6 * 13.1 / 11.6
CONVERSION_CAD_KWH_MJ = 3.6
CONVERSION_ELECTRICITE_PAC_KWH_MJ = 3.6
CONVERSION_ELECTRICITE_DIRECTE_KWH_MJ = 3.6
CONVERSION_AUTRE_KWH_MJ = 3.6

## Agent énergétique facteur de pondération
FACTEUR_PONDERATION_MAZOUT = 1
FACTEUR_PONDERATION_GAZ_NATUREL = 1
FACTEUR_PONDERATION_BOIS_BUCHES_DUR = 1
FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE = 1
FACTEUR_PONDERATION_PELLETS = 1
FACTEUR_PONDERATION_PLAQUETTES = 1
FACTEUR_PONDERATION_CAD = 1
FACTEUR_PONDERATION_ELECTRICITE_PAC = 2
FACTEUR_PONDERATION_ELECTRICITE_DIRECTE = 2
FACTEUR_PONDERATION_AUTRE = 1

# Variable pour la mise a jour de la météo
last_update_time_meteo = datetime.datetime(2021, 1, 1)

# IDC query
FIELDS = "*"
URL_INDICE_MOYENNES_3_ANS = "https://vector.sitg.ge.ch/arcgis/rest/services/Hosted/SCANE_INDICE_MOYENNES_3_ANS/FeatureServer/0/query"

# Variables pour l'envoi de mail
# GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
# GMAIL_PASSWORD = st.secrets["GMAIL_PASSWORD"]
# TO_ADRESS_EMAIL = st.secrets["TO_ADRESS_EMAIL"]

MONGODB_URI = st.secrets["MONGODB_URI"]

# BD mongodb
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db_sites = client["amoen_ancienne_methodo"]
mycol_historique_sites = db_sites["historique"]
mycol_authentification_site = db_sites["authentification"]
mycol_historique_index_avusy = db_sites["avusy"]

if "data_site" not in st.session_state:
    st.session_state["data_site"] = {}


@st.cache_data
def load_project_data(project_name):
    data = mycol_historique_sites.find_one({"nom_projet": project_name})
    return data


@st.cache_data
def load_projets_liste(project_name):
    if username_login == "admin":
        nom_projets_liste = mycol_historique_sites.distinct("nom_projet")
    else:
        nom_projets_liste = mycol_historique_sites.distinct(
            "nom_projet", {"amoen_id": username}
        )
    return nom_projets_liste


def load_projets_admin():
    # Retrieve all documents from the collection
    data = list(mycol_historique_sites.find({}))
    return data


# Mise à jour météo
now = datetime.datetime.now()
if (now - last_update_time_meteo).days > 1:
    last_update_time_meteo = now
    df_meteo_tre200d0 = get_meteo_data()
    st.session_state.df_meteo_tre200d0 = df_meteo_tre200d0


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
    with st.sidebar.popover("Change password"):
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
                st.success("Password modified successfully")
                # update a specific field in mongodb
                mycol_authentification_site.update_one(
                    {"_id": ObjectId("66ad0b102f5cc6cb3c64e1d1")}, {"$set": config}
                )
        except Exception as e:
            st.error(e)
    authenticator.logout(location="sidebar")
    st.sidebar.write("You are logged as: ", st.session_state["username"])

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
        tabs.append("6 Admin")
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tabs)
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

        st.subheader("Liens utiles")
        st.markdown(
            "**[GitHub de la dashboard](https://github.com/denisiglesiasgarcia/amoen_calcul_objectif_dashboard)**",
            unsafe_allow_html=True,
        )

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
                    value=data_sites_db["sre_renovation_m2"],
                    help="La SRE rénovée est la partie du batiment qui a été rénovée, la surélévation/extension n'est pas incluse",
                )
                validate_input("SRE rénovée:", sre_renovation_m2, "m²")
                st.session_state["data_site"]["sre_renovation_m2"] = float(
                    sre_renovation_m2
                )
            with tab2_col02:
                st.session_state["data_site"]["adresse_projet"] = st.text_input(
                    "Adresse(s) du projet", value=data_sites_db["adresse_projet"]
                )
                st.session_state["data_site"]["amoen_id"] = st.text_input(
                    "AMOen", value=data_sites_db["amoen_id"]
                )

            try:
                if st.session_state["data_site"]["sre_renovation_m2"] <= 0:
                    st.warning(
                        f"SRE doit être > 0 ({st.session_state['data_site']['sre_renovation_m2']})"
                    )
            except ValueError:
                st.warning("Problème dans la somme des pourcentages des affectations")

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
                    value=data_sites_db["ef_avant_corr_kwh_m2"],
                    help="Surélévation: C92 / Rénovation: C61",
                )
                if ef_avant_corr_kwh_m2 != "0":
                    validate_energie_input(
                        "Ef,avant,corr:", ef_avant_corr_kwh_m2, "kWh/m²/an", "MJ/m²/an"
                    )
                st.session_state["data_site"]["ef_avant_corr_kwh_m2"] = float(
                    ef_avant_corr_kwh_m2
                )
                try:
                    if float(ef_avant_corr_kwh_m2) <= 0:
                        st.warning("Ef,avant,corr [kWh/m²/an] doit être supérieur à 0")
                except ValueError:
                    st.warning("Problème dans Ef,avant,corr [kWh/m²/an]")

            with tab2_col6:
                ef_objectif_pondere_kwh_m2 = st.text_input(
                    "Ef,obj * fp [kWh/m²/an]:",
                    value=data_sites_db["ef_objectif_pondere_kwh_m2"],
                    help="Surélévation: C94 / Rénovation: C63",
                )
                if ef_objectif_pondere_kwh_m2 != "0":
                    validate_energie_input(
                        "Ef,obj * fp:",
                        ef_objectif_pondere_kwh_m2,
                        "kWh/m²/an",
                        "MJ/m²/an",
                    )
                st.session_state["data_site"]["ef_objectif_pondere_kwh_m2"] = float(
                    ef_objectif_pondere_kwh_m2
                )
                try:
                    if float(ef_objectif_pondere_kwh_m2) <= 0:
                        st.warning("Ef,obj *fp [kWh/m²/an] doit être supérieur à 0")
                except ValueError:
                    st.warning("Problème dans Ef,obj *fp [kWh/m²/an]")

            st.session_state["data_site"]["delta_ef_visee_kwh_m2"] = (
                st.session_state["data_site"]["ef_avant_corr_kwh_m2"]
                - st.session_state["data_site"]["ef_objectif_pondere_kwh_m2"]
            )

            st.markdown(
                '<span style="font-size:1.2em;">**Répartition énergie finale ECS/Chauffage**</span>',
                unsafe_allow_html=True,
            )

            # st.text("Ces données se trouvent dans le tableau Excel de fixation d'objectif de performances:\n\
            # - Surélévation: C77:C81\n\
            # - Rénovation: C49:C50")
            # Determine if the checkbox should be auto-checked
            tab2_col7, tab2_col8 = st.columns(2)
            with tab2_col7:
                # Répartition énergie finale
                repartition_energie_finale_partie_renovee_chauffage = st.text_input(
                    "Chauffage partie rénovée [%]",
                    value=data_sites_db[
                        "repartition_energie_finale_partie_renovee_chauffage"
                    ],
                    help="Surélévation: C77 / Rénovation: C49",
                )
                if repartition_energie_finale_partie_renovee_chauffage != "0":
                    validate_input(
                        "Répartition EF - Chauffage partie rénovée:",
                        repartition_energie_finale_partie_renovee_chauffage,
                        "%",
                    )
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_chauffage"
                ] = float(repartition_energie_finale_partie_renovee_chauffage)

                repartition_energie_finale_partie_surelevee_chauffage = st.text_input(
                    "Chauffage partie surélévée",
                    value=data_sites_db[
                        "repartition_energie_finale_partie_surelevee_chauffage"
                    ],
                    help="C79",
                )
                if repartition_energie_finale_partie_surelevee_chauffage != "0":
                    validate_input(
                        "Répartition EF - Chauffage partie surélévée:",
                        repartition_energie_finale_partie_surelevee_chauffage,
                        "%",
                    )
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_surelevee_chauffage"
                ] = float(repartition_energie_finale_partie_surelevee_chauffage)

            with tab2_col8:
                repartition_energie_finale_partie_renovee_ecs = st.text_input(
                    "ECS partie rénovée [%]",
                    value=data_sites_db[
                        "repartition_energie_finale_partie_renovee_ecs"
                    ],
                    help="Surélévation: C78 / Rénovation: C50",
                )
                if repartition_energie_finale_partie_renovee_ecs != "0":
                    validate_input(
                        "Répartition EF - ECS partie rénovée:",
                        repartition_energie_finale_partie_renovee_ecs,
                        "%",
                    )
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_ecs"
                ] = float(repartition_energie_finale_partie_renovee_ecs)

                repartition_energie_finale_partie_surelevee_ecs = st.text_input(
                    "ECS partie surélévée [%]",
                    value=data_sites_db[
                        "repartition_energie_finale_partie_surelevee_ecs"
                    ],
                    help="C80",
                )
                if repartition_energie_finale_partie_surelevee_ecs != "0":
                    validate_input(
                        "Répartition EF - ECS partie surélevée:",
                        repartition_energie_finale_partie_surelevee_ecs,
                        "%",
                    )
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_surelevee_ecs"
                ] = float(repartition_energie_finale_partie_surelevee_ecs)

            # Validation somme des pourcentages
            try:
                repartition_ef_somme_avertissement = (
                    st.session_state["data_site"][
                        "repartition_energie_finale_partie_renovee_chauffage"
                    ]
                    + st.session_state["data_site"][
                        "repartition_energie_finale_partie_renovee_ecs"
                    ]
                    + st.session_state["data_site"][
                        "repartition_energie_finale_partie_surelevee_chauffage"
                    ]
                    + st.session_state["data_site"][
                        "repartition_energie_finale_partie_surelevee_ecs"
                    ]
                )
                if repartition_ef_somme_avertissement != 100:
                    st.warning(
                        f"La somme des pourcentages de répartition de l'énergie finale doit être égale à 100% ({repartition_ef_somme_avertissement}%)"
                    )
            except ValueError:
                st.warning(
                    "Problème dans la somme des pourcentages de répartition de l'énergie finale"
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
                    df_meteo_tre200d0["time"].max()
                ) - pd.DateOffset(days=365)
                periode_start = st.date_input(
                    "Début de la période",
                    datetime.date(last_year.year, last_year.month, last_year.day),
                )

            with tab2_col4:
                fin_periode_txt = f"Fin de la période (météo disponible jusqu'au: {df_meteo_tre200d0['time'].max().strftime('%Y-%m-%d')})"
                max_date = pd.to_datetime(df_meteo_tre200d0["time"].max())
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
                # SRE pourcentage
                st.markdown(
                    '<span style="font-size:1.2em;">**Affectations**</span>',
                    unsafe_allow_html=True,
                )

                options_sre_pourcentage = [
                    {
                        "label": "Habitat collectif (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_habitat_collectif",
                        "value": 0.0,
                    },
                    {
                        "label": "Habitat individuel (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_habitat_individuel",
                        "value": 0.0,
                    },
                    {
                        "label": "Administration (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_administration",
                        "value": 0.0,
                    },
                    {
                        "label": "Écoles (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_ecoles",
                        "value": 0.0,
                    },
                    {
                        "label": "Commerce (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_commerce",
                        "value": 0.0,
                    },
                    {
                        "label": "Restauration (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_restauration",
                        "value": 0.0,
                    },
                    {
                        "label": "Lieux de rassemblement (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_lieux_de_rassemblement",
                        "value": 0.0,
                    },
                    {
                        "label": "Hôpitaux (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_hopitaux",
                        "value": 0.0,
                    },
                    {
                        "label": "Industrie (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_industrie",
                        "value": 0.0,
                    },
                    {
                        "label": "Dépôts (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_depots",
                        "value": 0.0,
                    },
                    {
                        "label": "Installations sportives (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_installations_sportives",
                        "value": 0.0,
                    },
                    {
                        "label": "Piscines couvertes (%)",
                        "unit": "%",
                        "variable": "sre_pourcentage_piscines_couvertes",
                        "value": 0.0,
                    },
                ]

                # Pre-select options based on database values
                if data_sites_db:
                    selected_sre_pourcentage = [
                        option["label"]
                        for option in options_sre_pourcentage
                        if data_sites_db.get(option["variable"], 0) > 0
                    ]
                else:
                    selected_sre_pourcentage = []

                selected_sre_pourcentage = st.multiselect(
                    "Affectation(s):",
                    [option["label"] for option in options_sre_pourcentage],
                    default=selected_sre_pourcentage,
                )

                sre_pourcentage = {}

                if data_sites_db:
                    for option in options_sre_pourcentage:
                        if option["label"] in selected_sre_pourcentage:
                            value = st.text_input(
                                option["label"] + ":",
                                value=data_sites_db[option["variable"]],
                            )
                            if value != "0":
                                validate_input_affectation(
                                    option["label"] + ":",
                                    value,
                                    option["unit"],
                                    sre_renovation_m2,
                                )
                                option["value"] = float(value)
                else:
                    for option in options_sre_pourcentage:
                        if option["label"] in selected_sre_pourcentage:
                            value = st.text_input(option["label"] + ":", value=0.0)
                            if value != "0":
                                validate_input_affectation(
                                    option["label"] + ":",
                                    value,
                                    option["unit"],
                                    sre_renovation_m2,
                                )
                                option["value"] = float(value)

                st.session_state["data_site"]["sre_pourcentage_habitat_collectif"] = (
                    options_sre_pourcentage[0]["value"]
                )
                st.session_state["data_site"]["sre_pourcentage_habitat_individuel"] = (
                    options_sre_pourcentage[1]["value"]
                )
                st.session_state["data_site"]["sre_pourcentage_administration"] = (
                    options_sre_pourcentage[2]["value"]
                )
                st.session_state["data_site"]["sre_pourcentage_ecoles"] = (
                    options_sre_pourcentage[3]["value"]
                )
                st.session_state["data_site"]["sre_pourcentage_commerce"] = (
                    options_sre_pourcentage[4]["value"]
                )
                st.session_state["data_site"]["sre_pourcentage_restauration"] = (
                    options_sre_pourcentage[5]["value"]
                )
                st.session_state["data_site"][
                    "sre_pourcentage_lieux_de_rassemblement"
                ] = options_sre_pourcentage[6]["value"]
                st.session_state["data_site"]["sre_pourcentage_hopitaux"] = (
                    options_sre_pourcentage[7]["value"]
                )
                st.session_state["data_site"]["sre_pourcentage_industrie"] = (
                    options_sre_pourcentage[8]["value"]
                )
                st.session_state["data_site"]["sre_pourcentage_depots"] = (
                    options_sre_pourcentage[9]["value"]
                )
                st.session_state["data_site"][
                    "sre_pourcentage_installations_sportives"
                ] = options_sre_pourcentage[10]["value"]
                st.session_state["data_site"]["sre_pourcentage_piscines_couvertes"] = (
                    options_sre_pourcentage[11]["value"]
                )

                # Somme des pourcentages
                try:
                    sre_pourcentage_affectations_somme_avertisement = (
                        float(
                            st.session_state["data_site"][
                                "sre_pourcentage_habitat_collectif"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "sre_pourcentage_habitat_individuel"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "sre_pourcentage_administration"
                            ]
                        )
                        + float(st.session_state["data_site"]["sre_pourcentage_ecoles"])
                        + float(
                            st.session_state["data_site"]["sre_pourcentage_commerce"]
                        )
                        + float(
                            st.session_state["data_site"][
                                "sre_pourcentage_restauration"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "sre_pourcentage_lieux_de_rassemblement"
                            ]
                        )
                        + float(
                            st.session_state["data_site"]["sre_pourcentage_hopitaux"]
                        )
                        + float(
                            st.session_state["data_site"]["sre_pourcentage_industrie"]
                        )
                        + float(st.session_state["data_site"]["sre_pourcentage_depots"])
                        + float(
                            st.session_state["data_site"][
                                "sre_pourcentage_installations_sportives"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "sre_pourcentage_piscines_couvertes"
                            ]
                        )
                    )
                    if sre_pourcentage_affectations_somme_avertisement != 100:
                        st.warning(
                            f"Somme des pourcentages doit être égale à 100% ({sre_pourcentage_affectations_somme_avertisement})"
                        )
                except ValueError:
                    st.warning(
                        "Problème dans la somme des pourcentages des affectations"
                    )

            with tab2_col2:
                # Agents énergétiques
                st.markdown(
                    '<span style="font-size:1.2em;">**Agents énergétiques utilisés**</span>',
                    unsafe_allow_html=True,
                )

                options_agent_energetique_ef = [
                    {
                        "label": "CAD (kWh)",
                        "unit": "kWh",
                        "variable": "agent_energetique_ef_cad_kwh",
                        "value": 0.0,
                    },
                    {
                        "label": "Electricité pour les PAC (kWh)",
                        "unit": "kWh",
                        "variable": "agent_energetique_ef_electricite_pac_kwh",
                        "value": 0.0,
                    },
                    {
                        "label": "Electricité directe (kWh)",
                        "unit": "kWh",
                        "variable": "agent_energetique_ef_electricite_directe_kwh",
                        "value": 0.0,
                    },
                    {
                        "label": "Gaz naturel (m³)",
                        "unit": "m³",
                        "variable": "agent_energetique_ef_gaz_naturel_m3",
                        "value": 0.0,
                    },
                    {
                        "label": "Gaz naturel (kWh)",
                        "unit": "kWh",
                        "variable": "agent_energetique_ef_gaz_naturel_kwh",
                        "value": 0.0,
                    },
                    {
                        "label": "Mazout (litres)",
                        "unit": "litres",
                        "variable": "agent_energetique_ef_mazout_litres",
                        "value": 0.0,
                    },
                    {
                        "label": "Mazout (kg)",
                        "unit": "kg",
                        "variable": "agent_energetique_ef_mazout_kg",
                        "value": 0.0,
                    },
                    {
                        "label": "Mazout (kWh)",
                        "unit": "kWh",
                        "variable": "agent_energetique_ef_mazout_kwh",
                        "value": 0.0,
                    },
                    {
                        "label": "Bois buches dur (stère)",
                        "unit": "stère",
                        "variable": "agent_energetique_ef_bois_buches_dur_stere",
                        "value": 0.0,
                    },
                    {
                        "label": "Bois buches tendre (stère)",
                        "unit": "stère",
                        "variable": "agent_energetique_ef_bois_buches_tendre_stere",
                        "value": 0.0,
                    },
                    {
                        "label": "Bois buches tendre (kWh)",
                        "unit": "kWh",
                        "variable": "agent_energetique_ef_bois_buches_tendre_kwh",
                        "value": 0.0,
                    },
                    {
                        "label": "Pellets (m³)",
                        "unit": "m³",
                        "variable": "agent_energetique_ef_pellets_m3",
                        "value": 0.0,
                    },
                    {
                        "label": "Pellets (kg)",
                        "unit": "kg",
                        "variable": "agent_energetique_ef_pellets_kg",
                        "value": 0.0,
                    },
                    {
                        "label": "Pellets (kWh)",
                        "unit": "kWh",
                        "variable": "agent_energetique_ef_pellets_kwh",
                        "value": 0.0,
                    },
                    {
                        "label": "Plaquettes (m³)",
                        "unit": "m³",
                        "variable": "agent_energetique_ef_plaquettes_m3",
                        "value": 0.0,
                    },
                    {
                        "label": "Plaquettes (kWh)",
                        "unit": "kWh",
                        "variable": "agent_energetique_ef_plaquettes_kwh",
                        "value": 0.0,
                    },
                    {
                        "label": "Autre (kWh)",
                        "unit": "kWh",
                        "variable": "agent_energetique_ef_autre_kwh",
                        "value": 0.0,
                    },
                ]

                if st.session_state["data_site"]["nom_projet"] == "Avusy 10-10A":
                    conso_elec_pac_immeuble, nearest_start_date, nearest_end_date = (
                        avusy_consommation_energie_elec_periode(
                            st.session_state["data_site"]["periode_start"],
                            st.session_state["data_site"]["periode_end"],
                            mycol_historique_index_avusy,
                        )
                    )
                    if (
                        conso_elec_pac_immeuble
                        and nearest_start_date.date()
                        == st.session_state["data_site"]["periode_start"].date()
                        and nearest_end_date.date()
                        == st.session_state["data_site"]["periode_end"].date()
                    ):
                        success = st.success("Dates OK!")
                        time.sleep(3)
                        success.empty()
                    else:
                        st.warning(
                            f"Pas de données pour ces dates, dates les plus proches: du {nearest_start_date.date()} au {nearest_end_date.date()}"
                        )

                if data_sites_db:
                    selected_agent_energetique_ef = [
                        option["label"]
                        for option in options_agent_energetique_ef
                        if data_sites_db.get(option["variable"], 0) > 0
                    ]
                else:
                    selected_agent_energetique_ef = []

                selected_agent_energetique_ef = st.multiselect(
                    "Agent(s) énergétique(s):",
                    [option["label"] for option in options_agent_energetique_ef],
                    default=selected_agent_energetique_ef,
                )

                if st.session_state["data_site"]["nom_projet"] != "Avusy 10-10A":
                    for option in options_agent_energetique_ef:
                        if option["label"] in selected_agent_energetique_ef:
                            value = st.text_input(option["label"] + ":", value=0.0)
                            if value != "0":
                                value = validate_agent_energetique_input(
                                    option["label"] + ":", value, option["unit"]
                                )
                                option["value"] = float(value)

                    st.session_state["data_site"]["agent_energetique_ef_mazout_kg"] = (
                        options_agent_energetique_ef[6]["value"]
                    )
                    st.session_state["data_site"][
                        "agent_energetique_ef_mazout_litres"
                    ] = options_agent_energetique_ef[5]["value"]
                    st.session_state["data_site"]["agent_energetique_ef_mazout_kwh"] = (
                        options_agent_energetique_ef[7]["value"]
                    )
                    st.session_state["data_site"][
                        "agent_energetique_ef_gaz_naturel_m3"
                    ] = options_agent_energetique_ef[4]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_gaz_naturel_kwh"
                    ] = options_agent_energetique_ef[3]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_dur_stere"
                    ] = options_agent_energetique_ef[8]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_tendre_stere"
                    ] = options_agent_energetique_ef[9]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_tendre_kwh"
                    ] = options_agent_energetique_ef[10]["value"]
                    st.session_state["data_site"]["agent_energetique_ef_pellets_m3"] = (
                        options_agent_energetique_ef[11]["value"]
                    )
                    st.session_state["data_site"]["agent_energetique_ef_pellets_kg"] = (
                        options_agent_energetique_ef[12]["value"]
                    )
                    st.session_state["data_site"][
                        "agent_energetique_ef_pellets_kwh"
                    ] = options_agent_energetique_ef[13]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_plaquettes_m3"
                    ] = options_agent_energetique_ef[14]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_plaquettes_kwh"
                    ] = options_agent_energetique_ef[15]["value"]
                    st.session_state["data_site"]["agent_energetique_ef_cad_kwh"] = (
                        options_agent_energetique_ef[0]["value"]
                    )
                    st.session_state["data_site"][
                        "agent_energetique_ef_electricite_pac_kwh"
                    ] = options_agent_energetique_ef[1]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_electricite_directe_kwh"
                    ] = options_agent_energetique_ef[2]["value"]
                    st.session_state["data_site"]["agent_energetique_ef_autre_kwh"] = (
                        options_agent_energetique_ef[16]["value"]
                    )

                elif st.session_state["data_site"]["nom_projet"] == "Avusy 10-10A":
                    for option in options_agent_energetique_ef:
                        if option["label"] in selected_agent_energetique_ef:
                            if option["label"] == "Electricité pour les PAC (kWh)":
                                value = st.text_input(
                                    option["label"] + ":",
                                    value=round(conso_elec_pac_immeuble, 1),
                                )
                                if value != "0":
                                    value = validate_agent_energetique_input(
                                        option["label"] + ":", value, option["unit"]
                                    )
                                    option["value"] = float(value)
                            else:
                                value = st.text_input(option["label"] + ":", value=0.0)
                                if value != "0":
                                    value = validate_agent_energetique_input(
                                        option["label"] + ":", value, option["unit"]
                                    )
                                    option["value"] = float(value)

                    st.session_state["data_site"]["agent_energetique_ef_mazout_kg"] = (
                        options_agent_energetique_ef[6]["value"]
                    )
                    st.session_state["data_site"][
                        "agent_energetique_ef_mazout_litres"
                    ] = options_agent_energetique_ef[5]["value"]
                    st.session_state["data_site"]["agent_energetique_ef_mazout_kwh"] = (
                        options_agent_energetique_ef[7]["value"]
                    )
                    st.session_state["data_site"][
                        "agent_energetique_ef_gaz_naturel_m3"
                    ] = options_agent_energetique_ef[4]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_gaz_naturel_kwh"
                    ] = options_agent_energetique_ef[3]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_dur_stere"
                    ] = options_agent_energetique_ef[8]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_tendre_stere"
                    ] = options_agent_energetique_ef[9]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_tendre_kwh"
                    ] = options_agent_energetique_ef[10]["value"]
                    st.session_state["data_site"]["agent_energetique_ef_pellets_m3"] = (
                        options_agent_energetique_ef[11]["value"]
                    )
                    st.session_state["data_site"]["agent_energetique_ef_pellets_kg"] = (
                        options_agent_energetique_ef[12]["value"]
                    )
                    st.session_state["data_site"][
                        "agent_energetique_ef_pellets_kwh"
                    ] = options_agent_energetique_ef[13]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_plaquettes_m3"
                    ] = options_agent_energetique_ef[14]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_plaquettes_kwh"
                    ] = options_agent_energetique_ef[15]["value"]
                    st.session_state["data_site"]["agent_energetique_ef_cad_kwh"] = (
                        options_agent_energetique_ef[0]["value"]
                    )
                    st.session_state["data_site"][
                        "agent_energetique_ef_electricite_pac_kwh"
                    ] = options_agent_energetique_ef[1]["value"]
                    st.session_state["data_site"][
                        "agent_energetique_ef_electricite_directe_kwh"
                    ] = options_agent_energetique_ef[2]["value"]
                    st.session_state["data_site"]["agent_energetique_ef_autre_kwh"] = (
                        options_agent_energetique_ef[16]["value"]
                    )

                try:
                    agent_energetique_ef_somme_avertissement = (
                        float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_mazout_kg"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_mazout_litres"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_mazout_kwh"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_gaz_naturel_m3"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_gaz_naturel_kwh"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_bois_buches_dur_stere"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_bois_buches_tendre_stere"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_bois_buches_tendre_kwh"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_pellets_m3"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_pellets_kg"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_pellets_kwh"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_plaquettes_m3"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_plaquettes_kwh"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_cad_kwh"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_electricite_pac_kwh"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_electricite_directe_kwh"
                            ]
                        )
                        + float(
                            st.session_state["data_site"][
                                "agent_energetique_ef_autre_kwh"
                            ]
                        )
                    )
                    if agent_energetique_ef_somme_avertissement <= 0:
                        st.warning(
                            f"Veuillez renseigner une quantité d'énergie utilisée sur la période ({agent_energetique_ef_somme_avertissement})"
                        )
                except ValueError:
                    st.warning("Problème dans la somme des agents énergétiques")

            st.session_state["data_site"]["annees_calcul_idc_avant_travaux"] = (
                data_sites_db["annees_calcul_idc_avant_travaux"]
            )
            st.session_state["data_site"]["sre_extension_surelevation_m2"] = (
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
            avusy_consommation_energie_dashboard(
                st.session_state["data_site"]["periode_start"],
                st.session_state["data_site"]["periode_end"],
                mycol_historique_index_avusy,
            )
            update_existing_data_avusy(mycol_historique_index_avusy)

    with tab3:
        columns = [
            "Dénomination",
            "Valeur",
            "Unité",
            "Commentaire",
            "Excel",
            "Variable/Formule",
        ]
        df_periode_list = []
        df_list = []

        # C65 → Début période
        df_periode_list.append(
            {
                "Dénomination": "Début période",
                "Valeur": st.session_state["data_site"]["periode_start"],
                "Unité": "-",
                "Commentaire": "Date de début de la période",
                "Excel": "C65",
                "Variable/Formule": "periode_start",
            }
        )

        # C66 → Fin période
        df_periode_list.append(
            {
                "Dénomination": "Fin période",
                "Valeur": st.session_state["data_site"]["periode_end"],
                "Unité": "-",
                "Commentaire": "Date de fin de la période",
                "Excel": "C66",
                "Variable/Formule": "periode_end",
            }
        )

        # C67 → Nombre de jours
        df_list.append(
            {
                "Dénomination": "Nombre de jour(s)",
                "Valeur": st.session_state["data_site"]["periode_nb_jours"],
                "Unité": "jour(s)",
                "Commentaire": "Nombre de jour(s) dans la période",
                "Excel": "C67",
                "Variable/Formule": "periode_nb_jours",
            }
        )

        # C86 → Répartition en énergie finale - Chauffage partie rénovée
        df_list.append(
            {
                "Dénomination": "Répartition en énergie finale (chauffage) pour la partie rénové",
                "Valeur": st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_chauffage"
                ],
                "Unité": "%",
                "Commentaire": "",
                "Excel": "C86",
                "Variable/Formule": "repartition_energie_finale_partie_renovee_chauffage",
            }
        )

        # C87 → Répartition en énergie finale - ECS partie rénovée
        df_list.append(
            {
                "Dénomination": "Répartition en énergie finale (ECS) pour la partie rénové",
                "Valeur": st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_ecs"
                ],
                "Unité": "%",
                "Commentaire": "",  # You can add a comment if needed
                "Excel": "C87",
                "Variable/Formule": "repartition_energie_finale_partie_renovee_ecs",
            }
        )

        # C88 → Répartition en énergie finale - Chauffage partie surélévée
        df_list.append(
            {
                "Dénomination": "Répartition en énergie finale (chauffage) pour la partie surélévée",
                "Valeur": st.session_state["data_site"][
                    "repartition_energie_finale_partie_surelevee_chauffage"
                ],
                "Unité": "%",
                "Commentaire": "0 if no surélévation",  # You can add a comment if needed
                "Excel": "C88",
                "Variable/Formule": "repartition_energie_finale_partie_surelevee_chauffage",
            }
        )

        # C89 → Répartition EF - ECS partie surélévée
        df_list.append(
            {
                "Dénomination": "Répartition en énergie finale - ECS partie surélévée",
                "Valeur": st.session_state["data_site"][
                    "repartition_energie_finale_partie_surelevee_ecs"
                ],
                "Unité": "%",
                "Commentaire": "Part d'énergie finale (ECS) pour la partie surélévée. 0 s'il n'y a pas de surélévation",
                "Excel": "C89",
                "Variable/Formule": "repartition_energie_finale_partie_surelevee_ecs",
            }
        )

        # C91 → Part EF pour partie rénové (Chauffage + ECS)
        st.session_state["data_site"][
            "repartition_energie_finale_partie_renovee_somme"
        ] = (
            st.session_state["data_site"][
                "repartition_energie_finale_partie_renovee_chauffage"
            ]
            + st.session_state["data_site"][
                "repartition_energie_finale_partie_renovee_ecs"
            ]
        )
        df_list.append(
            {
                "Dénomination": "Part EF pour partie rénové (Chauffage + ECS)",
                "Valeur": st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_somme"
                ],
                "Unité": "%",
                "Commentaire": "Part d'énergie finale (Chauffage + ECS) pour la partie rénové. 100% si pas de surélévation",
                "Excel": "C91",
                "Variable/Formule": "repartition_energie_finale_partie_renovee_somme = repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_renovee_ecs",
            }
        )

        # C92 → Est. ECS/ECS annuelle
        st.session_state["data_site"]["estimation_ecs_annuel"] = (
            st.session_state["data_site"]["periode_nb_jours"] / 365
        )
        df_list.append(
            {
                "Dénomination": "Est. ECS/ECS annuelle",
                "Valeur": st.session_state["data_site"]["estimation_ecs_annuel"],
                "Unité": "-",
                "Commentaire": "Estimation de la part ECS sur une année",
                "Excel": "C92",
                "Variable/Formule": "estimation_ecs_annuel = periode_nb_jours/365",
            }
        )

        # C93 → Est. Chauffage/Chauffage annuel prévisible
        st.session_state["data_site"]["dj_periode"] = float(
            calcul_dj_periode(
                df_meteo_tre200d0,
                st.session_state["data_site"]["periode_start"],
                st.session_state["data_site"]["periode_end"],
            )
        )
        st.session_state["data_site"][
            "estimation_part_chauffage_periode_sur_annuel"
        ] = float(st.session_state["data_site"]["dj_periode"] / DJ_REF_ANNUELS)
        df_list.append(
            {
                "Dénomination": "Est. Chauffage/Chauffage annuel prévisible",
                "Valeur": st.session_state["data_site"][
                    "estimation_part_chauffage_periode_sur_annuel"
                ]
                * 100,
                "Unité": "%",
                "Commentaire": "Est. Chauffage/Chauffage annuel prévisible → dj_periode (C101) / DJ_REF_ANNUELS (C102)",
                "Excel": "C93",
                "Variable/Formule": "estimation_part_chauffage_periode_sur_annuel = dj_periode / DJ_REF_ANNUELS",
            }
        )

        # C94 → Est. EF période / EF année
        st.session_state["data_site"][
            "estimation_energie_finale_periode_sur_annuel"
        ] = (
            st.session_state["data_site"]["estimation_ecs_annuel"]
            * (
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_ecs"
                ]
                + st.session_state["data_site"][
                    "repartition_energie_finale_partie_surelevee_ecs"
                ]
            )
        ) + (
            st.session_state["data_site"][
                "estimation_part_chauffage_periode_sur_annuel"
            ]
            * (
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_chauffage"
                ]
                + st.session_state["data_site"][
                    "repartition_energie_finale_partie_surelevee_chauffage"
                ]
            )
        )
        df_list.append(
            {
                "Dénomination": "Est. EF période / EF année",
                "Valeur": st.session_state["data_site"][
                    "estimation_energie_finale_periode_sur_annuel"
                ],
                "Unité": "%",
                "Commentaire": "Estimation en énergie finale sur la période / énergie finale sur une année",
                "Excel": "C94",
                "Variable/Formule": "estimation_energie_finale_periode_sur_annuel = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) + (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage))",
            }
        )

        # C95 → Est. Part ECS période comptage
        try:
            if (
                st.session_state["data_site"][
                    "estimation_energie_finale_periode_sur_annuel"
                ]
                != 0
            ):
                st.session_state["data_site"]["part_ecs_periode_comptage"] = (
                    st.session_state["data_site"]["estimation_ecs_annuel"]
                    * (
                        st.session_state["data_site"][
                            "repartition_energie_finale_partie_renovee_ecs"
                        ]
                        + st.session_state["data_site"][
                            "repartition_energie_finale_partie_surelevee_ecs"
                        ]
                    )
                ) / st.session_state["data_site"][
                    "estimation_energie_finale_periode_sur_annuel"
                ]
            else:
                st.session_state["data_site"]["part_ecs_periode_comptage"] = 0.0
        except ZeroDivisionError:
            st.session_state["data_site"]["part_ecs_periode_comptage"] = 0.0
        df_list.append(
            {
                "Dénomination": "Est. Part ECS période comptage",
                "Valeur": st.session_state["data_site"]["part_ecs_periode_comptage"]
                * 100,
                "Unité": "%",
                "Commentaire": "",
                "Excel": "C95",
                "Variable/Formule": "part_ecs_periode_comptage = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) / estimation_energie_finale_periode_sur_annuel",
            }
        )

        # C96 → Est. Part Chauffage période comptage
        try:
            if (
                st.session_state["data_site"][
                    "estimation_energie_finale_periode_sur_annuel"
                ]
                != 0
            ):
                st.session_state["data_site"]["part_chauffage_periode_comptage"] = (
                    st.session_state["data_site"][
                        "estimation_part_chauffage_periode_sur_annuel"
                    ]
                    * (
                        st.session_state["data_site"][
                            "repartition_energie_finale_partie_renovee_chauffage"
                        ]
                        + st.session_state["data_site"][
                            "repartition_energie_finale_partie_surelevee_chauffage"
                        ]
                    )
                ) / st.session_state["data_site"][
                    "estimation_energie_finale_periode_sur_annuel"
                ]
            else:
                st.session_state["data_site"]["part_chauffage_periode_comptage"] = 0.0
        except ZeroDivisionError:
            st.session_state["data_site"]["part_chauffage_periode_comptage"] = 0.0
        df_list.append(
            {
                "Dénomination": "Est. Part Chauffage période comptage",
                "Valeur": st.session_state["data_site"][
                    "part_chauffage_periode_comptage"
                ]
                * 100,
                "Unité": "%",
                "Commentaire": "",
                "Excel": "C96",
                "Variable/Formule": "part_chauffage_periode_comptage = (estimation_part_chauffage_periode_sur_annuel * \
            (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage)) / estimation_energie_finale_periode_sur_annuel",
            }
        )

        # C97 → correction ECS = 365/nb jour comptage
        st.session_state["data_site"]["correction_ecs"] = (
            365 / st.session_state["data_site"]["periode_nb_jours"]
        )
        df_list.append(
            {
                "Dénomination": "Correction ECS",
                "Valeur": st.session_state["data_site"]["correction_ecs"],
                "Unité": "-",
                "Commentaire": "",
                "Excel": "C97",
                "Variable/Formule": "correction_ecs = 365/periode_nb_jours",
            }
        )

        # C98 → Energie finale indiqué par le(s) compteur(s)
        st.session_state["data_site"]["agent_energetique_ef_mazout_somme_mj"] = (
            st.session_state["data_site"]["agent_energetique_ef_mazout_kg"]
            * CONVERSION_MAZOUT_KG_MJ
            + st.session_state["data_site"]["agent_energetique_ef_mazout_litres"]
            * CONVERSION_MAZOUT_LITRES_MJ
            + st.session_state["data_site"]["agent_energetique_ef_mazout_kwh"]
            * CONVERSION_MAZOUT_KWH_MJ
        )
        st.session_state["data_site"]["agent_energetique_ef_gaz_naturel_somme_mj"] = (
            st.session_state["data_site"]["agent_energetique_ef_gaz_naturel_m3"]
            * CONVERSION_GAZ_NATUREL_M3_MJ
            + st.session_state["data_site"]["agent_energetique_ef_gaz_naturel_kwh"]
            * CONVERSION_GAZ_NATUREL_KWH_MJ
        )
        st.session_state["data_site"][
            "agent_energetique_ef_bois_buches_dur_somme_mj"
        ] = (
            st.session_state["data_site"]["agent_energetique_ef_bois_buches_dur_stere"]
            * CONVERSION_BOIS_BUCHES_DUR_STERE_MJ
        )
        st.session_state["data_site"][
            "agent_energetique_ef_bois_buches_tendre_somme_mj"
        ] = (
            st.session_state["data_site"][
                "agent_energetique_ef_bois_buches_tendre_stere"
            ]
            * CONVERSION_BOIS_BUCHES_TENDRE_STERE_MJ
            + st.session_state["data_site"][
                "agent_energetique_ef_bois_buches_tendre_kwh"
            ]
            * CONVERSION_BOIS_BUCHES_TENDRE_KWH_MJ
        )
        st.session_state["data_site"]["agent_energetique_ef_pellets_somme_mj"] = (
            st.session_state["data_site"]["agent_energetique_ef_pellets_m3"]
            * CONVERSION_PELLETS_M3_MJ
            + st.session_state["data_site"]["agent_energetique_ef_pellets_kg"]
            * CONVERSION_PELLETS_KG_MJ
            + st.session_state["data_site"]["agent_energetique_ef_pellets_kwh"]
            * CONVERSION_PELLETS_KWH_MJ
        )
        st.session_state["data_site"]["agent_energetique_ef_plaquettes_somme_mj"] = (
            st.session_state["data_site"]["agent_energetique_ef_plaquettes_m3"]
            * CONVERSION_PLAQUETTES_M3_MJ
            + st.session_state["data_site"]["agent_energetique_ef_plaquettes_kwh"]
            * CONVERSION_PLAQUETTES_KWH_MJ
        )
        st.session_state["data_site"]["agent_energetique_ef_cad_somme_mj"] = (
            st.session_state["data_site"]["agent_energetique_ef_cad_kwh"]
            * CONVERSION_CAD_KWH_MJ
        )
        st.session_state["data_site"][
            "agent_energetique_ef_electricite_pac_somme_mj"
        ] = (
            st.session_state["data_site"]["agent_energetique_ef_electricite_pac_kwh"]
            * CONVERSION_ELECTRICITE_PAC_KWH_MJ
        )
        st.session_state["data_site"][
            "agent_energetique_ef_electricite_directe_somme_mj"
        ] = (
            st.session_state["data_site"][
                "agent_energetique_ef_electricite_directe_kwh"
            ]
            * CONVERSION_ELECTRICITE_DIRECTE_KWH_MJ
        )
        st.session_state["data_site"]["agent_energetique_ef_autre_somme_mj"] = (
            st.session_state["data_site"]["agent_energetique_ef_autre_kwh"]
            * CONVERSION_AUTRE_KWH_MJ
        )

        st.session_state["data_site"]["agent_energetique_ef_somme_kwh"] = (
            st.session_state["data_site"]["agent_energetique_ef_mazout_somme_mj"]
            + st.session_state["data_site"]["agent_energetique_ef_gaz_naturel_somme_mj"]
            + st.session_state["data_site"][
                "agent_energetique_ef_bois_buches_dur_somme_mj"
            ]
            + st.session_state["data_site"][
                "agent_energetique_ef_bois_buches_tendre_somme_mj"
            ]
            + st.session_state["data_site"]["agent_energetique_ef_pellets_somme_mj"]
            + st.session_state["data_site"]["agent_energetique_ef_plaquettes_somme_mj"]
            + st.session_state["data_site"]["agent_energetique_ef_cad_somme_mj"]
            + st.session_state["data_site"][
                "agent_energetique_ef_electricite_pac_somme_mj"
            ]
            + st.session_state["data_site"][
                "agent_energetique_ef_electricite_directe_somme_mj"
            ]
            + st.session_state["data_site"]["agent_energetique_ef_autre_somme_mj"]
        ) / 3.6
        df_list.append(
            {
                "Dénomination": "Energie finale indiqué par le(s) compteur(s)",
                "Valeur": st.session_state["data_site"][
                    "agent_energetique_ef_somme_kwh"
                ],
                "Unité": "kWh",
                "Commentaire": "Somme de l'énergie finale indiqué par le(s) compteur(s) en kWh",
                "Excel": "C98",
                "Variable/Formule": "agent_energetique_ef_somme_kwh",
            }
        )

        # C99 → Methodo_Bww → Part de ECS en énergie finale sur la période
        st.session_state["data_site"]["methodo_b_ww_kwh"] = (
            st.session_state["data_site"]["agent_energetique_ef_somme_kwh"]
        ) * st.session_state["data_site"]["part_ecs_periode_comptage"]
        df_list.append(
            {
                "Dénomination": "Methodo_Bww",
                "Valeur": st.session_state["data_site"]["methodo_b_ww_kwh"],
                "Unité": "kWh",
                "Commentaire": "",
                "Excel": "C99",
                "Variable/Formule": "methodo_b_ww_kwh",
            }
        )

        # C100 → Methodo_Eww
        try:
            if (
                st.session_state["data_site"]["sre_renovation_m2"] != 0
                and st.session_state["data_site"]["periode_nb_jours"] != 0
            ):
                st.session_state["data_site"]["methodo_e_ww_kwh"] = (
                    st.session_state["data_site"]["methodo_b_ww_kwh"]
                    / st.session_state["data_site"]["sre_renovation_m2"]
                ) * (365 / st.session_state["data_site"]["periode_nb_jours"])
            else:
                st.session_state["data_site"]["methodo_e_ww_kwh"] = 0.0
        except ZeroDivisionError:
            st.session_state["data_site"]["methodo_e_ww_kwh"] = 0.0
        df_list.append(
            {
                "Dénomination": "Methodo_Eww",
                "Valeur": st.session_state["data_site"]["methodo_e_ww_kwh"],
                "Unité": "kWh",
                "Commentaire": "",
                "Excel": "C100",
                "Variable/Formule": "Methodo_Eww",
            }
        )

        # C101 → DJ ref annuels
        df_list.append(
            {
                "Dénomination": "DJ ref annuels",
                "Valeur": DJ_REF_ANNUELS,
                "Unité": "Degré-jour",
                "Commentaire": "Degré-jour 20/16 avec les températures extérieures de référence pour Genève-Cointrin selon SIA 2028:2008",
                "Excel": "C101",
                "Variable/Formule": "DJ_REF_ANNUELS",
            }
        )

        # C102 → DJ période comptage
        df_list.append(
            {
                "Dénomination": "DJ période comptage",
                "Valeur": st.session_state["data_site"]["dj_periode"],
                "Unité": "Degré-jour",
                "Commentaire": "Degré-jour 20/16 avec les températures extérieures (tre200d0) pour Genève-Cointrin relevée par MétéoSuisse",
                "Excel": "C102",
                "Variable/Formule": "dj_periode",
            }
        )

        # C103 → Methodo_Bh → Part de chauffage en énergie finale sur la période
        st.session_state["data_site"]["methodo_b_h_kwh"] = (
            st.session_state["data_site"]["agent_energetique_ef_somme_kwh"]
            * st.session_state["data_site"]["part_chauffage_periode_comptage"]
        )
        df_list.append(
            {
                "Dénomination": "Methodo_Bh",
                "Valeur": st.session_state["data_site"]["methodo_b_h_kwh"],
                "Unité": "kWh",
                "Commentaire": "Part de chauffage en énergie finale sur la période",
                "Excel": "C103",
                "Variable/Formule": "methodo_b_h_kwh = agent_energetique_ef_somme_kwh * part_chauffage_periode_comptage",
            }
        )

        # C104 → Methodo_Eh
        try:
            if (
                st.session_state["data_site"]["sre_renovation_m2"] != 0
                and st.session_state["data_site"]["dj_periode"] != 0
            ):
                st.session_state["data_site"]["methodo_e_h_kwh"] = (
                    st.session_state["data_site"]["methodo_b_h_kwh"]
                    / st.session_state["data_site"]["sre_renovation_m2"]
                ) * (DJ_REF_ANNUELS / st.session_state["data_site"]["dj_periode"])
            else:
                st.session_state["data_site"]["methodo_e_h_kwh"] = 0.0
        except ZeroDivisionError:
            st.session_state["data_site"]["methodo_e_h_kwh"] = 0.0
        df_list.append(
            {
                "Dénomination": "Methodo_Eh",
                "Valeur": st.session_state["data_site"]["methodo_e_h_kwh"],
                "Unité": "kWh/m²",
                "Commentaire": "Energie finale par unité de surface pour le chauffage sur la période climatiquement corrigée",
                "Excel": "C104",
                "Variable/Formule": "methodo_e_h_kwh = (methodo_b_h_kwh / sre_renovation_m2) * (DJ_REF_ANNUELS / dj_periode)",
            }
        )

        # C105 → Ef,après,corr → Methodo_Eww + Methodo_Eh
        st.session_state["data_site"][
            "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2"
        ] = (
            st.session_state["data_site"]["methodo_e_ww_kwh"]
            + st.session_state["data_site"]["methodo_e_h_kwh"]
        )
        df_list.append(
            {
                "Dénomination": "Ef,après,corr (inclus surélévation)",
                "Valeur": st.session_state["data_site"][
                    "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2"
                ],
                "Unité": "kWh/m²",
                "Commentaire": "Energie finale par unité de surface pour le chauffage climatiquement corrigée et l'ECS sur la période (inclus surélévation)",
                "Excel": "C105",
                "Variable/Formule": "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 = methodo_e_ww_kwh + methodo_e_h_kwh",
            }
        )

        # C106 → Part de l'énergie finale théorique dédiée à la partie rénovée (ECS+Ch.)
        df_list.append(
            {
                "Dénomination": "Part de l'énergie finale théorique dédiée à la partie rénovée (ECS+Ch.)",
                "Valeur": st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_somme"
                ],
                "Unité": "%",
                "Commentaire": "Part de l'énergie finale théorique dédiée à la partie rénovée (ECS+Ch.)",
                "Excel": "C106",
                "Variable/Formule": "repartition_energie_finale_partie_renovee_somme",
            }
        )

        # C107 → Ef,après,corr,rénové →Total en énergie finale (Eww+Eh) pour la partie rénovée
        st.session_state["data_site"][
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2"
        ] = st.session_state["data_site"][
            "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2"
        ] * (
            st.session_state["data_site"][
                "repartition_energie_finale_partie_renovee_somme"
            ]
            / 100
        )
        df_list.append(
            {
                "Dénomination": "Ef,après,corr,rénové",
                "Valeur": st.session_state["data_site"][
                    "energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2"
                ],
                "Unité": "kWh/m²",
                "Commentaire": "Energie finale par unité de surface pour le chauffage et l'ECS sur la période climatiquement corrigée pour la partie rénovée",
                "Excel": "C107",
                "Variable/Formule": "energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 = energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 * (repartition_energie_finale_partie_renovee_somme / 100)",
            }
        )

        # C108 → fp → facteur de pondération moyen
        try:
            if st.session_state["data_site"]["agent_energetique_ef_somme_kwh"]:
                st.session_state["data_site"]["facteur_ponderation_moyen"] = (
                    st.session_state["data_site"][
                        "agent_energetique_ef_mazout_somme_mj"
                    ]
                    * FACTEUR_PONDERATION_MAZOUT
                    + st.session_state["data_site"][
                        "agent_energetique_ef_gaz_naturel_somme_mj"
                    ]
                    * FACTEUR_PONDERATION_GAZ_NATUREL
                    + st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_dur_somme_mj"
                    ]
                    * FACTEUR_PONDERATION_BOIS_BUCHES_DUR
                    + st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_tendre_somme_mj"
                    ]
                    * FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE
                    + st.session_state["data_site"][
                        "agent_energetique_ef_pellets_somme_mj"
                    ]
                    * FACTEUR_PONDERATION_PELLETS
                    + st.session_state["data_site"][
                        "agent_energetique_ef_plaquettes_somme_mj"
                    ]
                    * FACTEUR_PONDERATION_PLAQUETTES
                    + st.session_state["data_site"]["agent_energetique_ef_cad_somme_mj"]
                    * FACTEUR_PONDERATION_CAD
                    + st.session_state["data_site"][
                        "agent_energetique_ef_electricite_pac_somme_mj"
                    ]
                    * FACTEUR_PONDERATION_ELECTRICITE_PAC
                    + st.session_state["data_site"][
                        "agent_energetique_ef_electricite_directe_somme_mj"
                    ]
                    * FACTEUR_PONDERATION_ELECTRICITE_DIRECTE
                    + st.session_state["data_site"][
                        "agent_energetique_ef_autre_somme_mj"
                    ]
                    * FACTEUR_PONDERATION_AUTRE
                ) / (
                    st.session_state["data_site"]["agent_energetique_ef_somme_kwh"]
                    * 3.6
                )
            else:
                st.session_state["data_site"]["facteur_ponderation_moyen"] = 0
        except ZeroDivisionError:
            st.session_state["data_site"]["facteur_ponderation_moyen"] = 0
        df_list.append(
            {
                "Dénomination": "Facteur de pondération des agents énergétiques",
                "Valeur": st.session_state["data_site"]["facteur_ponderation_moyen"],
                "Unité": "-",
                "Commentaire": "Facteur de pondération moyen des agents énergétiques",
                "Excel": "C108",
                "Variable/Formule": "facteur_ponderation_moyen",
            }
        )

        # C109 → Methodo_Eww*fp
        st.session_state["data_site"]["methodo_e_ww_renovee_pondere_kwh_m2"] = (
            st.session_state["data_site"]["methodo_e_ww_kwh"]
            * st.session_state["data_site"]["facteur_ponderation_moyen"]
            * (
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_somme"
                ]
                / 100
            )
        )
        df_list.append(
            {
                "Dénomination": "Methodo_Eww*fp",
                "Valeur": st.session_state["data_site"][
                    "methodo_e_ww_renovee_pondere_kwh_m2"
                ],
                "Unité": "kWh/m²",
                "Commentaire": "",
                "Excel": "C109",
                "Variable/Formule": "methodo_e_ww_renovee_pondere_kwh_m2 = methodo_e_ww_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)",
            }
        )

        # C110 → Methodo_Eh*fp
        st.session_state["data_site"]["methodo_e_h_renovee_pondere_kwh_m2"] = (
            st.session_state["data_site"]["methodo_e_h_kwh"]
            * st.session_state["data_site"]["facteur_ponderation_moyen"]
            * (
                st.session_state["data_site"][
                    "repartition_energie_finale_partie_renovee_somme"
                ]
                / 100
            )
        )
        df_list.append(
            {
                "Dénomination": "Methodo_Eh*fp",
                "Valeur": st.session_state["data_site"][
                    "methodo_e_h_renovee_pondere_kwh_m2"
                ],
                "Unité": "kWh/m²",
                "Commentaire": "",
                "Excel": "C110",
                "Variable/Formule": "methodo_e_h_renovee_pondere_kwh_m2 = methodo_e_h_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)",
            }
        )

        # C113 → Ef,après,corr,rénové*fp
        st.session_state["data_site"][
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
        ] = (
            st.session_state["data_site"][
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2"
            ]
            * st.session_state["data_site"]["facteur_ponderation_moyen"]
        )
        df_list.append(
            {
                "Dénomination": "Ef,après,corr,rénové*fp",
                "Valeur": st.session_state["data_site"][
                    "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
                ],
                "Unité": "kWh/m²",
                "Commentaire": "",
                "Excel": "C113",
                "Variable/Formule": "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 * facteur_ponderation_moyen",
            }
        )

        # C114 → Ef,après,corr,rénové*fp
        st.session_state["data_site"][
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2"
        ] = (
            st.session_state["data_site"][
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
            ]
            * 3.6
        )
        df_list.append(
            {
                "Dénomination": "Ef,après,corr,rénové*fp",
                "Valeur": st.session_state["data_site"][
                    "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2"
                ],
                "Unité": "MJ/m²",
                "Commentaire": "",
                "Excel": "C114",
                "Variable/Formule": "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 * 3.6",
            }
        )

        # Autres dataframe
        df_periode = pd.DataFrame(df_periode_list, columns=columns)

        df = pd.DataFrame(df_list, columns=columns)

        df_meteo_note_calcul = df_meteo_tre200d0[
            (
                df_meteo_tre200d0["time"]
                >= st.session_state["data_site"]["periode_start"]
            )
            & (
                df_meteo_tre200d0["time"]
                <= st.session_state["data_site"]["periode_end"]
            )
        ][["time", "tre200d0", "DJ_theta0_16"]]

        df_agent_energetique = pd.DataFrame(
            {
                "Agent énergétique": [
                    "Mazout",
                    "Gaz naturel",
                    "Bois (buches dur)",
                    "Bois (buches tendre)",
                    "Pellets",
                    "Plaquettes",
                    "CAD",
                    "Electricité (PAC)",
                    "Electricité (directe)",
                    "Autre",
                ],
                "Somme MJ": [
                    st.session_state["data_site"][
                        "agent_energetique_ef_mazout_somme_mj"
                    ],
                    st.session_state["data_site"][
                        "agent_energetique_ef_gaz_naturel_somme_mj"
                    ],
                    st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_dur_somme_mj"
                    ],
                    st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_tendre_somme_mj"
                    ],
                    st.session_state["data_site"][
                        "agent_energetique_ef_pellets_somme_mj"
                    ],
                    st.session_state["data_site"][
                        "agent_energetique_ef_plaquettes_somme_mj"
                    ],
                    st.session_state["data_site"]["agent_energetique_ef_cad_somme_mj"],
                    st.session_state["data_site"][
                        "agent_energetique_ef_electricite_pac_somme_mj"
                    ],
                    st.session_state["data_site"][
                        "agent_energetique_ef_electricite_directe_somme_mj"
                    ],
                    st.session_state["data_site"][
                        "agent_energetique_ef_autre_somme_mj"
                    ],
                ],
                "Somme kWh": [
                    st.session_state["data_site"][
                        "agent_energetique_ef_mazout_somme_mj"
                    ]
                    / 3.6,
                    st.session_state["data_site"][
                        "agent_energetique_ef_gaz_naturel_somme_mj"
                    ]
                    / 3.6,
                    st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_dur_somme_mj"
                    ]
                    / 3.6,
                    st.session_state["data_site"][
                        "agent_energetique_ef_bois_buches_tendre_somme_mj"
                    ]
                    / 3.6,
                    st.session_state["data_site"][
                        "agent_energetique_ef_pellets_somme_mj"
                    ]
                    / 3.6,
                    st.session_state["data_site"][
                        "agent_energetique_ef_plaquettes_somme_mj"
                    ]
                    / 3.6,
                    st.session_state["data_site"]["agent_energetique_ef_cad_somme_mj"]
                    / 3.6,
                    st.session_state["data_site"][
                        "agent_energetique_ef_electricite_pac_somme_mj"
                    ]
                    / 3.6,
                    st.session_state["data_site"][
                        "agent_energetique_ef_electricite_directe_somme_mj"
                    ]
                    / 3.6,
                    st.session_state["data_site"]["agent_energetique_ef_autre_somme_mj"]
                    / 3.6,
                ],
                "Facteur de pondération": [
                    FACTEUR_PONDERATION_MAZOUT,
                    FACTEUR_PONDERATION_GAZ_NATUREL,
                    FACTEUR_PONDERATION_BOIS_BUCHES_DUR,
                    FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE,
                    FACTEUR_PONDERATION_PELLETS,
                    FACTEUR_PONDERATION_PLAQUETTES,
                    FACTEUR_PONDERATION_CAD,
                    FACTEUR_PONDERATION_ELECTRICITE_PAC,
                    FACTEUR_PONDERATION_ELECTRICITE_DIRECTE,
                    FACTEUR_PONDERATION_AUTRE,
                ],
                "Variable Agent énergétique": [
                    "agent_energetique_ef_mazout_somme_mj",
                    "agent_energetique_ef_gaz_naturel_somme_mj",
                    "agent_energetique_ef_bois_buches_dur_somme_mj",
                    "agent_energetique_ef_bois_buches_tendre_somme_mj",
                    "agent_energetique_ef_pellets_somme_mj",
                    "agent_energetique_ef_plaquettes_somme_mj",
                    "agent_energetique_ef_cad_somme_mj",
                    "agent_energetique_ef_electricite_pac_somme_mj",
                    "agent_energetique_ef_electricite_directe_somme_mj",
                    "agent_energetique_ef_autre_somme_mj",
                ],
                "Variable facteur de pondération": [
                    "FACTEUR_PONDERATION_MAZOUT",
                    "FACTEUR_PONDERATION_GAZ_NATUREL",
                    "FACTEUR_PONDERATION_BOIS_BUCHES_DUR",
                    "FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE",
                    "FACTEUR_PONDERATION_PELLETS",
                    "FACTEUR_PONDERATION_PLAQUETTES",
                    "FACTEUR_PONDERATION_CAD",
                    "FACTEUR_PONDERATION_ELECTRICITE_PAC",
                    "FACTEUR_PONDERATION_ELECTRICITE_DIRECTE",
                    "FACTEUR_PONDERATION_AUTRE",
                ],
            }
        )

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
        st.subheader("Note de calcul")
        st.write("Période sélectionnée")
        st.dataframe(df_periode)
        st.write("Calculs effectués pour la période sélectionnée")
        st.dataframe(df)
        st.write("Agents énergétiques")
        st.dataframe(df_agent_energetique)

        # Define the formula
        formula_facteur_ponderation_moyen = r"facteur\_ponderation\_moyen = \frac{{(agent\_energetique\_mazout\_somme\_mj \times FACTEUR\_PONDERATION\_MAZOUT + \
                    agent\_energetique\_gaz\_naturel\_somme\_mj \times FACTEUR\_PONDERATION\_GAZ\_NATUREL + \
                    agent\_energetique\_bois\_buches\_dur\_somme\_mj \times FACTEUR\_PONDERATION\_BOIS\_BUCHES\_DUR + \
                    agent\_energetique\_bois\_buches\_tendre\_somme\_mj \times FACTEUR\_PONDERATION\_BOIS\_BUCHES\_TENDRE + \
                    agent\_energetique\_pellets\_somme\_mj \times FACTEUR\_PONDERATION\_PELLETS + \
                    agent\_energetique\_plaquettes\_somme\_mj \times FACTEUR\_PONDERATION\_PLAQUETTES + \
                    agent\_energetique\_cad\_somme\_mj \times FACTEUR\_PONDERATION\_CAD + \
                    agent\_energetique\_electricite\_pac\_somme\_mj \times FACTEUR\_PONDERATION\_ELECTRICITE\_PAC + \
                    agent\_energetique\_electricite\_directe\_somme\_mj \times FACTEUR\_PONDERATION\_ELECTRICITE\_DIRECTE + \
                    agent\_energetique\_autre\_somme\_mj \times FACTEUR\_PONDERATION\_AUTRE)}}{{(agent\_energetique\_somme\_kwh \times 3.6)}}"

        # Render the formula in LaTeX
        st.latex(formula_facteur_ponderation_moyen)

        # Render the formula in LaTeX
        formula_facteur_ponderation_moyen = (
            r"facteur\_ponderation\_moyen = \frac{{({0})}}{{({1})}} = {2}".format(
                st.session_state["data_site"]["agent_energetique_ef_mazout_somme_mj"]
                * FACTEUR_PONDERATION_MAZOUT
                + st.session_state["data_site"][
                    "agent_energetique_ef_gaz_naturel_somme_mj"
                ]
                * FACTEUR_PONDERATION_GAZ_NATUREL
                + st.session_state["data_site"][
                    "agent_energetique_ef_bois_buches_dur_somme_mj"
                ]
                * FACTEUR_PONDERATION_BOIS_BUCHES_DUR
                + st.session_state["data_site"][
                    "agent_energetique_ef_bois_buches_tendre_somme_mj"
                ]
                * FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE
                + st.session_state["data_site"]["agent_energetique_ef_pellets_somme_mj"]
                * FACTEUR_PONDERATION_PELLETS
                + st.session_state["data_site"][
                    "agent_energetique_ef_plaquettes_somme_mj"
                ]
                * FACTEUR_PONDERATION_PLAQUETTES
                + st.session_state["data_site"]["agent_energetique_ef_cad_somme_mj"]
                * FACTEUR_PONDERATION_CAD
                + st.session_state["data_site"][
                    "agent_energetique_ef_electricite_pac_somme_mj"
                ]
                * FACTEUR_PONDERATION_ELECTRICITE_PAC
                + st.session_state["data_site"][
                    "agent_energetique_ef_electricite_directe_somme_mj"
                ]
                * FACTEUR_PONDERATION_ELECTRICITE_DIRECTE
                + st.session_state["data_site"]["agent_energetique_ef_autre_somme_mj"]
                * FACTEUR_PONDERATION_AUTRE,
                st.session_state["data_site"]["agent_energetique_ef_somme_kwh"] * 3.6,
                st.session_state["data_site"]["facteur_ponderation_moyen"],
            )
        )

        # Render the formula in LaTeX
        st.latex(formula_facteur_ponderation_moyen)

        st.write("Données météo station Genève-Cointrin pour la période sélectionnée")
        st.dataframe(df_meteo_note_calcul)

    with tab4:
        st.subheader("Synthèse des résultats")

        # calculs
        st.session_state["data_site"]["delta_ef_realisee_kwh_m2"] = (
            st.session_state["data_site"]["ef_avant_corr_kwh_m2"]
            - st.session_state["data_site"][
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
            ]
        )
        try:
            if (
                st.session_state["data_site"][
                    "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
                ]
                != 0
            ):
                st.session_state["data_site"]["atteinte_objectif"] = (
                    st.session_state["data_site"]["delta_ef_realisee_kwh_m2"]
                    / st.session_state["data_site"]["delta_ef_visee_kwh_m2"]
                )
            else:
                st.session_state["data_site"]["atteinte_objectif"] = 0.0
        except ZeroDivisionError:
            st.session_state["data_site"]["atteinte_objectif"] = 0.0

        df_resultats1 = pd.DataFrame(
            {
                "Variable": [
                    "IDC moyen 3 ans avant travaux → (Ef,avant,corr)",
                    "EF pondéré corrigé clim. après travaux → (Ef,après,corr,rénové*fp)",
                    "Objectif en énergie finale (Ef,obj *fp)",
                    "Baisse ΔEf réalisée → ∆Ef,réel = Ef,avant,corr - Ef,après,corr*fp",
                    "Baisse ΔEf visée → ∆Ef,visée = Ef,avant,corr - Ef,obj*fp",
                ],
                "kWh/m²/an": [
                    round(st.session_state["data_site"]["ef_avant_corr_kwh_m2"], 4),
                    round(
                        st.session_state["data_site"][
                            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
                        ],
                        4,
                    ),
                    round(
                        st.session_state["data_site"]["ef_objectif_pondere_kwh_m2"], 4
                    ),
                    round(st.session_state["data_site"]["delta_ef_realisee_kwh_m2"], 4),
                    round(st.session_state["data_site"]["delta_ef_visee_kwh_m2"], 4),
                ],
                "MJ/m²/an": [
                    round(
                        st.session_state["data_site"]["ef_avant_corr_kwh_m2"] * 3.6, 4
                    ),
                    round(
                        st.session_state["data_site"][
                            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
                        ]
                        * 3.6,
                        4,
                    ),
                    round(
                        st.session_state["data_site"]["ef_objectif_pondere_kwh_m2"]
                        * 3.6,
                        4,
                    ),
                    round(
                        st.session_state["data_site"]["delta_ef_realisee_kwh_m2"] * 3.6,
                        4,
                    ),
                    round(
                        st.session_state["data_site"]["delta_ef_visee_kwh_m2"] * 3.6, 4
                    ),
                ],
            }
        )

        # dtypes
        df_resultats1["Variable"] = df_resultats1["Variable"].astype(str)
        df_resultats1["kWh/m²/an"] = df_resultats1["kWh/m²/an"].astype(float)
        df_resultats1["MJ/m²/an"] = df_resultats1["MJ/m²/an"].astype(float)
        st.table(df_resultats1)

        # résultats en latex

        if st.session_state["data_site"]["facteur_ponderation_moyen"] > 0:
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
            st.session_state["data_site"]["amoen_id"]
            and st.session_state["data_site"]["ef_avant_corr_kwh_m2"]
            and st.session_state["data_site"][
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
            ]
            and st.session_state["data_site"]["ef_objectif_pondere_kwh_m2"]
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
                fig = create_barplot(data_df)
                st.plotly_chart(fig)

                # show dataframe in something hidden like a
                if st.checkbox("Afficher les données IDC"):
                    show_dataframe(data_df)
            else:
                st.write("No data retrieved for the selected EGIDs.")
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
                fig_historique_amoen = create_barplot_historique_amoen(
                    df_historique_complet
                )
                st.plotly_chart(fig_historique_amoen)

                # Show DataFrame in a hidden section
                if st.checkbox("Afficher les données historiques"):
                    st.dataframe(df_historique_complet)
            else:
                st.error("Pas de données historiques disponibles")

    with tab6:
        st.subheader("Générer rapport")

        # Check if all fields are valid
        def is_valid(var):
            return var is not None and var != ""

        def check_validity():
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
        if not invalid_fields:
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
                ] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Remove the _id field if it exists to ensure MongoDB generates a new one
                if "_id" in st.session_state["data_site"]:
                    del st.session_state["data_site"]["_id"]

                # Send data_site to MongoDB
                # x = mycol_historique_sites.insert_one(st.session_state['data_site'])
        else:
            st.warning(
                "Toutes les informations nécessaires ne sont pas disponibles pour générer le PDF."
            )
            invalid_fields_list = "\n".join([f"- {field}" for field in invalid_fields])
            st.warning(
                f"Les champs suivants sont invalides ou manquants:\n\n{invalid_fields_list}"
            )

    if username_login == "admin":
        with tab7:
            # TODO: convertir en helper
            # data
            data_admin = load_projets_admin()
            df = pd.DataFrame(data_admin)
            # chiffres clés
            st.subheader("Chiffres-clés")
            # Filtrer les atteinte_projets sans agents énergétiques
            df_date = df.copy()
            df_date = df_date[
                (
                    df_date["agent_energetique_ef_mazout_litres"]
                    + df_date["agent_energetique_ef_mazout_kwh"]
                    + df_date["agent_energetique_ef_gaz_naturel_m3"]
                    + df_date["agent_energetique_ef_gaz_naturel_kwh"]
                    + df_date["agent_energetique_ef_bois_buches_dur_stere"]
                    + df_date["agent_energetique_ef_bois_buches_tendre_stere"]
                    + df_date["agent_energetique_ef_bois_buches_tendre_kwh"]
                    + df_date["agent_energetique_ef_pellets_m3"]
                    + df_date["agent_energetique_ef_pellets_kg"]
                    + df_date["agent_energetique_ef_pellets_kwh"]
                    + df_date["agent_energetique_ef_plaquettes_m3"]
                    + df_date["agent_energetique_ef_plaquettes_kwh"]
                    + df_date["agent_energetique_ef_cad_kwh"]
                    + df_date["agent_energetique_ef_electricite_pac_kwh"]
                    + df_date["agent_energetique_ef_electricite_directe_kwh"]
                    + df_date["agent_energetique_ef_autre_kwh"]
                )
                > 0
            ]
            # date dernier rapport par projet
            df_date_sorted = df_date.sort_values(["nom_projet", "date_rapport"])
            df_date_sorted["date_rapport"] = pd.to_datetime(
                df_date_sorted["date_rapport"], format="%Y-%m-%d"
            )
            df_date_sorted["date_rapport"] = df_date_sorted["date_rapport"].astype(str)
            df_date_sorted["periode_start"] = pd.to_datetime(
                df_date_sorted["periode_start"], format="%Y-%m-%d"
            )
            df_date_sorted["periode_start"] = df_date_sorted["periode_start"].astype(
                str
            )
            df_date_sorted["periode_end"] = pd.to_datetime(
                df_date_sorted["periode_end"], format="%Y-%m-%d"
            )
            df_date_sorted["periode_end"] = df_date_sorted["periode_end"].astype(str)
            df_date_sorted["atteinte_objectif"] = (
                df_date_sorted["atteinte_objectif"] * 100
            )
            df_date_sorted["atteinte_objectif"] = df_date_sorted[
                "atteinte_objectif"
            ].apply(lambda x: f"{x:.2f}%")
            idx = df_date_sorted.groupby("nom_projet")["date_rapport"].idxmax()
            df_date = df_date_sorted.loc[
                idx,
                [
                    "nom_projet",
                    "date_rapport",
                    "periode_start",
                    "periode_end",
                    "atteinte_objectif",
                ],
            ]
            df_date = df_date.sort_values(by=["date_rapport"])
            st.write("Date dernier calcul atteinte objectif par projet")
            st.dataframe(df_date)
            st.subheader("Données")
            # Drop unnecessary columns
            df_filtre = df.drop(
                columns=[
                    "_id",
                    "sre_pourcentage_lieux_de_rassemblement",
                    "sre_pourcentage_hopitaux",
                    "sre_pourcentage_industrie",
                    "sre_pourcentage_depots",
                    "sre_pourcentage_installations_sportives",
                    "sre_pourcentage_piscines_couvertes",
                ]
            )
            # Filtres
            all_projets = df_filtre["nom_projet"].unique()
            all_amoen = df_filtre["amoen_id"].unique()
            filtre_amoen = st.multiselect("AMOén", all_amoen, default=all_amoen)
            filtre_projets = st.multiselect(
                "Projet",
                all_projets,
                default=df_filtre[df_filtre["amoen_id"].isin(filtre_amoen)][
                    "nom_projet"
                ].unique(),
            )
            # Apply the final filter to the DataFrame
            df_filtre = df_filtre[
                (df_filtre["nom_projet"].isin(filtre_projets))
                & (df_filtre["amoen_id"].isin(filtre_amoen))
            ]
            # Display the filtered DataFrame
            st.write(df_filtre)

            # Sort the dataframe by 'nom_projet' and 'periode_start'
            df_barplot = df_filtre.sort_values(by=["nom_projet", "periode_start"])

            # Filtrer les atteinte_projets sans agents énergétiques
            df_barplot = df_barplot[
                (
                    df_barplot["agent_energetique_ef_mazout_litres"]
                    + df_barplot["agent_energetique_ef_mazout_kwh"]
                    + df_barplot["agent_energetique_ef_gaz_naturel_m3"]
                    + df_barplot["agent_energetique_ef_gaz_naturel_kwh"]
                    + df_barplot["agent_energetique_ef_bois_buches_dur_stere"]
                    + df_barplot["agent_energetique_ef_bois_buches_tendre_stere"]
                    + df_barplot["agent_energetique_ef_bois_buches_tendre_kwh"]
                    + df_barplot["agent_energetique_ef_pellets_m3"]
                    + df_barplot["agent_energetique_ef_pellets_kg"]
                    + df_barplot["agent_energetique_ef_pellets_kwh"]
                    + df_barplot["agent_energetique_ef_plaquettes_m3"]
                    + df_barplot["agent_energetique_ef_plaquettes_kwh"]
                    + df_barplot["agent_energetique_ef_cad_kwh"]
                    + df_barplot["agent_energetique_ef_electricite_pac_kwh"]
                    + df_barplot["agent_energetique_ef_electricite_directe_kwh"]
                    + df_barplot["agent_energetique_ef_autre_kwh"]
                )
                > 0
            ]

            df_barplot["atteinte_objectif"] = df_barplot["atteinte_objectif"] * 100
            df_barplot["periode_start"] = pd.to_datetime(
                df_barplot["periode_start"], errors="coerce"
            )
            df_barplot["periode_end"] = pd.to_datetime(
                df_barplot["periode_end"], errors="coerce"
            )
            df_barplot["periode"] = (
                df_barplot["periode_start"].dt.strftime("%Y-%m-%d")
                + " - "
                + df_barplot["periode_end"].dt.strftime("%Y-%m-%d")
            )

            # Add a new column that assigns a rank based on the order of the periods within each project
            df_barplot["periode_rank"] = df_barplot.groupby("nom_projet").cumcount()

            # Add a new column with formatted percentage values
            df_barplot["atteinte_objectif_formatted"] = df_barplot[
                "atteinte_objectif"
            ].apply(lambda x: f"{x:.0f}%")

            # Create the chart
            fig = (
                alt.Chart(df_barplot)
                .mark_bar()
                .encode(
                    x=alt.X("nom_projet:N", axis=alt.Axis(title="", labels=True)),
                    y=alt.Y("atteinte_objectif:Q", title="Atteinte Objectif [%]"),
                    xOffset="periode_rank:N",
                    color="periode:N",
                    tooltip=[
                        alt.Tooltip("nom_projet:N", title="Site"),
                        alt.Tooltip("amoen_id:N", title="AMOén"),
                        alt.Tooltip("periode:N", title="Période"),
                        alt.Tooltip(
                            "atteinte_objectif:Q",
                            title="Atteinte Objectif [%]",
                            format=".2f",
                        ),
                    ],
                )
                .properties(width=600, title="Atteinte Objectif par Site")
            )

            # Add text labels on top of the bars with percentage symbol
            text = (
                alt.Chart(df_barplot)
                .mark_text(
                    align="left", baseline="bottom", dx=-4, fontSize=12, color="black"
                )
                .encode(
                    x=alt.X("nom_projet:N", axis=alt.Axis(title="", labels=True)),
                    y=alt.Y("atteinte_objectif:Q", title="Atteinte Objectif [%]"),
                    text="atteinte_objectif_formatted:N",  # Use the new formatted column
                    xOffset="periode_rank:N",
                )
            )

            # Combine the bar chart and text labels
            fig = alt.layer(fig, text)

            # Customize the X-Axis
            fig = fig.configure_axisX(
                labelAngle=-45,
                labelFontSize=12,
            )

            # Remove the legend
            fig = fig.configure_legend(disable=True)

            # Display the chart
            st.altair_chart(fig, use_container_width=True)


elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
