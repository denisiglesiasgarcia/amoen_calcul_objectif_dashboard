# TODO: 


import pandas as pd
import numpy as np
import streamlit as st
from streamlit_date_picker import date_range_picker, PickerType, Unit, date_picker
import datetime
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import io

# Constantes

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
        if variable.isnumeric() or variable.replace('.', '', 1).isnumeric():
            st.write(name, variable, " ", unité)
        else:
            st.write(name, "doit être un chiffre")
    
    # Calcul des degrés-jours
    def calcul_dj_periode(df_meteo_tre200d0, periode_start, periode_end):
        dj_periode = df_meteo_tre200d0[(df_meteo_tre200d0['time'] >= periode_start) & (df_meteo_tre200d0['time'] <= periode_end)]['DJ_theta0_16'].sum()
        return dj_periode

    st.title("Outil pour calculer l'atteinte des objectifs AMOén")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["0 Readme", '1 Données site', "2 Note de calcul", '3 Résultats', '4 Validation des données'])

    # Calcul des index selon dates
    with tab1:
        st.subheader('Différences entre méthodologie et calcul IDC:')
        st.write("- PAC: Dans la méthodologie on applique un facteur de pondération de 2 sur l'électricité consommée par les PAC.\
                 Dans le règlement IDC on doit appliquer un COP de 3.25 sur l'électricité consommée par les PAC après 2010.")
        st.write('- CAD: Tous les CAD sont identiques dans la méthodologie. Dans le règlement IDC, on doit appliquer des pertes \
                 → 1kWh utile = 3.6/0.925 MJ = 3.892 MJ normalisés')
        st.write("- Météo: utilisation de MétéoSuisse station Cointrin, mesure tre200d0. Le tableau Excel IDC utilise des \
                 données similaires mais la mesure exacte n'est pas indiquée. La différence est d'environ 3% d'erreur sur \
                le calcul des DJ de l'outil Excel de l'OCEN. Ce tableau reprend la mesure tre200d0 pour tous les calculs.")
        st.write("- Répartition ECS/chauffage: méthodologie se base sur la répartition théorique des besoins ECS/chauffage \
                 selon rénové/neuf ou les compteurs si disponible (ECS/Chauffage). Règlement IDC se base sur consommation \
                 normalisé de ECS (Eww) et le reste est pour le chauffage ou bien sur les compteurs disponibles (ECS/Chauffage).")
        st.write("- ECS: L'outil IDC estime un Eww sur la base de la 380/1 (par exemple 128MJ/m² pour du logement). \
                 Selon la méthodologie, les besoins d'eau chaude sont calculés selon la SIA380/1 en déduisant la production de \
                 solaire thermique (400 kWh/m² de panneau ST).")
        
        st.subheader('Limitations du calcul')
        st.write("On ne peut pas prédire de manière fiable le futur. Lorsqu'on a moins de 6 mois de consommation d'énergie, \
                 l'influence des degré-jour de l'année de référence va hautement influencer le calcul et va faire une \
                 prédiction avec un haut degré d'incertitude. Normalisation = DJ_ref/DJ_période (eq. 2 règlement IDC). \
                 La période minimale recommandée est de 6 mois de données.")

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
            show_text_input_sre_pourcentage_habitat_collectif = st.checkbox("Habitat collectif", value=0)
            if show_text_input_sre_pourcentage_habitat_collectif:
                sre_pourcentage_habitat_collectif = st.text_input("Habitat collectif (% SRE):", value=0, label_visibility="collapsed")
                validate_input("Habitat collectif:", sre_pourcentage_habitat_collectif, "%")
                sre_pourcentage_habitat_collectif = float(sre_pourcentage_habitat_collectif)
            else:
                sre_pourcentage_habitat_collectif = 0.0
            
            show_text_input_sre_pourcentage_habitat_individuel = st.checkbox("Habitat individuel")
            if show_text_input_sre_pourcentage_habitat_individuel:
                sre_pourcentage_habitat_individuel = st.text_input("Habitat individuel (% SRE):", value=0)
                validate_input("Habitat individuel:", sre_pourcentage_habitat_individuel, "%")
                sre_pourcentage_habitat_individuel = float(sre_pourcentage_habitat_individuel)
            else:
                sre_pourcentage_habitat_individuel = 0.0
            
            show_text_input_sre_pourcentage_administration = st.checkbox("Administration")
            if show_text_input_sre_pourcentage_administration:
                sre_pourcentage_administration = st.text_input("Administration (% SRE):", value=0)
                validate_input("Administration:", sre_pourcentage_administration, "%")
                sre_pourcentage_administration = float(sre_pourcentage_administration)
            else:
                sre_pourcentage_administration = 0.0
            
            show_text_input_sre_pourcentage_ecoles = st.checkbox("Écoles")
            if show_text_input_sre_pourcentage_ecoles:
                sre_pourcentage_ecoles = st.text_input("Écoles (% SRE):", value=0)
                validate_input("Écoles.", sre_pourcentage_ecoles, "%")
                sre_pourcentage_ecoles = float(sre_pourcentage_ecoles)
            else:
                sre_pourcentage_ecoles = 0.0
            
            show_text_input_sre_pourcentage_commerce = st.checkbox("Commerce")
            if show_text_input_sre_pourcentage_commerce:
                sre_pourcentage_commerce = st.text_input("Commerce (% SRE):", value=0)
                validate_input("Commerce:", sre_pourcentage_commerce, "%")
                sre_pourcentage_commerce = float(sre_pourcentage_commerce)
            else:
                sre_pourcentage_commerce = 0.0
            
            show_text_input_sre_pourcentage_restauration = st.checkbox("Restauration")
            if show_text_input_sre_pourcentage_restauration:
                sre_pourcentage_restauration = st.text_input("Restauration (% SRE):", value=0)
                validate_input("Restauration:", sre_pourcentage_restauration, "%")
                sre_pourcentage_restauration = float(sre_pourcentage_restauration)
            else:
                sre_pourcentage_restauration = 0.0
            
            show_text_input_sre_pourcentage_lieux_de_rassemblement = st.checkbox("Lieux de rassemblement")
            if show_text_input_sre_pourcentage_lieux_de_rassemblement:
                sre_pourcentage_lieux_de_rassemblement = st.text_input("Lieux de rassemblement (% SRE):", value=0)
                validate_input("Lieux de rassemblement:", sre_pourcentage_lieux_de_rassemblement, "%")
                sre_pourcentage_lieux_de_rassemblement = float(sre_pourcentage_lieux_de_rassemblement)
            else:
                sre_pourcentage_lieux_de_rassemblement = 0.0
            
            show_text_input_sre_pourcentage_hopitaux = st.checkbox("Hôpitaux")
            if show_text_input_sre_pourcentage_hopitaux:
                sre_pourcentage_hopitaux = st.text_input("Hôpitaux (% SRE):", value=0)
                validate_input("Hôpitaux:", sre_pourcentage_hopitaux, "%")
                sre_pourcentage_hopitaux = float(sre_pourcentage_hopitaux)
            else:
                sre_pourcentage_hopitaux = 0.0
            
            show_text_input_sre_pourcentage_industrie = st.checkbox("Industrie")
            if show_text_input_sre_pourcentage_industrie:
                sre_pourcentage_industrie = st.text_input("Industrie (% SRE):", value=0)
                validate_input("Industrie:", sre_pourcentage_industrie, "%")
                sre_pourcentage_industrie = float(sre_pourcentage_industrie)
            else:
                sre_pourcentage_industrie = 0.0
            
            show_text_input_sre_pourcentage_depots = st.checkbox("Dépôts")
            if show_text_input_sre_pourcentage_depots:
                sre_pourcentage_depots = st.text_input("Dépôts (% SRE):", value=0)
                validate_input("Dépôts:", sre_pourcentage_depots, "%")
                sre_pourcentage_depots = float(sre_pourcentage_depots)
            else:
                sre_pourcentage_depots = 0.0
            
            show_text_input_sre_pourcentage_installations_sportives = st.checkbox("Installations sportives")
            if show_text_input_sre_pourcentage_installations_sportives:
                sre_pourcentage_installations_sportives = st.text_input("Installations sportives (% SRE):", value=0)
                validate_input("Installations sportives:", sre_pourcentage_installations_sportives, "%")
                sre_pourcentage_installations_sportives = float(sre_pourcentage_installations_sportives)
            else:
                sre_pourcentage_installations_sportives = 0.0
            
            show_text_input_sre_pourcentage_piscines_couvertes = st.checkbox("Piscines couvertes")
            if show_text_input_sre_pourcentage_piscines_couvertes:
                sre_pourcentage_piscines_couvertes = st.text_input("Piscines couvertes (% SRE):", value=0)
                validate_input("Piscines couvertes:", sre_pourcentage_piscines_couvertes, "%")
                sre_pourcentage_piscines_couvertes = float(sre_pourcentage_piscines_couvertes)
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

            show_text_input_agent_energetique_ef_mazout_kg = st.checkbox("Mazout (kg)")
            if show_text_input_agent_energetique_ef_mazout_kg:
                agent_energetique_ef_mazout_kg = st.text_input("Mazout (kg):", value=0, label_visibility="collapsed")
                validate_input("Mazout:", agent_energetique_ef_mazout_kg, "kg")
                agent_energetique_ef_mazout_kg = float(agent_energetique_ef_mazout_kg)
            else:
                agent_energetique_ef_mazout_kg = 0.0
            
            show_text_input_agent_energetique_ef_mazout_litres = st.checkbox("Mazout (litres)")
            if show_text_input_agent_energetique_ef_mazout_litres:
                agent_energetique_ef_mazout_litres = st.text_input("Mazout (litres):", value=0, label_visibility="collapsed")
                validate_input("Mazout:", agent_energetique_ef_mazout_litres, "litres")
                agent_energetique_ef_mazout_litres = float(agent_energetique_ef_mazout_litres)
            else:
                agent_energetique_ef_mazout_litres = 0.0
            
            show_text_input_agent_energetique_ef_mazout_kwh = st.checkbox("Mazout (kWh)")
            if show_text_input_agent_energetique_ef_mazout_kwh:
                agent_energetique_ef_mazout_kwh = st.text_input("Mazout (kWh):", value=0, label_visibility="collapsed")
                validate_input("Mazout:", agent_energetique_ef_mazout_kwh, "kWh")
                agent_energetique_ef_mazout_kwh = float(agent_energetique_ef_mazout_kwh)
            else:
                agent_energetique_ef_mazout_kwh = 0.0
            
            show_text_input_agent_energetique_ef_gaz_naturel_m3 = st.checkbox("Gaz naturel (m³)")
            if show_text_input_agent_energetique_ef_gaz_naturel_m3:
                agent_energetique_ef_gaz_naturel_m3 = st.text_input("Gaz naturel (m³):", value=0, label_visibility="collapsed")
                validate_input("Gaz naturel:", agent_energetique_ef_gaz_naturel_m3, "m³")
                agent_energetique_ef_gaz_naturel_m3 = float(agent_energetique_ef_gaz_naturel_m3)
            else:
                agent_energetique_ef_gaz_naturel_m3 = 0.0
            
            show_text_input_agent_energetique_ef_gaz_naturel_kwh = st.checkbox("Gaz naturel (kWh)")
            if show_text_input_agent_energetique_ef_gaz_naturel_kwh:
                agent_energetique_ef_gaz_naturel_kwh = st.text_input("Gaz naturel (kWh):", value=0, label_visibility="collapsed")
                validate_input("Gaz naturel:", agent_energetique_ef_gaz_naturel_kwh, "kWh")
                agent_energetique_ef_gaz_naturel_kwh = float(agent_energetique_ef_gaz_naturel_kwh)
            else:
                agent_energetique_ef_gaz_naturel_kwh = 0.0
            
            show_text_input_agent_energetique_ef_bois_buches_dur_stere = st.checkbox("Bois buches dur (stère)")
            if show_text_input_agent_energetique_ef_bois_buches_dur_stere:
                agent_energetique_ef_bois_buches_dur_stere = st.text_input("Bois buches dur (stère):", value=0, label_visibility="collapsed")
                validate_input("Bois buches dur:", agent_energetique_ef_bois_buches_dur_stere, "stère")
                agent_energetique_ef_bois_buches_dur_stere = float(agent_energetique_ef_bois_buches_dur_stere)
            else:
                agent_energetique_ef_bois_buches_dur_stere = 0.0
            
            show_text_input_agent_energetique_ef_bois_buches_tendre_stere = st.checkbox("Bois buches tendre (stère)")
            if show_text_input_agent_energetique_ef_bois_buches_tendre_stere:
                agent_energetique_ef_bois_buches_tendre_stere = st.text_input("Bois buches tendre (stère):", value=0, label_visibility="collapsed")
                validate_input("Bois buches tendre:", agent_energetique_ef_bois_buches_tendre_stere, "stère")
                agent_energetique_ef_bois_buches_tendre_stere = float(agent_energetique_ef_bois_buches_tendre_stere)
            else:
                agent_energetique_ef_bois_buches_tendre_stere = 0.0
            
            show_text_input_agent_energetique_ef_bois_buches_tendre_kwh = st.checkbox("Bois buches tendre (kWh)")
            if show_text_input_agent_energetique_ef_bois_buches_tendre_kwh:
                agent_energetique_ef_bois_buches_tendre_kwh = st.text_input("Bois buches tendre (kWh):", value=0, label_visibility="collapsed")
                validate_input("Bois buches tendre:", agent_energetique_ef_bois_buches_tendre_kwh, "kWh")
                agent_energetique_ef_bois_buches_tendre_kwh = float(agent_energetique_ef_bois_buches_tendre_kwh)
            else:
                agent_energetique_ef_bois_buches_tendre_kwh = 0.0
            
            show_text_input_agent_energetique_ef_pellets_m3 = st.checkbox("Pellets (m³)")
            if show_text_input_agent_energetique_ef_pellets_m3:
                agent_energetique_ef_pellets_m3 = st.text_input("Pellets (m³):", value=0, label_visibility="collapsed")
                validate_input("Pellets:", agent_energetique_ef_pellets_m3, "m³")
                agent_energetique_ef_pellets_m3 = float(agent_energetique_ef_pellets_m3)
            else:
                agent_energetique_ef_pellets_m3 = 0.0
            
            show_text_input_agent_energetique_ef_pellets_kg = st.checkbox("Pellets (kg)")
            if show_text_input_agent_energetique_ef_pellets_kg:
                agent_energetique_ef_pellets_kg = st.text_input("Pellets (kg):", value=0, label_visibility="collapsed")
                validate_input("Pellets:", agent_energetique_ef_pellets_kg, "kg")
                agent_energetique_ef_pellets_kg = float(agent_energetique_ef_pellets_kg)
            else:
                agent_energetique_ef_pellets_kg = 0.0
            
            show_text_input_agent_energetique_ef_pellets_kwh = st.checkbox("Pellets (kWh)")
            if show_text_input_agent_energetique_ef_pellets_kwh:
                agent_energetique_ef_pellets_kwh = st.text_input("Pellets (kWh):", value=0, label_visibility="collapsed")
                validate_input("Pellets:", agent_energetique_ef_pellets_kwh, "kWh")
                agent_energetique_ef_pellets_kwh = float(agent_energetique_ef_pellets_kwh)
            else:
                agent_energetique_ef_pellets_kwh = 0.0
            
            show_text_input_agent_energetique_ef_plaquettes_m3 = st.checkbox("Plaquettes (m³)")
            if show_text_input_agent_energetique_ef_plaquettes_m3:
                agent_energetique_ef_plaquettes_m3 = st.text_input("Plaquettes (m³):", value=0, label_visibility="collapsed")
                validate_input("Plaquettes:", agent_energetique_ef_plaquettes_m3, "m³")
                agent_energetique_ef_plaquettes_m3 = float(agent_energetique_ef_plaquettes_m3)
            else:
                agent_energetique_ef_plaquettes_m3 = 0.0
            
            show_text_input_agent_energetique_ef_plaquettes_kwh = st.checkbox("Plaquettes (kWh)")
            if show_text_input_agent_energetique_ef_plaquettes_kwh:
                agent_energetique_ef_plaquettes_kwh = st.text_input("Plaquettes (kWh):", value=0, label_visibility="collapsed")
                validate_input("Plaquettes:", agent_energetique_ef_plaquettes_kwh, "kWh")
                agent_energetique_ef_plaquettes_kwh = float(agent_energetique_ef_plaquettes_kwh)
            else:
                agent_energetique_ef_plaquettes_kwh = 0.0
            
            show_text_input_agent_energetique_ef_cad_kwh = st.checkbox("CAD (kWh)")
            if show_text_input_agent_energetique_ef_cad_kwh:
                agent_energetique_ef_cad_kwh = st.text_input("CAD (kWh):", value=0, label_visibility="collapsed")
                validate_input("CAD:", agent_energetique_ef_cad_kwh, "kWh")
                agent_energetique_ef_cad_kwh = float(agent_energetique_ef_cad_kwh)
            else:
                agent_energetique_ef_cad_kwh = 0.0
            
            show_text_input_agent_energetique_ef_electricite_pac_kwh = st.checkbox("Electricité pour les PAC (kWh)")
            if show_text_input_agent_energetique_ef_electricite_pac_kwh:
                agent_energetique_ef_electricite_pac_kwh = st.text_input("Electricité pour les PAC (kWh):", value=0, label_visibility="collapsed")
                validate_input("Electricité pour les PAC:", agent_energetique_ef_electricite_pac_kwh, "kWh")
                agent_energetique_ef_electricite_pac_kwh = float(agent_energetique_ef_electricite_pac_kwh)
            else:
                agent_energetique_ef_electricite_pac_kwh = 0.0
            
            show_text_input_agent_energetique_ef_electricite_directe_kwh = st.checkbox("Electricité directe (kWh)")
            if show_text_input_agent_energetique_ef_electricite_directe_kwh:
                agent_energetique_ef_electricite_directe_kwh = st.text_input("Electricité directe (kWh):", value=0, label_visibility="collapsed")
                validate_input("Electricité directe:", agent_energetique_ef_electricite_directe_kwh, "kWh")
                agent_energetique_ef_electricite_directe_kwh = float(agent_energetique_ef_electricite_directe_kwh)
            else:
                agent_energetique_ef_electricite_directe_kwh = 0.0
            
            show_text_input_agent_energetique_ef_autre_kwh = st.checkbox("Autre (kWh)")
            if show_text_input_agent_energetique_ef_autre_kwh:
                agent_energetique_ef_autre_kwh = st.text_input("Autre (kWh):", value=0, label_visibility="collapsed")
                validate_input("Autre:", agent_energetique_ef_autre_kwh, "kWh")
                agent_energetique_ef_autre_kwh = float(agent_energetique_ef_autre_kwh)
            else:
                agent_energetique_ef_autre_kwh = 0.0
            
            try:
                agent_energetique_ef_somme_avertissement = float(agent_energetique_ef_mazout_kg) + \
                    float(agent_energetique_ef_mazout_litres) + \
                    float(agent_energetique_ef_mazout_kwh) + \
                    float(agent_energetique_ef_gaz_naturel_m3) + \
                    float(agent_energetique_ef_gaz_naturel_kwh) + \
                    float(agent_energetique_ef_bois_buches_dur_stere) + \
                    float(agent_energetique_ef_bois_buches_tendre_stere) + \
                    float(agent_energetique_ef_bois_buches_tendre_kwh) + \
                    float(agent_energetique_ef_pellets_m3) + \
                    float(agent_energetique_ef_pellets_kg) + \
                    float(agent_energetique_ef_pellets_kwh) + \
                    float(agent_energetique_ef_plaquettes_m3) + \
                    float(agent_energetique_ef_plaquettes_kwh) + \
                    float(agent_energetique_ef_cad_kwh) + \
                    float(agent_energetique_ef_electricite_pac_kwh) + \
                    float(agent_energetique_ef_electricite_directe_kwh) + \
                    float(agent_energetique_ef_autre_kwh)
                if agent_energetique_ef_somme_avertissement <= 0:
                    st.write(f"<p style='color: red;'><strong>Veuillez renseigner une quantité d'énergie utilisée sur la période ({agent_energetique_ef_somme_avertissement})</strong></p>", unsafe_allow_html=True)
            except ValueError:
                st.write("Problème dans la somme des agents énergétiques")

        # dates
        st.subheader('Sélectionner les dates de début et fin de période')
        # https://github.com/imdreamer2018/streamlit-date-picker
        date_range_string = date_range_picker(picker_type=PickerType.date.string_value,
                                            start=-365, end=0, unit=Unit.days.string_value,
                                            key='range_picker',
                                            refresh_button={'is_show': True, 'button_name': 'Last 365 days',
                                                            'refresh_date': -365,
                                                            'unit': Unit.days.string_value})
        if date_range_string is not None:
            periode_start = pd.to_datetime(date_range_string[0])
            periode_end = pd.to_datetime(date_range_string[1])
            periode_nb_jours = (periode_end - periode_start).days + 1
            st.write(f"Période du {periode_start} - {periode_end} soit {periode_nb_jours} jours")

        st.subheader('Données Excel validation atteinte performances')
        col3, col4 = st.columns(2)
                
        with col3:
            # Autres données
            st.write('IDC moyen 3 ans avant travaux (Ef,avant,corr [kWh/m²/an])')
            
            ef_avant_corr_kwh_m2 = st.text_input("Ef,avant,corr [kWh/m²/an]:", value=0, help="IDC moyen 3 ans avant travaux", label_visibility="collapsed")
            validate_input("Ef,avant,corr:", ef_avant_corr_kwh_m2, "kWh/m²/an")
            ef_avant_corr_kwh_m2 = float(ef_avant_corr_kwh_m2)
            try:
                if float(ef_avant_corr_kwh_m2) <= 0:
                    st.write("<p style='color: red;'><strong>Ef,avant,corr [kWh/m²/an] doit être supérieur à 0</strong></p>", unsafe_allow_html=True)
            except ValueError:
                st.write("Problème dans Ef,avant,corr [kWh/m²/an]")
            
            st.write('Objectif en énergie finale (Ef,obj *fp [kWh/m²/an])')
            ef_objectif_pondere_kwh_m2 = st.text_input("Ef,obj *fp [kWh/m²/an]:", value=0, label_visibility="collapsed")
            validate_input("Ef,obj *fp:", ef_objectif_pondere_kwh_m2, "kWh/m²/an")
            ef_objectif_pondere_kwh_m2 = float(ef_objectif_pondere_kwh_m2)
            try:
                if float(ef_objectif_pondere_kwh_m2) <= 0:
                    st.write("<p style='color: red;'><strong>Ef,obj *fp [kWh/m²/an] doit être supérieur à 0</strong></p>", unsafe_allow_html=True)
            except ValueError:
                st.write("Problème dans Ef,obj *fp [kWh/m²/an]")
            delta_ef_visee_kwh_m2 = float(ef_avant_corr_kwh_m2) - float(ef_objectif_pondere_kwh_m2)
            st.write(f"Baisse ΔEf visée: {round(delta_ef_visee_kwh_m2,2)} kWh/m²/an")

        with col4:
            # Répartition énergie finale
            st.write('Répartition en énergie finale - Chauffage partie rénovée')
            repartition_energie_finale_partie_renovee_chauffage = st.text_input("Répartition EF - Chauffage partie rénovée", value=0, label_visibility="collapsed")
            validate_input("Répartition EF - Chauffage partie rénovée:", repartition_energie_finale_partie_renovee_chauffage, "%")
            repartition_energie_finale_partie_renovee_chauffage = float(repartition_energie_finale_partie_renovee_chauffage)

            st.write('Répartition en énergie finale - ECS partie rénovée')
            repartition_energie_finale_partie_renovee_ecs = st.text_input("Répartition EF - ECS partie rénovée", value=0, label_visibility="collapsed")
            validate_input("Répartition EF - ECS partie rénovée:", repartition_energie_finale_partie_renovee_ecs, "%")
            repartition_energie_finale_partie_renovee_ecs = float(repartition_energie_finale_partie_renovee_ecs)
            
            show_text_input_agent_energetique_ef_autre_kwh = st.checkbox("Surélévation")
            if show_text_input_agent_energetique_ef_autre_kwh:
                st.write('Répartition en énergie finale - Chauffage partie surélévée')
                repartition_energie_finale_partie_surelevee_chauffage = st.text_input("Répartition EF - Chauffage partie surélévée",
                                                                                        value=0,
                                                                                        help= "Laisser a 0 si pas de surélévation",
                                                                                        label_visibility="collapsed")
                validate_input("Répartition en énergie finale - Chauffage partie surélévée:", repartition_energie_finale_partie_surelevee_chauffage, "%")
                repartition_energie_finale_partie_surelevee_chauffage = float(repartition_energie_finale_partie_surelevee_chauffage)
                
                repartition_energie_finale_partie_surelevee_ecs = st.text_input("Répartition EF - ECS partie surélevée", value=0, help= "Laisser a 0 si pas de surélévation")
                validate_input("Répartition en énergie finale - ECS partie surélevée:", repartition_energie_finale_partie_surelevee_ecs, "%")
                repartition_energie_finale_partie_surelevee_ecs = float(repartition_energie_finale_partie_surelevee_ecs)
            else:
                repartition_energie_finale_partie_surelevee_chauffage = 0.0
                repartition_energie_finale_partie_surelevee_ecs = 0.0
            
            # Validation somme des pourcentages
            try:
                repartition_ef_somme_avertissement = int(repartition_energie_finale_partie_renovee_chauffage) + \
                    int(repartition_energie_finale_partie_renovee_ecs) +\
                    int(repartition_energie_finale_partie_surelevee_chauffage) + \
                    int(repartition_energie_finale_partie_surelevee_ecs)
                if repartition_ef_somme_avertissement != 100:
                    st.write(f"<p style='color: red;'><strong>La somme des pourcentages de répartition de l'énergie finale doit être égale à 100% ({repartition_ef_somme_avertissement}%)</strong></p>", unsafe_allow_html=True)
            except ValueError:
                st.write("Problème dans la somme des pourcentages de répartition de l'énergie finale")

    with tab3:
        # Create a DataFrame
        df = pd.DataFrame({
            'Dénomination': [],
            'Valeur': [],
            'Unité': [],
            'Commentaire': [],
            'Excel': [],
            'Variable/Formule': []
        })

        df_periode = pd.DataFrame({
            'Dénomination': [],
            'Valeur': [],
            'Unité': [],
            'Commentaire': [],
            'Excel': [],
            'Variable/Formule': []
        })

        def new_row(df, denomination, valeur, unite, commentaire, excel, formule=''):
            new_row_added = {'Dénomination': denomination, 'Valeur': valeur, 'Unité': unite, 'Commentaire': commentaire, 'Excel': excel, 'Variable/Formule': formule}
            df = pd.concat([df, pd.DataFrame(new_row_added, index=[0])], ignore_index=True)
            return df
        
        # C65 → Début période
        df_periode = new_row(df_periode,
            'Début période',
            periode_start,
            '-',
            'Date de début de la période',
            'C65',
            'periode_start')
        
        # C66 → Fin période
        df_periode = new_row(df_periode,
            'Fin période',
            periode_end,
            '-',
            'Date de fin de la période',
            'C66',
            'periode_end')

        # C67 → Nombre de jours
        df = new_row(df,
            'Nombre de jours',
            periode_nb_jours,
            'jours',
            'Nombre de jours de la période',
            'C67',
            'periode_nb_jours')


        # C86 → Répartition EF - Chauffage partie rénovée
        df = new_row(df,
            'Répartition en énergie finale - Chauffage partie rénovée',
            repartition_energie_finale_partie_renovee_chauffage,
            '%',
            "Part d'énergie finale (chauffage) pour la partie rénové.",
            'C86',
            "repartition_energie_finale_partie_renovee_chauffage")
        
        # C87 → Répartition EF - ECS partie rénovée
        df = new_row(df,
            'Répartition en énergie finale - ECS partie rénovée',
            repartition_energie_finale_partie_renovee_ecs,
            '%',
            "Part d'énergie finale (ECS) pour la partie rénové.",
            'C87',
            "repartition_energie_finale_partie_renovee_ecs")

        # C88 → Répartition EF - Chauffage partie surélévée
        df = new_row(df,
            'Répartition en énergie finale - Chauffage partie surélévée',
            repartition_energie_finale_partie_surelevee_chauffage,
            '%',
             "Part d'énergie finale (chauffage) pour la partie surélévée. 0 s'il n'y a pas de surélévation",
            'C88',
            "repartition_energie_finale_partie_surelevee_chauffage")
        
        # C89 → Répartition EF - ECS partie surélévée
        df = new_row(df,
            'Répartition en énergie finale - ECS partie surélévée',
            repartition_energie_finale_partie_surelevee_ecs,
            '%',
            "Part d'énergie finale (ECS) pour la partie surélévée. 0 s'il n'y a pas de surélévation",
            'C89',
            "repartition_energie_finale_partie_surelevee_ecs")
        
        # C91 → Part EF pour partie rénové (Chauffage + ECS)
        repartition_energie_finale_partie_renovee_somme = repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_renovee_ecs
        df = new_row(df,
            'Part EF pour partie rénové (Chauffage + ECS)',
            repartition_energie_finale_partie_renovee_somme,
            '%',
            "Part d'énergie finale (Chauffage + ECS) pour la partie rénové. 100% si pas de surélévation",
            'C91',
            "repartition_energie_finale_partie_renovee_somme = repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_renovee_ecs")
        
        # C92 → Est. ECS/ECS annuelle
        estimation_ecs_annuel = periode_nb_jours/365
        df = new_row(df,
            'Est. ECS/ECS annuelle',
            estimation_ecs_annuel,
            '-',
            'Estimation de la part ECS sur une année',
            'C92',
            'estimation_ecs_annuel = periode_nb_jours/365')

        # C93 → Est. Chauffage/Chauffage annuel prévisible
        dj_periode = calcul_dj_periode(df_meteo_tre200d0, periode_start, periode_end)
        dj_periode = float(dj_periode)
        estimation_part_chauffage_periode_sur_annuel = dj_periode / DJ_REF_ANNUELS
        estimation_part_chauffage_periode_sur_annuel = float(estimation_part_chauffage_periode_sur_annuel)
        df = new_row(df,
            'Est. Chauffage/Chauffage annuel prévisible',
            estimation_part_chauffage_periode_sur_annuel*100,
            '%',
            'Est. Chauffage/Chauffage annuel prévisible → dj_periode (C101) / DJ_REF_ANNUELS (C102)',
            'C93',
            'estimation_part_chauffage_periode_sur_annuel = dj_periode / DJ_REF_ANNUELS')

        # C94 → Est. EF période / EF année
        estimation_energie_finale_periode_sur_annuel = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) +\
                                            (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage))
        df = new_row(df,
            'Est. EF période / EF année',
            estimation_energie_finale_periode_sur_annuel,
            '%',
            "Estimation en énergie finale sur la période / énergie finale sur une année",
            'C94',
            'estimation_energie_finale_periode_sur_annuel = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) +\
                (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage))')

        print(estimation_energie_finale_periode_sur_annuel)
        # C95 → Est. Part ECS période comptage
        part_ecs_periode_comptage = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + \
            repartition_energie_finale_partie_surelevee_ecs)) / estimation_energie_finale_periode_sur_annuel
        df = new_row(df,
            'Est. Part ECS période comptage',
            part_ecs_periode_comptage*100,
            '%', 
            "",
            'C95',
            'part_ecs_periode_comptage = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + \
            repartition_energie_finale_partie_surelevee_ecs)) / estimation_energie_finale_periode_sur_annuel')

        # C96 → Est. Part Chauffage période comptage
        part_chauffage_periode_comptage = (estimation_part_chauffage_periode_sur_annuel * \
            (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage)) / estimation_energie_finale_periode_sur_annuel
        df = new_row(df,
            'Est. Part Chauffage période comptage',
            part_chauffage_periode_comptage*100,
            '%',
            "",
            'C96',
            'part_chauffage_periode_comptage = (estimation_part_chauffage_periode_sur_annuel * \
            (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage)) / estimation_energie_finale_periode_sur_annuel')

        # C97 → correction ECS = 365/nb jour comptage
        correction_ecs = 365/periode_nb_jours
        df = new_row(df,
            'Correction ECS',
            correction_ecs,
            '-',
            "",
            'C97',
            'correction_ecs = 365/periode_nb_jours')

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
        df = new_row(df,
            'Energie finale indiqué par le(s) compteur(s)',
            agent_energetique_ef_somme_kwh,
            'kWh', 
            "Somme de l'énergie finale indiqué par le(s) compteur(s) en kWh",
            'C98',
            'agent_energetique_ef_somme_kwh')

        # C99 → Methodo_Bww → Part de ECS en énergie finale sur la période
        methodo_b_ww_kwh = (agent_energetique_ef_somme_kwh) * part_ecs_periode_comptage
        df = new_row(df,
            'Methodo_Bww',
            methodo_b_ww_kwh,
            'kWh',
            "",
            'C99',
            'Part de ECS en énergie finale sur la période')

        # C100 → Methodo_Eww
        methodo_e_ww_kwh = (methodo_b_ww_kwh / sre_renovation_m2) * (365 / periode_nb_jours)
        df = new_row(df,
            'Methodo_Eww',
            methodo_e_ww_kwh,
            'kWh',
            "",
            'C100',
            'Methodo_Eww')

        # C101 → DJ ref annuels
        df = new_row(df,
            'DJ ref annuels',
            DJ_REF_ANNUELS,
            'Degré-jour',
            'Degré-jour 20/16 avec les températures extérieures de référence pour Genève-Cointrin selon SIA 2028:2008',
            'C101',
            "DJ_REF_ANNUELS")

        # C102 → DJ période comptage
        df = new_row(df,
            'DJ période comptage',
            dj_periode,
            'Degré-jour',
            'Degré-jour 20/16 avec les températures extérieures (tre200d0) pour Genève-Cointrin relevée par MétéoSuisse',
            'C102',
            'dj_periode')

        # C103 → Methodo_Bh → Part de chauffage en énergie finale sur la période
        methodo_b_h_kwh = agent_energetique_ef_somme_kwh * part_chauffage_periode_comptage
        df = new_row(df,
            'Methodo_Bh',
            methodo_b_h_kwh,
            'kWh',
            'Part de chauffage en énergie finale sur la période',
            'C103',
            "methodo_b_h_kwh = agent_energetique_ef_somme_kwh * part_chauffage_periode_comptage")

        # C104 → Methodo_Eh
        methodo_e_h_kwh = (methodo_b_h_kwh / sre_renovation_m2) * (DJ_REF_ANNUELS / dj_periode)
        df = new_row(df,
            'Methodo_Eh',
            methodo_e_h_kwh,
            'kWh/m²',
            'Energie finale par unité de surface pour le chauffage sur la période climatiquement corrigée',
            'C104',
            'methodo_e_h_kwh = (methodo_b_h_kwh / sre_renovation_m2) * (DJ_REF_ANNUELS / dj_periode)')

        # C105 → Ef,après,corr → Methodo_Eww + Methodo_Eh
        energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 = methodo_e_ww_kwh + methodo_e_h_kwh
        df = new_row(df,
            'Ef,après,corr (inclus surélévation)',
            energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2,
            'kWh/m²',
            "Energie finale par unité de surface pour le chauffage climatiquement corrigée et l'ECS sur la période (inclus surélévation)",
            'C105',
            'energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 = methodo_e_ww_kwh + methodo_e_h_kwh')

        # C106 → Part de l'énergie finale théorique dédiée à la partie rénovée (ECS+Ch.)
        df = new_row(df,
            'Part de l\'énergie finale théorique dédiée à la partie rénovée (ECS+Ch.)',
            repartition_energie_finale_partie_renovee_somme,
            '%',
            'Part de l\'énergie finale théorique dédiée à la partie rénovée (ECS+Ch.)',
            'C106',
            "repartition_energie_finale_partie_renovee_somme")

        # C107 → Ef,après,corr,rénové →Total en énergie finale (Eww+Eh) pour la partie rénovée
        energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 = energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 * (repartition_energie_finale_partie_renovee_somme / 100)
        df = new_row(df,
            'Ef,après,corr,rénové',
            energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2,
            'kWh/m²',
            'Energie finale par unité de surface pour le chauffage et l\'ECS sur la période climatiquement corrigée pour la partie rénovée',
            'C107',
            'energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 = \
                energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 * (repartition_energie_finale_partie_renovee_somme / 100)',)

        # C108 → fp → facteur de pondération moyen
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
        df = new_row(df,
            'Facteur de pondération des agents énergétiques',
            facteur_ponderation_moyen,
            '-',
            'Facteur de pondération moyen des agents énergétiques',
            'C108',
            'facteur_ponderation_moyen')

        # C109 → Methodo_Eww*fp
        methodo_e_ww_renovee_pondere_kwh_m2 = methodo_e_ww_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)
        df = new_row(df,
            'Methodo_Eww*fp',
            methodo_e_ww_renovee_pondere_kwh_m2,
            'kWh/m²',
            '',
            'C109',
            'methodo_e_ww_renovee_pondere_kwh_m2 = methodo_e_ww_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)')

        # C110 → Methodo_Eh*fp
        methodo_e_h_renovee_pondere_kwh_m2 = methodo_e_h_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)
        df = new_row(df,
            'Methodo_Eh*fp',
            methodo_e_h_renovee_pondere_kwh_m2,
            'kWh/m²',
            '',
            'C110',
            'methodo_e_h_renovee_pondere_kwh_m2 = methodo_e_h_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)')

        # C113 → Ef,après,corr,rénové*fp
        energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 * facteur_ponderation_moyen
        df = new_row(df,
            'Ef,après,corr,rénové*fp',
            energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
            'kWh/m²',
            "",
            'C113',
            'energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 * facteur_ponderation_moyen')

        # C114 → Ef,après,corr,rénové*fp
        energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 * 3.6
        df = new_row(df,
            'Ef,après,corr,rénové*fp',
            energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2,
            'MJ/m²',
            "",
            'C114',
            'energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 * 3.6')

        # Reset the index to make it a column
        df = df.reset_index(drop=True)

        # Autres dataframe
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
        
        st.write("Atteinte des objectifs")
        # calculs
        delta_ef_realisee_kwh_m2 = ef_avant_corr_kwh_m2 - energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
        atteinte_objectif = delta_ef_realisee_kwh_m2/delta_ef_visee_kwh_m2

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

        st.table(df_resultats1)

        # résultats en latex

        formula_atteinte_objectif = r"Atteinte\ objectif = \frac{{\Delta Ef_{{réel}}}}{{\Delta Ef_{{visée}}}} = \frac{{E_{{f,avant,corr}} - E_{{f,après,corr,rénové}}*f_{{p}}}}{{E_{{f,avant,corr}} - E_{{f,obj}}*f_{{p}}}}"

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

        st.write("Analyse des données")

    with tab5:
        st.subheader("Envoi des données")

        nom_projet = st.text_input("Nom du projet")
        adresse_projet = st.text_input("Adresse")
        amoen_id = st.text_input("AMOEN")

        df_envoi = pd.DataFrame({
            'Nom_projet': [nom_projet],
            'Adresse': [adresse_projet],
            'AMOEN': [amoen_id],
            'SRE rénovée' : [sre_renovation_m2],
            'Affectation habitat collectif pourcentage': [sre_pourcentage_habitat_collectif],
            'Affectation habitat individuel pourcentage': [sre_pourcentage_habitat_individuel],
            'Affectation administration pourcentage': [sre_pourcentage_administration],
            'Affectation écoles pourcentage': [sre_pourcentage_ecoles],
            'Affectation commerce pourcentage': [sre_pourcentage_commerce],
            'Affectation restauration pourcentage': [sre_pourcentage_restauration],
            'Affectation lieux de rassemblement pourcentage': [sre_pourcentage_lieux_de_rassemblement],
            'Affectation hopitaux pourcentage': [sre_pourcentage_hopitaux],
            'Affectation industrie pourcentage': [sre_pourcentage_industrie],
            'Affectation dépots pourcentage': [sre_pourcentage_depots],
            'Affectation installations sportives pourcentage': [sre_pourcentage_installations_sportives],
            'Affectation piscines couvertes pourcentage': [sre_pourcentage_piscines_couvertes],
            'Agent énergétique mazout kg': [agent_energetique_ef_mazout_kg],
            'Agent énergétique mazout litres': [agent_energetique_ef_mazout_litres],
            'Agent énergétique mazout kWh': [agent_energetique_ef_mazout_kwh],
            'Agent énergétique gaz naturel m3': [agent_energetique_ef_gaz_naturel_m3],
            'Agent énergétique gaz naturel kWh': [agent_energetique_ef_gaz_naturel_kwh],
            'Agent énergétique bois buches dur stère': [agent_energetique_ef_bois_buches_dur_stere],
            'Agent énergétique bois buches tendre stère': [agent_energetique_ef_bois_buches_tendre_stere],
            'Agent énergétique bois buches tendre kWh': [agent_energetique_ef_bois_buches_tendre_kwh],
            'Agent énergétique pellets m3': [agent_energetique_ef_pellets_m3],
            'Agent énergétique pellets kg': [agent_energetique_ef_pellets_kg],
            'Agent énergétique pellets kWh': [agent_energetique_ef_pellets_kwh],
            'Agent énergétique plaquettes m3': [agent_energetique_ef_plaquettes_m3],
            'Agent énergétique plaquettes kWh': [agent_energetique_ef_plaquettes_kwh],
            'Agent énergétique CAD kWh': [agent_energetique_ef_cad_kwh],
            'Agent énergétique Electricité PAC kWh': [agent_energetique_ef_electricite_pac_kwh],
            'Agent énergétique Electricité directe kWh': [agent_energetique_ef_electricite_directe_kwh],
            'Agent énergétique Autre kWh': [agent_energetique_ef_autre_kwh],
            'Période début': [periode_start],
            'Période fin': [periode_end],
            'Répartition en énergie finale - Chauffage partie rénovée': [repartition_energie_finale_partie_renovee_chauffage],
            'Répartition en énergie finale - ECS partie rénovée': [repartition_energie_finale_partie_renovee_ecs],
            'Répartition en énergie finale - Chauffage partie surélévée': [repartition_energie_finale_partie_surelevee_chauffage],
            'Répartition en énergie finale - ECS partie surélévée': [repartition_energie_finale_partie_surelevee_ecs],
            'IDC moyen 3 ans avant travaux (Ef,avant,corr [kWh/m²/an])' : [ef_avant_corr_kwh_m2],
            'Objectif en énergie finale (Ef,obj *fp [kWh/m²/an])' : [ef_objectif_pondere_kwh_m2],
            })
        st.dataframe(df_envoi.transpose())

        def send_email(subject, body, dataframe, attachment_name="data.csv"):
            GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
            GMAIL_PASSWORD = st.secrets["GMAIL_PASSWORD"]
            TO_ADRESS_EMAIL = st.secrets["TO_ADRESS_EMAIL"]
            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = 'AMOén Dashboard - envoi données'
            msg["From"] = GMAIL_ADDRESS
            msg["To"] = TO_ADRESS_EMAIL

            # Convert DataFrame to CSV and attach it to the email
            csv_buffer = io.StringIO()
            dataframe.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            attachment = MIMEApplication(csv_buffer.read(), _subtype="csv")
            attachment.add_header("Content-Disposition", f"attachment; filename={attachment_name}")
            msg.attach(attachment)

            try:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
                server.send_message(msg)
                server.quit()
                st.success("Email envoyé!")
                
            except Exception as e:
                st.error(f"Error sending email: {e}")


        if st.button("Envoyer les données"):
            send_email("DataFrame Attachment", "Here is the data you requested.", df_envoi, "my_data.csv")




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
    # Mise à jour météo
    now = datetime.datetime.now()
    if (now - last_update_time_meteo).days > 1:
        last_update_time_meteo = now
        df_meteo_tre200d0 = get_meteo_data()
        st.session_state.df_meteo_tre200d0 = df_meteo_tre200d0
    st.set_page_config(page_title="AMOEN Dashboard", page_icon=":bar_chart:", layout="wide")
    generate_dashboard()
    # st.experimental_run()
