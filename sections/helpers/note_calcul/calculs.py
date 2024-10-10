# sections/helpers/note_calcul/calculs.py


# C91 → Part EF pour partie rénové (Chauffage + ECS)
def fonction_repartition_energie_finale_partie_renovee_somme(
    repartition_energie_finale_partie_renovee_chauffage,
    repartition_energie_finale_partie_renovee_ecs,
):
    repartition_energie_finale_partie_renovee_somme = (
        repartition_energie_finale_partie_renovee_chauffage
        + repartition_energie_finale_partie_renovee_ecs
    )
    return repartition_energie_finale_partie_renovee_somme


# C92 → Est. ECS/ECS annuelle
def fonction_estimation_ecs_annuel(periode_nb_jours):
    estimation_ecs_annuel = periode_nb_jours / 365
    return estimation_ecs_annuel


# C93 → Est. Chauffage/Chauffage annuel prévisible
def fonction_estimation_part_chauffage_periode_sur_annuel(dj_periode, DJ_REF_ANNUELS):
    try:
        if dj_periode > 0 and DJ_REF_ANNUELS > 0:
            estimation_part_chauffage_periode_sur_annuel = float(
                dj_periode / DJ_REF_ANNUELS
            )
        else:
            estimation_part_chauffage_periode_sur_annuel = 0.0
    except:
        estimation_part_chauffage_periode_sur_annuel = 0.0
    return estimation_part_chauffage_periode_sur_annuel


# C94 → Est. EF période / EF année
def fonction_estimation_energie_finale_periode_sur_annuel(
    estimation_ecs_annuel,
    repartition_energie_finale_partie_renovee_ecs,
    repartition_energie_finale_partie_surelevee_ecs,
    estimation_part_chauffage_periode_sur_annuel,
    repartition_energie_finale_partie_renovee_chauffage,
    repartition_energie_finale_partie_surelevee_chauffage,
):
    estimation_energie_finale_periode_sur_annuel = (
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
    return estimation_energie_finale_periode_sur_annuel


# C95 → Est. Part ECS période comptage
def fonction_part_ecs_periode_comptage(
    estimation_energie_finale_periode_sur_annuel,
    estimation_ecs_annuel,
    repartition_energie_finale_partie_renovee_ecs,
    repartition_energie_finale_partie_surelevee_ecs,
):
    try:
        if estimation_energie_finale_periode_sur_annuel != 0:
            part_ecs_periode_comptage = (
                estimation_ecs_annuel
                * (
                    repartition_energie_finale_partie_renovee_ecs
                    + repartition_energie_finale_partie_surelevee_ecs
                )
            ) / estimation_energie_finale_periode_sur_annuel
        else:
            part_ecs_periode_comptage = 0.0
    except:
        part_ecs_periode_comptage = 0.0
    return part_ecs_periode_comptage


# C96 → Est. Part Chauffage période comptage
def fonction_part_chauffage_periode_comptage(
    estimation_energie_finale_periode_sur_annuel,
    estimation_part_chauffage_periode_sur_annuel,
    repartition_energie_finale_partie_renovee_chauffage,
    repartition_energie_finale_partie_surelevee_chauffage,
):
    try:
        if estimation_energie_finale_periode_sur_annuel != 0:
            part_chauffage_periode_comptage = (
                estimation_part_chauffage_periode_sur_annuel
                * (
                    repartition_energie_finale_partie_renovee_chauffage
                    + repartition_energie_finale_partie_surelevee_chauffage
                )
            ) / estimation_energie_finale_periode_sur_annuel
        else:
            part_chauffage_periode_comptage = 0.0
    except:
        part_chauffage_periode_comptage = 0.0
    return part_chauffage_periode_comptage


# C97 → correction ECS = 365/nb jour comptage
def fonction_correction_ecs(periode_nb_jours):
    try:
        if periode_nb_jours != 0:
            correction_ecs = 365 / periode_nb_jours
        else:
            correction_ecs = 0.0
    except:
        correction_ecs = 0.0
    return correction_ecs


# C98 → Energie finale indiqué par le(s) compteur(s)
def fonction_agent_energetique_ef_mazout_somme_mj(
    agent_energetique_ef_mazout_kg,
    agent_energetique_ef_mazout_litres,
    agent_energetique_ef_mazout_kwh,
    CONVERSION_MAZOUT_MJ_KG,
    CONVERSION_MAZOUT_MJ_LITRES,
    CONVERSION_MAZOUT_MJ_KWH,
):
    try:
        if (
            agent_energetique_ef_mazout_kg >= 0
            and agent_energetique_ef_mazout_litres >= 0
            and agent_energetique_ef_mazout_kwh >= 0
        ):
            agent_energetique_ef_mazout_somme_mj = (
                agent_energetique_ef_mazout_kg * CONVERSION_MAZOUT_MJ_KG
                + agent_energetique_ef_mazout_litres * CONVERSION_MAZOUT_MJ_LITRES
                + agent_energetique_ef_mazout_kwh * CONVERSION_MAZOUT_MJ_KWH
            )
        else:
            agent_energetique_ef_mazout_somme_mj = 0.0
    except:
        agent_energetique_ef_mazout_somme_mj = 0.0
    return agent_energetique_ef_mazout_somme_mj


def fonction_agent_energetique_ef_gaz_naturel_somme_mj(
    agent_energetique_ef_gaz_naturel_m3,
    agent_energetique_ef_gaz_naturel_kwh,
    CONVERSION_GAZ_NATUREL_MJ_M3,
    CONVERSION_GAZ_NATUREL_MJ_KWH,
):
    try:
        if (
            agent_energetique_ef_gaz_naturel_m3 >= 0
            and agent_energetique_ef_gaz_naturel_kwh >= 0
        ):
            agent_energetique_ef_gaz_naturel_somme_mj = (
                agent_energetique_ef_gaz_naturel_m3 * CONVERSION_GAZ_NATUREL_MJ_M3
                + agent_energetique_ef_gaz_naturel_kwh * CONVERSION_GAZ_NATUREL_MJ_KWH
            )
        else:
            agent_energetique_ef_gaz_naturel_somme_mj = 0.0
    except:
        agent_energetique_ef_gaz_naturel_somme_mj = 0.0
    return agent_energetique_ef_gaz_naturel_somme_mj


def fonction_agent_energetique_ef_bois_buches_dur_somme_mj(
    agent_energetique_ef_bois_buches_dur_stere,
    CONVERSION_BOIS_BUCHES_DUR_MJ_STERE,
):
    try:
        if agent_energetique_ef_bois_buches_dur_stere >= 0:
            agent_energetique_ef_bois_buches_dur_somme_mj = (
                agent_energetique_ef_bois_buches_dur_stere
                * CONVERSION_BOIS_BUCHES_DUR_MJ_STERE
            )
        else:
            agent_energetique_ef_bois_buches_dur_somme_mj = 0.0
    except:
        agent_energetique_ef_bois_buches_dur_somme_mj = 0.0
    return agent_energetique_ef_bois_buches_dur_somme_mj


def fonction_agent_energetique_ef_bois_buches_tendre_somme_mj(
    agent_energetique_ef_bois_buches_tendre_stere,
    agent_energetique_ef_bois_buches_tendre_kwh,
    CONVERSION_BOIS_BUCHES_TENDRE_MJ_STERE,
    CONVERSION_BOIS_BUCHES_TENDRE_MJ_KWH,
):

    try:
        if (
            agent_energetique_ef_bois_buches_tendre_stere >= 0
            and agent_energetique_ef_bois_buches_tendre_kwh >= 0
        ):
            agent_energetique_ef_bois_buches_tendre_somme_mj = (
                agent_energetique_ef_bois_buches_tendre_stere
                * CONVERSION_BOIS_BUCHES_TENDRE_MJ_STERE
                + agent_energetique_ef_bois_buches_tendre_kwh
                * CONVERSION_BOIS_BUCHES_TENDRE_MJ_KWH
            )
        else:
            agent_energetique_ef_bois_buches_tendre_somme_mj = 0.0
    except:
        agent_energetique_ef_bois_buches_tendre_somme_mj = 0.0
    return agent_energetique_ef_bois_buches_tendre_somme_mj


def fonction_agent_energetique_ef_pellets_somme_mj(
    agent_energetique_ef_pellets_m3,
    agent_energetique_ef_pellets_kg,
    agent_energetique_ef_pellets_kwh,
    CONVERSION_PELLETS_MJ_M3,
    CONVERSION_PELLETS_MJ_KG,
    CONVERSION_PELLETS_MJ_KWH,
):
    try:
        if (
            agent_energetique_ef_pellets_m3 >= 0
            and agent_energetique_ef_pellets_kg >= 0
            and agent_energetique_ef_pellets_kwh >= 0
        ):
            agent_energetique_ef_pellets_somme_mj = (
                agent_energetique_ef_pellets_m3 * CONVERSION_PELLETS_MJ_M3
                + agent_energetique_ef_pellets_kg * CONVERSION_PELLETS_MJ_KG
                + agent_energetique_ef_pellets_kwh * CONVERSION_PELLETS_MJ_KWH
            )
        else:
            agent_energetique_ef_pellets_somme_mj = 0.0
    except:
        agent_energetique_ef_pellets_somme_mj = 0.0
    return agent_energetique_ef_pellets_somme_mj


def fonction_agent_energetique_ef_plaquettes_somme_mj(
    agent_energetique_ef_plaquettes_m3,
    agent_energetique_ef_plaquettes_kwh,
    CONVERSION_PLAQUETTES_MJ_M3,
    CONVERSION_PLAQUETTES_MJ_KWH,
):
    try:
        if (
            agent_energetique_ef_plaquettes_m3 >= 0
            and agent_energetique_ef_plaquettes_kwh >= 0
        ):
            agent_energetique_ef_plaquettes_somme_mj = (
                agent_energetique_ef_plaquettes_m3 * CONVERSION_PLAQUETTES_MJ_M3
                + agent_energetique_ef_plaquettes_kwh * CONVERSION_PLAQUETTES_MJ_KWH
            )
        else:
            agent_energetique_ef_plaquettes_somme_mj = 0.0
    except:
        agent_energetique_ef_plaquettes_somme_mj = 0.0
    return agent_energetique_ef_plaquettes_somme_mj


def fonction_agent_energetique_ef_cad_somme_mj(
    agent_energetique_ef_cad_kwh,
    CONVERSION_CAD_MJ_KWH,
):
    try:
        if agent_energetique_ef_cad_kwh >= 0:
            agent_energetique_ef_cad_somme_mj = (
                agent_energetique_ef_cad_kwh * CONVERSION_CAD_MJ_KWH
            )
        else:
            agent_energetique_ef_cad_somme_mj = 0.0
    except:
        agent_energetique_ef_cad_somme_mj = 0.0
    return agent_energetique_ef_cad_somme_mj


def fonction_agent_energetique_ef_electricite_pac_somme_mj(
    agent_energetique_ef_electricite_pac_kwh,
    CONVERSION_ELECTRICITE_PAC_MJ_KWH,
):
    try:
        if agent_energetique_ef_electricite_pac_kwh >= 0:
            agent_energetique_ef_electricite_pac_somme_mj = (
                agent_energetique_ef_electricite_pac_kwh
                * CONVERSION_ELECTRICITE_PAC_MJ_KWH
            )
        else:
            agent_energetique_ef_electricite_pac_somme_mj = 0.0
    except:
        agent_energetique_ef_electricite_pac_somme_mj = 0.0
    return agent_energetique_ef_electricite_pac_somme_mj


def fonction_agent_energetique_ef_electricite_directe_somme_mj(
    agent_energetique_ef_electricite_directe_kwh,
    CONVERSION_ELECTRICITE_DIRECTE_MJ_KWH,
):
    try:
        if agent_energetique_ef_electricite_directe_kwh >= 0:
            agent_energetique_ef_electricite_directe_somme_mj = (
                agent_energetique_ef_electricite_directe_kwh
                * CONVERSION_ELECTRICITE_DIRECTE_MJ_KWH
            )
        else:
            agent_energetique_ef_electricite_directe_somme_mj = 0.0
    except:
        agent_energetique_ef_electricite_directe_somme_mj = 0.0
    return agent_energetique_ef_electricite_directe_somme_mj


def fonction_agent_energetique_ef_autre_somme_mj(
    agent_energetique_ef_autre_kwh,
    CONVERSION_AUTRE_MJ_KWH,
):
    try:
        if agent_energetique_ef_autre_kwh >= 0:
            agent_energetique_ef_autre_somme_mj = (
                agent_energetique_ef_autre_kwh * CONVERSION_AUTRE_MJ_KWH
            )
        else:
            agent_energetique_ef_autre_somme_mj = 0.0
    except:
        agent_energetique_ef_autre_somme_mj = 0.0
    return agent_energetique_ef_autre_somme_mj


def fonction_agent_energetique_ef_somme_kwh(
    agent_energetique_ef_mazout_somme_mj,
    agent_energetique_ef_gaz_naturel_somme_mj,
    agent_energetique_ef_bois_buches_dur_somme_mj,
    agent_energetique_ef_bois_buches_tendre_somme_mj,
    agent_energetique_ef_pellets_somme_mj,
    agent_energetique_ef_plaquettes_somme_mj,
    agent_energetique_ef_cad_somme_mj,
    agent_energetique_ef_electricite_pac_somme_mj,
    agent_energetique_ef_electricite_directe_somme_mj,
    agent_energetique_ef_autre_somme_mj,
):
    try:
        if (
            agent_energetique_ef_mazout_somme_mj >= 0
            and agent_energetique_ef_gaz_naturel_somme_mj >= 0
            and agent_energetique_ef_bois_buches_dur_somme_mj >= 0
            and agent_energetique_ef_bois_buches_tendre_somme_mj >= 0
            and agent_energetique_ef_pellets_somme_mj >= 0
            and agent_energetique_ef_plaquettes_somme_mj >= 0
            and agent_energetique_ef_cad_somme_mj >= 0
            and agent_energetique_ef_electricite_pac_somme_mj >= 0
            and agent_energetique_ef_electricite_directe_somme_mj >= 0
            and agent_energetique_ef_autre_somme_mj >= 0
        ):
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
        else:
            agent_energetique_ef_somme_kwh = 0.0
    except:
        agent_energetique_ef_somme_kwh = 0.0
    return agent_energetique_ef_somme_kwh


# C99 → Methodo_Bww → Part de ECS en énergie finale sur la période
def fonction_methodo_b_ww_kwh(
    agent_energetique_ef_somme_kwh, part_ecs_periode_comptage
):
    try:
        if agent_energetique_ef_somme_kwh >= 0 and part_ecs_periode_comptage >= 0:
            methodo_b_ww_kwh = (
                agent_energetique_ef_somme_kwh * part_ecs_periode_comptage
            )
        else:
            methodo_b_ww_kwh = 0.0
    except:
        methodo_b_ww_kwh = 0.0
    return methodo_b_ww_kwh


# C100 → Methodo_Eww
def fonction_methodo_e_ww_kwh(methodo_b_ww_kwh, sre_renovation_m2, periode_nb_jours):
    try:
        if sre_renovation_m2 != 0 and periode_nb_jours != 0:
            methodo_e_ww_kwh = (methodo_b_ww_kwh / sre_renovation_m2) * (
                365 / periode_nb_jours
            )
        else:
            methodo_e_ww_kwh = 0.0
    except:
        methodo_e_ww_kwh = 0.0
    return methodo_e_ww_kwh


# C103 → Methodo_Bh → Part de chauffage en énergie finale sur la période
def fonction_methodo_b_h_kwh(
    agent_energetique_ef_somme_kwh, part_chauffage_periode_comptage
):
    try:
        if agent_energetique_ef_somme_kwh and part_chauffage_periode_comptage:
            methodo_b_h_kwh = (
                agent_energetique_ef_somme_kwh * part_chauffage_periode_comptage
            )
        else:
            methodo_b_h_kwh = 0.0
    except:
        methodo_b_h_kwh = 0.0
    return methodo_b_h_kwh


# C104 → Methodo_Eh
def fonction_methodo_e_h_kwh(
    sre_renovation_m2, dj_periode, methodo_b_h_kwh, DJ_REF_ANNUELS
):
    try:
        if sre_renovation_m2 != 0 and dj_periode != 0:
            methodo_e_h_kwh = (methodo_b_h_kwh / sre_renovation_m2) * (
                DJ_REF_ANNUELS / dj_periode
            )
        else:
            methodo_e_h_kwh = 0.0
    except:
        methodo_e_h_kwh = 0.0
    return methodo_e_h_kwh


# C105 → Ef,après,corr → Methodo_Eww + Methodo_Eh
def fonction_energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2(
    methodo_e_ww_kwh, methodo_e_h_kwh
):
    try:
        if methodo_e_ww_kwh >= 0 and methodo_e_h_kwh >= 0:
            energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 = (
                methodo_e_ww_kwh + methodo_e_h_kwh
            )
        else:
            energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 = (
                0.0
            )
    except:
        energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2 = (
            0.0
        )
    return (
        energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2
    )


# C107 → Ef,après,corr,rénové →Total en énergie finale (Eww+Eh) pour la partie rénovée
def fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2(
    energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2,
    repartition_energie_finale_partie_renovee_somme,
):
    energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 = (
        energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2
        * (repartition_energie_finale_partie_renovee_somme / 100)
    )
    return energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2


# C108 → fp → facteur de pondération moyen
def fonction_facteur_ponderation_moyen(
    agent_energetique_ef_mazout_somme_mj,
    agent_energetique_ef_gaz_naturel_somme_mj,
    agent_energetique_ef_bois_buches_dur_somme_mj,
    agent_energetique_ef_bois_buches_tendre_somme_mj,
    agent_energetique_ef_pellets_somme_mj,
    agent_energetique_ef_plaquettes_somme_mj,
    agent_energetique_ef_cad_somme_mj,
    agent_energetique_ef_electricite_pac_somme_mj,
    agent_energetique_ef_electricite_directe_somme_mj,
    agent_energetique_ef_autre_somme_mj,
    agent_energetique_ef_somme_kwh,
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
):
    try:
        if agent_energetique_ef_somme_kwh:
            facteur_ponderation_moyen = (
                agent_energetique_ef_mazout_somme_mj * FACTEUR_PONDERATION_MAZOUT
                + agent_energetique_ef_gaz_naturel_somme_mj
                * FACTEUR_PONDERATION_GAZ_NATUREL
                + agent_energetique_ef_bois_buches_dur_somme_mj
                * FACTEUR_PONDERATION_BOIS_BUCHES_DUR
                + agent_energetique_ef_bois_buches_tendre_somme_mj
                * FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE
                + agent_energetique_ef_pellets_somme_mj * FACTEUR_PONDERATION_PELLETS
                + agent_energetique_ef_plaquettes_somme_mj
                * FACTEUR_PONDERATION_PLAQUETTES
                + agent_energetique_ef_cad_somme_mj * FACTEUR_PONDERATION_CAD
                + agent_energetique_ef_electricite_pac_somme_mj
                * FACTEUR_PONDERATION_ELECTRICITE_PAC
                + agent_energetique_ef_electricite_directe_somme_mj
                * FACTEUR_PONDERATION_ELECTRICITE_DIRECTE
                + agent_energetique_ef_autre_somme_mj * FACTEUR_PONDERATION_AUTRE
            ) / (agent_energetique_ef_somme_kwh * 3.6)
        else:
            facteur_ponderation_moyen = 0
    except ZeroDivisionError:
        facteur_ponderation_moyen = 0
    return facteur_ponderation_moyen


# C109 → Methodo_Eww*fp
def fonction_methodo_e_ww_renovee_pondere_kwh_m2(
    methodo_e_ww_kwh,
    facteur_ponderation_moyen,
    repartition_energie_finale_partie_renovee_somme,
):
    try:
        if (
            methodo_e_ww_kwh >= 0
            and facteur_ponderation_moyen >= 0
            and repartition_energie_finale_partie_renovee_somme >= 0
        ):
            methodo_e_ww_renovee_pondere_kwh_m2 = (
                methodo_e_ww_kwh
                * facteur_ponderation_moyen
                * (repartition_energie_finale_partie_renovee_somme / 100)
            )
        else:
            methodo_e_ww_renovee_pondere_kwh_m2 = 0
    except:
        methodo_e_ww_renovee_pondere_kwh_m2 = 0
    return methodo_e_ww_renovee_pondere_kwh_m2


# C110 → Methodo_Eh*fp
def fonction_methodo_e_h_renovee_pondere_kwh_m2(
    methodo_e_h_kwh,
    facteur_ponderation_moyen,
    repartition_energie_finale_partie_renovee_somme,
):
    try:
        if (
            methodo_e_h_kwh >= 0
            and facteur_ponderation_moyen >= 0
            and repartition_energie_finale_partie_renovee_somme >= 0
        ):
            methodo_e_h_renovee_pondere_kwh_m2 = (
                methodo_e_h_kwh
                * facteur_ponderation_moyen
                * (repartition_energie_finale_partie_renovee_somme / 100)
            )
        else:
            methodo_e_h_renovee_pondere_kwh_m2 = 0
    except:
        methodo_e_h_renovee_pondere_kwh_m2 = 0
    return methodo_e_h_renovee_pondere_kwh_m2


# C113 → Ef,après,corr,rénové*fp
def fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2(
    energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2,
    facteur_ponderation_moyen,
):
    try:
        if (
            energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2 >= 0
            and facteur_ponderation_moyen >= 0
        ):
            energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 = (
                energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2
                * facteur_ponderation_moyen
            )
        else:
            energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 = (
                0
            )
    except:
        energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 = 0
    return energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2


# C114 → Ef,après,corr,rénové*fp
def fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2(
    energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
):
    try:
        if (
            energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
            >= 0
        ):
            energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2 = (
                energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
                * 3.6
            )
        else:
            energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2 = (
                0
            )
    except:
        energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2 = 0
    return energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2


# atteinte objectifs
def fonction_delta_ef_realisee_kwh_m2(
    ef_avant_corr_kwh_m2,
    energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
):
    try:
        if (
            ef_avant_corr_kwh_m2 > 0
            and energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
            > 0
        ):
            delta_ef_realisee_kwh_m2 = (
                ef_avant_corr_kwh_m2
                - energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
            )
        else:
            delta_ef_realisee_kwh_m2 = 0.0
    except:
        delta_ef_realisee_kwh_m2 = 0.0
    return delta_ef_realisee_kwh_m2


def fonction_delta_ef_visee_kwh_m2(ef_avant_corr_kwh_m2, ef_objectif_pondere_kwh_m2):
    try:
        if ef_avant_corr_kwh_m2 > 0 and ef_objectif_pondere_kwh_m2 > 0:
            delta_ef_visee_kwh_m2 = ef_avant_corr_kwh_m2 - ef_objectif_pondere_kwh_m2
        else:
            delta_ef_visee_kwh_m2 = 0.0
    except:
        delta_ef_visee_kwh_m2 = 0.0
    return delta_ef_visee_kwh_m2


def fonction_atteinte_objectif(
    delta_ef_realisee_kwh_m2,
    energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
    delta_ef_visee_kwh_m2,
):
    try:
        if (
            energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
            != 0
        ):
            atteinte_objectif = delta_ef_realisee_kwh_m2 / delta_ef_visee_kwh_m2
        else:
            atteinte_objectif = 0.0
    except:
        atteinte_objectif = 0.0

    return atteinte_objectif
