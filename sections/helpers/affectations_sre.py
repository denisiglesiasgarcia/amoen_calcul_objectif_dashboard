# sections/helpers/affectation_helper.py

import streamlit as st
from typing import List, Dict

# Define data structure
AFFECTATION_OPTIONS = [
    {
        "label": "Habitat collectif (%)",
        "unit": "%",
        "variable": "sre_pourcentage_habitat_collectif",
        "value": 0.0,
    },
    {
        "label": "Habitat individuel (%)",
        "unit": "%",
        "variable": "sre_pourcentage_habitat_individuel",
        "value": 0.0,
    },
    {
        "label": "Administration (%)",
        "unit": "%",
        "variable": "sre_pourcentage_administration",
        "value": 0.0,
    },
    {
        "label": "Écoles (%)",
        "unit": "%",
        "variable": "sre_pourcentage_ecoles",
        "value": 0.0,
    },
    {
        "label": "Commerce (%)",
        "unit": "%",
        "variable": "sre_pourcentage_commerce",
        "value": 0.0,
    },
    {
        "label": "Restauration (%)",
        "unit": "%",
        "variable": "sre_pourcentage_restauration",
        "value": 0.0,
    },
    {
        "label": "Lieux de rassemblement (%)",
        "unit": "%",
        "variable": "sre_pourcentage_lieux_de_rassemblement",
        "value": 0.0,
    },
    {
        "label": "Hôpitaux (%)",
        "unit": "%",
        "variable": "sre_pourcentage_hopitaux",
        "value": 0.0,
    },
    {
        "label": "Industrie (%)",
        "unit": "%",
        "variable": "sre_pourcentage_industrie",
        "value": 0.0,
    },
    {
        "label": "Dépôts (%)",
        "unit": "%",
        "variable": "sre_pourcentage_depots",
        "value": 0.0,
    },
    {
        "label": "Installations sportives (%)",
        "unit": "%",
        "variable": "sre_pourcentage_installations_sportives",
        "value": 0.0,
    },
    {
        "label": "Piscines couvertes (%)",
        "unit": "%",
        "variable": "sre_pourcentage_piscines_couvertes",
        "value": 0.0,
    },
]


def get_selected_affectations(data_sites_db: Dict) -> List[str]:
    """Return list of selected affectations based on database values."""
    return (
        [
            option["label"]
            for option in AFFECTATION_OPTIONS
            if data_sites_db.get(option["variable"], 0) > 0
        ]
        if data_sites_db
        else []
    )


def display_affectation_inputs(
    data_sites_db: Dict, selected_affectations: List[str], sre_renovation_m2: float
):
    """Display and process affectation inputs."""
    for option in AFFECTATION_OPTIONS:
        if option["label"] in selected_affectations:
            value = st.text_input(
                option["label"] + ":",
                value=(
                    data_sites_db.get(option["variable"], 0.0) if data_sites_db else 0.0
                ),
            )
            if value != "0":
                validate_input_affectation(
                    option["label"] + ":",
                    value,
                    option["unit"],
                    sre_renovation_m2,
                )
                option["value"] = float(value)
                st.session_state["data_site"][option["variable"]] = float(value)
            else:
                option["value"] = 0.0
                st.session_state["data_site"][option["variable"]] = 0.0


def calculate_affectation_sum() -> float:
    """Calculate sum of all affectation percentages."""
    return sum(
        float(st.session_state["data_site"].get(option["variable"], 0))
        for option in AFFECTATION_OPTIONS
    )


def display_affectations(data_sites_db: Dict, sre_renovation_m2: float):
    """Main function to display and process affectations."""
    st.markdown(
        '<span style="font-size:1.2em;">**Affectations**</span>', unsafe_allow_html=True
    )

    selected_affectations = st.multiselect(
        "Affectation(s):",
        [option["label"] for option in AFFECTATION_OPTIONS],
        default=get_selected_affectations(data_sites_db),
    )

    display_affectation_inputs(data_sites_db, selected_affectations, sre_renovation_m2)

    affectation_sum = calculate_affectation_sum()
    if affectation_sum != 100:
        st.warning(f"Somme des pourcentages doit être égale à 100% ({affectation_sum})")

