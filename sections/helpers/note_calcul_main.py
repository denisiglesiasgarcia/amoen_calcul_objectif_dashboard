# sections/note_calcul.py

import pandas as pd

from sections.helpers.note_calcul.create_dataframe_periode_list import (
    make_dataframe_df_periode_list,
)

from sections.helpers.note_calcul.create_dataframe_list import make_dataframe_df_list

from sections.helpers.note_calcul.create_dataframe_agent_energetique import (
    make_dataframe_df_agent_energetique,
)

from sections.helpers.note_calcul.create_dataframe_meteo import (
    make_dataframe_df_meteo_note_calcul,
)

from sections.helpers.calcul_dj import (
    calcul_dj_periode,
    DJ_REF_ANNUELS,
    DJ_TEMPERATURE_REFERENCE,
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
    fonction_methodo_e_ww_kwh,
    fonction_methodo_b_h_kwh,
    fonction_methodo_e_h_kwh,
    fonction_energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2,
    fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2,
    fonction_facteur_ponderation_moyen,
    fonction_methodo_e_ww_renovee_pondere_kwh_m2,
    fonction_methodo_e_h_renovee_pondere_kwh_m2,
    fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
    fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2,
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
)

from sections.helpers.note_calcul.latex import (
    make_latex_formula_facteur_ponderation_moyen_texte,
    make_latex_formula_facteur_ponderation_moyen,
)

def fonction_note_calcul(data_site, df_meteo_tre200d0):
    """
    déjà calculé dans data_site:
    - data_site["periode_start"]
    - data_site["periode_end"]
    - data_site["periode_nb_jours"]
    - data_site["repartition_energie_finale_partie_renovee_chauffage"]
    - data_site["repartition_energie_finale_partie_renovee_ecs"]
    - data_site["repartition_energie_finale_partie_surelevee_chauffage"]
    - data_site["repartition_energie_finale_partie_surelevee_ecs"]
    - data_site["repartition_energie_finale_partie_renovee_ecs"],
    - data_site["repartition_energie_finale_partie_surelevee_ecs"],
    - data_site["repartition_energie_finale_partie_renovee_chauffage"],
    - data_site["repartition_energie_finale_partie_surelevee_chauffage"],

    Calculs réalisés ici:
    - data_site["dj_periode"]
    - data_site["repartition_energie_finale_partie_renovee_somme"]
    - data_site["estimation_ecs_annuel"]
    - data_site["estimation_part_chauffage_periode_sur_annuel"]
    - data_site["part_ecs_periode_comptage"]
    - data_site["part_chauffage_periode_comptage"]
    - data_site["correction_ecs"]
    - data_site["agent_energetique_ef_mazout_somme_mj"]
    - data_site["agent_energetique_ef_gaz_naturel_somme_mj"]
    - data_site["agent_energetique_ef_bois_buches_dur_somme_mj"]
    - data_site["agent_energetique_ef_bois_buches_tendre_somme_mj"]
    - data_site["agent_energetique_ef_pellets_somme_mj"]
    - data_site["agent_energetique_ef_plaquettes_somme_mj"]
    - data_site["agent_energetique_ef_cad_somme_mj"]
    - data_site["agent_energetique_ef_electricite_pac_somme_mj"]
    - data_site["agent_energetique_ef_electricite_directe_somme_mj"]
    - data_site["agent_energetique_ef_autre_somme_mj"]
    - data_site["agent_energetique_ef_somme_kwh"]
    - data_site["methodo_b_ww_kwh"]
    - data_site["methodo_e_ww_kwh"]
    - data_site["methodo_b_h_kwh"]
    - data_site["methodo_e_h_kwh"]
    - data_site["energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2"]
    - data_site["energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2"]
    - data_site["facteur_ponderation_moyen"]
    - data_site["methodo_e_ww_renovee_pondere_kwh_m2"]
    - data_site["methodo_e_h_renovee_pondere_kwh_m2"]
    - data_site["energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"]
    - data_site["energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2"]

    éléments créés:
    - df_periode_list (dataframe des periodes considérées)
    - df_list (dataframe avec la pluspart des données)
    - df_agent_energetique (dataframe des agents énergétiques et facteur de pondération)
    - df_meteo_note_calcul (dataframe météo utilisée pour le calcul)
    - formule_facteur_ponderation_moyen_texte (latex texte formule du facteur de pondération moyen)
    - formule_facteur_ponderation_moyen (latex formule résolue numériquement du facteur de pondération moyen)

    """

    # df_periode_list
    df_periode_list = make_dataframe_df_periode_list(
        data_site["periode_start"], data_site["periode_end"]
    )

    # df_list
    # calculs préalables
    data_site["dj_periode"] = calcul_dj_periode(
        df_meteo_tre200d0,
        data_site["periode_start"],
        data_site["periode_end"],
    )
    data_site["repartition_energie_finale_partie_renovee_somme"] = (
        fonction_repartition_energie_finale_partie_renovee_somme(
            data_site["repartition_energie_finale_partie_renovee_chauffage"],
            data_site["repartition_energie_finale_partie_renovee_ecs"],
        )
    )
    data_site["estimation_ecs_annuel"] = fonction_estimation_ecs_annuel(
        data_site["periode_nb_jours"]
    )
    data_site["estimation_part_chauffage_periode_sur_annuel"] = (
        fonction_estimation_part_chauffage_periode_sur_annuel(
            data_site["dj_periode"], DJ_REF_ANNUELS
        )
    )
    data_site["estimation_energie_finale_periode_sur_annuel"] = (
        fonction_estimation_energie_finale_periode_sur_annuel(
            data_site["estimation_ecs_annuel"],
            data_site["repartition_energie_finale_partie_renovee_ecs"],
            data_site["repartition_energie_finale_partie_surelevee_ecs"],
            data_site["estimation_part_chauffage_periode_sur_annuel"],
            data_site["repartition_energie_finale_partie_renovee_chauffage"],
            data_site["repartition_energie_finale_partie_surelevee_chauffage"],
        )
    )
    data_site["part_ecs_periode_comptage"] = fonction_part_ecs_periode_comptage(
        data_site["estimation_energie_finale_periode_sur_annuel"],
        data_site["estimation_ecs_annuel"],
        data_site["repartition_energie_finale_partie_renovee_ecs"],
        data_site["repartition_energie_finale_partie_surelevee_ecs"],
    )
    data_site["part_chauffage_periode_comptage"] = (
        fonction_part_chauffage_periode_comptage(
            data_site["estimation_energie_finale_periode_sur_annuel"],
            data_site["estimation_part_chauffage_periode_sur_annuel"],
            data_site["repartition_energie_finale_partie_renovee_chauffage"],
            data_site["repartition_energie_finale_partie_surelevee_chauffage"],
        )
    )
    data_site["correction_ecs"] = fonction_correction_ecs(data_site["periode_nb_jours"])
    data_site["agent_energetique_ef_mazout_somme_mj"] = (
        fonction_agent_energetique_ef_mazout_somme_mj(
            data_site["agent_energetique_ef_mazout_kg"],
            data_site["agent_energetique_ef_mazout_litres"],
            data_site["agent_energetique_ef_mazout_kwh"],
            CONVERSION_MAZOUT_MJ_KG,
            CONVERSION_MAZOUT_MJ_LITRES,
            CONVERSION_MAZOUT_MJ_KWH,
        )
    )
    data_site["agent_energetique_ef_gaz_naturel_somme_mj"] = (
        fonction_agent_energetique_ef_gaz_naturel_somme_mj(
            data_site["agent_energetique_ef_gaz_naturel_m3"],
            data_site["agent_energetique_ef_gaz_naturel_kwh"],
            CONVERSION_GAZ_NATUREL_MJ_M3,
            CONVERSION_GAZ_NATUREL_MJ_KWH,
        )
    )
    data_site["agent_energetique_ef_bois_buches_dur_somme_mj"] = (
        fonction_agent_energetique_ef_bois_buches_dur_somme_mj(
            data_site["agent_energetique_ef_bois_buches_dur_stere"],
            CONVERSION_BOIS_BUCHES_DUR_MJ_STERE,
        )
    )
    data_site["agent_energetique_ef_bois_buches_tendre_somme_mj"] = (
        fonction_agent_energetique_ef_bois_buches_tendre_somme_mj(
            data_site["agent_energetique_ef_bois_buches_tendre_stere"],
            data_site["agent_energetique_ef_bois_buches_tendre_kwh"],
            CONVERSION_BOIS_BUCHES_TENDRE_MJ_STERE,
            CONVERSION_BOIS_BUCHES_TENDRE_MJ_KWH,
        )
    )
    data_site["agent_energetique_ef_pellets_somme_mj"] = (
        fonction_agent_energetique_ef_pellets_somme_mj(
            data_site["agent_energetique_ef_pellets_m3"],
            data_site["agent_energetique_ef_pellets_kg"],
            data_site["agent_energetique_ef_pellets_kwh"],
            CONVERSION_PELLETS_MJ_M3,
            CONVERSION_PELLETS_MJ_KG,
            CONVERSION_PELLETS_MJ_KWH,
        )
    )
    data_site["agent_energetique_ef_plaquettes_somme_mj"] = (
        fonction_agent_energetique_ef_plaquettes_somme_mj(
            data_site["agent_energetique_ef_plaquettes_m3"],
            data_site["agent_energetique_ef_plaquettes_kwh"],
            CONVERSION_PLAQUETTES_MJ_M3,
            CONVERSION_PLAQUETTES_MJ_KWH,
        )
    )
    data_site["agent_energetique_ef_cad_somme_mj"] = (
        fonction_agent_energetique_ef_cad_somme_mj(
            data_site["agent_energetique_ef_cad_kwh"],
            CONVERSION_CAD_MJ_KWH,
        )
    )
    data_site["agent_energetique_ef_electricite_pac_somme_mj"] = (
        fonction_agent_energetique_ef_electricite_pac_somme_mj(
            data_site["agent_energetique_ef_electricite_pac_kwh"],
            CONVERSION_ELECTRICITE_PAC_MJ_KWH,
        )
    )
    data_site["agent_energetique_ef_electricite_directe_somme_mj"] = (
        fonction_agent_energetique_ef_electricite_directe_somme_mj(
            data_site["agent_energetique_ef_electricite_directe_kwh"],
            CONVERSION_ELECTRICITE_DIRECTE_MJ_KWH,
        )
    )
    data_site["agent_energetique_ef_autre_somme_mj"] = (
        fonction_agent_energetique_ef_autre_somme_mj(
            data_site["agent_energetique_ef_autre_kwh"],
            CONVERSION_AUTRE_MJ_KWH,
        )
    )
    data_site["agent_energetique_ef_somme_kwh"] = (
        fonction_agent_energetique_ef_somme_kwh(
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
        )
    )
    data_site["methodo_b_ww_kwh"] = fonction_methodo_b_ww_kwh(
        data_site["agent_energetique_ef_somme_kwh"],
        data_site["part_ecs_periode_comptage"],
    )
    data_site["methodo_e_ww_kwh"] = fonction_methodo_e_ww_kwh(
        data_site["methodo_b_ww_kwh"],
        data_site["sre_renovation_m2"],
        data_site["periode_nb_jours"],
    )
    data_site["methodo_b_h_kwh"] = fonction_methodo_b_h_kwh(
        data_site["agent_energetique_ef_somme_kwh"],
        data_site["part_chauffage_periode_comptage"],
    )
    data_site["methodo_e_h_kwh"] = fonction_methodo_e_h_kwh(
        data_site["sre_renovation_m2"],
        data_site["dj_periode"],
        data_site["methodo_b_h_kwh"],
        DJ_REF_ANNUELS,
    )
    data_site[
        "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2"
    ] = fonction_energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2(
        data_site["methodo_e_ww_kwh"], data_site["methodo_e_h_kwh"]
    )
    data_site["energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2"] = (
        fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2(
            data_site[
                "energie_finale_apres_travaux_climatiquement_corrigee_inclus_surelevation_kwh_m2"
            ],
            data_site["repartition_energie_finale_partie_renovee_somme"],
        )
    )
    data_site["facteur_ponderation_moyen"] = fonction_facteur_ponderation_moyen(
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
        data_site["agent_energetique_ef_somme_kwh"],
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
    )
    data_site["methodo_e_ww_renovee_pondere_kwh_m2"] = (
        fonction_methodo_e_ww_renovee_pondere_kwh_m2(
            data_site["methodo_e_ww_kwh"],
            data_site["facteur_ponderation_moyen"],
            data_site["repartition_energie_finale_partie_renovee_somme"],
        )
    )
    data_site["methodo_e_h_renovee_pondere_kwh_m2"] = (
        fonction_methodo_e_h_renovee_pondere_kwh_m2(
            data_site["methodo_e_h_kwh"],
            data_site["facteur_ponderation_moyen"],
            data_site["repartition_energie_finale_partie_renovee_somme"],
        )
    )
    data_site[
        "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
    ] = fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2(
        data_site[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_kwh_m2"
        ],
        data_site["facteur_ponderation_moyen"],
    )
    data_site[
        "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2"
    ] = fonction_energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_MJ_m2(
        data_site[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
        ],
    )
    # générer dataframe df_list
    df_list = make_dataframe_df_list(data_site, DJ_REF_ANNUELS)

    # df_agent_energetique
    df_agent_energetique = make_dataframe_df_agent_energetique(
        data_site,
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

    # df_meteo_note_calcul
    df_meteo_note_calcul = make_dataframe_df_meteo_note_calcul(
        data_site["periode_start"],
        data_site["periode_start"],
        df_meteo_tre200d0,
    )

    # latex text
    formula_facteur_ponderation_moyen_texte = (
        make_latex_formula_facteur_ponderation_moyen_texte(),
    )

    # latex formula
    formula_facteur_ponderation_moyen = make_latex_formula_facteur_ponderation_moyen(
        data_site,
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

    return (
        data_site,
        df_periode_list,
        df_list,
        df_agent_energetique,
        df_meteo_note_calcul,
        formula_facteur_ponderation_moyen_texte,
        formula_facteur_ponderation_moyen,
    )
