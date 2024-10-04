# sections/helpers/agents_energetiques.py

import streamlit as st
from typing import List, Dict
import time
import numpy as np

# Import necessary functions
from sections.helpers.avusy import avusy_consommation_energie_elec_periode

ENERGY_AGENTS = [
    {
        "label": "CAD (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_cad_kwh",
        "index": 0,
    },
    {
        "label": "Electricité pour les PAC (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_electricite_pac_kwh",
        "index": 1,
    },
    {
        "label": "Electricité directe (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_electricite_directe_kwh",
        "index": 2,
    },
    {
        "label": "Gaz naturel (m³)",
        "unit": "m³",
        "variable": "agent_energetique_ef_gaz_naturel_m3",
        "index": 3,
    },
    {
        "label": "Gaz naturel (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_gaz_naturel_kwh",
        "index": 4,
    },
    {
        "label": "Mazout (litres)",
        "unit": "litres",
        "variable": "agent_energetique_ef_mazout_litres",
        "index": 5,
    },
    {
        "label": "Mazout (kg)",
        "unit": "kg",
        "variable": "agent_energetique_ef_mazout_kg",
        "index": 6,
    },
    {
        "label": "Mazout (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_mazout_kwh",
        "index": 7,
    },
    {
        "label": "Bois buches dur (stère)",
        "unit": "stère",
        "variable": "agent_energetique_ef_bois_buches_dur_stere",
        "index": 8,
    },
    {
        "label": "Bois buches tendre (stère)",
        "unit": "stère",
        "variable": "agent_energetique_ef_bois_buches_tendre_stere",
        "index": 9,
    },
    {
        "label": "Bois buches tendre (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_bois_buches_tendre_kwh",
        "index": 10,
    },
    {
        "label": "Pellets (m³)",
        "unit": "m³",
        "variable": "agent_energetique_ef_pellets_m3",
        "index": 11,
    },
    {
        "label": "Pellets (kg)",
        "unit": "kg",
        "variable": "agent_energetique_ef_pellets_kg",
        "index": 12,
    },
    {
        "label": "Pellets (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_pellets_kwh",
        "index": 13,
    },
    {
        "label": "Plaquettes (m³)",
        "unit": "m³",
        "variable": "agent_energetique_ef_plaquettes_m3",
        "index": 14,
    },
    {
        "label": "Plaquettes (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_plaquettes_kwh",
        "index": 15,
    },
    {
        "label": "Autre (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_autre_kwh",
        "index": 16,
    },
]


def get_selected_energy_agents(data_sites_db: Dict) -> List[str]:
    """Return list of selected energy agents based on database values."""
    return (
        [
            option["label"]
            for option in ENERGY_AGENTS
            if data_sites_db.get(option["variable"], 0) > 0
        ]
        if data_sites_db
        else []
    )


def validate_agent_energetique_input(label: str, value: str, unit: str) -> float:
    if value is None or value == "":
        st.text(f"{name} doit être un chiffre")
        return 0

    try:
        if isinstance(value, (int, float, np.float64)):
            value = float(value)
        else:
            value = float(str(value).replace(",", ".", 1))

        if value > 0:
            st.text(f"{name} {value} {unit}")
            return value
        else:
            st.text(f"{name} doit être un chiffre positif")
            return 0
    except ValueError:
        st.text(f"{name} doit être un chiffre")
        return 0


def handle_avusy_project(data_site: Dict, mycol_historique_index_avusy):
    """Handle special case for Avusy 10-10A project."""
    conso_elec_pac_immeuble, nearest_start_date, nearest_end_date = (
        avusy_consommation_energie_elec_periode(
            data_site["periode_start"],
            data_site["periode_end"],
            mycol_historique_index_avusy,
        )
    )
    if (
        conso_elec_pac_immeuble
        and nearest_start_date.date() == data_site["periode_start"].date()
        and nearest_end_date.date() == data_site["periode_end"].date()
    ):
        success = st.success("Dates OK!")
        time.sleep(3)
        success.empty()
    else:
        st.warning(
            f"Pas de données pour ces dates, dates les plus proches: du {nearest_start_date.date()} au {nearest_end_date.date()}"
        )
    return conso_elec_pac_immeuble


def display_energy_agent_inputs(
    data_site: Dict,
    selected_agents: List[str],
    is_avusy: bool,
    conso_elec_pac_immeuble: float = None,
):
    """Display and process energy agent inputs."""
    for option in ENERGY_AGENTS:
        if option["label"] in selected_agents:
            if is_avusy and option["label"] == "Electricité pour les PAC (kWh)":
                value = st.text_input(
                    option["label"] + ":",
                    value=(
                        round(conso_elec_pac_immeuble, 1)
                        if conso_elec_pac_immeuble
                        else 0.0
                    ),
                )
            else:
                value = st.text_input(
                    option["label"] + ":", value=data_site.get(option["variable"], 0.0)
                )

            if value != "0":
                validated_value = validate_agent_energetique_input(
                    option["label"], value, option["unit"]
                )
                data_site[option["variable"]] = validated_value
            else:
                data_site[option["variable"]] = 0.0


def calculate_energy_agent_sum(data_site: Dict) -> float:
    """Calculate sum of all energy agent values."""
    return sum(float(data_site.get(option["variable"], 0)) for option in ENERGY_AGENTS)


def display_energy_agents(
    data_site: Dict, data_sites_db: Dict, mycol_historique_index_avusy
):
    """Main function to display and process energy agents."""
    st.markdown(
        '<span style="font-size:1.2em;">**Agents énergétiques utilisés**</span>',
        unsafe_allow_html=True,
    )

    is_avusy = data_site["nom_projet"] == "Avusy 10-10A"
    conso_elec_pac_immeuble = None

    if is_avusy:
        conso_elec_pac_immeuble = handle_avusy_project(
            data_site, mycol_historique_index_avusy
        )

    selected_agents = st.multiselect(
        "Agent(s) énergétique(s):",
        [option["label"] for option in ENERGY_AGENTS],
        default=get_selected_energy_agents(data_sites_db),
    )

    display_energy_agent_inputs(
        data_site, selected_agents, is_avusy, conso_elec_pac_immeuble
    )

    energy_agent_sum = calculate_energy_agent_sum(data_site)
    if energy_agent_sum <= 0:
        st.warning(
            f"Veuillez renseigner une quantité d'énergie utilisée sur la période ({energy_agent_sum})"
        )

    # Ensure all energy agent variables are set in data_site
    for option in ENERGY_AGENTS:
        if option["variable"] not in data_site:
            data_site[option["variable"]] = 0.0
