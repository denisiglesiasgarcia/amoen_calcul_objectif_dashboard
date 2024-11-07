# import pandas as pd
import plotly.express as px

# from datetime import datetime
import streamlit as st


@st.cache_data
def create_barplot_historique_amoen(data_df):
    """
    Creates a bar plot to visualize the historical achievement of objectives for a given project.
    """
    # Data preparation
    df_barplot = data_df.copy()
    # Sort by periode_start first
    df_barplot = df_barplot[
        ["nom_projet", "periode_start", "periode_end", "atteinte_objectif"]
    ].sort_values(by=["periode_start"])

    # Create period labels after sorting
    df_barplot["periode"] = (
        "Du "
        + df_barplot["periode_start"].dt.strftime("%Y-%m-%d")
        + "<br>"
        + "au "
        + df_barplot["periode_end"].dt.strftime("%Y-%m-%d")
        + "<br>"
        + "365 jours"
    )

    # Convert to percentage
    df_barplot["atteinte_objectif"] = df_barplot["atteinte_objectif"] * 100
    nom_projet = df_barplot["nom_projet"].iloc[0]

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
        category_orders={"periode": df_barplot["periode"].tolist()},  # Enforce order
    )

    # Customize the layout
    fig.update_layout(
        xaxis_title="Période",
        yaxis_title="Atteinte de l'objectif [%]",
        xaxis={
            "type": "category",
            "tickangle": 0,
            "gridcolor": "rgba(211, 211, 211, 0.2)",
            "tickfont": {"size": 12},
        },
        yaxis={
            "range": [0, max(max(df_barplot["atteinte_objectif"]) * 1.15, 100)],
            "gridcolor": "rgba(211, 211, 211, 0.2)",
            "gridwidth": 0.1,
            "tickfont": {"size": 12},
        },
        # Margins
        margin=dict(
            t=50,  # top
            r=50,  # right
            b=100,  # bottom - increased for 3-line labels
            l=50,  # left
        ),
        # Style
        plot_bgcolor="white",
        paper_bgcolor="white",
        bargap=0.2,
        showlegend=False,
        title={"y": 0.95, "x": 0.5, "xanchor": "center", "yanchor": "top"},
        font=dict(size=12, family="Arial"),
    )

    # Add value labels on top of bars with conditional coloring
    fig.update_traces(
        texttemplate="%{y:.1f}%",
        textposition="outside",
        textfont=dict(
            color=[
                "#006400" if y >= 85 else "#e74c3c"
                for y in df_barplot["atteinte_objectif"]  # Darker green
            ]
        ),
        marker_color=[
            "#27ae60" if y >= 85 else "#e74c3c"
            for y in df_barplot["atteinte_objectif"]  # Changed from #2ecc71 to #27ae60
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
                "scale": 2,
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
