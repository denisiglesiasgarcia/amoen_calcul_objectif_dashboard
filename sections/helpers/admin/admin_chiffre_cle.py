import pandas as pd
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
    Display the objective achievement chart

    Args:
        df (pd.DataFrame): Input DataFrame containing filtered project data
    """
    try:
        df_barplot = df.sort_values(by=["nom_projet", "periode_start"])
        df_barplot = filter_energy_data(df_barplot)

        if df_barplot.empty:
            st.warning("No data available for visualization")
            return

        # Process data for visualization
        df_barplot["atteinte_objectif"] = (
            pd.to_numeric(df_barplot["atteinte_objectif"], errors="coerce").fillna(0)
            * 100
        )

        # Handle dates
        for col in ["periode_start", "periode_end"]:
            df_barplot[col] = pd.to_datetime(df_barplot[col], errors="coerce")

        # Create period string
        df_barplot["periode"] = df_barplot.apply(
            lambda row: (
                f"{row['periode_start'].strftime('%Y-%m-%d')} - {row['periode_end'].strftime('%Y-%m-%d')}"
                if pd.notnull(row["periode_start"]) and pd.notnull(row["periode_end"])
                else "Date non spécifiée"
            ),
            axis=1,
        )

        df_barplot["periode_rank"] = df_barplot.groupby("nom_projet").cumcount()
        df_barplot["atteinte_objectif_formatted"] = df_barplot[
            "atteinte_objectif"
        ].apply(lambda x: f"{x:.0f}%")

        # Create chart
        bars = (
            alt.Chart(df_barplot)
            .mark_bar()
            .encode(
                x=alt.X("nom_projet:N", axis=alt.Axis(title="", labels=True)),
                y=alt.Y(
                    "atteinte_objectif:Q",
                    title="Atteinte Objectif [%]",
                    scale=alt.Scale(domain=[0, 100]),
                ),
                xOffset="periode_rank:N",
                color="periode:N",
                tooltip=[
                    alt.Tooltip("nom_projet:N", title="Site"),
                    alt.Tooltip("amoen_id:N", title="AMOén"),
                    alt.Tooltip("periode:N", title="Période"),
                    alt.Tooltip(
                        "atteinte_objectif:Q",
                        title="Atteinte Objectif [%]",
                        format=".2f",
                    ),
                ],
            )
            .properties(width=600, title="Atteinte Objectif par Site")
        )

        # Add labels
        text = (
            alt.Chart(df_barplot)
            .mark_text(
                align="left", baseline="bottom", dx=-4, fontSize=12, color="black"
            )
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
