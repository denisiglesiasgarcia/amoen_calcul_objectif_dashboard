import pandas as pd
import streamlit as st

from calcul_dj import calcul_dj_periode


def repartition_energie_finale_partie_renovee_somme(repartition_energie_finale_partie_renovee_chauffage, repartition_energie_finale_partie_renovee_ecs):
    return repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_renovee_ecs

def estimation_ecs_annuel(periode_nb_jours):
    return periode_nb_jours/365

def estimation_part_chauffage_periode_sur_annuel(dj_periode, DJ_REF_ANNUELS):
    dj_periode = float(calcul_dj_periode(df_meteo_tre200d0, periode_start, periode_end))
    return float(dj_periode / DJ_REF_ANNUELS)

def estimation_energie_finale_periode_sur_annuel(estimation_ecs_annuel,
                                                    repartition_energie_finale_partie_renovee_ecs,
                                                    repartition_energie_finale_partie_surelevee_ecs,
                                                    estimation_part_chauffage_periode_sur_annuel,
                                                    repartition_energie_finale_partie_renovee_chauffage,
                                                    repartition_energie_finale_partie_surelevee_chauffage):
    return (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) + (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage))

def part_ecs_periode_comptage(estimation_ecs_annuel, repartition_energie_finale_partie_renovee_ecs, repartition_energie_finale_partie_surelevee_ecs, estimation_energie_finale_periode_sur_annuel):
    try:
        if estimation_energie_finale_periode_sur_annuel != 0:
            return (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) / estimation_energie_finale_periode_sur_annuel
        else:
            return 0.0
    except ZeroDivisionError:
        return 0.0

def part_chauffage_periode_comptage(estimation_energie_finale_periode_sur_annuel, estimation_part_chauffage_periode_sur_annuel, repartition_energie_finale_partie_renovee_chauffage, repartition_energie_finale_partie_surelevee_chauffage):
    try:
        if estimation_energie_finale_periode_sur_annuel != 0:
            return (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage)) / estimation_energie_finale_periode_sur_annuel
        else:
            return 0.0
    except ZeroDivisionError:
        return 0.0

def correction_ecs(periode_nb_jours):
    return 365/periode_nb_jours

def agent_energetique_ef_somme_kwh(agent_energetique_ef_mazout_kg, agent_energetique_ef_mazout_litres, agent_energetique_ef_mazout_kwh, agent_energetique_ef_gaz_naturel_m3, agent_energetique_ef_gaz_naturel_kwh, agent_energetique_ef_bois_buches_dur_stere, agent_energetique_ef_bois_buches_tendre_stere, agent_energetique_ef_bois_buches_tendre_kwh, agent_energetique_ef_pellets_m3, agent_energetique_ef_pellets_kg, agent_energetique_ef_pellets_kwh, agent_energetique_ef_plaquettes_m3, agent_energetique_ef_plaquettes_kwh, agent_energetique_ef_cad_kwh, agent_energetique_ef_electricite_pac_kwh, agent_energetique_ef_electricite_directe_kwh, agent_energetique_ef_autre_kwh):
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
    return agent_energetique_ef_somme_kwh


data_periode = {
        'Début période': {'Valeur': periode_start, 'Unité': '-', 'Commentaire': 'Date de début de la période', 'Excel': 'C65', 'Variable/Formule': 'periode_start'},
        'Fin période': {'Valeur': periode_end, 'Unité': '-', 'Commentaire': 'Date de fin de la période', 'Excel': 'C66', 'Variable/Formule': 'periode_end'},
}

data_calculs = {
    'Nombre de jour(s)': {'Valeur': periode_nb_jours, 'Unité': 'jour(s)', 'Commentaire': 'Nombre de jour(s) dans la période', 'Excel': 'C67', 'Variable/Formule': 'periode_nb_jours'},
    'Répartition en énergie finale (chauffage) pour la partie rénové': {'Valeur': repartition_energie_finale_partie_renovee_chauffage, 'Unité': '%', 'Commentaire': '', 'Excel': 'C86', 'Variable/Formule': "repartition_energie_finale_partie_renovee_chauffage"},
    'Répartition en énergie finale (ECS) pour la partie rénové': {'Valeur': repartition_energie_finale_partie_renovee_ecs, 'Unité': '%', 'Commentaire': '', 'Excel': 'C87', 'Variable/Formule': "repartition_energie_finale_partie_renovee_ecs"},
    'Répartition en énergie finale (chauffage) pour la partie surélévée': {'Valeur': repartition_energie_finale_partie_surelevee_chauffage, 'Unité': '%', 'Commentaire': "0 if no surélévation", 'Excel': 'C88', 'Variable/Formule': "repartition_energie_finale_partie_surelevee_chauffage"},
    'Répartition en énergie finale - ECS partie surélévée': {'Valeur': repartition_energie_finale_partie_surelevee_ecs, 'Unité': '%', 'Commentaire': "Part d'énergie finale (ECS) pour la partie surélévée. 0 s'il n'y a pas de surélévation", 'Excel': 'C89', 'Variable/Formule': "repartition_energie_finale_partie_surelevee_ecs"},
    'Part EF pour partie rénové (Chauffage + ECS)': {'Valeur': repartition_energie_finale_partie_renovee_somme(repartition_energie_finale_partie_renovee_chauffage, repartition_energie_finale_partie_renovee_ecs), 'Unité': '%', 'Commentaire': "Part d'énergie finale (Chauffage + ECS) pour la partie rénové. 100% si pas de surélévation", 'Excel': 'C91', 'Variable/Formule': "repartition_energie_finale_partie_renovee_somme = repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_renovee_ecs"},
    'Est. ECS/ECS annuelle': {'Valeur': estimation_ecs_annuel(periode_nb_jours), 'Unité': '-', 'Commentaire': 'Estimation de la part ECS sur une année', 'Excel': 'C92', 'Variable/Formule': 'estimation_ecs_annuel = periode_nb_jours/365'},
    'Est. Chauffage/Chauffage annuel prévisible': {'Valeur': estimation_part_chauffage_periode_sur_annuel(dj_periode, DJ_REF_ANNUELS)*100, 'Unité': '%', 'Commentaire': 'Est. Chauffage/Chauffage annuel prévisible → dj_periode (C101) / DJ_REF_ANNUELS (C102)', 'Excel': 'C93', 'Variable/Formule': 'estimation_part_chauffage_periode_sur_annuel = dj_periode / DJ_REF_ANNUELS'},
    'Est. EF période / EF année': {'Valeur': estimation_energie_finale_periode_sur_annuel(estimation_ecs_annuel,repartition_energie_finale_partie_renovee_ecs,repartition_energie_finale_partie_surelevee_ecs,estimation_part_chauffage_periode_sur_annuel,repartition_energie_finale_partie_renovee_chauffage,repartition_energie_finale_partie_surelevee_chauffage), 'Unité': '%', 'Commentaire': 'Estimation en énergie finale sur la période / énergie finale sur une année', 'Excel': 'C94', 'Variable/Formule': 'estimation_energie_finale_periode_sur_annuel = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) + (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage))'},
    'Est. Part ECS période comptage': {'Valeur': part_ecs_periode_comptage(estimation_ecs_annuel, repartition_energie_finale_partie_renovee_ecs, repartition_energie_finale_partie_surelevee_ecs, estimation_energie_finale_periode_sur_annuel)*100, 'Unité': '%', 'Commentaire': '', 'Excel': 'C95', 'Variable/Formule': 'part_ecs_periode_comptage = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) / estimation_energie_finale_periode_sur_annuel'},
    'Est. Part Chauffage période comptage': {'Valeur': part_chauffage_periode_comptage(estimation_energie_finale_periode_sur_annuel, estimation_part_chauffage_periode_sur_annuel, repartition_energie_finale_partie_renovee_chauffage, repartition_energie_finale_partie_surelevee_chauffage)*100, 'Unité': '%', 'Commentaire': '', 'Excel': 'C96', 'Variable/Formule': 'part_chauffage_periode_comptage = (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage)) / estimation_energie_finale_periode_sur_annuel'},
    'Correction ECS': {'Valeur': correction_ecs(periode_nb_jours), 'Unité': '-', 'Commentaire': '', 'Excel': 'C97', 'Variable/Formule': 'correction_ecs = 365/periode_nb_jours'},
    'Energie finale indiqué par le(s) compteur(s)': {'Valeur': agent_energetique_ef_somme_kwh(agent_energetique_ef_mazout_kg, agent_energetique_ef_mazout_litres, agent_energetique_ef_mazout_kwh, agent_energetique_ef_gaz_naturel_m3, agent_energetique_ef_gaz_naturel_kwh, agent_energetique_ef_bois_buches_dur_stere, agent_energetique_ef_bois_buches_tendre_stere, agent_energetique_ef_bois_buches_tendre_kwh, agent_energetique_ef_pellets_m3, agent_energetique_ef_pellets_kg, agent_energetique_ef_pellets_kwh, agent_energetique_ef_plaquettes_m3, agent_energetique_ef_plaquettes_kwh, agent_energetique_ef_cad_kwh, agent_energetique_ef_electricite_pac_kwh, agent_energetique_ef_electricite_directe_kwh, agent_energetique_ef_autre_kwh), 'Unité': 'kWh', 'Commentaire': '', 'Excel': 'C98', 'Variable/Formule': 'agent_energetique_ef_somme_kwh = (agent_energetique_ef_mazout_somme_mj + agent_energetique_ef_gaz_naturel_somme_mj + agent_energetique_ef_bois_buches_dur_somme_mj + agent_energetique_ef_bois_buches_tendre_somme_mj + agent_energetique_ef_pellets_somme_mj + agent_energetique_ef_plaquettes_somme_mj + agent_energetique_ef_cad_somme_mj + agent_energetique_ef_electricite_pac_somme_mj + agent_energetique_ef_electricite_directe_somme_mj + agent_energetique_ef_autre_somme_mj) / 3.6'}
    





}

# # C65 → Début période
# df_periode_list.append({
#     'Dénomination': 'Début période',
#     'Valeur': periode_start,
#     'Unité': '-',
#     'Commentaire': 'Date de début de la période',
#     'Excel': 'C65',
#     'Variable/Formule' : 'periode_start'})

# # C66 → Fin période
# df_periode_list.append({
#     'Dénomination': 'Fin période',
#     'Valeur': periode_end,
#     'Unité': '-',
#     'Commentaire': 'Date de fin de la période',
#     'Excel': 'C66',
#     'Variable/Formule': 'periode_end'
# })

# # C67 → Nombre de jours
# df_list.append({
#     'Dénomination': 'Nombre de jour(s)',
#     'Valeur': periode_nb_jours,
#     'Unité': 'jour(s)',
#     'Commentaire': 'Nombre de jour(s) dans la période',
#     'Excel': 'C67',
#     'Variable/Formule': 'periode_nb_jours'
# })


# # C86 → Répartition en énergie finale - Chauffage partie rénovée
# df_list.append({
#     'Dénomination': 'Répartition en énergie finale (chauffage) pour la partie rénové',
#     'Valeur': repartition_energie_finale_partie_renovee_chauffage,
#     'Unité': '%',
#     'Commentaire': '',
#     'Excel': 'C86',
#     'Variable/Formule': "repartition_energie_finale_partie_renovee_chauffage"
# })

# # C87 → Répartition en énergie finale - ECS partie rénovée
# df_list.append({
#     'Dénomination': 'Répartition en énergie finale (ECS) pour la partie rénové',
#     'Valeur': repartition_energie_finale_partie_renovee_ecs,
#     'Unité': '%',
#     'Commentaire': '',  # You can add a comment if needed
#     'Excel': 'C87',
#     'Variable/Formule': "repartition_energie_finale_partie_renovee_ecs"
# })

# # C88 → Répartition en énergie finale - Chauffage partie surélévée
# df_list.append({
#     'Dénomination': 'Répartition en énergie finale (chauffage) pour la partie surélévée',
#     'Valeur': repartition_energie_finale_partie_surelevee_chauffage,
#     'Unité': '%',
#     'Commentaire': "0 if no surélévation",  # You can add a comment if needed
#     'Excel': 'C88',
#     'Variable/Formule': "repartition_energie_finale_partie_surelevee_chauffage"
# })

# # C89 → Répartition EF - ECS partie surélévée
# df_list.append({
#     'Dénomination': 'Répartition en énergie finale - ECS partie surélévée',
#     'Valeur': repartition_energie_finale_partie_surelevee_ecs,
#     'Unité': '%',
#     'Commentaire': "Part d'énergie finale (ECS) pour la partie surélévée. 0 s'il n'y a pas de surélévation",
#     'Excel': 'C89',
#     'Variable/Formule': "repartition_energie_finale_partie_surelevee_ecs"
# })

# # C91 → Part EF pour partie rénové (Chauffage + ECS)
# repartition_energie_finale_partie_renovee_somme = repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_renovee_ecs
# df_list.append({
#     'Dénomination': 'Part EF pour partie rénové (Chauffage + ECS)',
#     'Valeur': repartition_energie_finale_partie_renovee_somme(repartition_energie_finale_partie_renovee_chauffage, repartition_energie_finale_partie_renovee_ecs),
#     'Unité': '%',
#     'Commentaire': "Part d'énergie finale (Chauffage + ECS) pour la partie rénové. 100% si pas de surélévation",
#     'Excel': 'C91',
#     'Variable/Formule': "repartition_energie_finale_partie_renovee_somme = repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_renovee_ecs"
# })

# # C92 → Est. ECS/ECS annuelle
# # estimation_ecs_annuel = periode_nb_jours/365
# df_list.append({
#     'Dénomination': 'Est. ECS/ECS annuelle',
#     'Valeur': estimation_ecs_annuel(periode_nb_jours),
#     'Unité': '-',
#     'Commentaire': 'Estimation de la part ECS sur une année',
#     'Excel': 'C92',
#     'Variable/Formule': 'estimation_ecs_annuel = periode_nb_jours/365'
# })

# # C93 → Est. Chauffage/Chauffage annuel prévisible
# dj_periode = calcul_dj_periode(df_meteo_tre200d0, periode_start, periode_end)
# dj_periode = float(dj_periode)
# estimation_part_chauffage_periode_sur_annuel = dj_periode / DJ_REF_ANNUELS
# estimation_part_chauffage_periode_sur_annuel = float(estimation_part_chauffage_periode_sur_annuel)
# df_list.append({
#     'Dénomination': 'Est. Chauffage/Chauffage annuel prévisible',
#     'Valeur': estimation_part_chauffage_periode_sur_annuel(dj_periode, DJ_REF_ANNUELS)*100,
#     'Unité': '%',
#     'Commentaire': 'Est. Chauffage/Chauffage annuel prévisible → dj_periode (C101) / DJ_REF_ANNUELS (C102)',
#     'Excel': 'C93',
#     'Variable/Formule': 'estimation_part_chauffage_periode_sur_annuel = dj_periode / DJ_REF_ANNUELS'
# })

# # C94 → Est. EF période / EF année
# estimation_energie_finale_periode_sur_annuel = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) +\
#                                     (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage))
# df_list.append({
#     'Dénomination': 'Est. EF période / EF année',
#     'Valeur': estimation_energie_finale_periode_sur_annuel(estimation_ecs_annuel,repartition_energie_finale_partie_renovee_ecs,repartition_energie_finale_partie_surelevee_ecs,estimation_part_chauffage_periode_sur_annuel,repartition_energie_finale_partie_renovee_chauffage,repartition_energie_finale_partie_surelevee_chauffage),
#     'Unité': '%',
#     'Commentaire': 'Estimation en énergie finale sur la période / énergie finale sur une année',
#     'Excel': 'C94',
#     'Variable/Formule': 'estimation_energie_finale_periode_sur_annuel = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) + (estimation_part_chauffage_periode_sur_annuel * (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage))'
# })

# # C95 → Est. Part ECS période comptage
# try:
#     if estimation_energie_finale_periode_sur_annuel != 0:
#         part_ecs_periode_comptage = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + \
#             repartition_energie_finale_partie_surelevee_ecs)) / estimation_energie_finale_periode_sur_annuel
#     else:
#         part_ecs_periode_comptage = 0.0
# except ZeroDivisionError:
#     part_ecs_periode_comptage = 0.0
# df_list.append({
#     'Dénomination': 'Est. Part ECS période comptage',
#     'Valeur': part_ecs_periode_comptage(estimation_ecs_annuel, repartition_energie_finale_partie_renovee_ecs, repartition_energie_finale_partie_surelevee_ecs, estimation_energie_finale_periode_sur_annuel)*100,
#     'Unité': '%',
#     'Commentaire': '',
#     'Excel': 'C95',
#     'Variable/Formule': 'part_ecs_periode_comptage = (estimation_ecs_annuel * (repartition_energie_finale_partie_renovee_ecs + repartition_energie_finale_partie_surelevee_ecs)) / estimation_energie_finale_periode_sur_annuel'
# })

# # C96 → Est. Part Chauffage période comptage
# try:
#     if estimation_energie_finale_periode_sur_annuel != 0:
#         part_chauffage_periode_comptage = (estimation_part_chauffage_periode_sur_annuel * \
#             (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage)) / estimation_energie_finale_periode_sur_annuel
#     else:
#         part_chauffage_periode_comptage = 0.0
# except ZeroDivisionError:
#     part_chauffage_periode_comptage = 0.0
# df_list.append({
#     'Dénomination': 'Est. Part Chauffage période comptage',
#     'Valeur': part_chauffage_periode_comptage(estimation_energie_finale_periode_sur_annuel, estimation_part_chauffage_periode_sur_annuel, repartition_energie_finale_partie_renovee_chauffage, repartition_energie_finale_partie_surelevee_chauffage)*100,
#     'Unité': '%',
#     'Commentaire': '',
#     'Excel': 'C96',
#     'Variable/Formule': 'part_chauffage_periode_comptage = (estimation_part_chauffage_periode_sur_annuel * \
#     (repartition_energie_finale_partie_renovee_chauffage + repartition_energie_finale_partie_surelevee_chauffage)) / estimation_energie_finale_periode_sur_annuel'
# })

# # C97 → correction ECS = 365/nb jour comptage
# correction_ecs = 365/periode_nb_jours
# df_list.append({
#     'Dénomination': 'Correction ECS',
#     'Valeur': correction_ecs(periode_nb_jours),
#     'Unité': '-',
#     'Commentaire': '',
#     'Excel': 'C97',
#     'Variable/Formule': 'correction_ecs = 365/periode_nb_jours'
# })

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
    'Valeur': agent_energetique_ef_somme_kwh(agent_energetique_ef_mazout_kg, agent_energetique_ef_mazout_litres, agent_energetique_ef_mazout_kwh, agent_energetique_ef_gaz_naturel_m3, agent_energetique_ef_gaz_naturel_kwh, agent_energetique_ef_bois_buches_dur_stere, agent_energetique_ef_bois_buches_tendre_stere, agent_energetique_ef_bois_buches_tendre_kwh, agent_energetique_ef_pellets_m3, agent_energetique_ef_pellets_kg, agent_energetique_ef_pellets_kwh, agent_energetique_ef_plaquettes_m3, agent_energetique_ef_plaquettes_kwh, agent_energetique_ef_cad_kwh, agent_energetique_ef_electricite_pac_kwh, agent_energetique_ef_electricite_directe_kwh, agent_energetique_ef_autre_kwh),
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
