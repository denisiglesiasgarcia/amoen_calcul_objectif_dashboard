import pandas as pd
import polars as pl
import altair as alt
import streamlit as st
import numpy as np
from typing import Tuple


def safe_numeric_conversion(series):
    """Convert series to numeric, replacing errors with 0"""
    return pd.to_numeric(series, errors="coerce").fillna(0)


def filter_energy_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter data to include only rows with energy agents > 0
    Handles type conversion and missing data safely

    Args:
        df (pd.DataFrame): Input DataFrame containing energy data

    Returns:
        pd.DataFrame: Filtered DataFrame containing only rows with positive energy values
    """
    # List of energy-related columns
    energy_columns = [
        "agent_energetique_ef_mazout_litres",
        "agent_energetique_ef_mazout_kwh",
        "agent_energetique_ef_gaz_naturel_m3",
        "agent_energetique_ef_gaz_naturel_kwh",
        "agent_energetique_ef_bois_buches_dur_stere",
        "agent_energetique_ef_bois_buches_tendre_stere",
        "agent_energetique_ef_bois_buches_tendre_kwh",
        "agent_energetique_ef_pellets_m3",
        "agent_energetique_ef_pellets_kg",
        "agent_energetique_ef_pellets_kwh",
        "agent_energetique_ef_plaquettes_m3",
        "agent_energetique_ef_plaquettes_kwh",
        "agent_energetique_ef_cad_kwh",
        "agent_energetique_ef_electricite_pac_kwh",
        "agent_energetique_ef_electricite_directe_kwh",
        "agent_energetique_ef_autre_kwh",
    ]

    try:
        # Create a copy of the dataframe
        df_clean = df.copy()

        # Convert all energy columns to numeric, replacing errors with 0
        for col in energy_columns:
            if col in df_clean.columns:
                df_clean[col] = safe_numeric_conversion(df_clean[col])
            else:
                df_clean[col] = 0

        # Calculate total energy
        total_energy = sum(df_clean[col] for col in energy_columns)

        # Return filtered dataframe
        return df_clean[total_energy > 0]

    except Exception as e:
        st.error(f"Error in filter_energy_data: {str(e)}")
        return pd.DataFrame()


def display_last_calculations(df: pd.DataFrame):
    """
    Display the last calculation dates for each project

    Args:
        df (pd.DataFrame): Input DataFrame containing project data
    """
    try:
        # Filter energy data with safe conversion
        df_date = filter_energy_data(df.copy())

        if df_date.empty:
            st.warning("No energy data available to display")
            return

        # Convert date columns safely
        date_columns = ["date_rapport", "periode_start", "periode_end"]
        for col in date_columns:
            if col in df_date.columns:
                df_date[col] = pd.to_datetime(df_date[col], errors="coerce")
            else:
                df_date[col] = pd.NaT

        # Sort values safely
        df_date_sorted = df_date.sort_values(
            ["nom_projet", "date_rapport"], na_position="last"
        )

        # Format dates
        for col in date_columns:
            df_date_sorted[col] = df_date_sorted[col].dt.strftime("%Y-%m-%d")

        # Safely handle atteinte_objectif formatting
        if "atteinte_objectif" in df_date_sorted.columns:
            df_date_sorted["atteinte_objectif"] = pd.to_numeric(
                df_date_sorted["atteinte_objectif"], errors="coerce"
            ).fillna(0)
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

    except Exception as e:
        st.error(f"Error in display_last_calculations: {str(e)}")
        st.dataframe(pd.DataFrame())


def display_filtered_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Display filtered data based on user selections

    Args:
        df (pd.DataFrame): Input DataFrame containing project data

    Returns:
        pd.DataFrame: Filtered DataFrame based on user selections
    """
    try:
        # Drop unnecessary columns
        columns_to_drop = [
            "_id",
            "sre_pourcentage_lieux_de_rassemblement",
            "sre_pourcentage_hopitaux",
            "sre_pourcentage_industrie",
            "sre_pourcentage_depots",
            "sre_pourcentage_installations_sportives",
            "sre_pourcentage_piscines_couvertes",
        ]

        df_filtre = df.drop(
            columns=[col for col in columns_to_drop if col in df.columns]
        )

        # Filters
        all_amoen = sorted(df_filtre["amoen_id"].unique())
        filtre_amoen = st.multiselect("AMOén", all_amoen, default=all_amoen)

        # Get projects for selected AMOén
        projects_for_selected_amoen = sorted(
            df_filtre[df_filtre["amoen_id"].isin(filtre_amoen)]["nom_projet"].unique()
        )
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

    except Exception as e:
        st.error(f"Error in display_filtered_data: {str(e)}")
        return pd.DataFrame()


def display_objective_chart(df: pd.DataFrame):
    """
    Display objective achievement chart.
    Improvements: dynamic Y-axis, dashed 100% reference line,
    legend re-enabled at bottom, labels centered above bars.

    Args:
        df (pd.DataFrame): Filtered project DataFrame
    """
    try:
        # Convert to Polars for data processing
        lf = pl.from_pandas(df)

        lf = (
            lf.sort(["nom_projet", "periode_start"])
            .with_columns(
                (
                    pl.col("atteinte_objectif")
                    .cast(pl.Float64, strict=False)
                    .fill_null(0.0)
                    * 100
                ).alias("atteinte_objectif"),
                pl.col("periode_start")
                .cast(pl.Utf8)
                .str.to_date(format="%Y-%m-%d", strict=False)
                .alias("periode_start"),
                pl.col("periode_end")
                .cast(pl.Utf8)
                .str.to_date(format="%Y-%m-%d", strict=False)
                .alias("periode_end"),
            )
            .filter(pl.col("atteinte_objectif") > 0)
        )

        if lf.is_empty():
            st.warning("No data available for visualization")
            return

        lf = lf.with_columns(
            # Period label for legend and tooltip
            pl.when(
                pl.col("periode_start").is_not_null()
                & pl.col("periode_end").is_not_null()
            )
            .then(
                pl.col("periode_start").dt.strftime("%Y-%m-%d")
                + " – "
                + pl.col("periode_end").dt.strftime("%Y-%m-%d")
            )
            .otherwise(pl.lit("Date non spécifiée"))
            .alias("periode"),
            # Rank within each project group for xOffset positioning
            pl.int_range(pl.len()).over("nom_projet").alias("periode_rank"),
            # Pre-formatted label string
            pl.col("atteinte_objectif")
            .map_elements(lambda x: f"{x:.0f}%", return_dtype=pl.Utf8)
            .alias("atteinte_objectif_formatted"),
        )

        df_plot = lf.to_pandas()

        # Dynamic Y upper bound: next 10-step above max + one extra step, min 110
        y_max = max(110, (int(df_plot["atteinte_objectif"].max()) // 10 + 2) * 10)

        # Bars
        bars = (
            alt.Chart(df_plot)
            .mark_bar()
            .encode(
                x=alt.X(
                    "nom_projet:N",
                    axis=alt.Axis(title="", labelAngle=-40, labelFontSize=11),
                ),
                y=alt.Y(
                    "atteinte_objectif:Q",
                    title="Atteinte Objectif [%]",
                    scale=alt.Scale(domain=[0, y_max]),
                    axis=alt.Axis(grid=True, tickCount=6),
                ),
                xOffset=alt.XOffset(
                    "periode_rank:O",
                    scale=alt.Scale(paddingInner=0.05),
                ),
                color=alt.Color(
                    "periode:N",
                    legend=alt.Legend(
                        title="Période",
                        orient="bottom",
                        columns=4,
                        labelFontSize=10,
                        titleFontSize=11,
                    ),
                ),
                tooltip=[
                    alt.Tooltip("nom_projet:N", title="Site"),
                    alt.Tooltip("amoen_id:N", title="AMOén"),
                    alt.Tooltip("periode:N", title="Période"),
                    alt.Tooltip("atteinte_objectif:Q", title="Atteinte Objectif [%]", format=".1f"),
                ],
            )
        )

        # Percentage labels centered above each bar
        labels = (
            alt.Chart(df_plot)
            .mark_text(
                align="center",
                baseline="bottom",
                dy=-2,
                fontSize=9,
                fontWeight="bold",
                color="black",
            )
            .encode(
                x=alt.X("nom_projet:N"),
                y=alt.Y("atteinte_objectif:Q"),
                xOffset=alt.XOffset("periode_rank:O"),
                text="atteinte_objectif_formatted:N",
            )
        )

        # Dashed reference line at 100%
        ref_line = (
            alt.Chart(pd.DataFrame({"y": [100]}))
            .mark_rule(color="red", strokeWidth=1.5, strokeDash=[5, 4])
            .encode(y=alt.Y("y:Q"))
        )

        fig = (
            alt.layer(bars, labels, ref_line)
            .properties(
                width=700,
                height=400,
                title=alt.TitleParams(
                    "Atteinte Objectif par Site",
                    fontSize=14,
                    fontWeight="bold",
                    anchor="start",
                ),
            )
            .configure_view(strokeWidth=0)
            .configure_axis(labelFontSize=11)
        )

        st.altair_chart(fig, width='stretch')

    except Exception as e:
        st.error(f"Error in display_objective_chart: {str(e)}")


def display_admin_dashboard(df: pd.DataFrame):
    """
    Display the admin dashboard with key figures and visualizations

    Args:
        df (pd.DataFrame): Input DataFrame containing the projects data
    """
    try:
        # Validate input dataframe
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")

        if df.empty:
            st.warning("No data available to display")
            return

        # Chiffres clés section
        st.subheader("Chiffres-clés")
        display_last_calculations(df)

        # Données section
        st.subheader("Données")
        filtered_df = display_filtered_data(df)

        # Visualization
        if not filtered_df.empty:
            display_objective_chart(filtered_df)

    except Exception as e:
        st.error(f"Error in admin dashboard: {str(e)}")
