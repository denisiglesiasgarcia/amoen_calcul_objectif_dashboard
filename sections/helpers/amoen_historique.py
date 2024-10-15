# import pandas as pd
import plotly.express as px
# from datetime import datetime
import streamlit as st


@st.cache_data
def create_barplot_historique_amoen(data_df):
    """
    Creates a bar plot to visualize the historical achievement of objectives for a given project.
    Parameters:
    data_df (pandas.DataFrame): DataFrame containing the following columns:
        - 'nom_projet': Name of the project.
        - 'periode_start': Start date of the period (datetime).
        - 'periode_end': End date of the period (datetime).
        - 'atteinte_objectif': Achievement of the objective (float, should be between 0 and 1).
    Returns:
    plotly.graph_objs._figure.Figure: A Plotly figure object representing the bar plot.
    """
    df_barplot = data_df.copy()
    df_barplot = df_barplot[
        ["nom_projet", "periode_start", "periode_end", "atteinte_objectif"]
    ].sort_values(by=["periode_start"])
    df_barplot["periode"] = (
        df_barplot["periode_start"].dt.strftime("%Y-%m-%d")
        + " → "
        + df_barplot["periode_end"].dt.strftime("%Y-%m-%d")
    )
    df_barplot["atteinte_objectif"] = df_barplot["atteinte_objectif"] * 100

    nom_projet = df_barplot["nom_projet"][0]

    fig = px.bar(
        df_barplot,
        x="periode",
        y="atteinte_objectif",
        labels={
            "periode": "Période",
            "atteinte_objectif": "Atteinte de l'objectif [%]",
        },
        title=f"Historique atteinte objectifs pour {nom_projet}",
    )

    # Customize the layout
    fig.update_layout(
        xaxis_title="Période",
        yaxis_title="Atteinte de l'objectif [%]",
        xaxis={"type": "category"},  # Treat year as categorical
        yaxis_range=[
            0,
            max(df_barplot["atteinte_objectif"]) * 1.1,
        ],  # Extend y-axis range
        margin=dict(t=100, b=100),  # Increase top and bottom margins
        height=600,  # Increase overall height of the plot
    )

    # Add annotations for the values over the bars
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")

    return fig
