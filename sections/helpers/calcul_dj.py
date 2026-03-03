# /sections/helpers/calcul_dj.py

import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data
def get_meteo_data(DJ_TEMPERATURE_REFERENCE=20):
    """
    Fetch and process meteorological data for degree-day (DJ) calculations.

    Retrieves historical and recent temperature data from the Swiss Federal Office
    of Meteorology and Climatology (MeteoSwiss), combines them, and calculates
    heating degree days (DJ) based on a reference temperature threshold.

    Parameters
    ----------
    DJ_TEMPERATURE_REFERENCE : float, optional
        Reference temperature in Celsius for degree-day calculations (default: 20).

    Returns
    -------
    pd.DataFrame
        Processed meteorological data with columns:
        - stn : str
            Station abbreviation code
        - time : datetime
            Timestamp in format DD.MM.YYYY HH:MM
        - tre200d0 : float
            Temperature measurement in degrees Celsius
        - mois : int
            Month number (1-12)
        - saison_chauffe : int
            Binary indicator (1 if heating season, 0 otherwise)
            Heating season: September to May (months 9-12, 1-5)
        - tre200d0_sous_16 : int
            Binary indicator (1 if temperature <= 16°C, 0 otherwise)
        - DJ_theta0_16 : float
            Heating degree days calculated as:
            (DJ_TEMPERATURE_REFERENCE - temperature) during heating season
            when temperature <= 16°C, 0 otherwise

    Notes
    -----
    - Data is cached using Streamlit's @st.cache_data decorator
    - Only records from 2020-01-01 onwards are retained
    - Missing values ("-") are removed before processing
    - Duplicates are removed and data is sorted by timestamp
    """
    df_hist = pd.read_csv(
        "https://data.geo.admin.ch/ch.meteoschweiz.ogd-smn/gve/ogd-smn_gve_d_historical.csv",
        sep=";",
        encoding="latin1",
    )
    df_recent = pd.read_csv(
        "https://data.geo.admin.ch/ch.meteoschweiz.ogd-smn/gve/ogd-smn_gve_d_recent.csv",
        sep=";",
        encoding="latin1",
    )
    df = pd.concat([df_hist, df_recent])
    df.rename(
        columns={"station_abbr": "stn", "reference_timestamp": "time"}, inplace=True
    )
    df = df[["stn", "time", "tre200d0"]]

    # Replace "-" with NaN before any type conversion
    df.replace("-", pd.NA, inplace=True)
    df.dropna(inplace=True)

    # Explicit format required: CSV uses DD.MM.YYYY HH:MM
    df["time"] = pd.to_datetime(df["time"], format="%d.%m.%Y %H:%M")

    df = df[df["time"] >= "2020-01-01"]
    df.drop_duplicates(inplace=True)
    df.sort_values(by="time", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # DJ calculations
    df["tre200d0"] = df["tre200d0"].astype(float)
    df["mois"] = df["time"].dt.month
    df["saison_chauffe"] = np.where(
        df["mois"].isin([9, 10, 11, 12, 1, 2, 3, 4, 5]), 1, 0
    )
    df["tre200d0_sous_16"] = np.where(df["tre200d0"] <= 16, 1, 0)
    df["DJ_theta0_16"] = (
        df["saison_chauffe"]
        * df["tre200d0_sous_16"]
        * (DJ_TEMPERATURE_REFERENCE - df["tre200d0"])
    )

    return df


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
