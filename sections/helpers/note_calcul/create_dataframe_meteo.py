# sections/helpers/note_calcul/create_dataframe_meteo.py

import pandas as pd


def make_dataframe_df_meteo_note_calcul(periode_start, periode_end, df_meteo_tre200d0):
    try:
        periode_start = pd.to_datetime(periode_start)
        periode_end = pd.to_datetime(periode_end)
        if periode_start > periode_end:
            st.warning(
                "La date de début de la période doit être antérieure à la date de fin."
            )
        elif periode_start < periode_end and len(df_meteo_tre200d0) > 0:
            df_meteo_note_calcul = (
                df_meteo_tre200d0[
                    (df_meteo_tre200d0["time"] >= periode_start)
                    & (df_meteo_tre200d0["time"] <= periode_end)
                ][["time", "tre200d0", "DJ_theta0_16"]]
            ).copy()
        else:
            st.warning(
                "Erreur lors de la création du DataFrame de météo pour le calcul des degrés-jours."
            )
    except Exception as e:
        st.warning(
            f"Erreur lors de la création du DataFrame de météo pour le calcul des degrés-jours. Erreur : {e}"
        )
    return df_meteo_note_calcul
