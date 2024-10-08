# test_note_calcul.py
# Tests for the functions in the note_calcul.py file

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to sys.path to import the functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sections.helpers.note_calcul import (
    make_dataframe_df_periode_list,
)

# Import constants
from sections.helpers.note_calcul import (
    # Agents énergétiques conversion
    CONVERSION_MAZOUT_MJ_KG,
    CONVERSION_MAZOUT_MJ_LITRES,
    CONVERSION_MAZOUT_MJ_KWH,
    CONVERSION_GAZ_NATUREL_MJ_M3,
    CONVERSION_GAZ_NATUREL_MJ_KWH,
    CONVERSION_BOIS_BUCHES_DUR_MJ_STERE,
    CONVERSION_BOIS_BUCHES_TENDRE_MJ_STERE,
    CONVERSION_BOIS_BUCHES_TENDRE_MJ_KWH,
    CONVERSION_PELLETS_MJ_M3,
    CONVERSION_PELLETS_MJ_KG,
    CONVERSION_PELLETS_MJ_KWH,
    CONVERSION_PLAQUETTES_MJ_M3,
    CONVERSION_PLAQUETTES_MJ_KWH,
    CONVERSION_CAD_MJ_KWH,
    CONVERSION_ELECTRICITE_PAC_MJ_KWH,
    CONVERSION_ELECTRICITE_DIRECTE_MJ_KWH,
    CONVERSION_AUTRE_MJ_KWH,
    # Agent énergétique facteur de pondération
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
)


# make_dataframe_df_periode_list
def test_make_dataframe_df_periode_list():
    data_site = {"periode_start": "2023-01-01", "periode_end": "2023-12-31"}
    df = make_dataframe_df_periode_list(data_site)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == [
        "Dénomination",
        "Valeur",
        "Unité",
        "Commentaire",
        "Excel",
        "Variable/Formule",
    ]
    assert df.iloc[0]["Dénomination"] == "Début période"
    assert df.iloc[1]["Dénomination"] == "Fin période"
    assert df.iloc[0]["Valeur"] == "2023-01-01"
    assert df.iloc[1]["Valeur"] == "2023-12-31"
    assert df.iloc[0]["Unité"] == "-"
    assert df.iloc[1]["Unité"] == "-"
    assert df.iloc[0]["Commentaire"] == "Date de début de la période"
    assert df.iloc[1]["Commentaire"] == "Date de fin de la période"
    assert df.iloc[0]["Excel"] == "C65"
    assert df.iloc[1]["Excel"] == "C66"
    assert df.iloc[0]["Variable/Formule"] == "periode_start"
    assert df.iloc[1]["Variable/Formule"] == "periode_end"


def test_make_dataframe_df_periode_list_empty():
    data_site = {"periode_start": "", "periode_end": ""}
    df = make_dataframe_df_periode_list(data_site)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.iloc[0]["Valeur"] == ""
    assert df.iloc[1]["Valeur"] == ""


def test_make_dataframe_df_periode_list_invalid_dates():
    data_site = {"periode_start": "invalid_date", "periode_end": "invalid_date"}
    df = make_dataframe_df_periode_list(data_site)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.iloc[0]["Valeur"] == "invalid_date"
    assert df.iloc[1]["Valeur"] == "invalid_date"


# test_note_calcul.py
# Tests for the functions in the note_calcul.py file


# Add the parent directory to sys.path to import the functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sections.helpers.note_calcul import (
    make_dataframe_df_periode_list,
    make_dataframe_df_list,
    calcul_dj_periode,
    DJ_REF_ANNUELS,
    # Agents énergétiques conversion
    CONVERSION_MAZOUT_MJ_KG,
    CONVERSION_MAZOUT_MJ_LITRES,
    CONVERSION_MAZOUT_MJ_KWH,
    CONVERSION_GAZ_NATUREL_MJ_M3,
    CONVERSION_GAZ_NATUREL_MJ_KWH,
    CONVERSION_BOIS_BUCHES_DUR_MJ_STERE,
    CONVERSION_BOIS_BUCHES_TENDRE_MJ_STERE,
    CONVERSION_BOIS_BUCHES_TENDRE_MJ_KWH,
    CONVERSION_PELLETS_MJ_M3,
    CONVERSION_PELLETS_MJ_KG,
    CONVERSION_PELLETS_MJ_KWH,
    CONVERSION_PLAQUETTES_MJ_M3,
    CONVERSION_PLAQUETTES_MJ_KWH,
    CONVERSION_CAD_MJ_KWH,
    CONVERSION_ELECTRICITE_PAC_MJ_KWH,
    CONVERSION_ELECTRICITE_DIRECTE_MJ_KWH,
    CONVERSION_AUTRE_MJ_KWH,
    # Agent énergétique facteur de pondération
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
)


# make_dataframe_df_periode_list
def test_make_dataframe_df_periode_list():
    data_site = {"periode_start": "2023-01-01", "periode_end": "2023-12-31"}
    df = make_dataframe_df_periode_list(data_site)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == [
        "Dénomination",
        "Valeur",
        "Unité",
        "Commentaire",
        "Excel",
        "Variable/Formule",
    ]
    assert df.iloc[0]["Dénomination"] == "Début période"
    assert df.iloc[1]["Dénomination"] == "Fin période"
    assert df.iloc[0]["Valeur"] == "2023-01-01"
    assert df.iloc[1]["Valeur"] == "2023-12-31"
    assert df.iloc[0]["Unité"] == "-"
    assert df.iloc[1]["Unité"] == "-"
    assert df.iloc[0]["Commentaire"] == "Date de début de la période"
    assert df.iloc[1]["Commentaire"] == "Date de fin de la période"
    assert df.iloc[0]["Excel"] == "C65"
    assert df.iloc[1]["Excel"] == "C66"
    assert df.iloc[0]["Variable/Formule"] == "periode_start"
    assert df.iloc[1]["Variable/Formule"] == "periode_end"


def test_make_dataframe_df_periode_list_empty():
    data_site = {"periode_start": "", "periode_end": ""}
    df = make_dataframe_df_periode_list(data_site)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.iloc[0]["Valeur"] == ""
    assert df.iloc[1]["Valeur"] == ""


def test_make_dataframe_df_periode_list_invalid_dates():
    data_site = {"periode_start": "invalid_date", "periode_end": "invalid_date"}
    df = make_dataframe_df_periode_list(data_site)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.iloc[0]["Valeur"] == "invalid_date"
    assert df.iloc[1]["Valeur"] == "invalid_date"


# make_dataframe_df_list
def test_make_dataframe_df_list():
    data_site = {
        "periode_nb_jours": 365,
        "repartition_energie_finale_partie_renovee_chauffage": 50,
        "repartition_energie_finale_partie_renovee_ecs": 30,
        "repartition_energie_finale_partie_surelevee_chauffage": 10,
        "repartition_energie_finale_partie_surelevee_ecs": 5,
        "periode_start": "2023-01-01",
        "periode_end": "2023-12-31",
        "sre_renovation_m2": 100,
        "agent_energetique_ef_mazout_kg": 100,
        "agent_energetique_ef_mazout_litres": 200,
        "agent_energetique_ef_mazout_kwh": 300,
        "agent_energetique_ef_gaz_naturel_m3": 400,
        "agent_energetique_ef_gaz_naturel_kwh": 500,
        "agent_energetique_ef_bois_buches_dur_stere": 600,
        "agent_energetique_ef_bois_buches_tendre_stere": 700,
        "agent_energetique_ef_bois_buches_tendre_kwh": 800,
        "agent_energetique_ef_pellets_m3": 900,
        "agent_energetique_ef_pellets_kg": 1000,
        "agent_energetique_ef_pellets_kwh": 1100,
        "agent_energetique_ef_plaquettes_m3": 1200,
        "agent_energetique_ef_plaquettes_kwh": 1300,
        "agent_energetique_ef_cad_kwh": 1400,
        "agent_energetique_ef_electricite_pac_kwh": 1500,
        "agent_energetique_ef_electricite_directe_kwh": 1600,
        "agent_energetique_ef_autre_kwh": 1700,
    }

    df_meteo_tre200d0 = pd.DataFrame(
        {
            "date": pd.date_range(start="2023-01-01", end="2023-12-31"),
            "temperature": [10] * 365,
        }
    )

    df = make_dataframe_df_list(data_site, df_meteo_tre200d0)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert list(df.columns) == [
        "Dénomination",
        "Valeur",
        "Unité",
        "Commentaire",
        "Excel",
        "Variable/Formule",
    ]


def test_make_dataframe_df_list_empty():
    data_site = {
        "periode_nb_jours": 0,
        "repartition_energie_finale_partie_renovee_chauffage": 0,
        "repartition_energie_finale_partie_renovee_ecs": 0,
        "repartition_energie_finale_partie_surelevee_chauffage": 0,
        "repartition_energie_finale_partie_surelevee_ecs": 0,
        "periode_start": "",
        "periode_end": "",
        "sre_renovation_m2": 0,
        "agent_energetique_ef_mazout_kg": 0,
        "agent_energetique_ef_mazout_litres": 0,
        "agent_energetique_ef_mazout_kwh": 0,
        "agent_energetique_ef_gaz_naturel_m3": 0,
        "agent_energetique_ef_gaz_naturel_kwh": 0,
        "agent_energetique_ef_bois_buches_dur_stere": 0,
        "agent_energetique_ef_bois_buches_tendre_stere": 0,
        "agent_energetique_ef_bois_buches_tendre_kwh": 0,
        "agent_energetique_ef_pellets_m3": 0,
        "agent_energetique_ef_pellets_kg": 0,
        "agent_energetique_ef_pellets_kwh": 0,
        "agent_energetique_ef_plaquettes_m3": 0,
        "agent_energetique_ef_plaquettes_kwh": 0,
        "agent_energetique_ef_cad_kwh": 0,
        "agent_energetique_ef_electricite_pac_kwh": 0,
        "agent_energetique_ef_electricite_directe_kwh": 0,
        "agent_energetique_ef_autre_kwh": 0,
    }

    df_meteo_tre200d0 = pd.DataFrame(
        {
            "date": pd.date_range(start="2023-01-01", end="2023-12-31"),
            "temperature": [10] * 365,
        }
    )

    df = make_dataframe_df_list(data_site, df_meteo_tre200d0)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_make_dataframe_df_list_invalid_data():
    data_site = {
        "periode_nb_jours": "invalid",
        "repartition_energie_finale_partie_renovee_chauffage": "invalid",
        "repartition_energie_finale_partie_renovee_ecs": "invalid",
        "repartition_energie_finale_partie_surelevee_chauffage": "invalid",
        "repartition_energie_finale_partie_surelevee_ecs": "invalid",
        "periode_start": "invalid",
        "periode_end": "invalid",
        "sre_renovation_m2": "invalid",
        "agent_energetique_ef_mazout_kg": "invalid",
        "agent_energetique_ef_mazout_litres": "invalid",
        "agent_energetique_ef_mazout_kwh": "invalid",
        "agent_energetique_ef_gaz_naturel_m3": "invalid",
        "agent_energetique_ef_gaz_naturel_kwh": "invalid",
        "agent_energetique_ef_bois_buches_dur_stere": "invalid",
        "agent_energetique_ef_bois_buches_tendre_stere": "invalid",
        "agent_energetique_ef_bois_buches_tendre_kwh": "invalid",
        "agent_energetique_ef_pellets_m3": "invalid",
        "agent_energetique_ef_pellets_kg": "invalid",
        "agent_energetique_ef_pellets_kwh": "invalid",
        "agent_energetique_ef_plaquettes_m3": "invalid",
        "agent_energetique_ef_plaquettes_kwh": "invalid",
        "agent_energetique_ef_cad_kwh": "invalid",
        "agent_energetique_ef_electricite_pac_kwh": "invalid",
        "agent_energetique_ef_electricite_directe_kwh": "invalid",
        "agent_energetique_ef_autre_kwh": "invalid",
    }

    df_meteo_tre200d0 = pd.DataFrame(
        {
            "date": pd.date_range(start="2023-01-01", end="2023-12-31"),
            "temperature": [10] * 365,
        }
    )

    with pytest.raises(Exception):
        make_dataframe_df_list(data_site, df_meteo_tre200d0)
