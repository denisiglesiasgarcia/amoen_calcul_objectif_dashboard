# sections/helpers/note_calcul/latex.py

def make_latex_formula_facteur_ponderation_moyen(
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
    facteur_ponderation_moyen,
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
):
    formula_facteur_ponderation_moyen = (
        r"facteur\_ponderation\_moyen = \frac{{({0})}}{{({1})}} = {2}".format(
            agent_energetique_ef_mazout_somme_mj * FACTEUR_PONDERATION_MAZOUT
            + agent_energetique_ef_gaz_naturel_somme_mj
            * FACTEUR_PONDERATION_GAZ_NATUREL
            + agent_energetique_ef_bois_buches_dur_somme_mj
            * FACTEUR_PONDERATION_BOIS_BUCHES_DUR
            + agent_energetique_ef_bois_buches_tendre_somme_mj
            * FACTEUR_PONDERATION_BOIS_BUCHES_TENDRE
            + agent_energetique_ef_pellets_somme_mj * FACTEUR_PONDERATION_PELLETS
            + agent_energetique_ef_plaquettes_somme_mj * FACTEUR_PONDERATION_PLAQUETTES
            + agent_energetique_ef_cad_somme_mj * FACTEUR_PONDERATION_CAD
            + agent_energetique_ef_electricite_pac_somme_mj
            * FACTEUR_PONDERATION_ELECTRICITE_PAC
            + agent_energetique_ef_electricite_directe_somme_mj
            * FACTEUR_PONDERATION_ELECTRICITE_DIRECTE
            + agent_energetique_ef_autre_somme_mj * FACTEUR_PONDERATION_AUTRE,
            agent_energetique_ef_somme_kwh * 3.6,
            facteur_ponderation_moyen,
        )
    )
    return formula_facteur_ponderation_moyen
