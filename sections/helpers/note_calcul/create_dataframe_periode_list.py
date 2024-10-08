# sections/helpers/note_calcul/create_dataframes.py

import pandas as pd


def make_dataframe_df_periode_list(periode_start, periode_end):
    df_periode_list = []

    columns = [
        "Dénomination",
        "Valeur",
        "Unité",
        "Commentaire",
        "Excel",
        "Variable/Formule",
    ]

    # C65 → Début période
    df_periode_list.append(
        {
            "Dénomination": "Début période",
            "Valeur": periode_start,
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
            "Valeur": periode_end,
            "Unité": "-",
            "Commentaire": "Date de fin de la période",
            "Excel": "C66",
            "Variable/Formule": "periode_end",
        }
    )

    return pd.DataFrame(df_periode_list, columns=columns)
