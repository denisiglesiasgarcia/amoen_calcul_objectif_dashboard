# sections/helpers/note_calcul/create_dataframe_results.py

import pandas as pd


def make_dataframe_df_results(
    ef_avant_corr_kwh_m2,
    ef_objectif_pondere_kwh_m2,
    delta_ef_realisee_kwh_m2,
    delta_ef_visee_kwh_m2,
    energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
):
    """
    Create a DataFrame with energy performance results.

    This function generates a DataFrame containing energy performance metrics
    before and after renovation, as well as the targeted and actual energy savings.

    Parameters:
    ef_avant_corr_kwh_m2 (float): Energy performance before correction in kWh/m²/year.
    ef_objectif_pondere_kwh_m2 (float): Weighted target energy performance in kWh/m²/year.
    delta_ef_realisee_kwh_m2 (float): Actual energy savings in kWh/m²/year.
    delta_ef_visee_kwh_m2 (float): Targeted energy savings in kWh/m²/year.
    energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2 (float):
        Weighted and climate-corrected energy performance after renovation in kWh/m²/year.

    Returns:
    pd.DataFrame: A DataFrame containing the energy performance metrics in both
    kWh/m²/year and MJ/m²/year.

    Raises:
    StreamlitError: If any of the input parameters are less than or equal to zero.
    """
    if (
        ef_avant_corr_kwh_m2 > 0
        and ef_objectif_pondere_kwh_m2 > 0
        and delta_ef_realisee_kwh_m2 > 0
        and delta_ef_visee_kwh_m2 > 0
        and energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
        > 0
    ):
        df_resultats = pd.DataFrame(
            {
                "Variable": [
                    "IDC moyen 3 ans avant travaux → (Ef,avant,corr)",
                    "EF pondéré corrigé clim. après travaux → (Ef,après,corr,rénové*fp)",
                    "Objectif en énergie finale (Ef,obj *fp)",
                    "Baisse ΔEf réalisée → ∆Ef,réel = Ef,avant,corr - Ef,après,corr*fp",
                    "Baisse ΔEf visée → ∆Ef,visée = Ef,avant,corr - Ef,obj*fp",
                ],
                "kWh/m²/an": [
                    round(ef_avant_corr_kwh_m2, 4),
                    round(
                        energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
                        4,
                    ),
                    round(ef_objectif_pondere_kwh_m2, 4),
                    round(delta_ef_realisee_kwh_m2, 4),
                    round(delta_ef_visee_kwh_m2, 4),
                ],
                "MJ/m²/an": [
                    round(ef_avant_corr_kwh_m2 * 3.6, 4),
                    round(
                        energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
                        * 3.6,
                        4,
                    ),
                    round(
                        ef_objectif_pondere_kwh_m2 * 3.6,
                        4,
                    ),
                    round(
                        delta_ef_realisee_kwh_m2 * 3.6,
                        4,
                    ),
                    round(delta_ef_visee_kwh_m2 * 3.6, 4),
                ],
            }
        )
        # dtypes
        df_resultats["Variable"] = df_resultats["Variable"].astype(str)
        df_resultats["kWh/m²/an"] = df_resultats["kWh/m²/an"].astype(float)
        df_resultats["MJ/m²/an"] = df_resultats["MJ/m²/an"].astype(float)
    return df_resultats
