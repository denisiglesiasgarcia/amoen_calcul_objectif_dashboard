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
    # Data preparation
    df_barplot = data_df.copy()
    df_barplot = df_barplot[
        ["nom_projet", "periode_start", "periode_end", "atteinte_objectif"]
    ].sort_values(by=["periode_start"])

    # Create period labels
    df_barplot["periode"] = (
        df_barplot["periode_start"].dt.strftime("%Y-%m-%d")
        + " → "
        + df_barplot["periode_end"].dt.strftime("%Y-%m-%d")
    )

    # Convert to percentage
    df_barplot["atteinte_objectif"] = df_barplot["atteinte_objectif"] * 100
    nom_projet = df_barplot["nom_projet"].iloc[0]  # Using iloc for safety

    # Calculate layout dimensions
    longest_period = max(df_barplot["periode"].str.len())
    pixels_per_char = 8
    bottom_margin = max(
        100, longest_period * pixels_per_char * 0.5
    )  # For rotated labels

    # Create the bar plot
    fig = px.bar(
        df_barplot,
        x="periode",
        y="atteinte_objectif",
        labels={
            "periode": "Période",
            "atteinte_objectif": "Atteinte de l'objectif [%]",
        },
        title=f"Historique atteinte objectifs pour {nom_projet}",
        height=500,
        width=1000,
    )

    # Customize the layout
    fig.update_layout(
        xaxis_title="Période",
        yaxis_title="Atteinte de l'objectif [%]",
        xaxis={
            "type": "category",
            "tickangle": -45,  # Rotate labels for better readability
            "tickfont": {"size": 10},
        },
        yaxis={
            "range": [
                0,
                max(max(df_barplot["atteinte_objectif"]) * 1.15, 100),
            ],  # Always show up to at least 100%
            "gridcolor": "lightgrey",
            "gridwidth": 0.1,
        },
        # Adjust margins
        margin=dict(
            t=50,  # top margin
            r=50,  # right margin
            b=bottom_margin,  # dynamic bottom margin for labels
            l=50,  # left margin
        ),
        # Style improvements
        plot_bgcolor="white",
        paper_bgcolor="white",
        bargap=0.2,  # Adjust gap between bars
        showlegend=False,
        title={"y": 0.95, "x": 0.5, "xanchor": "center", "yanchor": "top"},
        # Add a red reference line at 85%
        shapes=[
            dict(
                type="line",
                yref="y",
                y0=85,
                y1=85,
                xref="paper",
                x0=0,
                x1=1,
                line=dict(color="red", width=1, dash="dash"),
            )
        ],
    )

    # Add value labels on top of bars with conditional coloring
    fig.update_traces(
        texttemplate="%{y:.1f}%",
        textposition="outside",
        textfont=dict(
            color=[
                "green" if y >= 85 else "red" for y in df_barplot["atteinte_objectif"]
            ]
        ),
        marker_color=[
            "#2ecc71" if y >= 85 else "#e74c3c" for y in df_barplot["atteinte_objectif"]
        ],
    )

    # Display the plot
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "toImageButtonOptions": {
                "format": "png",
                "filename": "historique_objectifs",
                "height": 500,
                "width": 1000,
                "scale": 2,  # Higher resolution
            },
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "pan2d",
                "select2d",
                "lasso2d",
                "zoomIn2d",
                "zoomOut2d",
                "autoScale2d",
                "resetScale2d",
            ],
        },
    )

    return fig
