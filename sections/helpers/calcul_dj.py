import pandas as pd
import numpy as np
import streamlit as st

## Météo
DJ_REF_ANNUELS = 3260.539010836340
DJ_TEMPERATURE_REFERENCE = 20

@st.cache_data
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

# Calcul des degrés-jours
@st.cache_data
def calcul_dj_periode(df_meteo_tre200d0, periode_start, periode_end):
    dj_periode = df_meteo_tre200d0[(df_meteo_tre200d0['time'] >= periode_start) & (df_meteo_tre200d0['time'] <= periode_end)]['DJ_theta0_16'].sum()
    return dj_periode