# sections/helpers/note_calcul/create_dataframe_list.py

import pandas as pd


def make_dataframe_df_list(data_site, DJ_REF_ANNUELS):
    df_list = []

    columns = [
        "Dénomination",
        "Valeur",
        "Unité",
        "Commentaire",
        "Excel",
        "Variable/Formule",
    ]

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
