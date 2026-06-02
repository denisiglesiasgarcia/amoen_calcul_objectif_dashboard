import altair as alt
import pandas as pd
import polars as pl
import streamlit as st

TARGET = 85.0  # cible en %

ENERGY_AGENT_GROUPS = {
    "Mazout": [
        "agent_energetique_ef_mazout_kg",
        "agent_energetique_ef_mazout_litres",
        "agent_energetique_ef_mazout_kwh",
    ],
    "Gaz naturel": [
        "agent_energetique_ef_gaz_naturel_m3",
        "agent_energetique_ef_gaz_naturel_kwh",
    ],
    "Bois bûches dur": ["agent_energetique_ef_bois_buches_dur_stere"],
    "Bois bûches tendre": [
        "agent_energetique_ef_bois_buches_tendre_stere",
        "agent_energetique_ef_bois_buches_tendre_kwh",
    ],
    "Pellets": [
        "agent_energetique_ef_pellets_m3",
        "agent_energetique_ef_pellets_kg",
        "agent_energetique_ef_pellets_kwh",
    ],
    "Plaquettes": [
        "agent_energetique_ef_plaquettes_m3",
        "agent_energetique_ef_plaquettes_kwh",
    ],
    "CAD": ["agent_energetique_ef_cad_kwh"],
    "Électricité PAC": ["agent_energetique_ef_electricite_pac_kwh"],
    "Électricité directe": ["agent_energetique_ef_electricite_directe_kwh"],
    "Autre": ["agent_energetique_ef_autre_kwh"],
}


def safe_numeric_conversion(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def filter_energy_data(df: pd.DataFrame) -> pd.DataFrame:
    all_energy_cols = [col for cols in ENERGY_AGENT_GROUPS.values() for col in cols]
    try:
        df_clean = df.copy()
        for col in all_energy_cols:
            if col in df_clean.columns:
                df_clean[col] = safe_numeric_conversion(df_clean[col])
            else:
                df_clean[col] = 0
        # Ensure total_energy is always a Series (one value per row).
        total_energy = pd.Series(0, index=df_clean.index, dtype=float)
        for col in all_energy_cols:
            if col in df_clean.columns:
                total_energy = total_energy + df_clean[col]

        return df_clean[total_energy > 0]
    except Exception as e:
        st.error(f"Erreur filter_energy_data: {str(e)}")
        return pd.DataFrame()


def _last_per_project(df: pd.DataFrame) -> pd.DataFrame:
    """One row per project — the most recent date_rapport."""
    df = df.copy()
    for col in ["date_rapport", "periode_start", "periode_end"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df = df.sort_values(["nom_projet", "date_rapport"], na_position="last")
    idx = df.groupby("nom_projet")["date_rapport"].idxmax()
    return df.loc[idx]


def display_kpi_metrics(df: pd.DataFrame):
    try:
        last = _last_per_project(df)
        if last.empty:
            return

        obj = pd.to_numeric(last["atteinte_objectif"], errors="coerce").fillna(0) * 100

        total = len(last)
        above = int((obj >= TARGET).sum())
        avg = obj.mean()

        c1, c2, c3 = st.columns(3)
        c1.metric("Sites actifs", total)
        c2.metric(
            "Objectif atteint ≥ 85%",
            f"{above}/{total}",
            delta=f"{above / total * 100:.0f}%" if total else "0%",
        )
        c3.metric(
            "Objectif moyen",
            f"{avg:.1f}%",
            delta=f"{avg - TARGET:+.1f}% vs cible",
            delta_color="normal" if avg >= TARGET else "inverse",
        )
    except Exception as e:
        st.error(f"Erreur KPI: {str(e)}")


def display_last_calculations(df: pd.DataFrame):
    try:
        df_date = filter_energy_data(df.copy())
        if df_date.empty:
            st.warning("Aucune donnée énergétique disponible")
            return

        for col in ["date_rapport", "periode_start", "periode_end"]:
            if col in df_date.columns:
                df_date[col] = pd.to_datetime(df_date[col], errors="coerce")

        df_date = df_date.sort_values(
            ["nom_projet", "date_rapport"], na_position="last"
        )

        if "atteinte_objectif" in df_date.columns:
            df_date["atteinte_objectif"] = (
                pd.to_numeric(df_date["atteinte_objectif"], errors="coerce").fillna(0)
                * 100
            )

        idx = df_date.groupby("nom_projet")["date_rapport"].idxmax()
        want_cols = [
            "nom_projet",
            "amoen_id",
            "date_rapport",
            "periode_start",
            "periode_end",
            "atteinte_objectif",
        ]
        want_cols = [c for c in want_cols if c in df_date.columns]
        df_last = df_date.loc[idx, want_cols].sort_values(
            "atteinte_objectif", ascending=True
        )

        for col in ["date_rapport", "periode_start", "periode_end"]:
            if col in df_last.columns:
                df_last[col] = df_last[col].dt.strftime("%Y-%m-%d")

        df_last = df_last.rename(
            columns={
                "nom_projet": "Projet",
                "amoen_id": "AMOén",
                "date_rapport": "Dernier rapport",
                "periode_start": "Début période",
                "periode_end": "Fin période",
                "atteinte_objectif": "Objectif (%)",
            }
        ).reset_index(drop=True)

        def color_objective(val):
            try:
                v = float(val)
                if v >= TARGET:
                    return "background-color: #d4edda; color: #155724"
                return "background-color: #f8d7da; color: #721c24"
            except (ValueError, TypeError):
                return ""

        styled = df_last.style.applymap(
            color_objective, subset=["Objectif (%)"]
        ).format({"Objectif (%)": "{:.1f}%"})
        st.dataframe(styled, width="stretch")

    except Exception as e:
        st.error(f"Erreur derniers calculs: {str(e)}")


def display_objective_chart(df: pd.DataFrame):
    try:
        lf = pl.from_pandas(df.drop(columns=["_id"], errors="ignore"))

        lf = (
            lf
            .sort(["nom_projet", "periode_start"])
            .with_columns(
                (
                    pl
                    .col("atteinte_objectif")
                    .cast(pl.Float64, strict=False)
                    .fill_null(0.0)
                    * 100
                ).alias("atteinte_objectif"),
                pl
                .col("periode_start")
                .cast(pl.Utf8)
                .str.slice(0, 10)
                .alias("periode_start"),
                pl
                .col("periode_end")
                .cast(pl.Utf8)
                .str.slice(0, 10)
                .alias("periode_end"),
            )
            .filter(pl.col("atteinte_objectif") > 0)
        )

        if lf.is_empty():
            st.warning("Aucune donnée disponible pour le graphique")
            return

        lf = lf.with_columns(
            pl
            .when(
                pl.col("periode_start").is_not_null()
                & pl.col("periode_end").is_not_null()
            )
            .then(pl.col("periode_start") + " – " + pl.col("periode_end"))
            .otherwise(pl.lit("Date non spécifiée"))
            .alias("periode"),
            pl.int_range(pl.len()).over("nom_projet").alias("periode_rank"),
            pl
            .when(pl.col("atteinte_objectif") >= TARGET)
            .then(pl.lit("≥ 85% ✓"))
            .otherwise(pl.lit("< 85% ✗"))
            .alias("statut"),
        )

        df_plot = lf.to_pandas()
        y_max = max(110, (int(df_plot["atteinte_objectif"].max()) // 10 + 2) * 10)

        bars = (
            alt
            .Chart(df_plot)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X(
                    "nom_projet:N",
                    axis=alt.Axis(title="", labelAngle=-40, labelFontSize=11),
                ),
                y=alt.Y(
                    "atteinte_objectif:Q",
                    title="Atteinte objectif [%]",
                    scale=alt.Scale(domain=[0, y_max]),
                    axis=alt.Axis(grid=True, tickCount=6),
                ),
                xOffset=alt.XOffset(
                    "periode_rank:O", scale=alt.Scale(paddingInner=0.05)
                ),
                color=alt.Color(
                    "statut:N",
                    scale=alt.Scale(
                        domain=["≥ 85% ✓", "< 85% ✗"],
                        range=["#2ecc71", "#e74c3c"],
                    ),
                    legend=alt.Legend(title="", orient="top"),
                ),
                tooltip=[
                    alt.Tooltip("nom_projet:N", title="Site"),
                    alt.Tooltip("amoen_id:N", title="AMOén"),
                    alt.Tooltip("periode:N", title="Période"),
                    alt.Tooltip(
                        "atteinte_objectif:Q",
                        title="Atteinte objectif [%]",
                        format=".1f",
                    ),
                ],
            )
        )

        labels = (
            alt
            .Chart(df_plot)
            .mark_text(dy=-6, fontSize=9, fontWeight="bold")
            .encode(
                x=alt.X("nom_projet:N"),
                y=alt.Y("atteinte_objectif:Q"),
                xOffset=alt.XOffset("periode_rank:O"),
                text=alt.Text("atteinte_objectif:Q", format=".0f"),
                color=alt.condition(
                    alt.datum.atteinte_objectif >= TARGET,
                    alt.value("#27ae60"),
                    alt.value("#c0392b"),
                ),
            )
        )

        ref_line = (
            alt
            .Chart(pd.DataFrame({"y": [TARGET]}))
            .mark_rule(color="#c0392b", strokeWidth=2, strokeDash=[6, 3])
            .encode(y=alt.Y("y:Q"))
        )

        ref_label = (
            alt
            .Chart(pd.DataFrame({"y": [TARGET], "label": ["Cible 85%"]}))
            .mark_text(
                align="right",
                dx=-6,
                dy=-7,
                color="#c0392b",
                fontSize=10,
                fontWeight="bold",
            )
            .encode(y=alt.Y("y:Q"), text=alt.Text("label:N"), x=alt.value(700))
        )

        fig = (
            alt
            .layer(bars, labels, ref_line, ref_label)
            .properties(
                height=420,
                title=alt.TitleParams(
                    "Atteinte objectif par site",
                    fontSize=14,
                    fontWeight="bold",
                    anchor="start",
                ),
            )
            .configure_view(strokeWidth=0)
            .configure_axis(labelFontSize=11)
        )

        st.altair_chart(fig, width="stretch")

    except Exception as e:
        st.error(f"Erreur graphique objectif: {str(e)}")


def display_energy_mix_chart(df: pd.DataFrame):
    try:
        df_clean = df.copy()
        rows = []
        for agent_name, cols in ENERGY_AGENT_GROUPS.items():
            present = [c for c in cols if c in df_clean.columns]
            if not present:
                continue
            count = int(
                df_clean[present]
                .apply(lambda s: pd.to_numeric(s, errors="coerce").fillna(0))
                .sum(axis=1)
                .gt(0)
                .sum()
            )
            if count > 0:
                rows.append({"Agent": agent_name, "Entrées": count})

        if not rows:
            st.info("Aucun agent énergétique détecté")
            return

        df_mix = pd.DataFrame(rows).sort_values("Entrées", ascending=True)

        bars = (
            alt
            .Chart(df_mix)
            .mark_bar(
                color="#3498db", cornerRadiusTopRight=3, cornerRadiusBottomRight=3
            )
            .encode(
                y=alt.Y(
                    "Agent:N", sort=None, axis=alt.Axis(labelFontSize=11), title=""
                ),
                x=alt.X(
                    "Entrées:Q", axis=alt.Axis(tickMinStep=1), title="Nombre d'entrées"
                ),
                tooltip=["Agent:N", "Entrées:Q"],
            )
        )

        labels = (
            alt
            .Chart(df_mix)
            .mark_text(align="left", dx=4, fontSize=11)
            .encode(
                y=alt.Y("Agent:N", sort=None),
                x=alt.X("Entrées:Q"),
                text=alt.Text("Entrées:Q"),
            )
        )

        fig = (
            alt
            .layer(bars, labels)
            .properties(height=max(180, len(df_mix) * 36))
            .configure_view(strokeWidth=0)
            .configure_axisY(labelLimit=160)
        )
        st.altair_chart(fig, width="stretch")

    except Exception as e:
        st.error(f"Erreur graphique mix énergétique: {str(e)}")


def display_filtered_data(df: pd.DataFrame) -> pd.DataFrame:
    try:
        columns_to_drop = [
            "_id",
            "sre_pourcentage_lieux_de_rassemblement",
            "sre_pourcentage_hopitaux",
            "sre_pourcentage_industrie",
            "sre_pourcentage_depots",
            "sre_pourcentage_installations_sportives",
            "sre_pourcentage_piscines_couvertes",
        ]
        df_filtre = df.drop(columns=[c for c in columns_to_drop if c in df.columns])

        col1, col2 = st.columns(2)
        with col1:
            all_amoen = sorted(df_filtre["amoen_id"].unique())
            filtre_amoen = st.multiselect("AMOén", all_amoen, default=all_amoen)
        with col2:
            projects_for_selected = sorted(
                df_filtre[df_filtre["amoen_id"].isin(filtre_amoen)][
                    "nom_projet"
                ].unique()
            )
            filtre_projets = st.multiselect(
                "Projet", projects_for_selected, default=projects_for_selected
            )

        df_filtre = df_filtre[
            df_filtre["nom_projet"].isin(filtre_projets)
            & df_filtre["amoen_id"].isin(filtre_amoen)
        ]
        st.dataframe(df_filtre, width="stretch", hide_index=True)
        return df_filtre

    except Exception as e:
        st.error(f"Erreur données filtrées: {str(e)}")
        return pd.DataFrame()


def display_admin_dashboard(df: pd.DataFrame):
    try:
        if not isinstance(df, pd.DataFrame) or df.empty:
            st.warning("Aucune donnée disponible")
            return

        display_kpi_metrics(df)
        st.divider()

        df_energy = filter_energy_data(df)

        st.subheader("Atteinte objectif par site")
        if not df_energy.empty:
            display_objective_chart(df_energy)

        st.divider()

        col_left, col_right = st.columns([3, 2])
        with col_left:
            st.subheader("Dernier calcul par projet")
            display_last_calculations(df)
        with col_right:
            st.subheader("Mix énergétique")
            display_energy_mix_chart(df_energy if not df_energy.empty else df)

        st.divider()

        with st.expander("📋 Données brutes", expanded=False):
            display_filtered_data(df)

    except Exception as e:
        st.error(f"Erreur tableau de bord: {str(e)}")
