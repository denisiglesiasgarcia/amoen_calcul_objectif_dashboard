# sections/helpers/note_calcul/latex.py


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


def make_latex_formula_facteur_ponderation_moyen(
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
):
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
