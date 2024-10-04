import pandas as pd
from .calcul_dj import calcul_dj_periode

# Agent énergétique facteur de pondération
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

columns = [
    "Dénomination",
    "Valeur",
    "Unité",
    "Commentaire",
    "Excel",
    "Variable/Formule",
]


def make_dataframe_df_periode_list(data_site):
    df_periode_list = []

    # C65 → Début période
    df_periode_list.append(
        {
            "Dénomination": "Début période",
            "Valeur": data_site["periode_start"],
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
            "Valeur": data_site["periode_end"],
            "Unité": "-",
            "Commentaire": "Date de fin de la période",
            "Excel": "C66",
            "Variable/Formule": "periode_end",
        }
    )

    return pd.DataFrame(df_periode_list, columns=columns)


def make_dataframe_df_list(data_site, df_meteo_tre200d0):
    df_list = []

    # C67 → Nombre de jours
    df_list.append(
        {
            "Dénomination": "Nombre de jour(s)",
            "Valeur": data_site["periode_nb_jours"],
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
            "Valeur": data_site["repartition_energie_finale_partie_renovee_chauffage"],
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
            "Valeur": data_site["repartition_energie_finale_partie_renovee_ecs"],
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
            "Valeur": data_site[
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
            "Valeur": data_site["repartition_energie_finale_partie_surelevee_ecs"],
            "Unité": "%",
            "Commentaire": "Part d'énergie finale (ECS) pour la partie surélévée. 0 s'il n'y a pas de surélévation",
            "Excel": "C89",
            "Variable/Formule": "repartition_energie_finale_partie_surelevee_ecs",
        }
    )

    # C91 → Part EF pour partie rénové (Chauffage + ECS)
    data_site["repartition_energie_finale_partie_renovee_somme"] = (
        data_site["repartition_energie_finale_partie_renovee_chauffage"]
        + data_site["repartition_energie_finale_partie_renovee_ecs"]
    )
    df_list.append(
        {
            "Dénomination": "Part EF pour partie rénové (Chauffage + ECS)",
            "Valeur": data_site["repartition_energie_finale_partie_renovee_somme"],
            "Unité": "%",
            "Commentaire": "Part d'énergie finale (Chauffage + ECS) pour la partie rénové. 100% si pas de surélévation",
            "Excel": "C91",
            "Variable/Formule": "repartition_energie_finale_partie_renovee_somme = repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_renovee_ecs",
        }
    )

    # C92 → Est. ECS/ECS annuelle
    data_site["estimation_ecs_annuel"] = data_site["periode_nb_jours"] / 365
    df_list.append(
        {
            "Dénomination": "Est. ECS/ECS annuelle",
            "Valeur": data_site["estimation_ecs_annuel"],
            "Unité": "-",
            "Commentaire": "Estimation de la part ECS sur une année",
            "Excel": "C92",
            "Variable/Formule": "estimation_ecs_annuel = periode_nb_jours/365",
        }
    )

    # C93 → Est. Chauffage/Chauffage annuel prévisible
    data_site["dj_periode"] = float(
        calcul_dj_periode(
            df_meteo_tre200d0,
            data_site["periode_start"],
            data_site["periode_end"],
        )
    )
    data_site["estimation_part_chauffage_periode_sur_annuel"] = float(
        data_site["dj_periode"] / DJ_REF_ANNUELS
    )
    df_list.append(
        {
            "Dénomination": "Est. Chauffage/Chauffage annuel prévisible",
            "Valeur": data_site["estimation_part_chauffage_periode_sur_annuel"] * 100,
            "Unité": "%",
            "Commentaire": "Est. Chauffage/Chauffage annuel prévisible → dj_periode (C101) / DJ_REF_ANNUELS (C102)",
            "Excel": "C93",
            "Variable/Formule": "estimation_part_chauffage_periode_sur_annuel = dj_periode / DJ_REF_ANNUELS",
        }
    )

    # C94 → Est. EF période / EF année
    def estimation_ef_periode_ef_annee(data_site):
        data_site["estimation_energie_finale_periode_sur_annuel"] = (
            data_site["estimation_ecs_annuel"]
            * (
                data_site["repartition_energie_finale_partie_renovee_ecs"]
                + data_site["repartition_energie_finale_partie_surelevee_ecs"]
            )
        ) + (
            data_site["estimation_part_chauffage_periode_sur_annuel"]
            * (
                data_site["repartition_energie_finale_partie_renovee_chauffage"]
                + data_site["repartition_energie_finale_partie_surelevee_chauffage"]
            )
        )
        return data_site

    data_site = estimation_ef_periode_ef_annee(data_site)
    df_list.append(
        {
            "Dénomination": "Est. EF période / EF année",
            "Valeur": data_site["estimation_energie_finale_periode_sur_annuel"],
            "Unité": "%",
            "Commentaire": "Estimation en énergie finale sur la période / énergie finale sur une année",
            "Excel": "C94",
            "Variable/Formule": "estimation_energie_finale_periode_sur_annuel = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) + (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage))",
        }
    )

    # C95 → Est. Part ECS période comptage
    def part_ecs_periode_comptage(data_site):
        try:
            if data_site["estimation_energie_finale_periode_sur_annuel"] != 0:
                data_site["part_ecs_periode_comptage"] = (
                    data_site["estimation_ecs_annuel"]
                    * (
                        data_site["repartition_energie_finale_partie_renovee_ecs"]
                        + data_site["repartition_energie_finale_partie_surelevee_ecs"]
                    )
                ) / data_site["estimation_energie_finale_periode_sur_annuel"]
            else:
                data_site["part_ecs_periode_comptage"] = 0.0
        except ZeroDivisionError:
            data_site["part_ecs_periode_comptage"] = 0.0
        return data_site

    data_site = part_ecs_periode_comptage(data_site)

    df_list.append(
        {
            "Dénomination": "Est. Part ECS période comptage",
            "Valeur": data_site["part_ecs_periode_comptage"] * 100,
            "Unité": "%",
            "Commentaire": "",
            "Excel": "C95",
            "Variable/Formule": "part_ecs_periode_comptage = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) / estimation_energie_finale_periode_sur_annuel",
        }
    )

    # C96 → Est. Part Chauffage période comptage
    def part_chauffage_periode_comptage(data_site):
        try:
            if data_site["estimation_energie_finale_periode_sur_annuel"] != 0:
                data_site["part_chauffage_periode_comptage"] = (
                    data_site["estimation_part_chauffage_periode_sur_annuel"]
                    * (
                        data_site["repartition_energie_finale_partie_renovee_chauffage"]
                        + data_site[
                            "repartition_energie_finale_partie_surelevee_chauffage"
                        ]
                    )
                ) / data_site["estimation_energie_finale_periode_sur_annuel"]
            else:
                data_site["part_chauffage_periode_comptage"] = 0.0
        except ZeroDivisionError:
            data_site["part_chauffage_periode_comptage"] = 0.0
        return data_site

    data_site = part_chauffage_periode_comptage(data_site)
    df_list.append(
        {
            "Dénomination": "Est. Part Chauffage période comptage",
            "Valeur": data_site["part_chauffage_periode_comptage"] * 100,
            "Unité": "%",
            "Commentaire": "",
            "Excel": "C96",
            "Variable/Formule": "part_chauffage_periode_comptage = (estimation_part_chauffage_periode_sur_annuel * \
        (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage)) / estimation_energie_finale_periode_sur_annuel",
        }
    )

    # C97 → correction ECS = 365/nb jour comptage
    data_site["correction_ecs"] = 365 / data_site["periode_nb_jours"]
    df_list.append(
        {
            "Dénomination": "Correction ECS",
            "Valeur": data_site["correction_ecs"],
            "Unité": "-",
            "Commentaire": "",
            "Excel": "C97",
            "Variable/Formule": "correction_ecs = 365/periode_nb_jours",
        }
    )

    # C98 → Energie finale indiqué par le(s) compteur(s)
    data_site["agent_energetique_ef_mazout_somme_mj"] = (
        data_site["agent_energetique_ef_mazout_kg"] * CONVERSION_MAZOUT_KG_MJ
        + data_site["agent_energetique_ef_mazout_litres"] * CONVERSION_MAZOUT_LITRES_MJ
        + data_site["agent_energetique_ef_mazout_kwh"] * CONVERSION_MAZOUT_KWH_MJ
    )
    data_site["agent_energetique_ef_gaz_naturel_somme_mj"] = (
        data_site["agent_energetique_ef_gaz_naturel_m3"] * CONVERSION_GAZ_NATUREL_M3_MJ
        + data_site["agent_energetique_ef_gaz_naturel_kwh"]
        * CONVERSION_GAZ_NATUREL_KWH_MJ
    )
    data_site["agent_energetique_ef_bois_buches_dur_somme_mj"] = (
        data_site["agent_energetique_ef_bois_buches_dur_stere"]
        * CONVERSION_BOIS_BUCHES_DUR_STERE_MJ
    )
    data_site["agent_energetique_ef_bois_buches_tendre_somme_mj"] = (
        data_site["agent_energetique_ef_bois_buches_tendre_stere"]
        * CONVERSION_BOIS_BUCHES_TENDRE_STERE_MJ
        + data_site["agent_energetique_ef_bois_buches_tendre_kwh"]
        * CONVERSION_BOIS_BUCHES_TENDRE_KWH_MJ
    )
    data_site["agent_energetique_ef_pellets_somme_mj"] = (
        data_site["agent_energetique_ef_pellets_m3"] * CONVERSION_PELLETS_M3_MJ
        + data_site["agent_energetique_ef_pellets_kg"] * CONVERSION_PELLETS_KG_MJ
        + data_site["agent_energetique_ef_pellets_kwh"] * CONVERSION_PELLETS_KWH_MJ
    )
    data_site["agent_energetique_ef_plaquettes_somme_mj"] = (
        data_site["agent_energetique_ef_plaquettes_m3"] * CONVERSION_PLAQUETTES_M3_MJ
        + data_site["agent_energetique_ef_plaquettes_kwh"]
        * CONVERSION_PLAQUETTES_KWH_MJ
    )
    data_site["agent_energetique_ef_cad_somme_mj"] = (
        data_site["agent_energetique_ef_cad_kwh"] * CONVERSION_CAD_KWH_MJ
    )
    data_site["agent_energetique_ef_electricite_pac_somme_mj"] = (
        data_site["agent_energetique_ef_electricite_pac_kwh"]
        * CONVERSION_ELECTRICITE_PAC_KWH_MJ
    )
    data_site["agent_energetique_ef_electricite_directe_somme_mj"] = (
        data_site["agent_energetique_ef_electricite_directe_kwh"]
        * CONVERSION_ELECTRICITE_DIRECTE_KWH_MJ
    )
    data_site["agent_energetique_ef_autre_somme_mj"] = (
        data_site["agent_energetique_ef_autre_kwh"] * CONVERSION_AUTRE_KWH_MJ
    )

    data_site["agent_energetique_ef_somme_kwh"] = (
        data_site["agent_energetique_ef_mazout_somme_mj"]
        + data_site["agent_energetique_ef_gaz_naturel_somme_mj"]
        + data_site["agent_energetique_ef_bois_buches_dur_somme_mj"]
        + data_site["agent_energetique_ef_bois_buches_tendre_somme_mj"]
        + data_site["agent_energetique_ef_pellets_somme_mj"]
        + data_site["agent_energetique_ef_plaquettes_somme_mj"]
        + data_site["agent_energetique_ef_cad_somme_mj"]
        + data_site["agent_energetique_ef_electricite_pac_somme_mj"]
        + data_site["agent_energetique_ef_electricite_directe_somme_mj"]
        + data_site["agent_energetique_ef_autre_somme_mj"]
    ) / 3.6
    df_list.append(
        {
            "Dénomination": "Energie finale indiqué par le(s) compteur(s)",
            "Valeur": data_site["agent_energetique_ef_somme_kwh"],
            "Unité": "kWh",
            "Commentaire": "Somme de l'énergie finale indiqué par le(s) compteur(s) en kWh",
            "Excel": "C98",
            "Variable/Formule": "agent_energetique_ef_somme_kwh",
        }
    )

    # C99 → Methodo_Bww → Part de ECS en énergie finale sur la période
    data_site["methodo_b_ww_kwh"] = (
        data_site["agent_energetique_ef_somme_kwh"]
    ) * data_site["part_ecs_periode_comptage"]
    df_list.append(
        {
            "Dénomination": "Methodo_Bww",
            "Valeur": data_site["methodo_b_ww_kwh"],
            "Unité": "kWh",
            "Commentaire": "",
            "Excel": "C99",
            "Variable/Formule": "methodo_b_ww_kwh",
        }
    )

    # C100 → Methodo_Eww
    try:
        if data_site["sre_renovation_m2"] != 0 and data_site["periode_nb_jours"] != 0:
            data_site["methodo_e_ww_kwh"] = (
                data_site["methodo_b_ww_kwh"] / data_site["sre_renovation_m2"]
            ) * (365 / data_site["periode_nb_jours"])
        else:
            data_site["methodo_e_ww_kwh"] = 0.0
    except ZeroDivisionError:
        data_site["methodo_e_ww_kwh"] = 0.0
    df_list.append(
        {
            "Dénomination": "Methodo_Eww",
            "Valeur": data_site["methodo_e_ww_kwh"],
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
            "Valeur": data_site["dj_periode"],
            "Unité": "Degré-jour",
            "Commentaire": "Degré-jour 20/16 avec les températures extérieures (tre200d0) pour Genève-Cointrin relevée par MétéoSuisse",
            "Excel": "C102",
            "Variable/Formule": "dj_periode",
        }
    )

    # C103 → Methodo_Bh → Part de chauffage en énergie finale sur la période
    data_site["methodo_b_h_kwh"] = (
        data_site["agent_energetique_ef_somme_kwh"]
        * data_site["part_chauffage_periode_comptage"]
    )
    df_list.append(
        {
            "Dénomination": "Methodo_Bh",
            "Valeur": data_site["methodo_b_h_kwh"],
            "Unité": "kWh",
            "Commentaire": "Part de chauffage en énergie finale sur la période",
            "Excel": "C103",
            "Variable/Formule": "methodo_b_h_kwh = agent_energetique_ef_somme_kwh * part_chauffage_periode_comptage",
        }
    )

    # C104 → Methodo_Eh
    try:
        if data_site["sre_renovation_m2"] != 0 and data_site["dj_periode"] != 0:
            data_site["methodo_e_h_kwh"] = (
                data_site["methodo_b_h_kwh"] / data_site["sre_renovation_m2"]
            ) * (DJ_REF_ANNUELS / data_site["dj_periode"])
        else:
            data_site["methodo_e_h_kwh"] = 0.0
    except ZeroDivisionError:
        data_site["methodo_e_h_kwh"] = 0.0
    df_list.append(
        {
            "Dénomination": "Methodo_Eh",
            "Valeur": data_site["methodo_e_h_kwh"],
            "Unité": "kWh/m²",
            "Commentaire": "Energie finale par unité de surface pour le chauffage sur la période climatiquement corrigée",
            "Excel": "C104",
            "Variable/Formule": "methodo_e_h_kwh = (methodo_b_h_kwh / sre_renovation_m2) * (DJ_REF_ANNUELS / dj_periode)",
        }
    )

    # C105 → Ef,après,corr → Methodo_Eww + Methodo_Eh
    data_site[
        "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2"
    ] = (data_site["methodo_e_ww_kwh"] + data_site["methodo_e_h_kwh"])
    df_list.append(
        {
            "Dénomination": "Ef,après,corr (inclus surélévation)",
            "Valeur": data_site[
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
            "Valeur": data_site["repartition_energie_finale_partie_renovee_somme"],
            "Unité": "%",
            "Commentaire": "Part de l'énergie finale théorique dédiée à la partie rénovée (ECS+Ch.)",
            "Excel": "C106",
            "Variable/Formule": "repartition_energie_finale_partie_renovee_somme",
        }
    )

    # C107 → Ef,après,corr,rénové →Total en énergie finale (Eww+Eh) pour la partie rénovée
    data_site["energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2"] = (
        data_site[
            "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2"
        ]
        * (data_site["repartition_energie_finale_partie_renovee_somme"] / 100)
    )
    df_list.append(
        {
            "Dénomination": "Ef,après,corr,rénové",
            "Valeur": data_site[
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
        if data_site["agent_energetique_ef_somme_kwh"]:
            data_site["facteur_ponderation_moyen"] = (
                data_site["agent_energetique_ef_mazout_somme_mj"]
                * FACTEUR_PONDERATION_MAZOUT
                + data_site["agent_energetique_ef_gaz_naturel_somme_mj"]
                * FACTEUR_PONDERATION_GAZ_NATUREL
                + data_site["agent_energetique_ef_bois_buches_dur_somme_mj"]
                * FACTEUR_PONDERATION_BOIS_BUCHES_DUR
                + data_site["agent_energetique_ef_bois_buches_tendre_somme_mj"]
                * FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE
                + data_site["agent_energetique_ef_pellets_somme_mj"]
                * FACTEUR_PONDERATION_PELLETS
                + data_site["agent_energetique_ef_plaquettes_somme_mj"]
                * FACTEUR_PONDERATION_PLAQUETTES
                + data_site["agent_energetique_ef_cad_somme_mj"]
                * FACTEUR_PONDERATION_CAD
                + data_site["agent_energetique_ef_electricite_pac_somme_mj"]
                * FACTEUR_PONDERATION_ELECTRICITE_PAC
                + data_site["agent_energetique_ef_electricite_directe_somme_mj"]
                * FACTEUR_PONDERATION_ELECTRICITE_DIRECTE
                + data_site["agent_energetique_ef_autre_somme_mj"]
                * FACTEUR_PONDERATION_AUTRE
            ) / (data_site["agent_energetique_ef_somme_kwh"] * 3.6)
        else:
            data_site["facteur_ponderation_moyen"] = 0
    except ZeroDivisionError:
        data_site["facteur_ponderation_moyen"] = 0
    df_list.append(
        {
            "Dénomination": "Facteur de pondération des agents énergétiques",
            "Valeur": data_site["facteur_ponderation_moyen"],
            "Unité": "-",
            "Commentaire": "Facteur de pondération moyen des agents énergétiques",
            "Excel": "C108",
            "Variable/Formule": "facteur_ponderation_moyen",
        }
    )

    # C109 → Methodo_Eww*fp
    data_site["methodo_e_ww_renovee_pondere_kwh_m2"] = (
        data_site["methodo_e_ww_kwh"]
        * data_site["facteur_ponderation_moyen"]
        * (data_site["repartition_energie_finale_partie_renovee_somme"] / 100)
    )
    df_list.append(
        {
            "Dénomination": "Methodo_Eww*fp",
            "Valeur": data_site["methodo_e_ww_renovee_pondere_kwh_m2"],
            "Unité": "kWh/m²",
            "Commentaire": "",
            "Excel": "C109",
            "Variable/Formule": "methodo_e_ww_renovee_pondere_kwh_m2 = methodo_e_ww_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)",
        }
    )

    # C110 → Methodo_Eh*fp
    data_site["methodo_e_h_renovee_pondere_kwh_m2"] = (
        data_site["methodo_e_h_kwh"]
        * data_site["facteur_ponderation_moyen"]
        * (data_site["repartition_energie_finale_partie_renovee_somme"] / 100)
    )
    df_list.append(
        {
            "Dénomination": "Methodo_Eh*fp",
            "Valeur": data_site["methodo_e_h_renovee_pondere_kwh_m2"],
            "Unité": "kWh/m²",
            "Commentaire": "",
            "Excel": "C110",
            "Variable/Formule": "methodo_e_h_renovee_pondere_kwh_m2 = methodo_e_h_kwh * facteur_ponderation_moyen * (repartition_energie_finale_partie_renovee_somme / 100)",
        }
    )

    # C113 → Ef,après,corr,rénové*fp
    data_site[
        "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
    ] = (
        data_site["energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2"]
        * data_site["facteur_ponderation_moyen"]
    )
    df_list.append(
        {
            "Dénomination": "Ef,après,corr,rénové*fp",
            "Valeur": data_site[
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
            ],
            "Unité": "kWh/m²",
            "Commentaire": "",
            "Excel": "C113",
            "Variable/Formule": "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 * facteur_ponderation_moyen",
        }
    )

    # C114 → Ef,après,corr,rénové*fp
    data_site[
        "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2"
    ] = (
        data_site[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
        ]
        * 3.6
    )
    df_list.append(
        {
            "Dénomination": "Ef,après,corr,rénové*fp",
            "Valeur": data_site[
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2"
            ],
            "Unité": "MJ/m²",
            "Commentaire": "",
            "Excel": "C114",
            "Variable/Formule": "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 * 3.6",
        }
    )
    return pd.DataFrame(df_list, columns=columns)


def make_dataframe_df_meteo_note_calcul(data_site, df_meteo_tre200d0):
    df_meteo_note_calcul = df_meteo_tre200d0[
        (df_meteo_tre200d0["time"] >= data_site["periode_start"])
        & (df_meteo_tre200d0["time"] <= data_site["periode_end"])
    ][["time", "tre200d0", "DJ_theta0_16"]]
    return df_meteo_note_calcul


def make_dataframe_df_agent_energetique(data_site):
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
                data_site["agent_energetique_ef_mazout_somme_mj"],
                data_site["agent_energetique_ef_gaz_naturel_somme_mj"],
                data_site["agent_energetique_ef_bois_buches_dur_somme_mj"],
                data_site["agent_energetique_ef_bois_buches_tendre_somme_mj"],
                data_site["agent_energetique_ef_pellets_somme_mj"],
                data_site["agent_energetique_ef_plaquettes_somme_mj"],
                data_site["agent_energetique_ef_cad_somme_mj"],
                data_site["agent_energetique_ef_electricite_pac_somme_mj"],
                data_site["agent_energetique_ef_electricite_directe_somme_mj"],
                data_site["agent_energetique_ef_autre_somme_mj"],
            ],
            "Somme kWh": [
                data_site["agent_energetique_ef_mazout_somme_mj"] / 3.6,
                data_site["agent_energetique_ef_gaz_naturel_somme_mj"] / 3.6,
                data_site["agent_energetique_ef_bois_buches_dur_somme_mj"] / 3.6,
                data_site["agent_energetique_ef_bois_buches_tendre_somme_mj"] / 3.6,
                data_site["agent_energetique_ef_pellets_somme_mj"] / 3.6,
                data_site["agent_energetique_ef_plaquettes_somme_mj"] / 3.6,
                data_site["agent_energetique_ef_cad_somme_mj"] / 3.6,
                data_site["agent_energetique_ef_electricite_pac_somme_mj"] / 3.6,
                data_site["agent_energetique_ef_electricite_directe_somme_mj"] / 3.6,
                data_site["agent_energetique_ef_autre_somme_mj"] / 3.6,
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
    return df_agent_energetique


def make_latex_formula_facteur_ponderation_moyen_texte():
    # Define the formula
    formula_facteur_ponderation_moyen_texte = r"facteur\_ponderation\_moyen = \frac{{(agent\_energetique\_mazout\_somme\_mj \times FACTEUR\_PONDERATION\_MAZOUT + \
                agent\_energetique\_gaz\_naturel\_somme\_mj \times FACTEUR\_PONDERATION\_GAZ\_NATUREL + \
                agent\_energetique\_bois\_buches\_dur\_somme\_mj \times FACTEUR\_PONDERATION\_BOIS\_BUCHES\_DUR + \
                agent\_energetique\_bois\_buches\_tendre\_somme\_mj \times FACTEUR\_PONDERATION\_BOIS\_BUCHES\_TENDRE + \
                agent\_energetique\_pellets\_somme\_mj \times FACTEUR\_PONDERATION\_PELLETS + \
                agent\_energetique\_plaquettes\_somme\_mj \times FACTEUR\_PONDERATION\_PLAQUETTES + \
                agent\_energetique\_cad\_somme\_mj \times FACTEUR\_PONDERATION\_CAD + \
                agent\_energetique\_electricite\_pac\_somme\_mj \times FACTEUR\_PONDERATION\_ELECTRICITE\_PAC + \
                agent\_energetique\_electricite\_directe\_somme\_mj \times FACTEUR\_PONDERATION\_ELECTRICITE\_DIRECTE + \
                agent\_energetique\_autre\_somme\_mj \times FACTEUR\_PONDERATION\_AUTRE)}}{{(agent\_energetique\_somme\_kwh \times 3.6)}}"
    return formula_facteur_ponderation_moyen_texte


def make_latex_formula_facteur_ponderation_moyen(data_site):
    formula_facteur_ponderation_moyen = (
        r"facteur\_ponderation\_moyen = \frac{{({0})}}{{({1})}} = {2}".format(
            data_site["agent_energetique_ef_mazout_somme_mj"]
            * FACTEUR_PONDERATION_MAZOUT
            + data_site["agent_energetique_ef_gaz_naturel_somme_mj"]
            * FACTEUR_PONDERATION_GAZ_NATUREL
            + data_site["agent_energetique_ef_bois_buches_dur_somme_mj"]
            * FACTEUR_PONDERATION_BOIS_BUCHES_DUR
            + data_site["agent_energetique_ef_bois_buches_tendre_somme_mj"]
            * FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE
            + data_site["agent_energetique_ef_pellets_somme_mj"]
            * FACTEUR_PONDERATION_PELLETS
            + data_site["agent_energetique_ef_plaquettes_somme_mj"]
            * FACTEUR_PONDERATION_PLAQUETTES
            + data_site["agent_energetique_ef_cad_somme_mj"] * FACTEUR_PONDERATION_CAD
            + data_site["agent_energetique_ef_electricite_pac_somme_mj"]
            * FACTEUR_PONDERATION_ELECTRICITE_PAC
            + data_site["agent_energetique_ef_electricite_directe_somme_mj"]
            * FACTEUR_PONDERATION_ELECTRICITE_DIRECTE
            + data_site["agent_energetique_ef_autre_somme_mj"]
            * FACTEUR_PONDERATION_AUTRE,
            data_site["agent_energetique_ef_somme_kwh"] * 3.6,
            data_site["facteur_ponderation_moyen"],
        )
    )
    return formula_facteur_ponderation_moyen
