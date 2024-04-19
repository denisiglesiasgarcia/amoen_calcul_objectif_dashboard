# TODO: renseigner les consommations ECS séparées du total

import os
import datetime
import io
import numpy as np
import pandas as pd
import smtplib
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

os.environ['USE_ARROW_extension'] = '1'

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
CONVERSION_PLAQUETTES_M3_MJ = 200*20
CONVERSION_PLAQUETTES_KWH_MJ = 3.6*13.1/11.6
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

# Variables pour l'envoi de mail
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_PASSWORD = st.secrets["GMAIL_PASSWORD"]
TO_ADRESS_EMAIL = st.secrets["TO_ADRESS_EMAIL"]

# Météo
def get_meteo_data():
    global DJ_TEMPERATURE_REFERENCE
    # Mise à jour des données météo de manière journalière
    df_meteo_tre200d0_historique = pd.read_csv("https://data.geo.admin.ch/ch.meteoschweiz.klima/nbcn-tageswerte/nbcn-daily_GVE_previous.csv", sep=';', encoding='latin1', parse_dates=['date'])
    df_meteo_tre200d0_annee_cours = pd.read_csv("https://data.geo.admin.ch/ch.meteoschweiz.klima/nbcn-tageswerte/nbcn-daily_GVE_current.csv", sep=';', encoding='latin1', parse_dates=['date'])
    df_meteo_tre200d0 = pd.concat([df_meteo_tre200d0_historique, df_meteo_tre200d0_annee_cours])
    df_meteo_tre200d0.rename(columns={"station/location": "stn",
                        'date': 'time'}, inplace=True)
    df_meteo_tre200d0 = df_meteo_tre200d0[['stn', 'time', 'tre200d0']]
    df_meteo_tre200d0 = df_meteo_tre200d0[df_meteo_tre200d0['time'] >= '2015-01-01']
    df_meteo_tre200d0.drop_duplicates(inplace=True)
    # replace values with "-" with nan and drop them
    df_meteo_tre200d0.replace("-", pd.NA, inplace=True)
    df_meteo_tre200d0.dropna(inplace=True)
    df_meteo_tre200d0.sort_values(by="time", inplace=True)
    df_meteo_tre200d0.reset_index(drop=True, inplace=True)
    # Calculs pour DJ
    df_meteo_tre200d0['tre200d0'] = df_meteo_tre200d0['tre200d0'].astype(float)
    df_meteo_tre200d0['mois'] = df_meteo_tre200d0['time'].dt.month
    df_meteo_tre200d0['saison_chauffe'] = np.where(df_meteo_tre200d0['mois'].isin([9, 10, 11, 12, 1, 2, 3, 4, 5]), 1, 0)
    df_meteo_tre200d0['tre200d0_sous_16'] = np.where(df_meteo_tre200d0['tre200d0'] <= 16, 1, 0)
    df_meteo_tre200d0['DJ_theta0_16'] = df_meteo_tre200d0['saison_chauffe'] * df_meteo_tre200d0['tre200d0_sous_16'] * (DJ_TEMPERATURE_REFERENCE - df_meteo_tre200d0['tre200d0'])

    return df_meteo_tre200d0

def generate_dashboard():
    # Validation données saisies
    def validate_input(name, variable, unité):
        if (variable.isnumeric() or variable.replace('.', '', 1).isnumeric()):
            st.text(f"{name} {variable} {unité}")
        else:
            st.text(name, "doit être un chiffre")
    
    def validate_input_affectation(name, variable, unite, sre_renovation_m2):
        try:
            variable = float(variable.replace(',', '.', 1))
            if 0 <= variable <= 100:
                st.text(f"{name} {variable} {unite} → {round(variable * float(sre_renovation_m2) / 100, 2)} m²")
            else:
                st.text(f"Valeur doit être comprise entre 0 et 100")
        except ValueError:
            st.text(f"{name} doit être un chiffre")
            variable = 0
    
    def validate_agent_energetique_input(name, value, unit):
        if value is None or value == "":
            st.text(f"{name} doit être un chiffre")
            return 0
        
        try:
            value = float(value.replace(',', '.', 1))
            if value > 0:
                st.text(f"{name} {value} {unit}")
                return value
            else:
                st.text(f"{name} doit être un chiffre positif")
                return 0
        except ValueError:
            st.text(f"{name} doit être un chiffre")
            return 0

    # Calcul des degrés-jours
    def calcul_dj_periode(df_meteo_tre200d0, periode_start, periode_end):
        dj_periode = df_meteo_tre200d0[(df_meteo_tre200d0['time'] >= periode_start) & (df_meteo_tre200d0['time'] <= periode_end)]['DJ_theta0_16'].sum()
        return dj_periode

    st.title("Outil pour calculer l'atteinte des objectifs AMOén")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["0 Readme", '1 Données site', "2 Note de calcul", '3 Résultats', '4 Validation des données'])

    # Calcul des index selon dates
    with tab1:
        st.subheader('Différences entre méthodologie et calcul IDC:')
        tab1_col1, tab1_col2 = st.columns(2)
        with tab1_col1:
            st.write("Méthodologie")
            st.write("- PAC: Dans la méthodologie on applique un facteur de pondération de 2 sur l'électricité consommée par les PAC.")
            st.write("- CAD: Tous les CAD sont identiques dans la méthodologie. Il n'y a pas de différence entre CAD réparti ou tarifé")
            st.write("- Météo: utilisation des données MétéoSuisse station Cointrin, mesure tre200d0.")
            st.write("- Répartition ECS/chauffage: la méthodologie se base sur la répartition théorique des besoins ECS/chauffage \
                    selon rénové/neuf ou les compteurs si disponible (ECS/Chauffage). Ces chiffres sont indiqueés dans le tableau Excel\
                    de fixation d'objectif de performances")

        with tab1_col2:
            st.write("Règlement IDC")
            st.write("- PAC: Dans le règlement IDC on doit appliquer un COP de 3.25 sur l'électricité consommée par les PAC après 2010.")
            st.write('- CAD: Dans le cas du CAD tarifé, on doit appliquer des pertes → 1kWh utile = 3.6/0.925 MJ = 3.892 MJ normalisés')
            st.write("- Météo: Le tableau Excel IDC ne précise pas les données météo exactes utilisées.")
            st.write("- Répartition ECS/chauffage: Le règlement IDC se base sur consommation normalisé de ECS (Eww), par exemple 128 MJ/m²\
                     pour du logement collectif. Tout le reste de l'énergie est pour le chauffage donc soumis a correction climatique.")
        
        st.subheader('Limitations du calcul')
        st.write("La période minimale recommandée de calcul est de 6 mois de données.")

        st.subheader('Liens utiles')
        st.markdown("**[GitHub de la dashboard](https://github.com/denisiglesiasgarcia/amoen_calcul_objectif_dashboard)**", unsafe_allow_html=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('SRE rénovée')
            # SRE rénovée
            sre_renovation_m2 = st.text_input("SRE rénovée (m²):", value=0, help="La SRE rénovée est la partie du batiment qui a été rénovée, la surélévation/extension n'est pas incluse")
            validate_input("SRE rénovée:", sre_renovation_m2, "m²")
            sre_renovation_m2 = float(sre_renovation_m2)

            try:
                sre_renovation_m2_avertissement = sre_renovation_m2
                if sre_renovation_m2_avertissement <= 0:
                    st.write(f"<p style='color: red;'><strong>SRE doit être > 0 ({sre_renovation_m2_avertissement})</strong></p>", unsafe_allow_html=True)
            except ValueError:
                st.write("Problème dans la somme des pourcentages des affectations")

            # SRE pourcentage
            st.subheader('Affectations')
            show_text_input_sre_pourcentage_habitat_collectif = st.checkbox("Habitat collectif (%)", value=0)
            if show_text_input_sre_pourcentage_habitat_collectif:
                sre_pourcentage_habitat_collectif = st.text_input("Habitat collectif (% SRE):",
                                                                  value=0,
                                                                  label_visibility="collapsed")
                if sre_pourcentage_habitat_collectif != "0":
                    validate_input_affectation("Habitat collectif:", sre_pourcentage_habitat_collectif, "%", sre_renovation_m2)
                    # sre_pourcentage_habitat_collectif = float(sre_pourcentage_habitat_collectif)
            else:
                sre_pourcentage_habitat_collectif = 0.0
            
            show_text_input_sre_pourcentage_habitat_individuel = st.checkbox("Habitat individuel (%)")
            if show_text_input_sre_pourcentage_habitat_individuel:
                sre_pourcentage_habitat_individuel = st.text_input("Habitat individuel (% SRE):", value=0)
                if sre_pourcentage_habitat_individuel != "0":
                    validate_input_affectation("Habitat individuel:", sre_pourcentage_habitat_individuel, "%", sre_renovation_m2)
                    # sre_pourcentage_habitat_individuel = float(sre_pourcentage_habitat_individuel)
            else:
                sre_pourcentage_habitat_individuel = 0.0
            
            show_text_input_sre_pourcentage_administration = st.checkbox("Administration (%)")
            if show_text_input_sre_pourcentage_administration:
                sre_pourcentage_administration = st.text_input("Administration (% SRE):", value=0)
                if sre_pourcentage_administration != "0":
                    validate_input_affectation("Administration:", sre_pourcentage_administration, "%", sre_renovation_m2)
                    # sre_pourcentage_administration = float(sre_pourcentage_administration)
            else:
                sre_pourcentage_administration = 0.0
            
            show_text_input_sre_pourcentage_ecoles = st.checkbox("Écoles (%)")
            if show_text_input_sre_pourcentage_ecoles:
                sre_pourcentage_ecoles = st.text_input("Écoles (% SRE):", value=0)
                if sre_pourcentage_ecoles != "0":
                    validate_input_affectation("Écoles:", sre_pourcentage_ecoles, "%", sre_renovation_m2)
                    # sre_pourcentage_ecoles = float(sre_pourcentage_ecoles)
            else:
                sre_pourcentage_ecoles = 0.0
            
            show_text_input_sre_pourcentage_commerce = st.checkbox("Commerce (%)")
            if show_text_input_sre_pourcentage_commerce:
                sre_pourcentage_commerce = st.text_input("Commerce (% SRE):", value=0)
                if sre_pourcentage_commerce != "0":
                    validate_input_affectation("Commerce:", sre_pourcentage_commerce, "%", sre_renovation_m2)
                    # sre_pourcentage_commerce = float(sre_pourcentage_commerce)
            else:
                sre_pourcentage_commerce = 0.0
            
            show_text_input_sre_pourcentage_restauration = st.checkbox("Restauration (%)")
            if show_text_input_sre_pourcentage_restauration:
                sre_pourcentage_restauration = st.text_input("Restauration (% SRE):", value=0)
                if sre_pourcentage_restauration != "0":
                    validate_input_affectation("Restauration:", sre_pourcentage_restauration, "%", sre_renovation_m2)
                    # sre_pourcentage_restauration = float(sre_pourcentage_restauration)
            else:
                sre_pourcentage_restauration = 0.0
            
            show_text_input_sre_pourcentage_lieux_de_rassemblement = st.checkbox("Lieux de rassemblement (%)")
            if show_text_input_sre_pourcentage_lieux_de_rassemblement:
                sre_pourcentage_lieux_de_rassemblement = st.text_input("Lieux de rassemblement (% SRE):", value=0)
                if sre_pourcentage_lieux_de_rassemblement != "0":
                    validate_input_affectation("Lieux de rassemblement:", sre_pourcentage_lieux_de_rassemblement, "%", sre_renovation_m2)
                    # sre_pourcentage_lieux_de_rassemblement = float(sre_pourcentage_lieux_de_rassemblement)
            else:
                sre_pourcentage_lieux_de_rassemblement = 0.0
            
            show_text_input_sre_pourcentage_hopitaux = st.checkbox("Hôpitaux (%)")
            if show_text_input_sre_pourcentage_hopitaux:
                sre_pourcentage_hopitaux = st.text_input("Hôpitaux (% SRE):", value=0)
                if sre_pourcentage_hopitaux != "0":
                    validate_input_affectation("Hôpitaux:", sre_pourcentage_hopitaux, "%", sre_renovation_m2)
                    # sre_pourcentage_hopitaux = float(sre_pourcentage_hopitaux)
            else:
                sre_pourcentage_hopitaux = 0.0
            
            show_text_input_sre_pourcentage_industrie = st.checkbox("Industrie (%)")
            if show_text_input_sre_pourcentage_industrie:
                sre_pourcentage_industrie = st.text_input("Industrie (% SRE):", value=0)
                if sre_pourcentage_industrie != "0":
                    validate_input_affectation("Industrie:", sre_pourcentage_industrie, "%", sre_renovation_m2)
                    # sre_pourcentage_industrie = float(sre_pourcentage_industrie)
            else:
                sre_pourcentage_industrie = 0.0
            
            show_text_input_sre_pourcentage_depots = st.checkbox("Dépôts (%)")
            if show_text_input_sre_pourcentage_depots:
                sre_pourcentage_depots = st.text_input("Dépôts (% SRE):", value=0)
                if sre_pourcentage_depots != "0":
                    validate_input_affectation("Dépôts:", sre_pourcentage_depots, "%", sre_renovation_m2)
                    # sre_pourcentage_depots = float(sre_pourcentage_depots)
            else:
                sre_pourcentage_depots = 0.0
            
            show_text_input_sre_pourcentage_installations_sportives = st.checkbox("Installations sportives (%)")
            if show_text_input_sre_pourcentage_installations_sportives:
                sre_pourcentage_installations_sportives = st.text_input("Installations sportives (% SRE):", value=0)
                if sre_pourcentage_installations_sportives != "0":
                    validate_input_affectation("Installations sportives:", sre_pourcentage_installations_sportives, "%", sre_renovation_m2)
                    # sre_pourcentage_installations_sportives = float(sre_pourcentage_installations_sportives)
            else:
                sre_pourcentage_installations_sportives = 0.0
            
            show_text_input_sre_pourcentage_piscines_couvertes = st.checkbox("Piscines couvertes (%)")
            if show_text_input_sre_pourcentage_piscines_couvertes:
                sre_pourcentage_piscines_couvertes = st.text_input("Piscines couvertes (% SRE):", value=0)
                if sre_pourcentage_piscines_couvertes != "0":
                    validate_input_affectation("Piscines couvertes:", sre_pourcentage_piscines_couvertes, "%", sre_renovation_m2)
                    # sre_pourcentage_piscines_couvertes = float(sre_pourcentage_piscines_couvertes)
            else:
                sre_pourcentage_piscines_couvertes = 0.0

            # Somme des pourcentages
            try:
                sre_pourcentage_affectations_somme_avertisement = float(sre_pourcentage_habitat_collectif) + \
                    float(sre_pourcentage_habitat_individuel) + \
                    float(sre_pourcentage_administration) + \
                    float(sre_pourcentage_ecoles) + \
                    float(sre_pourcentage_commerce) + \
                    float(sre_pourcentage_restauration) + \
                    float(sre_pourcentage_lieux_de_rassemblement) + \
                    float(sre_pourcentage_hopitaux) + \
                    float(sre_pourcentage_industrie) + \
                    float(sre_pourcentage_depots) + \
                    float(sre_pourcentage_installations_sportives) + \
                    float(sre_pourcentage_piscines_couvertes)
                if sre_pourcentage_affectations_somme_avertisement != 100:
                    st.write(f"<p style='color: red;'><strong>Somme des pourcentages doit être égale à 100% ({sre_pourcentage_affectations_somme_avertisement})</strong></p>", unsafe_allow_html=True)
            except ValueError:
                st.write("Problème dans la somme des pourcentages des affectations")

        with col2:
            # Agents énergétiques
            st.subheader('Agents énergétiques utilisés pour le chauffage et l\'ECS sur la période')

            options_agent_energetique_ef = ['Mazout (kg)',
                                            'Mazout (litres)',
                                            'Mazout (kWh)',
                                            'Gaz naturel (m³)',
                                            'Gaz naturel (kWh)',
                                            'Bois buches dur (stère)',
                                            'Bois buches tendre (stère)',
                                            'Bois buches tendre (kWh)',
                                            'Pellets (m³)',
                                            'Pellets (kg)',
                                            'Pellets (kWh)',
                                            'Plaquettes (m³)',
                                            'Plaquettes (kWh)',
                                            'CAD (kWh)',
                                            'Electricité pour les PAC (kWh)',
                                            'Electricité directe (kWh)',
                                            'Autre (kWh)']
            selected_agent_energetique_ef = st.multiselect('Agent(s) énergétique(s):', options_agent_energetique_ef)

            # initialisation des variables
            agent_energetique_ef_mazout_kg = 0.0
            agent_energetique_ef_mazout_litres = 0.0
            agent_energetique_ef_mazout_kwh = 0.0
            agent_energetique_ef_gaz_naturel_m3 = 0.0
            agent_energetique_ef_gaz_naturel_kwh = 0.0
            agent_energetique_ef_bois_buches_dur_stere = 0.0
            agent_energetique_ef_bois_buches_tendre_stere = 0.0
            agent_energetique_ef_bois_buches_tendre_kwh = 0.0
            agent_energetique_ef_pellets_m3 = 0.0
            agent_energetique_ef_pellets_kg = 0.0
            agent_energetique_ef_pellets_kwh = 0.0
            agent_energetique_ef_plaquettes_m3 = 0.0
            agent_energetique_ef_plaquettes_kwh = 0.0
            agent_energetique_ef_cad_kwh = 0.0
            agent_energetique_ef_electricite_pac_kwh = 0.0
            agent_energetique_ef_electricite_directe_kwh = 0.0
            agent_energetique_ef_autre_kwh = 0.0

            if 'Mazout (kg)' in selected_agent_energetique_ef:
                agent_energetique_ef_mazout_kg = st.text_input('Mazout (kg):', value=0.0)
                if agent_energetique_ef_mazout_kg != "0":
                    validate_agent_energetique_input("Mazout:", agent_energetique_ef_mazout_kg, "kg")
                    agent_energetique_ef_mazout_kg = float(agent_energetique_ef_mazout_kg)
            
            if 'Mazout (litres)' in selected_agent_energetique_ef:
                agent_energetique_ef_mazout_litres = st.text_input('Mazout (litres):', value=0.0)
                if agent_energetique_ef_mazout_litres != "0":
                    validate_agent_energetique_input("Mazout:", agent_energetique_ef_mazout_litres, "litres")
                    agent_energetique_ef_mazout_litres = float(agent_energetique_ef_mazout_litres)
            
            if 'Mazout (kWh)' in selected_agent_energetique_ef:
                agent_energetique_ef_mazout_kwh = st.text_input('Mazout (kWh):', value=0.0)
                if agent_energetique_ef_mazout_kwh != "0":
                    validate_agent_energetique_input("Mazout:", agent_energetique_ef_mazout_kwh, "kWh")
                    agent_energetique_ef_mazout_kwh = float(agent_energetique_ef_mazout_kwh)
            
            if 'Gaz naturel (m³)' in selected_agent_energetique_ef:
                agent_energetique_ef_gaz_naturel_m3 = st.text_input('Gaz naturel (m³):', value=0.0)
                if agent_energetique_ef_gaz_naturel_m3 != "0":
                    validate_agent_energetique_input("Gaz naturel:", agent_energetique_ef_gaz_naturel_m3, "m³")
                    agent_energetique_ef_gaz_naturel_m3 = float(agent_energetique_ef_gaz_naturel_m3)
            
            if 'Gaz naturel (kWh)' in selected_agent_energetique_ef:
                agent_energetique_ef_gaz_naturel_kwh = st.text_input('Gaz naturel (kWh):', value=0.0)
                if agent_energetique_ef_gaz_naturel_kwh != "0":
                    validate_agent_energetique_input("Gaz naturel:", agent_energetique_ef_gaz_naturel_kwh, "kWh")
                    agent_energetique_ef_gaz_naturel_kwh = float(agent_energetique_ef_gaz_naturel_kwh)
            
            if 'Bois buches dur (stère)' in selected_agent_energetique_ef:
                agent_energetique_ef_bois_buches_dur_stere = st.text_input('Bois buches dur (stère):', value=0.0)
                if agent_energetique_ef_bois_buches_dur_stere != "0":
                    validate_agent_energetique_input("Bois buches dur:", agent_energetique_ef_bois_buches_dur_stere, "stère")
                    agent_energetique_ef_bois_buches_dur_stere = float(agent_energetique_ef_bois_buches_dur_stere)
            
            if 'Bois buches tendre (stère)' in selected_agent_energetique_ef:
                agent_energetique_ef_bois_buches_tendre_stere = st.text_input('Bois buches tendre (stère):', value=0.0)
                if agent_energetique_ef_bois_buches_tendre_stere != "0":
                    validate_agent_energetique_input("Bois buches tendre:", agent_energetique_ef_bois_buches_tendre_stere, "stère")
                    agent_energetique_ef_bois_buches_tendre_stere = float(agent_energetique_ef_bois_buches_tendre_stere)
            
            if 'Bois buches tendre (kWh)' in selected_agent_energetique_ef:
                agent_energetique_ef_bois_buches_tendre_kwh = st.text_input('Bois buches tendre (kWh):', value=0.0)
                if agent_energetique_ef_bois_buches_tendre_kwh != "0":
                    validate_agent_energetique_input("Bois buches tendre:", agent_energetique_ef_bois_buches_tendre_kwh, "kWh")
                    agent_energetique_ef_bois_buches_tendre_kwh = float(agent_energetique_ef_bois_buches_tendre_kwh)
            
            if 'Pellets (m³)' in selected_agent_energetique_ef:
                agent_energetique_ef_pellets_m3 = st.text_input('Pellets (m³):', value=0.0)
                if agent_energetique_ef_pellets_m3 != "0":
                    validate_agent_energetique_input("Pellets:", agent_energetique_ef_pellets_m3, "m³")
                    agent_energetique_ef_pellets_m3 = float(agent_energetique_ef_pellets_m3)
            
            if 'Pellets (kg)' in selected_agent_energetique_ef:
                agent_energetique_ef_pellets_kg = st.text_input('Pellets (kg):', value=0.0)
                if agent_energetique_ef_pellets_kg != "0":
                    validate_agent_energetique_input("Pellets:", agent_energetique_ef_pellets_kg, "kg")
                    agent_energetique_ef_pellets_kg = float(agent_energetique_ef_pellets_kg)
            
            if 'Pellets (kWh)' in selected_agent_energetique_ef:
                agent_energetique_ef_pellets_kwh = st.text_input('Pellets (kWh):', value=0.0)
                if agent_energetique_ef_pellets_kwh != "0":
                    validate_agent_energetique_input("Pellets:", agent_energetique_ef_pellets_kwh, "kWh")
                    agent_energetique_ef_pellets_kwh = float(agent_energetique_ef_pellets_kwh)
            
            if 'Plaquettes (m³)' in selected_agent_energetique_ef:
                agent_energetique_ef_plaquettes_m3 = st.text_input('Plaquettes (m³):', value=0.0)
                if agent_energetique_ef_plaquettes_m3 != "0":
                    validate_agent_energetique_input("Plaquettes:", agent_energetique_ef_plaquettes_m3, "m³")
                    agent_energetique_ef_plaquettes_m3 = float(agent_energetique_ef_plaquettes_m3)
            
            if 'Plaquettes (kWh)' in selected_agent_energetique_ef:
                agent_energetique_ef_plaquettes_kwh = st.text_input('Plaquettes (kWh):', value=0.0)
                if agent_energetique_ef_plaquettes_kwh != "0":
                    validate_agent_energetique_input("Plaquettes:", agent_energetique_ef_plaquettes_kwh, "kWh")
                    agent_energetique_ef_plaquettes_kwh = float(agent_energetique_ef_plaquettes_kwh)
            
            if 'CAD (kWh)' in selected_agent_energetique_ef:
                agent_energetique_ef_cad_kwh = st.text_input('CAD (kWh):', value=0.0)
                if agent_energetique_ef_cad_kwh != "0":
                    validate_agent_energetique_input("CAD:", agent_energetique_ef_cad_kwh, "kWh")
                    agent_energetique_ef_cad_kwh = float(agent_energetique_ef_cad_kwh)
            
            if 'Electricité pour les PAC (kWh)' in selected_agent_energetique_ef:
                agent_energetique_ef_electricite_pac_kwh = st.text_input('Electricité pour les PAC (kWh):', value=0.0)
                if agent_energetique_ef_electricite_pac_kwh != "0":
                    validate_agent_energetique_input("Electricité pour les PAC:", agent_energetique_ef_electricite_pac_kwh, "kWh")
                    agent_energetique_ef_electricite_pac_kwh = float(agent_energetique_ef_electricite_pac_kwh)
            
            if 'Electricité directe (kWh)' in selected_agent_energetique_ef:
                agent_energetique_ef_electricite_directe_kwh = st.text_input('Electricité directe (kWh):', value=0.0)
                if agent_energetique_ef_electricite_directe_kwh != "0":
                    validate_agent_energetique_input("Electricité directe:", agent_energetique_ef_electricite_directe_kwh, "kWh")
                    agent_energetique_ef_electricite_directe_kwh = float(agent_energetique_ef_electricite_directe_kwh)
            
            if 'Autre (kWh)' in selected_agent_energetique_ef:
                agent_energetique_ef_autre_kwh = st.text_input('Autre (kWh):', value=0.0)
                if agent_energetique_ef_autre_kwh != "0":
                    validate_agent_energetique_input("Autre:", agent_energetique_ef_autre_kwh, "kWh")
                    agent_energetique_ef_autre_kwh = float(agent_energetique_ef_autre_kwh)

            try:
                agent_energetique_ef_somme_avertissement = agent_energetique_ef_mazout_kg + \
                    agent_energetique_ef_mazout_litres + \
                    agent_energetique_ef_mazout_kwh + \
                    agent_energetique_ef_gaz_naturel_m3 + \
                    agent_energetique_ef_gaz_naturel_kwh + \
                    agent_energetique_ef_bois_buches_dur_stere + \
                    agent_energetique_ef_bois_buches_tendre_stere + \
                    agent_energetique_ef_bois_buches_tendre_kwh + \
                    agent_energetique_ef_pellets_m3 + \
                    agent_energetique_ef_pellets_kg + \
                    agent_energetique_ef_pellets_kwh + \
                    agent_energetique_ef_plaquettes_m3 + \
                    agent_energetique_ef_plaquettes_kwh + \
                    agent_energetique_ef_cad_kwh + \
                    agent_energetique_ef_electricite_pac_kwh + \
                    agent_energetique_ef_electricite_directe_kwh + \
                    agent_energetique_ef_autre_kwh
                if agent_energetique_ef_somme_avertissement <= 0:
                    st.write(f"<p style='color: red;'><strong>Veuillez renseigner une quantité d'énergie utilisée sur la période ({agent_energetique_ef_somme_avertissement})</strong></p>", unsafe_allow_html=True)
            except ValueError:
                st.write("Problème dans la somme des agents énergétiques")

        st.subheader('Sélectionner les dates de début et fin de période')
        col3, col4 = st.columns(2)
        # dates
        with col3:
            last_year = pd.to_datetime(df_meteo_tre200d0['time'].max()) - pd.DateOffset(days=365)
            periode_start = st.date_input("Début de la période", datetime.date(last_year.year, last_year.month, last_year.day))
        
        with col4:
            fin_periode_txt = f"Fin de la période (météo disponible jusqu'au: {df_meteo_tre200d0['time'].max().strftime('%Y-%m-%d')})"
            max_date = pd.to_datetime(df_meteo_tre200d0['time'].max())
            periode_end = st.date_input(fin_periode_txt, datetime.date(max_date.year, max_date.month, max_date.day))
        
        periode_nb_jours = (periode_end - periode_start).days + 1
        periode_nb_jours = float(periode_nb_jours)

        periode_start = pd.to_datetime(periode_start)
        periode_end = pd.to_datetime(periode_end)
                
        try:
            if periode_nb_jours <= 180:
                st.write("<p style='color: red;'><strong>La période de mesure doit être supérieure à 3 mois (minimum recommandé 6 mois)</strong></p>", unsafe_allow_html=True)
        except ValueError:  
            st.write("Problème de date de début et de fin de période")
        st.write(f"Période du {periode_start.strftime('%Y-%m-%d')} au {periode_end.strftime('%Y-%m-%d')} soit {int(periode_nb_jours)} jours")

        st.subheader('IDC moyen avant travaux et objectif en énergie finale')
        # st.text("Ces données se trouvent dans le tableau Excel de fixation d'objectif de performances:\n\
        # - Surélévation: C92/C94\n\
        # - Rénovation: C61/C63")

        col5, col6 = st.columns(2)

        with col5:
            # Autres données
            # st.write('IDC moyen 3 ans avant travaux (Ef,avant,corr [kWh/m²/an])')
            ef_avant_corr_kwh_m2 = st.text_input("IDC moyen 3 ans avant travaux (Ef,avant,corr [kWh/m²/an]):",
                                                 value=0,
                                                 help="Surélévation: C92 / Rénovation: C61",)
            if ef_avant_corr_kwh_m2 != "0":
                validate_input("Ef,avant,corr:", ef_avant_corr_kwh_m2, "kWh/m²/an")
            ef_avant_corr_kwh_m2 = float(ef_avant_corr_kwh_m2)
            try:
                if float(ef_avant_corr_kwh_m2) <= 0:
                    st.write("<p style='color: red;'><strong>Ef,avant,corr [kWh/m²/an] doit être supérieur à 0</strong></p>", unsafe_allow_html=True)
            except ValueError:
                st.write("Problème dans Ef,avant,corr [kWh/m²/an]")

        with col6:
            # st.write('Objectif en énergie finale (Ef,obj *fp [kWh/m²/an])')
            ef_objectif_pondere_kwh_m2 = st.text_input("Ef,obj * fp [kWh/m²/an]:",
                                                       value=0,
                                                       help="Surélévation: C94 / Rénovation: C63",)
            if ef_objectif_pondere_kwh_m2 != "0":
                validate_input("Ef,obj * fp:", ef_objectif_pondere_kwh_m2, "kWh/m²/an")
            ef_objectif_pondere_kwh_m2 = float(ef_objectif_pondere_kwh_m2)
            try:
                if float(ef_objectif_pondere_kwh_m2) <= 0:
                    st.write("<p style='color: red;'><strong>Ef,obj *fp [kWh/m²/an] doit être supérieur à 0</strong></p>", unsafe_allow_html=True)
            except ValueError:
                st.write("Problème dans Ef,obj *fp [kWh/m²/an]")

        delta_ef_visee_kwh_m2 = float(ef_avant_corr_kwh_m2) - float(ef_objectif_pondere_kwh_m2)
        if delta_ef_visee_kwh_m2 > 0:
            eq = r"\begin{split}"
            eq += r"\Delta E_{f,\text{visée}} = E_{f,\text{avant,corr}} - E_{f,\text{objectif}} \cdot f_p = "
            eq += f"{round(ef_avant_corr_kwh_m2, 2)} - {round(ef_objectif_pondere_kwh_m2, 2)} = {round(delta_ef_visee_kwh_m2, 2)}"
            eq += r"\quad\text{kWh/m²/an}"
            eq += r"\end{split}"

            st.latex(eq)

        st.subheader('Répartition énergie finale ECS/Chauffage')
        # st.text("Ces données se trouvent dans le tableau Excel de fixation d'objectif de performances:\n\
        # - Surélévation: C77:C81\n\
        # - Rénovation: C49:C50")
        show_text_input_agent_energetique_ef_autre_kwh = st.checkbox("Surélévation")
        col7, col8 = st.columns(2)
        with col7:
            # Répartition énergie finale
            #st.write('Répartition en énergie finale - Chauffage partie rénovée [%]')
            repartition_energie_finale_partie_renovee_chauffage = st.text_input("Chauffage partie rénovée [%]",
                                                                                value=0,
                                                                                help="Surélévation: C77 / Rénovation: C49")
            if repartition_energie_finale_partie_renovee_chauffage != "0":
                validate_input("Répartition EF - Chauffage partie rénovée:", repartition_energie_finale_partie_renovee_chauffage, "%")
            repartition_energie_finale_partie_renovee_chauffage = float(repartition_energie_finale_partie_renovee_chauffage)
            
            if show_text_input_agent_energetique_ef_autre_kwh:
                # st.write('Répartition EF - Chauffage partie surélévée [%]')
                repartition_energie_finale_partie_surelevee_chauffage = st.text_input("Chauffage partie surélévée",
                                                                                        value=0,
                                                                                        help= "C79")
                if repartition_energie_finale_partie_surelevee_chauffage != "0":
                    validate_input("Répartition en énergie finale - Chauffage partie surélévée:", repartition_energie_finale_partie_surelevee_chauffage, "%")
                repartition_energie_finale_partie_surelevee_chauffage = float(repartition_energie_finale_partie_surelevee_chauffage)

        with col8:
            #st.write('Répartition en énergie finale - ECS partie rénovée [%]')
            repartition_energie_finale_partie_renovee_ecs = st.text_input("ECS partie rénovée [%]",
                                                                          value=0,
                                                                          help="Surélévation: C78 / Rénovation: C50")
            if repartition_energie_finale_partie_renovee_ecs != "0":
                validate_input("Répartition EF - ECS partie rénovée:", repartition_energie_finale_partie_renovee_ecs, "%")
            repartition_energie_finale_partie_renovee_ecs = float(repartition_energie_finale_partie_renovee_ecs)

            if show_text_input_agent_energetique_ef_autre_kwh:
                # st.write('Répartition en énergie finale - ECS partie surélévée [%]')
                repartition_energie_finale_partie_surelevee_ecs = st.text_input("ECS partie surélévée [%]",
                                                                                value=0,
                                                                                help= "C80")
                if repartition_energie_finale_partie_surelevee_ecs != "0":
                    validate_input("Répartition EF - ECS partie surélevée:", repartition_energie_finale_partie_surelevee_ecs, "%")
                repartition_energie_finale_partie_surelevee_ecs = float(repartition_energie_finale_partie_surelevee_ecs)
            else:
                repartition_energie_finale_partie_surelevee_chauffage = 0.0
                repartition_energie_finale_partie_surelevee_ecs = 0.0
            
        # Validation somme des pourcentages
        try:
            repartition_ef_somme_avertissement = repartition_energie_finale_partie_renovee_chauffage + \
                repartition_energie_finale_partie_renovee_ecs +\
                repartition_energie_finale_partie_surelevee_chauffage + \
                repartition_energie_finale_partie_surelevee_ecs
            if repartition_ef_somme_avertissement != 100:
                st.write(f"<p style='color: red;'><strong>La somme des pourcentages de répartition de l'énergie finale doit être égale à 100% ({repartition_ef_somme_avertissement}%)</strong></p>", unsafe_allow_html=True)
        except ValueError:
            st.write("Problème dans la somme des pourcentages de répartition de l'énergie finale")

    with tab3:
        columns = ['Dénomination', 'Valeur', 'Unité', 'Commentaire', 'Excel', 'Variable/Formule']
        df_periode_list = []
        df_list = []

        # C65 → Début période
        df_periode_list.append({
            'Dénomination': 'Début période',
            'Valeur': periode_start,
            'Unité': '-',
            'Commentaire': 'Date de début de la période',
            'Excel': 'C65',
            'Variable/Formule' : 'periode_start'})
        
        # C66 → Fin période
        df_periode_list.append({
            'Dénomination': 'Fin période',
            'Valeur': periode_end,
            'Unité': '-',
            'Commentaire': 'Date de fin de la période',
            'Excel': 'C66',
            'Variable/Formule': 'periode_end'
        })

        # C67 → Nombre de jours
        df_list.append({
            'Dénomination': 'Nombre de jour(s)',
            'Valeur': periode_nb_jours,
            'Unité': 'jour(s)',
            'Commentaire': 'Nombre de jour(s) dans la période',
            'Excel': 'C67',
            'Variable/Formule': 'periode_nb_jours'
        })


        # C86 → Répartition en énergie finale - Chauffage partie rénovée
        df_list.append({
            'Dénomination': 'Répartition en énergie finale (chauffage) pour la partie rénové',
            'Valeur': repartition_energie_finale_partie_renovee_chauffage,
            'Unité': '%',
            'Commentaire': '',
            'Excel': 'C86',
            'Variable/Formule': "repartition_energie_finale_partie_renovee_chauffage"
        })

        # C87 → Répartition en énergie finale - ECS partie rénovée
        df_list.append({
            'Dénomination': 'Répartition en énergie finale (ECS) pour la partie rénové',
            'Valeur': repartition_energie_finale_partie_renovee_ecs,
            'Unité': '%',
            'Commentaire': '',  # You can add a comment if needed
            'Excel': 'C87',
            'Variable/Formule': "repartition_energie_finale_partie_renovee_ecs"
        })

        # C88 → Répartition en énergie finale - Chauffage partie surélévée
        df_list.append({
            'Dénomination': 'Répartition en énergie finale (chauffage) pour la partie surélévée',
            'Valeur': repartition_energie_finale_partie_surelevee_chauffage,
            'Unité': '%',
            'Commentaire': "0 if no surélévation",  # You can add a comment if needed
            'Excel': 'C88',
            'Variable/Formule': "repartition_energie_finale_partie_surelevee_chauffage"
        })
        
        # C89 → Répartition EF - ECS partie surélévée
        df_list.append({
            'Dénomination': 'Répartition en énergie finale - ECS partie surélévée',
            'Valeur': repartition_energie_finale_partie_surelevee_ecs,
            'Unité': '%',
            'Commentaire': "Part d'énergie finale (ECS) pour la partie surélévée. 0 s'il n'y a pas de surélévation",
            'Excel': 'C89',
            'Variable/Formule': "repartition_energie_finale_partie_surelevee_ecs"
        })
        
        # C91 → Part EF pour partie rénové (Chauffage + ECS)
        repartition_energie_finale_partie_renovee_somme = repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_renovee_ecs
        df_list.append({
            'Dénomination': 'Part EF pour partie rénové (Chauffage + ECS)',
            'Valeur': repartition_energie_finale_partie_renovee_somme,
            'Unité': '%',
            'Commentaire': "Part d'énergie finale (Chauffage + ECS) pour la partie rénové. 100% si pas de surélévation",
            'Excel': 'C91',
            'Variable/Formule': "repartition_energie_finale_partie_renovee_somme = repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_renovee_ecs"
        })
        
        # C92 → Est. ECS/ECS annuelle
        estimation_ecs_annuel = periode_nb_jours/365
        df_list.append({
            'Dénomination': 'Est. ECS/ECS annuelle',
            'Valeur': estimation_ecs_annuel,
            'Unité': '-',
            'Commentaire': 'Estimation de la part ECS sur une année',
            'Excel': 'C92',
            'Variable/Formule': 'estimation_ecs_annuel = periode_nb_jours/365'
        })

        # C93 → Est. Chauffage/Chauffage annuel prévisible
        dj_periode = calcul_dj_periode(df_meteo_tre200d0, periode_start, periode_end)
        dj_periode = float(dj_periode)
        estimation_part_chauffage_periode_sur_annuel = dj_periode / DJ_REF_ANNUELS
        estimation_part_chauffage_periode_sur_annuel = float(estimation_part_chauffage_periode_sur_annuel)
        df_list.append({
            'Dénomination': 'Est. Chauffage/Chauffage annuel prévisible',
            'Valeur': estimation_part_chauffage_periode_sur_annuel*100,
            'Unité': '%',
            'Commentaire': 'Est. Chauffage/Chauffage annuel prévisible → dj_periode (C101) / DJ_REF_ANNUELS (C102)',
            'Excel': 'C93',
            'Variable/Formule': 'estimation_part_chauffage_periode_sur_annuel = dj_periode / DJ_REF_ANNUELS'
        })

        # C94 → Est. EF période / EF année
        estimation_energie_finale_periode_sur_annuel = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) +\
                                            (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage))
        df_list.append({
            'Dénomination': 'Est. EF période / EF année',
            'Valeur': estimation_energie_finale_periode_sur_annuel,
            'Unité': '%',
            'Commentaire': 'Estimation en énergie finale sur la période / énergie finale sur une année',
            'Excel': 'C94',
            'Variable/Formule': 'estimation_energie_finale_periode_sur_annuel = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) + (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage))'
        })

        # C95 → Est. Part ECS période comptage
        try:
            if estimation_energie_finale_periode_sur_annuel != 0:
                part_ecs_periode_comptage = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + \
                    repartition_energie_finale_partie_surelevee_ecs)) / estimation_energie_finale_periode_sur_annuel
            else:
                part_ecs_periode_comptage = 0.0
        except ZeroDivisionError:
            part_ecs_periode_comptage = 0.0
        df_list.append({
            'Dénomination': 'Est. Part ECS période comptage',
            'Valeur': part_ecs_periode_comptage*100,
            'Unité': '%',
            'Commentaire': '',
            'Excel': 'C95',
            'Variable/Formule': 'part_ecs_periode_comptage = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) / estimation_energie_finale_periode_sur_annuel'
        })

        # C96 → Est. Part Chauffage période comptage
        try:
            if estimation_energie_finale_periode_sur_annuel != 0:
                part_chauffage_periode_comptage = (estimation_part_chauffage_periode_sur_annuel * \
                    (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage)) / estimation_energie_finale_periode_sur_annuel
            else:
                part_chauffage_periode_comptage = 0.0
        except ZeroDivisionError:
            part_chauffage_periode_comptage = 0.0
        df_list.append({
            'Dénomination': 'Est. Part Chauffage période comptage',
            'Valeur': part_chauffage_periode_comptage*100,
            'Unité': '%',
            'Commentaire': '',
            'Excel': 'C96',
            'Variable/Formule': 'part_chauffage_periode_comptage = (estimation_part_chauffage_periode_sur_annuel * \
            (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage)) / estimation_energie_finale_periode_sur_annuel'
        })

        # C97 → correction ECS = 365/nb jour comptage
        correction_ecs = 365/periode_nb_jours
        df_list.append({
            'Dénomination': 'Correction ECS',
            'Valeur': correction_ecs,
            'Unité': '-',
            'Commentaire': '',
            'Excel': 'C97',
            'Variable/Formule': 'correction_ecs = 365/periode_nb_jours'
        })

        # C98 → Energie finale indiqué par le(s) compteur(s)
        agent_energetique_ef_mazout_somme_mj = (agent_energetique_ef_mazout_kg * CONVERSION_MAZOUT_KG_MJ + agent_energetique_ef_mazout_litres * CONVERSION_MAZOUT_LITRES_MJ + agent_energetique_ef_mazout_kwh * CONVERSION_MAZOUT_KWH_MJ)
        agent_energetique_ef_gaz_naturel_somme_mj = (agent_energetique_ef_gaz_naturel_m3 * CONVERSION_GAZ_NATUREL_M3_MJ + agent_energetique_ef_gaz_naturel_kwh * CONVERSION_GAZ_NATUREL_KWH_MJ)
        agent_energetique_ef_bois_buches_dur_somme_mj = (agent_energetique_ef_bois_buches_dur_stere * CONVERSION_BOIS_BUCHES_DUR_STERE_MJ)
        agent_energetique_ef_bois_buches_tendre_somme_mj = (agent_energetique_ef_bois_buches_tendre_stere * CONVERSION_BOIS_BUCHES_TENDRE_STERE_MJ + agent_energetique_ef_bois_buches_tendre_kwh * CONVERSION_BOIS_BUCHES_TENDRE_KWH_MJ)
        agent_energetique_ef_pellets_somme_mj = (agent_energetique_ef_pellets_m3 * CONVERSION_PELLETS_M3_MJ + agent_energetique_ef_pellets_kg * CONVERSION_PELLETS_KG_MJ + agent_energetique_ef_pellets_kwh * CONVERSION_PELLETS_KWH_MJ)
        agent_energetique_ef_plaquettes_somme_mj = (agent_energetique_ef_plaquettes_m3 * CONVERSION_PLAQUETTES_M3_MJ + agent_energetique_ef_plaquettes_kwh * CONVERSION_PLAQUETTES_KWH_MJ)
        agent_energetique_ef_cad_somme_mj = (agent_energetique_ef_cad_kwh * CONVERSION_CAD_KWH_MJ)
        agent_energetique_ef_electricite_pac_somme_mj = (agent_energetique_ef_electricite_pac_kwh * CONVERSION_ELECTRICITE_PAC_KWH_MJ)
        agent_energetique_ef_electricite_directe_somme_mj = (agent_energetique_ef_electricite_directe_kwh * CONVERSION_ELECTRICITE_DIRECTE_KWH_MJ)
        agent_energetique_ef_autre_somme_mj = (agent_energetique_ef_autre_kwh * CONVERSION_AUTRE_KWH_MJ)

        agent_energetique_ef_somme_kwh = (agent_energetique_ef_mazout_somme_mj + \
                                    agent_energetique_ef_gaz_naturel_somme_mj + \
                                        agent_energetique_ef_bois_buches_dur_somme_mj + \
                                        agent_energetique_ef_bois_buches_tendre_somme_mj + \
                                        agent_energetique_ef_pellets_somme_mj + \
                                        agent_energetique_ef_plaquettes_somme_mj + \
                                        agent_energetique_ef_cad_somme_mj +\
                                        agent_energetique_ef_electricite_pac_somme_mj + \
                                        agent_energetique_ef_electricite_directe_somme_mj + \
                                        agent_energetique_ef_autre_somme_mj) / 3.6
        df_list.append({
            'Dénomination': 'Energie finale indiqué par le(s) compteur(s)',
            'Valeur': agent_energetique_ef_somme_kwh,
            'Unité': 'kWh',
            'Commentaire': "Somme de l'énergie finale indiqué par le(s) compteur(s) en kWh",
            'Excel': 'C98',
            'Variable/Formule': 'agent_energetique_ef_somme_kwh'
        })

        # C99 → Methodo_Bww → Part de ECS en énergie finale sur la période
        methodo_b_ww_kwh = (agent_energetique_ef_somme_kwh) * part_ecs_periode_comptage
        df_list.append({
            'Dénomination': 'Methodo_Bww',
            'Valeur': methodo_b_ww_kwh,
            'Unité': 'kWh',
            'Commentaire': '',
            'Excel': 'C99',
            'Variable/Formule': 'methodo_b_ww_kwh'
        })

        # C100 → Methodo_Eww
        try:
            if sre_renovation_m2 != 0 and periode_nb_jours != 0:
                methodo_e_ww_kwh = (methodo_b_ww_kwh / sre_renovation_m2) * (365 / periode_nb_jours)
            else:
                methodo_e_ww_kwh = 0.0
        except ZeroDivisionError:
            methodo_e_ww_kwh = 0.0
        df_list.append({
            'Dénomination': 'Methodo_Eww',
            'Valeur': methodo_e_ww_kwh,
            'Unité': 'kWh',
            'Commentaire': '',
            'Excel': 'C100',
            'Variable/Formule': 'Methodo_Eww'
        })

        # C101 → DJ ref annuels
        df_list.append({
            'Dénomination': 'DJ ref annuels',
            'Valeur': DJ_REF_ANNUELS,
            'Unité': 'Degré-jour',
            'Commentaire': 'Degré-jour 20/16 avec les températures extérieures de référence pour Genève-Cointrin selon SIA 2028:2008',
            'Excel': 'C101',
            'Variable/Formule': 'DJ_REF_ANNUELS'
        })

        # C102 → DJ période comptage
        df_list.append({
            'Dénomination': 'DJ période comptage',
            'Valeur': dj_periode,
            'Unité': 'Degré-jour',
            'Commentaire': 'Degré-jour 20/16 avec les températures extérieures (tre200d0) pour Genève-Cointrin relevée par MétéoSuisse',
            'Excel': 'C102',
            'Variable/Formule': 'dj_periode'
        })

        # C103 → Methodo_Bh → Part de chauffage en énergie finale sur la période
        methodo_b_h_kwh = agent_energetique_ef_somme_kwh * part_chauffage_periode_comptage
        df_list.append({
            'Dénomination': 'Methodo_Bh',
            'Valeur': methodo_b_h_kwh,
            'Unité': 'kWh',
            'Commentaire': 'Part de chauffage en énergie finale sur la période',
            'Excel': 'C103',
            'Variable/Formule': 'methodo_b_h_kwh = agent_energetique_ef_somme_kwh * part_chauffage_periode_comptage'
        })

        # C104 → Methodo_Eh
        try:
            if sre_renovation_m2 != 0 and dj_periode != 0:
                methodo_e_h_kwh = (methodo_b_h_kwh / sre_renovation_m2) * (DJ_REF_ANNUELS / dj_periode)
            else:
                methodo_e_h_kwh = 0.0
        except ZeroDivisionError:
            methodo_e_h_kwh = 0.0
        df_list.append({
            'Dénomination': 'Methodo_Eh',
            'Valeur': methodo_e_h_kwh,
            'Unité': 'kWh/m²',
            'Commentaire': 'Energie finale par unité de surface pour le chauffage sur la période climatiquement corrigée',
            'Excel': 'C104',
            'Variable/Formule': 'methodo_e_h_kwh = (methodo_b_h_kwh / sre_renovation_m2) * (DJ_REF_ANNUELS / dj_periode)'
        })

        # C105 → Ef,après,corr → Methodo_Eww + Methodo_Eh
        energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 = methodo_e_ww_kwh + methodo_e_h_kwh
        df_list.append({
            'Dénomination': 'Ef,après,corr (inclus surélévation)',
            'Valeur': energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2,
            'Unité': 'kWh/m²',
            'Commentaire': "Energie finale par unité de surface pour le chauffage climatiquement corrigée et l'ECS sur la période (inclus surélévation)",
            'Excel': 'C105',
            'Variable/Formule': 'energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 = methodo_e_ww_kwh + methodo_e_h_kwh'
        })

        # C106 → Part de l'énergie finale théorique dédiée à la partie rénovée (ECS+Ch.)
        df_list.append({
            'Dénomination': "Part de l'énergie finale théorique dédiée à la partie rénovée (ECS+Ch.)",
            'Valeur': repartition_energie_finale_partie_renovee_somme,
            'Unité': '%',
            'Commentaire': "Part de l'énergie finale théorique dédiée à la partie rénovée (ECS+Ch.)",
            'Excel': 'C106',
            'Variable/Formule': 'repartition_energie_finale_partie_renovee_somme'
        })

        # C107 → Ef,après,corr,rénové →Total en énergie finale (Eww+Eh) pour la partie rénovée
        energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 = energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 * (repartition_energie_finale_partie_renovee_somme / 100)
        df_list.append({
            'Dénomination': 'Ef,après,corr,rénové',
            'Valeur': energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2,
            'Unité': 'kWh/m²',
            'Commentaire': "Energie finale par unité de surface pour le chauffage et l'ECS sur la période climatiquement corrigée pour la partie rénovée",
            'Excel': 'C107',
            'Variable/Formule': 'energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 = energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 * (repartition_energie_finale_partie_renovee_somme / 100)'
        })

        # C108 → fp → facteur de pondération moyen
        try:
            if agent_energetique_ef_somme_kwh:
                facteur_ponderation_moyen = (agent_energetique_ef_mazout_somme_mj * FACTEUR_PONDERATION_MAZOUT + \
                                    agent_energetique_ef_gaz_naturel_somme_mj * FACTEUR_PONDERATION_GAZ_NATUREL + \
                                    agent_energetique_ef_bois_buches_dur_somme_mj * FACTEUR_PONDERATION_BOIS_BUCHES_DUR + \
                                    agent_energetique_ef_bois_buches_tendre_somme_mj * FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE + \
                                    agent_energetique_ef_pellets_somme_mj * FACTEUR_PONDERATION_PELLETS + \
                                    agent_energetique_ef_plaquettes_somme_mj * FACTEUR_PONDERATION_PLAQUETTES + \
                                    agent_energetique_ef_cad_somme_mj * FACTEUR_PONDERATION_CAD + \
                                    agent_energetique_ef_electricite_pac_somme_mj * FACTEUR_PONDERATION_ELECTRICITE_PAC + \
                                    agent_energetique_ef_electricite_directe_somme_mj * FACTEUR_PONDERATION_ELECTRICITE_DIRECTE + \
                                    agent_energetique_ef_autre_somme_mj * FACTEUR_PONDERATION_AUTRE) / (agent_energetique_ef_somme_kwh * 3.6)
            else:
                facteur_ponderation_moyen = 0
        except ZeroDivisionError:
            facteur_ponderation_moyen = 0
        df_list.append({
            'Dénomination': 'Facteur de pondération des agents énergétiques',
            'Valeur': facteur_ponderation_moyen,
            'Unité': '-',
            'Commentaire': 'Facteur de pondération moyen des agents énergétiques',
            'Excel': 'C108',
            'Variable/Formule': 'facteur_ponderation_moyen'
        })

        # C109 → Methodo_Eww*fp
        methodo_e_ww_renovee_pondere_kwh_m2 = methodo_e_ww_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)
        df_list.append({
            'Dénomination': 'Methodo_Eww*fp',
            'Valeur': methodo_e_ww_renovee_pondere_kwh_m2,
            'Unité': 'kWh/m²',
            'Commentaire': '',
            'Excel': 'C109',
            'Variable/Formule': 'methodo_e_ww_renovee_pondere_kwh_m2 = methodo_e_ww_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)'
        })

        # C110 → Methodo_Eh*fp
        methodo_e_h_renovee_pondere_kwh_m2 = methodo_e_h_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)
        df_list.append({
            'Dénomination': 'Methodo_Eh*fp',
            'Valeur':methodo_e_h_renovee_pondere_kwh_m2,
            'Unité': 'kWh/m²',
            'Commentaire': '',
            'Excel': 'C110',
            'Variable/Formule': 'methodo_e_h_renovee_pondere_kwh_m2 = methodo_e_h_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)'
        })

        # C113 → Ef,après,corr,rénové*fp
        energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 * facteur_ponderation_moyen
        df_list.append({
            'Dénomination': 'Ef,après,corr,rénové*fp',
            'Valeur': energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
            'Unité': 'kWh/m²',
            'Commentaire': '',
            'Excel': 'C113',
            'Variable/Formule': 'energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 * facteur_ponderation_moyen'
        })

        # C114 → Ef,après,corr,rénové*fp
        energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 * 3.6
        df_list.append({
            'Dénomination': 'Ef,après,corr,rénové*fp',
            'Valeur': energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2,
            'Unité': 'MJ/m²',
            'Commentaire': '',
            'Excel': 'C114',
            'Variable/Formule': 'energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 * 3.6'
        })


        # Autres dataframe
        df_periode = pd.DataFrame(df_periode_list, columns=columns)

        df = pd.DataFrame(df_list, columns=columns)


        df_meteo_note_calcul = df_meteo_tre200d0[(df_meteo_tre200d0['time'] >= periode_start) & (df_meteo_tre200d0['time'] <= periode_end)][['time', 'tre200d0', 'DJ_theta0_16']]

        df_agent_energetique = pd.DataFrame({
            'Agent énergétique' : ['Mazout', 'Gaz naturel', 'Bois (buches dur)', 'Bois (buches tendre)', 'Pellets', 'Plaquettes', 'CAD', 'Electricité (PAC)', 'Electricité (directe)', 'Autre'],
            'Somme MJ' : [agent_energetique_ef_mazout_somme_mj, agent_energetique_ef_gaz_naturel_somme_mj, agent_energetique_ef_bois_buches_dur_somme_mj, agent_energetique_ef_bois_buches_tendre_somme_mj, agent_energetique_ef_pellets_somme_mj, agent_energetique_ef_plaquettes_somme_mj, agent_energetique_ef_cad_somme_mj, agent_energetique_ef_electricite_pac_somme_mj, agent_energetique_ef_electricite_directe_somme_mj, agent_energetique_ef_autre_somme_mj],
            'Somme kWh' : [agent_energetique_ef_mazout_somme_mj / 3.6, agent_energetique_ef_gaz_naturel_somme_mj / 3.6, agent_energetique_ef_bois_buches_dur_somme_mj / 3.6, agent_energetique_ef_bois_buches_tendre_somme_mj / 3.6, agent_energetique_ef_pellets_somme_mj / 3.6, agent_energetique_ef_plaquettes_somme_mj / 3.6, agent_energetique_ef_cad_somme_mj / 3.6, agent_energetique_ef_electricite_pac_somme_mj / 3.6, agent_energetique_ef_electricite_directe_somme_mj / 3.6, agent_energetique_ef_autre_somme_mj / 3.6],
            'Facteur de pondération' : [FACTEUR_PONDERATION_MAZOUT, FACTEUR_PONDERATION_GAZ_NATUREL, FACTEUR_PONDERATION_BOIS_BUCHES_DUR, FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE, FACTEUR_PONDERATION_PELLETS, FACTEUR_PONDERATION_PLAQUETTES, FACTEUR_PONDERATION_CAD, FACTEUR_PONDERATION_ELECTRICITE_PAC, FACTEUR_PONDERATION_ELECTRICITE_DIRECTE, FACTEUR_PONDERATION_AUTRE],
            'Variable Agent énergétique': ['agent_energetique_ef_mazout_somme_mj', 'agent_energetique_ef_gaz_naturel_somme_mj', 'agent_energetique_ef_bois_buches_dur_somme_mj', 'agent_energetique_ef_bois_buches_tendre_somme_mj', 'agent_energetique_ef_pellets_somme_mj', 'agent_energetique_ef_plaquettes_somme_mj', 'agent_energetique_ef_cad_somme_mj', 'agent_energetique_ef_electricite_pac_somme_mj', 'agent_energetique_ef_electricite_directe_somme_mj', 'agent_energetique_ef_autre_somme_mj'],
            'Variable facteur de pondération': ['FACTEUR_PONDERATION_MAZOUT', 'FACTEUR_PONDERATION_GAZ_NATUREL', 'FACTEUR_PONDERATION_BOIS_BUCHES_DUR', 'FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE', 'FACTEUR_PONDERATION_PELLETS', 'FACTEUR_PONDERATION_PLAQUETTES', 'FACTEUR_PONDERATION_CAD', 'FACTEUR_PONDERATION_ELECTRICITE_PAC', 'FACTEUR_PONDERATION_ELECTRICITE_DIRECTE', 'FACTEUR_PONDERATION_AUTRE']
        })

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
        st.subheader('Note de calcul')
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
        formula_facteur_ponderation_moyen = r"facteur\_ponderation\_moyen = \frac{{({0})}}{{({1})}} = {2}".format(
            agent_energetique_ef_mazout_somme_mj * FACTEUR_PONDERATION_MAZOUT + \
            agent_energetique_ef_gaz_naturel_somme_mj * FACTEUR_PONDERATION_GAZ_NATUREL + \
            agent_energetique_ef_bois_buches_dur_somme_mj * FACTEUR_PONDERATION_BOIS_BUCHES_DUR + \
            agent_energetique_ef_bois_buches_tendre_somme_mj * FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE + \
            agent_energetique_ef_pellets_somme_mj * FACTEUR_PONDERATION_PELLETS + \
            agent_energetique_ef_plaquettes_somme_mj * FACTEUR_PONDERATION_PLAQUETTES + \
            agent_energetique_ef_cad_somme_mj * FACTEUR_PONDERATION_CAD + \
            agent_energetique_ef_electricite_pac_somme_mj * FACTEUR_PONDERATION_ELECTRICITE_PAC + \
            agent_energetique_ef_electricite_directe_somme_mj * FACTEUR_PONDERATION_ELECTRICITE_DIRECTE + \
            agent_energetique_ef_autre_somme_mj * FACTEUR_PONDERATION_AUTRE,
            agent_energetique_ef_somme_kwh * 3.6,
            facteur_ponderation_moyen
        )

        # Render the formula in LaTeX
        st.latex(formula_facteur_ponderation_moyen)

        st.write("Données météo station Genève-Cointrin pour la période sélectionnée")
        st.dataframe(df_meteo_note_calcul)

    with tab4:
        st.subheader("Synthèse des résultats")

        # calculs
        delta_ef_realisee_kwh_m2 = ef_avant_corr_kwh_m2 - energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
        try:
            atteinte_objectif = delta_ef_realisee_kwh_m2/delta_ef_visee_kwh_m2
        except ZeroDivisionError:
            atteinte_objectif = 0.0

        df_resultats1 = pd.DataFrame({
            'Variable': [
                'IDC moyen 3 ans avant travaux → (Ef,avant,corr)',
                'EF pondéré corrigé clim. après travaux → (Ef,après,corr,rénové*fp)',
                'Objectif en énergie finale (Ef,obj *fp)',
                'Baisse ΔEf réalisée → ∆Ef,réel = Ef,avant,corr - Ef,après,corr*fp',
                'Baisse ΔEf visée → ∆Ef,visée = Ef,avant,corr - Ef,obj*fp'],
            'kWh/m²/an': [
                ef_avant_corr_kwh_m2,
                energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
                ef_objectif_pondere_kwh_m2,
                delta_ef_realisee_kwh_m2,
                delta_ef_visee_kwh_m2],
            'MJ/m²/an': [ ef_avant_corr_kwh_m2*3.6,
                energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2*3.6,
                ef_objectif_pondere_kwh_m2*3.6,
                delta_ef_realisee_kwh_m2*3.6,
                delta_ef_visee_kwh_m2*3.6],
        })

        # dtypes
        df_resultats1['Variable'] = df_resultats1['Variable'].astype(str)
        df_resultats1['kWh/m²/an'] = df_resultats1['kWh/m²/an'].astype(float)
        df_resultats1['MJ/m²/an'] = df_resultats1['MJ/m²/an'].astype(float)
        st.table(df_resultats1)

        # résultats en latex

        formula_atteinte_objectif = r"Atteinte\ objectif = \frac{{\Delta E_{{f,réel}}}}{{\Delta E_{{f,visée}}}} = \frac{{E_{{f,avant,corr}} - E_{{f,après,corr,rénové}}*f_{{p}}}}{{E_{{f,avant,corr}} - E_{{f,obj}}*f_{{p}}}}"

        formula_atteinte_objectif_num = r"Atteinte\ objectif = \frac{{{} - {}*{}}}{{{} - {}*{}}} = {}".format(
            ef_avant_corr_kwh_m2,
            round(energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2, 4),
            facteur_ponderation_moyen,
            ef_avant_corr_kwh_m2,
            ef_objectif_pondere_kwh_m2,
            facteur_ponderation_moyen,
            round(atteinte_objectif, 4)
        )

        formula_atteinte_objectifs_pourcent = r"Atteinte\ objectif\ [\%]= {} \%".format(
            round(atteinte_objectif*100, 2)
        )

        # latex color
        if atteinte_objectif >= 0.85:
            formula_atteinte_objectifs_pourcent = r"\textcolor{green}{" + formula_atteinte_objectifs_pourcent + "}"
        else:
            formula_atteinte_objectifs_pourcent = r"\textcolor{red}{" + formula_atteinte_objectifs_pourcent + "}"

        # Render the formula in LaTeX
        st.latex(formula_atteinte_objectif)
        st.latex(formula_atteinte_objectif_num)
        st.latex(formula_atteinte_objectifs_pourcent)
    
    with tab5:
        st.subheader("Envoi des données à eco21/HEPIA")

        nom_projet = st.text_input("Nom du projet")
        adresse_projet = st.text_input("Adresse")
        amoen_id = st.text_input("AMOEN")

        df_envoi_columns = [
            'Nom_projet', 'Adresse', 'AMOEN',
            'SRE rénovée', 'Affectation habitat collectif pourcentage',
            'Affectation habitat individuel pourcentage',
            'Affectation administration pourcentage',
            'Affectation écoles pourcentage',
            'Affectation commerce pourcentage',
            'Affectation restauration pourcentage',
            'Affectation lieux de rassemblement pourcentage',
            'Affectation hopitaux pourcentage',
            'Affectation industrie pourcentage',
            'Affectation dépots pourcentage',
            'Affectation installations sportives pourcentage',
            'Affectation piscines couvertes pourcentage',
            'Agent énergétique mazout kg',
            'Agent énergétique mazout litres',
            'Agent énergétique mazout kWh',
            'Agent énergétique gaz naturel m3',
            'Agent énergétique gaz naturel kWh',
            'Agent énergétique bois buches dur stère',
            'Agent énergétique bois buches tendre stère',
            'Agent énergétique bois buches tendre kWh',
            'Agent énergétique pellets m3',
            'Agent énergétique pellets kg',
            'Agent énergétique pellets kWh',
            'Agent énergétique plaquettes m3',
            'Agent énergétique plaquettes kWh',
            'Agent énergétique CAD kWh',
            'Agent énergétique Electricité PAC kWh',
            'Agent énergétique Electricité directe kWh',
            'Agent énergétique Autre kWh',
            'Période début', 'Période fin',
            'Répartition en énergie finale - Chauffage partie rénovée',
            'Répartition en énergie finale - ECS partie rénovée',
            'Répartition en énergie finale - Chauffage partie surélévée',
            'Répartition en énergie finale - ECS partie surélévée',
            'IDC moyen 3 ans avant travaux (Ef,avant,corr [kWh/m²/an])',
            'Objectif en énergie finale (Ef,obj *fp [kWh/m²/an])',
            'Atteinte objectif'
        ]

        df_envoi_values = [
            nom_projet, adresse_projet, amoen_id,
            sre_renovation_m2, sre_pourcentage_habitat_collectif,
            sre_pourcentage_habitat_individuel,
            sre_pourcentage_administration,
            sre_pourcentage_ecoles,
            sre_pourcentage_commerce,
            sre_pourcentage_restauration,
            sre_pourcentage_lieux_de_rassemblement,
            sre_pourcentage_hopitaux,
            sre_pourcentage_industrie,
            sre_pourcentage_depots,
            sre_pourcentage_installations_sportives,
            sre_pourcentage_piscines_couvertes,
            agent_energetique_ef_mazout_kg,
            agent_energetique_ef_mazout_litres,
            agent_energetique_ef_mazout_kwh,
            agent_energetique_ef_gaz_naturel_m3,
            agent_energetique_ef_gaz_naturel_kwh,
            agent_energetique_ef_bois_buches_dur_stere,
            agent_energetique_ef_bois_buches_tendre_stere,
            agent_energetique_ef_bois_buches_tendre_kwh,
            agent_energetique_ef_pellets_m3,
            agent_energetique_ef_pellets_kg,
            agent_energetique_ef_pellets_kwh,
            agent_energetique_ef_plaquettes_m3,
            agent_energetique_ef_plaquettes_kwh,
            agent_energetique_ef_cad_kwh,
            agent_energetique_ef_electricite_pac_kwh,
            agent_energetique_ef_electricite_directe_kwh,
            agent_energetique_ef_autre_kwh,
            periode_start, periode_end,
            repartition_energie_finale_partie_renovee_chauffage,
            repartition_energie_finale_partie_renovee_ecs,
            repartition_energie_finale_partie_surelevee_chauffage,
            repartition_energie_finale_partie_surelevee_ecs,
            ef_avant_corr_kwh_m2,
            ef_objectif_pondere_kwh_m2,
            atteinte_objectif
        ]

        df_envoi = pd.DataFrame([df_envoi_values], columns=df_envoi_columns)

        def send_email(subject, body, dataframe, GMAIL_ADDRESS, GMAIL_PASSWORD, TO_ADDRESS_EMAIL, attachment_name="data.csv"):
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = GMAIL_ADDRESS
            msg["To"] = TO_ADDRESS_EMAIL
            msg.set_content(body)  # Attach the body as the main content of the email

            # Convert DataFrame to CSV and attach it to the email
            csv_buffer = io.StringIO()
            dataframe.to_csv(csv_buffer, index=False, encoding="utf-8")
            csv_buffer.seek(0)
            attachment = MIMEApplication(csv_buffer.read(), _subtype="csv")
            attachment.add_header("Content-Disposition", "attachment", filename=attachment_name)
            msg.add_attachment(attachment)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
                    smtp_server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
                    smtp_server.send_message(msg)  # This automatically handles encoding
                st.write("Données envoyées!")

            except Exception as e:
                st.write(f"Error sending email: {e}")

        if st.button("Envoyer les données"):
            header = f"Envoi données AMOén - {nom_projet} - {adresse_projet} - {amoen_id}"
            send_email(header,
                        "Voici les données AMOén envoyées.",
                        df_envoi,
                        GMAIL_ADDRESS,
                        GMAIL_PASSWORD,
                        TO_ADRESS_EMAIL,
                        "df_envoi.csv")

        st.dataframe(df_envoi)

if __name__ == "__main__":
    # Météo
    st.session_state.DJ_REF_ANNUELS = DJ_REF_ANNUELS
    st.session_state.DJ_TEMPERATURE_REFERENCE = DJ_TEMPERATURE_REFERENCE
    # Agents énergétiques conversions
    st.session_state.CONVERSION_MAZOUT_KG_MJ = CONVERSION_MAZOUT_KG_MJ
    st.session_state.CONVERSION_MAZOUT_LITRES_MJ = CONVERSION_MAZOUT_LITRES_MJ
    st.session_state.CONVERSION_MAZOUT_KWH_MJ = CONVERSION_MAZOUT_KWH_MJ
    st.session_state.CONVERSION_GAZ_NATUREL_M3_MJ = CONVERSION_GAZ_NATUREL_M3_MJ
    st.session_state.CONVERSION_GAZ_NATUREL_KWH_MJ = CONVERSION_GAZ_NATUREL_KWH_MJ
    st.session_state.CONVERSION_BOIS_BUCHES_DUR_STERE_MJ = CONVERSION_BOIS_BUCHES_DUR_STERE_MJ
    st.session_state.CONVERSION_BOIS_BUCHES_TENDRE_STERE_MJ = CONVERSION_BOIS_BUCHES_TENDRE_STERE_MJ
    st.session_state.CONVERSION_BOIS_BUCHES_TENDRE_KWH_MJ = CONVERSION_BOIS_BUCHES_TENDRE_KWH_MJ
    st.session_state.CONVERSION_PELLETS_M3_MJ = CONVERSION_PELLETS_M3_MJ
    st.session_state.CONVERSION_PELLETS_KG_MJ = CONVERSION_PELLETS_KG_MJ
    st.session_state.CONVERSION_PELLETS_KWH_MJ = CONVERSION_PELLETS_KWH_MJ
    st.session_state.CONVERSION_PLAQUETTES_M3_MJ = CONVERSION_PLAQUETTES_M3_MJ
    st.session_state.CONVERSION_PLAQUETTES_KWH_MJ = CONVERSION_PLAQUETTES_KWH_MJ
    st.session_state.CONVERSION_CAD_KWH_MJ = CONVERSION_CAD_KWH_MJ
    st.session_state.CONVERSION_ELECTRICITE_PAC_KWH_MJ = CONVERSION_ELECTRICITE_PAC_KWH_MJ
    st.session_state.CONVERSION_ELECTRICITE_DIRECTE_KWH_MJ = CONVERSION_ELECTRICITE_DIRECTE_KWH_MJ
    st.session_state.CONVERSION_AUTRE_KWH_MJ = CONVERSION_AUTRE_KWH_MJ
    # Agents énergétiques facteurs de pondération
    st.session_state.FACTEUR_PONDERATION_MAZOUT = FACTEUR_PONDERATION_MAZOUT
    st.session_state.FACTEUR_PONDERATION_GAZ_NATUREL = FACTEUR_PONDERATION_GAZ_NATUREL
    st.session_state.FACTEUR_PONDERATION_BOIS_BUCHES_DUR = FACTEUR_PONDERATION_BOIS_BUCHES_DUR
    st.session_state.FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE = FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE
    st.session_state.FACTEUR_PONDERATION_PELLETS = FACTEUR_PONDERATION_PELLETS
    st.session_state.FACTEUR_PONDERATION_PLAQUETTES = FACTEUR_PONDERATION_PLAQUETTES
    st.session_state.FACTEUR_PONDERATION_CAD = FACTEUR_PONDERATION_CAD
    st.session_state.FACTEUR_PONDERATION_ELECTRICITE_PAC = FACTEUR_PONDERATION_ELECTRICITE_PAC
    st.session_state.FACTEUR_PONDERATION_ELECTRICITE_DIRECTE = FACTEUR_PONDERATION_ELECTRICITE_DIRECTE
    st.session_state.FACTEUR_PONDERATION_AUTRE = FACTEUR_PONDERATION_AUTRE
    # email
    st.session_state.GMAIL_ADDRESS = GMAIL_ADDRESS
    st.session_state.GMAIL_PASSWORD = GMAIL_PASSWORD
    st.session_state.TO_ADRESS_EMAIL = TO_ADRESS_EMAIL
    # Mise à jour météo
    now = datetime.datetime.now()
    if (now - last_update_time_meteo).days > 1:
        last_update_time_meteo = now
        df_meteo_tre200d0 = get_meteo_data()
        st.session_state.df_meteo_tre200d0 = df_meteo_tre200d0
    st.set_page_config(page_title="AMOEN Dashboard", page_icon=":bar_chart:", layout="wide")
    generate_dashboard()
    # st.experimental_run()
