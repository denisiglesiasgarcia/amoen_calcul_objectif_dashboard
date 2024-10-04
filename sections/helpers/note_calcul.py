import pandas as pd
import streamlit as st

from .calcul_dj import calcul_dj_periode

# TODO: utiliser ce truc car pas utiliser pour l'instant


def repartition_energie_finale_partie_renovee_somme(
    repartition_energie_finale_partie_renovee_chauffage,
    repartition_energie_finale_partie_renovee_ecs,
):
    """
    Calculate the sum of the final energy distribution for the renovated part.

    This function takes the final energy distribution for heating and the final energy distribution for domestic hot water (ECS)
    in the renovated part of a building and returns their sum.

    Args:
        repartition_energie_finale_partie_renovee_chauffage (float): The final energy distribution for heating in the renovated part.
        repartition_energie_finale_partie_renovee_ecs (float): The final energy distribution for domestic hot water (ECS) in the renovated part.

    Returns:
        float: The sum of the final energy distributions for heating and ECS in the renovated part.
    """
    return (
        repartition_energie_finale_partie_renovee_chauffage
        + repartition_energie_finale_partie_renovee_ecs
    )


def estimation_ecs_annuel(periode_nb_jours):
    """
    Estimate the annual ECS (Energy Consumption System) based on a given period in days.

    Args:
        periode_nb_jours (int): The number of days in the period.

    Returns:
        float: The estimated annual ECS as a fraction of the year.
    """
    return periode_nb_jours / 365


def estimation_part_chauffage_periode_sur_annuel(dj_periode, DJ_REF_ANNUELS):
    """
    Estimates the heating part of a period over an annual reference.

    Args:
        dj_periode (float): Degree days for the specific period.
        DJ_REF_ANNUELS (float): Annual reference degree days.

    Returns:
        float: The ratio of the period's degree days to the annual reference degree days.
    """
    dj_periode = float(calcul_dj_periode(df_meteo_tre200d0, periode_start, periode_end))
    return float(dj_periode / DJ_REF_ANNUELS)


def estimation_energie_finale_periode_sur_annuel(
    estimation_ecs_annuel,
    repartition_energie_finale_partie_renovee_ecs,
    repartition_energie_finale_partie_surelevee_ecs,
    estimation_part_chauffage_periode_sur_annuel,
    repartition_energie_finale_partie_renovee_chauffage,
    repartition_energie_finale_partie_surelevee_chauffage,
):
    """
    Estimate the final energy consumption for a period on an annual basis.

    This function calculates the final energy consumption by combining the
    estimated annual energy consumption for domestic hot water (ECS) and
    the estimated energy consumption for heating over a period, taking into
    account the energy distribution for renovated and elevated parts.

    Parameters:
    estimation_ecs_annuel (float): The estimated annual energy consumption for ECS.
    repartition_energie_finale_partie_renovee_ecs (float): The energy distribution for the renovated part for ECS.
    repartition_energie_finale_partie_surelevee_ecs (float): The energy distribution for the elevated part for ECS.
    estimation_part_chauffage_periode_sur_annuel (float): The estimated energy consumption for heating over a period.
    repartition_energie_finale_partie_renovee_chauffage (float): The energy distribution for the renovated part for heating.
    repartition_energie_finale_partie_surelevee_chauffage (float): The energy distribution for the elevated part for heating.

    Returns:
    float: The estimated final energy consumption for the period on an annual basis.
    """
    return (
        estimation_ecs_annuel
        * (
            repartition_energie_finale_partie_renovee_ecs
            + repartition_energie_finale_partie_surelevee_ecs
        )
    ) + (
        estimation_part_chauffage_periode_sur_annuel
        * (
            repartition_energie_finale_partie_renovee_chauffage
            + repartition_energie_finale_partie_surelevee_chauffage
        )
    )


def part_ecs_periode_comptage(
    estimation_ecs_annuel,
    repartition_energie_finale_partie_renovee_ecs,
    repartition_energie_finale_partie_surelevee_ecs,
    estimation_energie_finale_periode_sur_annuel,
):
    """
    Calculate the part of ECS (Eau Chaude Sanitaire) for a given period based on annual estimation and energy repartition.

    Args:
        estimation_ecs_annuel (float): Annual estimation of ECS.
        repartition_energie_finale_partie_renovee_ecs (float): Energy repartition for the renovated part of ECS.
        repartition_energie_finale_partie_surelevee_ecs (float): Energy repartition for the elevated part of ECS.
        estimation_energie_finale_periode_sur_annuel (float): Final energy estimation for the period over the year.

    Returns:
        float: The calculated part of ECS for the given period. Returns 0.0 if the final energy estimation for the period is zero or if a ZeroDivisionError occurs.
    """
    try:
        if estimation_energie_finale_periode_sur_annuel != 0:
            return (
                estimation_ecs_annuel
                * (
                    repartition_energie_finale_partie_renovee_ecs
                    + repartition_energie_finale_partie_surelevee_ecs
                )
            ) / estimation_energie_finale_periode_sur_annuel
        else:
            return 0.0
    except ZeroDivisionError:
        return 0.0


def part_chauffage_periode_comptage(
    estimation_energie_finale_periode_sur_annuel,
    estimation_part_chauffage_periode_sur_annuel,
    repartition_energie_finale_partie_renovee_chauffage,
    repartition_energie_finale_partie_surelevee_chauffage,
):
    """
    Calculate the heating part for a given period based on annual estimates and energy repartition.

    Args:
        estimation_energie_finale_periode_sur_annuel (float): Annual estimate of final energy for the period.
        estimation_part_chauffage_periode_sur_annuel (float): Annual estimate of the heating part for the period.
        repartition_energie_finale_partie_renovee_chauffage (float): Energy repartition for the renovated part for heating.
        repartition_energie_finale_partie_surelevee_chauffage (float): Energy repartition for the elevated part for heating.

    Returns:
        float: The calculated heating part for the given period. Returns 0.0 if the annual estimate of final energy for the period is zero or if a ZeroDivisionError occurs.
    """
    try:
        if estimation_energie_finale_periode_sur_annuel != 0:
            return (
                estimation_part_chauffage_periode_sur_annuel
                * (
                    repartition_energie_finale_partie_renovee_chauffage
                    + repartition_energie_finale_partie_surelevee_chauffage
                )
            ) / estimation_energie_finale_periode_sur_annuel
        else:
            return 0.0
    except ZeroDivisionError:
        return 0.0


def correction_ecs(periode_nb_jours):
    """
    Calculate the correction factor for ECS (Energy Correction System) based on the number of days in a period.

    Args:
        periode_nb_jours (int): The number of days in the period.

    Returns:
        float: The correction factor calculated as 365 divided by the number of days in the period.
    """
    return 365 / periode_nb_jours


def agent_energetique_ef_somme_kwh(
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
):
    """
    Calculate the total energy consumption in kWh from various energy sources.

    This function converts different energy sources into their equivalent energy
    in megajoules (MJ), sums them up, and then converts the total energy from MJ
    to kWh.

    Parameters:
    - agent_energetique_ef_mazout_kg (float): Energy from mazout in kilograms.
    - agent_energetique_ef_mazout_litres (float): Energy from mazout in litres.
    - agent_energetique_ef_mazout_kwh (float): Energy from mazout in kWh.
    - agent_energetique_ef_gaz_naturel_m3 (float): Energy from natural gas in cubic meters.
    - agent_energetique_ef_gaz_naturel_kwh (float): Energy from natural gas in kWh.
    - agent_energetique_ef_bois_buches_dur_stere (float): Energy from hard wood logs in stere.
    - agent_energetique_ef_bois_buches_tendre_stere (float): Energy from soft wood logs in stere.
    - agent_energetique_ef_bois_buches_tendre_kwh (float): Energy from soft wood logs in kWh.
    - agent_energetique_ef_pellets_m3 (float): Energy from pellets in cubic meters.
    - agent_energetique_ef_pellets_kg (float): Energy from pellets in kilograms.
    - agent_energetique_ef_pellets_kwh (float): Energy from pellets in kWh.
    - agent_energetique_ef_plaquettes_m3 (float): Energy from wood chips in cubic meters.
    - agent_energetique_ef_plaquettes_kwh (float): Energy from wood chips in kWh.
    - agent_energetique_ef_cad_kwh (float): Energy from district heating in kWh.
    - agent_energetique_ef_electricite_pac_kwh (float): Energy from heat pump electricity in kWh.
    - agent_energetique_ef_electricite_directe_kwh (float): Energy from direct electricity in kWh.
    - agent_energetique_ef_autre_kwh (float): Energy from other sources in kWh.

    Returns:
    - float: Total energy consumption in kWh.
    """
    agent_energetique_ef_mazout_somme_mj = (
        agent_energetique_ef_mazout_kg * CONVERSION_MAZOUT_KG_MJ
        + agent_energetique_ef_mazout_litres * CONVERSION_MAZOUT_LITRES_MJ
        + agent_energetique_ef_mazout_kwh * CONVERSION_MAZOUT_KWH_MJ
    )
    agent_energetique_ef_gaz_naturel_somme_mj = (
        agent_energetique_ef_gaz_naturel_m3 * CONVERSION_GAZ_NATUREL_M3_MJ
        + agent_energetique_ef_gaz_naturel_kwh * CONVERSION_GAZ_NATUREL_KWH_MJ
    )
    agent_energetique_ef_bois_buches_dur_somme_mj = (
        agent_energetique_ef_bois_buches_dur_stere * CONVERSION_BOIS_BUCHES_DUR_STERE_MJ
    )
    agent_energetique_ef_bois_buches_tendre_somme_mj = (
        agent_energetique_ef_bois_buches_tendre_stere
        * CONVERSION_BOIS_BUCHES_TENDRE_STERE_MJ
        + agent_energetique_ef_bois_buches_tendre_kwh
        * CONVERSION_BOIS_BUCHES_TENDRE_KWH_MJ
    )
    agent_energetique_ef_pellets_somme_mj = (
        agent_energetique_ef_pellets_m3 * CONVERSION_PELLETS_M3_MJ
        + agent_energetique_ef_pellets_kg * CONVERSION_PELLETS_KG_MJ
        + agent_energetique_ef_pellets_kwh * CONVERSION_PELLETS_KWH_MJ
    )
    agent_energetique_ef_plaquettes_somme_mj = (
        agent_energetique_ef_plaquettes_m3 * CONVERSION_PLAQUETTES_M3_MJ
        + agent_energetique_ef_plaquettes_kwh * CONVERSION_PLAQUETTES_KWH_MJ
    )
    agent_energetique_ef_cad_somme_mj = (
        agent_energetique_ef_cad_kwh * CONVERSION_CAD_KWH_MJ
    )
    agent_energetique_ef_electricite_pac_somme_mj = (
        agent_energetique_ef_electricite_pac_kwh * CONVERSION_ELECTRICITE_PAC_KWH_MJ
    )
    agent_energetique_ef_electricite_directe_somme_mj = (
        agent_energetique_ef_electricite_directe_kwh
        * CONVERSION_ELECTRICITE_DIRECTE_KWH_MJ
    )
    agent_energetique_ef_autre_somme_mj = (
        agent_energetique_ef_autre_kwh * CONVERSION_AUTRE_KWH_MJ
    )

    agent_energetique_ef_somme_kwh = (
        agent_energetique_ef_mazout_somme_mj
        + agent_energetique_ef_gaz_naturel_somme_mj
        + agent_energetique_ef_bois_buches_dur_somme_mj
        + agent_energetique_ef_bois_buches_tendre_somme_mj
        + agent_energetique_ef_pellets_somme_mj
        + agent_energetique_ef_plaquettes_somme_mj
        + agent_energetique_ef_cad_somme_mj
        + agent_energetique_ef_electricite_pac_somme_mj
        + agent_energetique_ef_electricite_directe_somme_mj
        + agent_energetique_ef_autre_somme_mj
    ) / 3.6
    return agent_energetique_ef_somme_kwh
