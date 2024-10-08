# sections/helpers/note_calcul/create_dataframe_meteo.py


def make_dataframe_df_meteo_note_calcul(periode_start, periode_end, df_meteo_tre200d0):
    df_meteo_note_calcul = df_meteo_tre200d0[
        (df_meteo_tre200d0["time"] >= periode_start)
        & (df_meteo_tre200d0["time"] <= periode_end)
    ][["time", "tre200d0", "DJ_theta0_16"]]
    return df_meteo_note_calcul
