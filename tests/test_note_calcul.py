# test_note_calcul.py
# Tests for the functions in the note_calcul.py file

# import pytest
from pytest import approx

# import pandas as pd
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path to import the functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sections.helpers.calcul_dj import (
    get_meteo_data,
    calcul_dj_periode,
)

from sections.helpers.note_calcul.calculs import (
    fonction_repartition_energie_finale_partie_renovee_somme,
    fonction_estimation_ecs_annuel,
    fonction_estimation_part_chauffage_periode_sur_annuel,
    fonction_estimation_energie_finale_periode_sur_annuel,
    fonction_part_ecs_periode_comptage,
    fonction_part_chauffage_periode_comptage,
    fonction_correction_ecs,
    fonction_agent_energetique_ef_mazout_somme_mj,
    fonction_agent_energetique_ef_gaz_naturel_somme_mj,
    fonction_agent_energetique_ef_bois_buches_dur_somme_mj,
    fonction_agent_energetique_ef_bois_buches_tendre_somme_mj,
    fonction_agent_energetique_ef_pellets_somme_mj,
    fonction_agent_energetique_ef_plaquettes_somme_mj,
    fonction_agent_energetique_ef_cad_somme_mj,
    fonction_agent_energetique_ef_electricite_pac_somme_mj,
    fonction_agent_energetique_ef_electricite_directe_somme_mj,
    fonction_agent_energetique_ef_autre_somme_mj,
    fonction_agent_energetique_ef_somme_kwh,
    fonction_methodo_b_ww_kwh,
    fonction_methodo_e_ww_kwh_m2,
    fonction_methodo_b_h_kwh,
    fonction_methodo_e_h_kwh_m2,
    fonction_energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2,
    fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2,
    fonction_facteur_ponderation_moyen,
    fonction_methodo_e_ww_renovee_pondere_kwh_m2,
    fonction_methodo_e_h_renovee_pondere_kwh_m2,
    fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
    fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2,
    fonction_delta_ef_realisee_kwh_m2,
    fonction_delta_ef_visee_kwh_m2,
    fonction_atteinte_objectif,
)

from sections.helpers.note_calcul.constantes import (
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
    DJ_REF_ANNUELS,
)

# Get the meteorological data
df_meteo_tre200d0 = get_meteo_data()

####################################################################################################

# Test data for the functions
# test_1 (Avusy)
test_avusy1_in = {
    "sre_renovation_m2": 1600.0,
    "ef_avant_corr_kwh_m2": ((663 + 625 + 688) / 3) / 3.6,
    "ef_objectif_pondere_kwh_m2": 41.91282051,
    "periode_start": datetime(2023, 2, 3),
    "periode_end": datetime(2024, 2, 3),
    "periode_nb_jours": 366,
    "repartition_energie_finale_partie_renovee_chauffage": 38.3335373,
    "repartition_energie_finale_partie_renovee_ecs": 61.6664627,
    "repartition_energie_finale_partie_surelevee_chauffage": 0.0,
    "repartition_energie_finale_partie_surelevee_ecs": 0.0,
    "agent_energetique_ef_mazout_kg": 0.0,
    "agent_energetique_ef_mazout_litres": 0.0,
    "agent_energetique_ef_mazout_kwh": 0.0,
    "agent_energetique_ef_gaz_naturel_m3": 0.0,
    "agent_energetique_ef_gaz_naturel_kwh": 0.0,
    "agent_energetique_ef_bois_buches_dur_stere": 0.0,
    "agent_energetique_ef_bois_buches_tendre_stere": 0.0,
    "agent_energetique_ef_bois_buches_tendre_kwh": 0.0,
    "agent_energetique_ef_pellets_m3": 0.0,
    "agent_energetique_ef_pellets_kg": 0.0,
    "agent_energetique_ef_pellets_kwh": 0.0,
    "agent_energetique_ef_plaquettes_m3": 0.0,
    "agent_energetique_ef_plaquettes_kwh": 0.0,
    "agent_energetique_ef_cad_kwh": 0.0,
    "agent_energetique_ef_electricite_pac_kwh": 36208.0,
    "agent_energetique_ef_electricite_directe_kwh": 0.0,
    "agent_energetique_ef_autre_kwh": 0.0,
}

test_avusy1_out = {
    "repartition_energie_finale_partie_renovee_somme": 100.0,
    "estimation_ecs_annuel": 1.002739726,
    "estimation_part_chauffage_periode_sur_annuel": 0.861882036,
    "estimation_energie_finale_periode_sur_annuel": 94.8743991,
    "part_ecs_periode_comptage": 0.651760776,
    "part_chauffage_periode_comptage": 0.348239224,
    "correction_ecs": 0.99726776,
    "agent_energetique_ef_mazout_somme_mj": 0.0,
    "agent_energetique_ef_gaz_naturel_somme_mj": 0.0,
    "agent_energetique_ef_bois_buches_dur_somme_mj": 0.0,
    "agent_energetique_ef_bois_buches_tendre_somme_mj": 0.0,
    "agent_energetique_ef_pellets_somme_mj": 0.0,
    "agent_energetique_ef_plaquettes_somme_mj": 0.0,
    "agent_energetique_ef_cad_somme_mj": 0.0,
    "agent_energetique_ef_electricite_pac_somme_mj": 36208.0 * 3.6,
    "agent_energetique_ef_electricite_directe_somme_mj": 0.0,
    "agent_energetique_ef_autre_somme_mj": 0.0,
    "agent_energetique_ef_somme_kwh": 36208.0,
    "methodo_b_ww_kwh": 23598.95417,
    "methodo_e_ww_kwh_m2": 14.7090476,
    "dj_periode": 2810.2,
    "methodo_b_h_kwh": 12609.04583,
    "methodo_e_h_kwh_m2": 9.143540897,
    "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2": 23.8525885,
    "energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2": 23.8525885,
    "facteur_ponderation_moyen": 2.0,
    "methodo_e_ww_renovee_pondere_kwh_m2": 29.4180952,
    "methodo_e_h_renovee_pondere_kwh_m2": 18.28708179,
    "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2": 47.70517699,
    "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2": 171.7386372,
    "delta_ef_realisee_kwh_m2": 135.257786,
    "delta_ef_visee_kwh_m2": 141.0501425,
    "atteinte_objectif": 0.958934061,
}

# combine the 2 dictionaries in data_site_avusy1
data_site_avusy1 = {**test_avusy1_in, **test_avusy1_out}


# calcul_dj.py
def test_calcul_dj_periode():
    assert (
        calcul_dj_periode(
            df_meteo_tre200d0,
            data_site_avusy1["periode_start"],
            data_site_avusy1["periode_end"],
        )
        == data_site_avusy1["dj_periode"]
    )
    assert (
        calcul_dj_periode(
            df_meteo_tre200d0,
            datetime(2023, 1, 1),
            datetime(2024, 1, 1),
        )
        == 2804.3
    )


# note_calcul.py
def test_fonction_repartition_energie_finale_partie_renovee_somme():
    assert fonction_repartition_energie_finale_partie_renovee_somme(
        data_site_avusy1["repartition_energie_finale_partie_renovee_chauffage"],
        data_site_avusy1["repartition_energie_finale_partie_renovee_ecs"],
    ) == approx(data_site_avusy1["repartition_energie_finale_partie_renovee_somme"])


def test_fonction_estimation_ecs_annuel():
    assert fonction_estimation_ecs_annuel(
        data_site_avusy1["periode_nb_jours"]
    ) == approx(data_site_avusy1["estimation_ecs_annuel"])


def test_fonction_estimation_part_chauffage_periode_sur_annuel():
    assert fonction_estimation_part_chauffage_periode_sur_annuel(
        data_site_avusy1["dj_periode"], DJ_REF_ANNUELS
    ) == approx(data_site_avusy1["estimation_part_chauffage_periode_sur_annuel"])


def test_fonction_estimation_energie_finale_periode_sur_annuel():
    assert fonction_estimation_energie_finale_periode_sur_annuel(
        data_site_avusy1["estimation_ecs_annuel"],
        data_site_avusy1["repartition_energie_finale_partie_renovee_ecs"],
        data_site_avusy1["repartition_energie_finale_partie_surelevee_ecs"],
        data_site_avusy1["estimation_part_chauffage_periode_sur_annuel"],
        data_site_avusy1["repartition_energie_finale_partie_renovee_chauffage"],
        data_site_avusy1["repartition_energie_finale_partie_surelevee_chauffage"],
    ) == approx(data_site_avusy1["estimation_energie_finale_periode_sur_annuel"])


def test_fonction_part_ecs_periode_comptage():
    assert fonction_part_ecs_periode_comptage(
        data_site_avusy1["estimation_energie_finale_periode_sur_annuel"],
        data_site_avusy1["estimation_ecs_annuel"],
        data_site_avusy1["repartition_energie_finale_partie_renovee_ecs"],
        data_site_avusy1["repartition_energie_finale_partie_surelevee_ecs"],
    ) == approx(data_site_avusy1["part_ecs_periode_comptage"])


def test_fonction_part_chauffage_periode_comptage():
    assert fonction_part_chauffage_periode_comptage(
        data_site_avusy1["estimation_energie_finale_periode_sur_annuel"],
        data_site_avusy1["estimation_part_chauffage_periode_sur_annuel"],
        data_site_avusy1["repartition_energie_finale_partie_renovee_chauffage"],
        data_site_avusy1["repartition_energie_finale_partie_surelevee_chauffage"],
    ) == approx(data_site_avusy1["part_chauffage_periode_comptage"])


def test_fonction_correction_ecs():
    assert fonction_correction_ecs(data_site_avusy1["periode_nb_jours"]) == approx(
        data_site_avusy1["correction_ecs"]
    )


def test_fonction_agent_energetique_ef_mazout_somme_mj():
    assert fonction_agent_energetique_ef_mazout_somme_mj(
        data_site_avusy1["agent_energetique_ef_mazout_kg"],
        data_site_avusy1["agent_energetique_ef_mazout_litres"],
        data_site_avusy1["agent_energetique_ef_mazout_kwh"],
        CONVERSION_MAZOUT_MJ_KG,
        CONVERSION_MAZOUT_MJ_LITRES,
        CONVERSION_MAZOUT_MJ_KWH,
    ) == approx(data_site_avusy1["agent_energetique_ef_mazout_somme_mj"])
    assert (
        fonction_agent_energetique_ef_mazout_somme_mj(
            0.0,
            0.0,
            0.0,
            CONVERSION_MAZOUT_MJ_KG,
            CONVERSION_MAZOUT_MJ_LITRES,
            CONVERSION_MAZOUT_MJ_KWH,
        )
        == 0.0
    )
    assert (
        fonction_agent_energetique_ef_mazout_somme_mj(
            1000,
            1000,
            1000,
            CONVERSION_MAZOUT_MJ_KG,
            CONVERSION_MAZOUT_MJ_LITRES,
            CONVERSION_MAZOUT_MJ_KWH,
        )
        == 86032
    )


def test_fonction_agent_energetique_ef_gaz_naturel_somme_mj():
    assert fonction_agent_energetique_ef_gaz_naturel_somme_mj(
        data_site_avusy1["agent_energetique_ef_gaz_naturel_m3"],
        data_site_avusy1["agent_energetique_ef_gaz_naturel_kwh"],
        CONVERSION_GAZ_NATUREL_MJ_M3,
        CONVERSION_GAZ_NATUREL_MJ_KWH,
    ) == approx(data_site_avusy1["agent_energetique_ef_gaz_naturel_somme_mj"])
    assert (
        fonction_agent_energetique_ef_gaz_naturel_somme_mj(
            1000,
            1000,
            CONVERSION_GAZ_NATUREL_MJ_M3,
            CONVERSION_GAZ_NATUREL_MJ_KWH,
        )
        == 42100
    )


def test_fonction_agent_energetique_ef_bois_buches_dur_somme_mj():
    assert fonction_agent_energetique_ef_bois_buches_dur_somme_mj(
        data_site_avusy1["agent_energetique_ef_bois_buches_dur_stere"],
        CONVERSION_BOIS_BUCHES_DUR_MJ_STERE,
    ) == approx(data_site_avusy1["agent_energetique_ef_bois_buches_dur_somme_mj"])
    assert (
        fonction_agent_energetique_ef_bois_buches_dur_somme_mj(
            1000,
            CONVERSION_BOIS_BUCHES_DUR_MJ_STERE,
        )
        == 7960000.000
    )


def test_fonction_agent_energetique_ef_bois_buches_tendre_somme_mj():
    assert fonction_agent_energetique_ef_bois_buches_tendre_somme_mj(
        data_site_avusy1["agent_energetique_ef_bois_buches_tendre_stere"],
        data_site_avusy1["agent_energetique_ef_bois_buches_tendre_kwh"],
        CONVERSION_BOIS_BUCHES_TENDRE_MJ_STERE,
        CONVERSION_BOIS_BUCHES_TENDRE_MJ_KWH,
    ) == approx(data_site_avusy1["agent_energetique_ef_bois_buches_tendre_somme_mj"])
    assert (
        fonction_agent_energetique_ef_bois_buches_tendre_somme_mj(
            1000,
            1000,
            CONVERSION_BOIS_BUCHES_TENDRE_MJ_STERE,
            CONVERSION_BOIS_BUCHES_TENDRE_MJ_KWH,
        )
        == 5575600.000
    )


def test_fonction_agent_energetique_ef_pellets_somme_mj():
    assert fonction_agent_energetique_ef_pellets_somme_mj(
        data_site_avusy1["agent_energetique_ef_pellets_m3"],
        data_site_avusy1["agent_energetique_ef_pellets_kg"],
        data_site_avusy1["agent_energetique_ef_pellets_kwh"],
        CONVERSION_PELLETS_MJ_M3,
        CONVERSION_PELLETS_MJ_KG,
        CONVERSION_PELLETS_MJ_KWH,
    ) == approx(data_site_avusy1["agent_energetique_ef_pellets_somme_mj"])
    assert (
        fonction_agent_energetique_ef_pellets_somme_mj(
            1000,
            1000,
            1000,
            CONVERSION_PELLETS_MJ_M3,
            CONVERSION_PELLETS_MJ_KG,
            CONVERSION_PELLETS_MJ_KWH,
        )
        == 13355800
    )


def test_fonction_agent_energetique_ef_plaquettes_somme_mj():
    assert fonction_agent_energetique_ef_plaquettes_somme_mj(
        data_site_avusy1["agent_energetique_ef_plaquettes_m3"],
        data_site_avusy1["agent_energetique_ef_plaquettes_kwh"],
        CONVERSION_PLAQUETTES_MJ_M3,
        CONVERSION_PLAQUETTES_MJ_KWH,
    ) == approx(data_site_avusy1["agent_energetique_ef_plaquettes_somme_mj"])
    assert fonction_agent_energetique_ef_plaquettes_somme_mj(
        1000,
        1000,
        CONVERSION_PLAQUETTES_MJ_M3,
        CONVERSION_PLAQUETTES_MJ_KWH,
    ) == approx(4004065.51724138)


def test_fonction_agent_energetique_ef_cad_somme_mj():
    assert fonction_agent_energetique_ef_cad_somme_mj(
        data_site_avusy1["agent_energetique_ef_cad_kwh"],
        CONVERSION_CAD_MJ_KWH,
    ) == approx(data_site_avusy1["agent_energetique_ef_cad_somme_mj"])
    assert (
        fonction_agent_energetique_ef_cad_somme_mj(
            1000,
            CONVERSION_CAD_MJ_KWH,
        )
        == 3600
    )


def test_fonction_agent_energetique_ef_electricite_pac_somme_mj():
    assert fonction_agent_energetique_ef_electricite_pac_somme_mj(
        data_site_avusy1["agent_energetique_ef_electricite_pac_kwh"],
        CONVERSION_ELECTRICITE_PAC_MJ_KWH,
    ) == approx(data_site_avusy1["agent_energetique_ef_electricite_pac_somme_mj"])
    assert (
        fonction_agent_energetique_ef_electricite_pac_somme_mj(
            1000,
            CONVERSION_ELECTRICITE_PAC_MJ_KWH,
        )
        == 3600
    )


def test_fonction_agent_energetique_ef_electricite_directe_somme_mj():
    assert fonction_agent_energetique_ef_electricite_directe_somme_mj(
        data_site_avusy1["agent_energetique_ef_electricite_directe_kwh"],
        CONVERSION_ELECTRICITE_DIRECTE_MJ_KWH,
    ) == approx(data_site_avusy1["agent_energetique_ef_electricite_directe_somme_mj"])
    assert (
        fonction_agent_energetique_ef_electricite_directe_somme_mj(
            1000,
            CONVERSION_ELECTRICITE_DIRECTE_MJ_KWH,
        )
        == 3600
    )


def test_fonction_agent_energetique_ef_autre_somme_mj():
    assert fonction_agent_energetique_ef_autre_somme_mj(
        data_site_avusy1["agent_energetique_ef_autre_kwh"],
        CONVERSION_AUTRE_MJ_KWH,
    ) == approx(data_site_avusy1["agent_energetique_ef_autre_somme_mj"])
    assert (
        fonction_agent_energetique_ef_autre_somme_mj(
            1000,
            CONVERSION_AUTRE_MJ_KWH,
        )
        == 3600
    )


def test_fonction_agent_energetique_ef_somme_kwh():
    assert fonction_agent_energetique_ef_somme_kwh(
        data_site_avusy1["agent_energetique_ef_mazout_somme_mj"],
        data_site_avusy1["agent_energetique_ef_gaz_naturel_somme_mj"],
        data_site_avusy1["agent_energetique_ef_bois_buches_dur_somme_mj"],
        data_site_avusy1["agent_energetique_ef_bois_buches_tendre_somme_mj"],
        data_site_avusy1["agent_energetique_ef_pellets_somme_mj"],
        data_site_avusy1["agent_energetique_ef_plaquettes_somme_mj"],
        data_site_avusy1["agent_energetique_ef_cad_somme_mj"],
        data_site_avusy1["agent_energetique_ef_electricite_pac_somme_mj"],
        data_site_avusy1["agent_energetique_ef_electricite_directe_somme_mj"],
        data_site_avusy1["agent_energetique_ef_autre_somme_mj"],
    ) == approx(data_site_avusy1["agent_energetique_ef_somme_kwh"])
    assert (
        fonction_agent_energetique_ef_somme_kwh(
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
            1000,
        )
        == 10000 / 3.6
    )


def test_fonction_methodo_b_ww_kwh():
    assert fonction_methodo_b_ww_kwh(
        data_site_avusy1["agent_energetique_ef_somme_kwh"],
        data_site_avusy1["part_ecs_periode_comptage"],
    ) == approx(data_site_avusy1["methodo_b_ww_kwh"])


def test_fonction_methodo_e_ww_kwh_m2():
    assert fonction_methodo_e_ww_kwh_m2(
        data_site_avusy1["methodo_b_ww_kwh"],
        data_site_avusy1["sre_renovation_m2"],
        data_site_avusy1["periode_nb_jours"],
    ) == approx(data_site_avusy1["methodo_e_ww_kwh_m2"])


def test_fonction_methodo_b_h_kwh():
    assert fonction_methodo_b_h_kwh(
        data_site_avusy1["agent_energetique_ef_somme_kwh"],
        data_site_avusy1["part_chauffage_periode_comptage"],
    ) == approx(data_site_avusy1["methodo_b_h_kwh"])


def test_fonction_methodo_e_h_kwh_m2():
    assert fonction_methodo_e_h_kwh_m2(
        data_site_avusy1["sre_renovation_m2"],
        data_site_avusy1["dj_periode"],
        data_site_avusy1["methodo_b_h_kwh"],
        DJ_REF_ANNUELS,
    ) == approx(data_site_avusy1["methodo_e_h_kwh_m2"])


def test_fonction_energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2():
    assert fonction_energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2(
        data_site_avusy1["methodo_e_ww_kwh_m2"],
        data_site_avusy1["methodo_e_h_kwh_m2"],
    ) == approx(
        data_site_avusy1[
            "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2"
        ]
    )


def test_fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2():
    assert fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2(
        data_site_avusy1[
            "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2"
        ],
        data_site_avusy1["repartition_energie_finale_partie_renovee_somme"],
    ) == approx(
        data_site_avusy1[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2"
        ]
    )


def test_fonction_facteur_ponderation_moyen():
    assert fonction_facteur_ponderation_moyen(
        data_site_avusy1["agent_energetique_ef_mazout_somme_mj"],
        data_site_avusy1["agent_energetique_ef_gaz_naturel_somme_mj"],
        data_site_avusy1["agent_energetique_ef_bois_buches_dur_somme_mj"],
        data_site_avusy1["agent_energetique_ef_bois_buches_tendre_somme_mj"],
        data_site_avusy1["agent_energetique_ef_pellets_somme_mj"],
        data_site_avusy1["agent_energetique_ef_plaquettes_somme_mj"],
        data_site_avusy1["agent_energetique_ef_cad_somme_mj"],
        data_site_avusy1["agent_energetique_ef_electricite_pac_somme_mj"],
        data_site_avusy1["agent_energetique_ef_electricite_directe_somme_mj"],
        data_site_avusy1["agent_energetique_ef_autre_somme_mj"],
        data_site_avusy1["agent_energetique_ef_somme_kwh"],
        FACTEUR_PONDERATION_GAZ_NATUREL,
        FACTEUR_PONDERATION_MAZOUT,
        FACTEUR_PONDERATION_BOIS_BUCHES_DUR,
        FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE,
        FACTEUR_PONDERATION_PELLETS,
        FACTEUR_PONDERATION_PLAQUETTES,
        FACTEUR_PONDERATION_CAD,
        FACTEUR_PONDERATION_ELECTRICITE_PAC,
        FACTEUR_PONDERATION_ELECTRICITE_DIRECTE,
        FACTEUR_PONDERATION_AUTRE,
    ) == approx(data_site_avusy1["facteur_ponderation_moyen"])


def test_fonction_methodo_e_ww_renovee_pondere_kwh_m2():
    assert fonction_methodo_e_ww_renovee_pondere_kwh_m2(
        data_site_avusy1["methodo_e_ww_kwh_m2"],
        data_site_avusy1["facteur_ponderation_moyen"],
        data_site_avusy1["repartition_energie_finale_partie_renovee_somme"],
    ) == approx(data_site_avusy1["methodo_e_ww_renovee_pondere_kwh_m2"])


def test_fonction_methodo_e_h_renovee_pondere_kwh_m2():
    assert fonction_methodo_e_h_renovee_pondere_kwh_m2(
        data_site_avusy1["methodo_e_h_kwh_m2"],
        data_site_avusy1["facteur_ponderation_moyen"],
        data_site_avusy1["repartition_energie_finale_partie_renovee_somme"],
    ) == approx(data_site_avusy1["methodo_e_h_renovee_pondere_kwh_m2"])


def test_fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2():
    assert fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2(
        data_site_avusy1[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2"
        ],
        data_site_avusy1["facteur_ponderation_moyen"],
    ) == approx(
        data_site_avusy1[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
        ]
    )


def test_fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2():
    assert fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2(
        data_site_avusy1[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
        ]
    ) == approx(
        data_site_avusy1[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2"
        ]
    )


def test_fonction_delta_ef_realisee_kwh_m2():
    assert fonction_delta_ef_realisee_kwh_m2(
        data_site_avusy1["ef_avant_corr_kwh_m2"],
        data_site_avusy1[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
        ],
    ) == approx(data_site_avusy1["delta_ef_realisee_kwh_m2"])


def test_fonction_delta_ef_visee_kwh_m2():
    assert fonction_delta_ef_visee_kwh_m2(
        data_site_avusy1["ef_avant_corr_kwh_m2"],
        data_site_avusy1["ef_objectif_pondere_kwh_m2"],
    ) == approx(data_site_avusy1["delta_ef_visee_kwh_m2"])


def test_fonction_atteinte_objectif():
    assert fonction_atteinte_objectif(
        data_site_avusy1["delta_ef_realisee_kwh_m2"],
        data_site_avusy1[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
        ],
        data_site_avusy1["delta_ef_visee_kwh_m2"],
    ) == approx(data_site_avusy1["atteinte_objectif"])
