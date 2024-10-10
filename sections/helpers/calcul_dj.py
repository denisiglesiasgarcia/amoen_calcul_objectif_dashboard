import pandas as pd
import numpy as np
import streamlit as st

## Météo
DJ_REF_ANNUELS = 3260.539010836340
DJ_TEMPERATURE_REFERENCE = 20


@st.cache_data
def get_meteo_data(DJ_TEMPERATURE_REFERENCE):
    """
    Fetches and processes meteorological data for calculating Degree Days (DJ).

    This function performs the following steps:
    1. Reads historical and current meteorological data from specified URLs.
    2. Concatenates the historical and current data into a single DataFrame.
    3. Renames columns for consistency and filters the data from January 1, 2015, onwards.
    4. Removes duplicate entries and handles missing values.
    5. Sorts the data by date and resets the index.
    6. Converts temperature values to float and extracts the month from the date.
    7. Identifies the heating season and calculates whether the temperature is below 16 degrees.
    8. Computes the Degree Days (DJ) based on a reference temperature.

    Returns:
        pd.DataFrame: A DataFrame containing processed meteorological data with additional columns for heating season, temperature below 16 degrees, and Degree Days (DJ).
    """
    # Mise à jour des données météo de manière journalière
    df_meteo_tre200d0_historique = pd.read_csv(
        "https://data.geo.admin.ch/ch.meteoschweiz.klima/nbcn-tageswerte/nbcn-daily_GVE_previous.csv",
        sep=";",
        encoding="latin1",
        parse_dates=["date"],
    )
    df_meteo_tre200d0_annee_cours = pd.read_csv(
        "https://data.geo.admin.ch/ch.meteoschweiz.klima/nbcn-tageswerte/nbcn-daily_GVE_current.csv",
        sep=";",
        encoding="latin1",
        parse_dates=["date"],
    )
    df_meteo_tre200d0 = pd.concat(
        [df_meteo_tre200d0_historique, df_meteo_tre200d0_annee_cours]
    )
    df_meteo_tre200d0.rename(
        columns={"station/location": "stn", "date": "time"}, inplace=True
    )
    df_meteo_tre200d0 = df_meteo_tre200d0[["stn", "time", "tre200d0"]]
    df_meteo_tre200d0 = df_meteo_tre200d0[df_meteo_tre200d0["time"] >= "2020-01-01"]
    df_meteo_tre200d0.drop_duplicates(inplace=True)
    # replace values with "-" with nan and drop them
    df_meteo_tre200d0.replace("-", pd.NA, inplace=True)
    df_meteo_tre200d0.dropna(inplace=True)
    df_meteo_tre200d0.sort_values(by="time", inplace=True)
    df_meteo_tre200d0.reset_index(drop=True, inplace=True)
    # Calculs pour DJ
    df_meteo_tre200d0["tre200d0"] = df_meteo_tre200d0["tre200d0"].astype(float)
    df_meteo_tre200d0["mois"] = df_meteo_tre200d0["time"].dt.month
    df_meteo_tre200d0["saison_chauffe"] = np.where(
        df_meteo_tre200d0["mois"].isin([9, 10, 11, 12, 1, 2, 3, 4, 5]), 1, 0
    )
    df_meteo_tre200d0["tre200d0_sous_16"] = np.where(
        df_meteo_tre200d0["tre200d0"] <= 16, 1, 0
    )
    df_meteo_tre200d0["DJ_theta0_16"] = (
        df_meteo_tre200d0["saison_chauffe"]
        * df_meteo_tre200d0["tre200d0_sous_16"]
        * (DJ_TEMPERATURE_REFERENCE - df_meteo_tre200d0["tre200d0"])
    )

    return df_meteo_tre200d0


# Calcul des degrés-jours
@st.cache_data
def calcul_dj_periode(df_meteo_tre200d0, periode_start, periode_end):
    """
    Calculate the sum of 'DJ_theta0_16' for a given period.

    This function filters the input DataFrame `df_meteo_tre200d0` to include only the rows where the 'time' column
    falls within the specified `periode_start` and `periode_end` range. It then sums the values in the 'DJ_theta0_16'
    column for the filtered rows.

    Parameters:
    df_meteo_tre200d0 (pd.DataFrame): DataFrame containing meteorological data with at least 'time' and 'DJ_theta0_16' columns.
    periode_start (str or pd.Timestamp): The start of the period for which to calculate the sum.
    periode_end (str or pd.Timestamp): The end of the period for which to calculate the sum.

    Returns:
    float: The sum of 'DJ_theta0_16' values for the specified period.
    """
    dj_periode = df_meteo_tre200d0[
        (df_meteo_tre200d0["time"] >= periode_start)
        & (df_meteo_tre200d0["time"] <= periode_end)
    ]["DJ_theta0_16"].sum()
    dj_periode = float(dj_periode)
    return dj_periode
