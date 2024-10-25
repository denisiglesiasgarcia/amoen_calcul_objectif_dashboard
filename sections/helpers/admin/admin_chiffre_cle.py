import pandas as pd
import altair as alt
import streamlit as st


def display_admin_dashboard(df: pd.DataFrame):
    """
    Display the admin dashboard with key figures and visualizations.
    This function generates an admin dashboard using Streamlit, displaying key figures, filtered data, and visualizations based on the provided DataFrame.
        df (pd.DataFrame): DataFrame containing the projects data.
    Sections:
        - Chiffres-clés: Displays key figures.
        - Données: Displays filtered data.
        - Visualization: Displays a chart if the filtered data is not empty.
    """
    # Chiffres clés section
    st.subheader("Chiffres-clés")
    display_last_calculations(df)

    # Données section
    st.subheader("Données")
    filtered_df = display_filtered_data(df)

    # Visualization
    if not filtered_df.empty:
        display_objective_chart(filtered_df)


def filter_energy_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter data to include only rows with energy agents > 0"""
    return df[
        (
            df["agent_energetique_ef_mazout_litres"]
            + df["agent_energetique_ef_mazout_kwh"]
            + df["agent_energetique_ef_gaz_naturel_m3"]
            + df["agent_energetique_ef_gaz_naturel_kwh"]
            + df["agent_energetique_ef_bois_buches_dur_stere"]
            + df["agent_energetique_ef_bois_buches_tendre_stere"]
            + df["agent_energetique_ef_bois_buches_tendre_kwh"]
            + df["agent_energetique_ef_pellets_m3"]
            + df["agent_energetique_ef_pellets_kg"]
            + df["agent_energetique_ef_pellets_kwh"]
            + df["agent_energetique_ef_plaquettes_m3"]
            + df["agent_energetique_ef_plaquettes_kwh"]
            + df["agent_energetique_ef_cad_kwh"]
            + df["agent_energetique_ef_electricite_pac_kwh"]
            + df["agent_energetique_ef_electricite_directe_kwh"]
            + df["agent_energetique_ef_autre_kwh"]
        )
        > 0
    ]


def display_last_calculations(df: pd.DataFrame):
    """Display the last calculation dates for each project"""
    df_date = filter_energy_data(df.copy())

    # Process dates
    df_date_sorted = df_date.sort_values(["nom_projet", "date_rapport"])
    for col in ["date_rapport", "periode_start", "periode_end"]:
        df_date_sorted[col] = pd.to_datetime(
            df_date_sorted[col], format="%Y-%m-%d"
        ).astype(str)

    # Format atteinte_objectif
    df_date_sorted["atteinte_objectif"] = (
        df_date_sorted["atteinte_objectif"] * 100
    ).apply(lambda x: f"{x:.2f}%")

    # Get last report for each project
    idx = df_date_sorted.groupby("nom_projet")["date_rapport"].idxmax()
    df_date = df_date_sorted.loc[
        idx,
        [
            "nom_projet",
            "date_rapport",
            "periode_start",
            "periode_end",
            "atteinte_objectif",
        ],
    ].sort_values(by=["date_rapport"])

    st.write("Date dernier calcul atteinte objectif par projet")
    st.dataframe(df_date)


def display_filtered_data(df: pd.DataFrame) -> pd.DataFrame:
    """Display filtered data based on user selections"""
    # Drop unnecessary columns
    df_filtre = df.drop(
        columns=[
            "_id",
            "sre_pourcentage_lieux_de_rassemblement",
            "sre_pourcentage_hopitaux",
            "sre_pourcentage_industrie",
            "sre_pourcentage_depots",
            "sre_pourcentage_installations_sportives",
            "sre_pourcentage_piscines_couvertes",
        ]
    )

    # Filters
    all_amoen = df_filtre["amoen_id"].unique()
    filtre_amoen = st.multiselect("AMOén", all_amoen, default=all_amoen)

    projects_for_selected_amoen = df_filtre[df_filtre["amoen_id"].isin(filtre_amoen)][
        "nom_projet"
    ].unique()
    filtre_projets = st.multiselect(
        "Projet", projects_for_selected_amoen, default=projects_for_selected_amoen
    )

    # Apply filters
    df_filtre = df_filtre[
        (df_filtre["nom_projet"].isin(filtre_projets))
        & (df_filtre["amoen_id"].isin(filtre_amoen))
    ]

    st.write(df_filtre)
    return df_filtre


def display_objective_chart(df: pd.DataFrame):
    """Display the objective achievement chart"""
    df_barplot = df.sort_values(by=["nom_projet", "periode_start"])
    df_barplot = filter_energy_data(df_barplot)

    # Process data for visualization
    df_barplot["atteinte_objectif"] = df_barplot["atteinte_objectif"] * 100
    df_barplot["periode_start"] = pd.to_datetime(
        df_barplot["periode_start"], errors="coerce"
    )
    df_barplot["periode_end"] = pd.to_datetime(
        df_barplot["periode_end"], errors="coerce"
    )
    df_barplot["periode"] = (
        df_barplot["periode_start"].dt.strftime("%Y-%m-%d")
        + " - "
        + df_barplot["periode_end"].dt.strftime("%Y-%m-%d")
    )

    df_barplot["periode_rank"] = df_barplot.groupby("nom_projet").cumcount()
    df_barplot["atteinte_objectif_formatted"] = df_barplot["atteinte_objectif"].apply(
        lambda x: f"{x:.0f}%"
    )

    # Create chart
    bars = (
        alt.Chart(df_barplot)
        .mark_bar()
        .encode(
            x=alt.X("nom_projet:N", axis=alt.Axis(title="", labels=True)),
            y=alt.Y("atteinte_objectif:Q", title="Atteinte Objectif [%]"),
            xOffset="periode_rank:N",
            color="periode:N",
            tooltip=[
                alt.Tooltip("nom_projet:N", title="Site"),
                alt.Tooltip("amoen_id:N", title="AMOén"),
                alt.Tooltip("periode:N", title="Période"),
                alt.Tooltip(
                    "atteinte_objectif:Q", title="Atteinte Objectif [%]", format=".2f"
                ),
            ],
        )
        .properties(width=600, title="Atteinte Objectif par Site")
    )

    # Add labels
    text = (
        alt.Chart(df_barplot)
        .mark_text(align="left", baseline="bottom", dx=-4, fontSize=12, color="black")
        .encode(
            x=alt.X("nom_projet:N", axis=alt.Axis(title="", labels=True)),
            y=alt.Y("atteinte_objectif:Q", title="Atteinte Objectif [%]"),
            text="atteinte_objectif_formatted:N",
            xOffset="periode_rank:N",
        )
    )

    # Combine and configure
    fig = alt.layer(bars, text)
    fig = fig.configure_axisX(labelAngle=-45, labelFontSize=12)
    fig = fig.configure_legend(disable=True)

    st.altair_chart(fig, use_container_width=True)
