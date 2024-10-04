import streamlit as st
import numpy as np
from typing import List, Dict
from sections.helpers.avusy import avusy_consommation_energie_elec_periode
import time

# Define energy agent options
OPTIONS_AGENT_ENERGETIQUE_EF = [
    {"label": "CAD (kWh)", "unit": "kWh", "variable": "agent_energetique_ef_cad_kwh"},
    {
        "label": "Electricité pour les PAC (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_electricite_pac_kwh",
    },
    {
        "label": "Electricité directe (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_electricite_directe_kwh",
    },
    {
        "label": "Gaz naturel (m³)",
        "unit": "m³",
        "variable": "agent_energetique_ef_gaz_naturel_m3",
    },
    {
        "label": "Gaz naturel (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_gaz_naturel_kwh",
    },
    {
        "label": "Mazout (litres)",
        "unit": "litres",
        "variable": "agent_energetique_ef_mazout_litres",
    },
    {
        "label": "Mazout (kg)",
        "unit": "kg",
        "variable": "agent_energetique_ef_mazout_kg",
    },
    {
        "label": "Mazout (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_mazout_kwh",
    },
    {
        "label": "Bois buches dur (stère)",
        "unit": "stère",
        "variable": "agent_energetique_ef_bois_buches_dur_stere",
    },
    {
        "label": "Bois buches tendre (stère)",
        "unit": "stère",
        "variable": "agent_energetique_ef_bois_buches_tendre_stere",
    },
    {
        "label": "Bois buches tendre (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_bois_buches_tendre_kwh",
    },
    {
        "label": "Pellets (m³)",
        "unit": "m³",
        "variable": "agent_energetique_ef_pellets_m3",
    },
    {
        "label": "Pellets (kg)",
        "unit": "kg",
        "variable": "agent_energetique_ef_pellets_kg",
    },
    {
        "label": "Pellets (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_pellets_kwh",
    },
    {
        "label": "Plaquettes (m³)",
        "unit": "m³",
        "variable": "agent_energetique_ef_plaquettes_m3",
    },
    {
        "label": "Plaquettes (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_plaquettes_kwh",
    },
    {
        "label": "Autre (kWh)",
        "unit": "kWh",
        "variable": "agent_energetique_ef_autre_kwh",
    },
]


def validate_agent_energetique_input(label: str, value: str, unit: str) -> float:
    """
    Validate and convert the input value for an energy agent.

    Args:
    label (str): The label of the energy agent.
    value (str): The input value to validate.
    unit (str): The unit of measurement.

    Returns:
    float: The validated and converted value, or 0 if invalid.
    """
    if value is None or value == "":
        st.error(f"{label} doit être un chiffre")
        return 0

    try:
        if isinstance(value, (int, float, np.float64)):
            value = float(value)
        else:
            value = float(str(value).replace(",", ".", 1))

        if value > 0:
            st.text(f"{label}: {value} {unit}")
            return value
        else:
            st.error(f"{label} doit être un chiffre positif")
            return 0
    except ValueError:
        st.error(f"{label} doit être un chiffre")
        return 0


def get_selected_agents(data_sites_db: Dict) -> List[str]:
    """
    Get the list of selected energy agents based on the database values.

    Args:
    data_sites_db (Dict): The database containing energy agent values.

    Returns:
    List[str]: A list of selected energy agent labels.
    """
    return [
        option["label"]
        for option in OPTIONS_AGENT_ENERGETIQUE_EF
        if data_sites_db.get(option["variable"], 0) > 0
    ]


def update_data_site(
    data_site: Dict, selected_agents: List[str], options: List[Dict]
) -> Dict:
    """
    Update the data_site dictionary with energy agent values, setting unselected agents to 0.

    Args:
    data_site (Dict): The dictionary to update.
    selected_agents (List[str]): The list of currently selected energy agents.
    options (List[Dict]): The list of energy agent options.

    Returns:
    Dict: The updated data_site dictionary.
    """
    for option in options:
        # Set unselected agents to 0
        if option["label"] not in selected_agents:
            data_site[option["variable"]] = 0
        # Update the values for selected agents
        else:
            data_site[option["variable"]] = option.get("value", 0)
    return data_site


def calculate_total_energy(data_site: Dict) -> float:
    """
    Calculate the total energy from all energy agents.

    Args:
    data_site (Dict): The dictionary containing energy agent values.

    Returns:
    float: The total energy sum.
    """
    return sum(
        float(data_site[option["variable"]]) for option in OPTIONS_AGENT_ENERGETIQUE_EF
    )


def display_energy_agents(
    data_site: Dict, data_sites_db: Dict, mycol_historique_index_avusy
):
    """
    Display energy agents inputs and handle user interactions.

    Args:
    data_site (Dict): The current site data.
    data_sites_db (Dict): The database containing energy agent values.
    mycol_historique_index_avusy: The database collection for Avusy project.
    """
    st.markdown(
        '<span style="font-size:1.2em;">**Agents énergétiques utilisés**</span>',
        unsafe_allow_html=True,
    )

    # Handle Avusy project specific logic
    if data_site["nom_projet"] == "Avusy 10-10A":
        handle_avusy_project(data_site, mycol_historique_index_avusy)

    # Get selected energy agents
    selected_agents = get_selected_agents(data_sites_db) if data_sites_db else []

    # Display multiselect for energy agents
    selected_agents = st.multiselect(
        "Agent(s) énergétique(s):",
        [option["label"] for option in OPTIONS_AGENT_ENERGETIQUE_EF],
        default=selected_agents,
    )

    # Display input fields for selected agents
    for option in OPTIONS_AGENT_ENERGETIQUE_EF:
        if option["label"] in selected_agents:
            default_value = get_default_value(data_site, option)
            value = st.text_input(option["label"] + ":", value=default_value)
            if value != "0":
                option["value"] = validate_agent_energetique_input(
                    option["label"], value, option["unit"]
                )

    # Update data_site with new values, setting unselected agents to 0
    data_site = update_data_site(data_site, selected_agents, OPTIONS_AGENT_ENERGETIQUE_EF)


    # Calculate and display total energy
    total_energy = calculate_total_energy(data_site)
    if total_energy <= 0:
        st.warning(
            f"Veuillez renseigner une quantité d'énergie utilisée sur la période ({total_energy})"
        )


def handle_avusy_project(data_site: Dict, mycol_historique_index_avusy):
    """
    Handle Avusy project specific logic.

    Args:
    data_site (Dict): The current site data.
    mycol_historique_index_avusy: The database collection for Avusy project.
    """
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


def get_default_value(data_site: Dict, option: Dict) -> float:
    """
    Get the default value for an energy agent input field.

    Args:
    data_site (Dict): The current site data.
    option (Dict): The energy agent option.

    Returns:
    float: The default value for the input field.
    """
    if (
        data_site["nom_projet"] == "Avusy 10-10A"
        and option["label"] == "Electricité pour les PAC (kWh)"
    ):
        return round(data_site.get("conso_elec_pac_immeuble", 0), 1)
    return 0.0
