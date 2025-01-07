import streamlit as st
from typing import List, Dict
from sections.helpers.validation_saisie import validate_percentage_sum

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


def validate_input_affectation(
    name: str, variable: str, unite: str, sre_renovation_m2: float
) -> float:
    """
    Validates an affectation input value and returns the validated value.

    Args:
        name: Name of the field
        variable: Input value to validate
        unite: Unit for display
        sre_renovation_m2: SRE renovation value for area calculation

    Returns:
        float: The validated value, or 0 if invalid
    """
    try:
        value = float(variable.replace(",", ".", 1))
        if 0 <= value <= 100:
            st.text(
                f"{name} {value} {unite} → {round(value * float(sre_renovation_m2) / 100, 2)} m²"
            )
            return value
        else:
            st.warning("Valeur doit être comprise entre 0 et 100")
            return 0.0
    except ValueError:
        st.warning(f"{name} doit être un chiffre")
        return 0.0


def get_selected_affectations(data_sites_db: Dict) -> List[str]:
    """Return list of selected affectations based on database values."""
    if not data_sites_db:
        return []
    return [
        option["label"]
        for option in AFFECTATION_OPTIONS
        if data_sites_db.get(option["variable"], 0) > 0
    ]


def display_affectation_inputs(
    data_sites_db: Dict, selected_affectations: List[str], sre_renovation_m2: float
):
    """Display and process affectation inputs."""
    for option in AFFECTATION_OPTIONS:
        if option["label"] in selected_affectations:
            default_value = (
                data_sites_db.get(option["variable"], 0.0) if data_sites_db else 0.0
            )
            value = st.text_input(option["label"] + ":", value=default_value)

            if value and value != "0":
                validated_value = validate_input_affectation(
                    option["label"] + ":",
                    value,
                    option["unit"],
                    sre_renovation_m2,
                )
                st.session_state["data_site"][option["variable"]] = validated_value
            else:
                st.session_state["data_site"][option["variable"]] = 0.0


def default_affectations(data_sites_db: Dict):
    """Set default affectation values."""
    for option in AFFECTATION_OPTIONS:
        if option["label"] not in get_selected_affectations(data_sites_db):
            st.session_state["data_site"][option["variable"]] = 0.0
        else:
            st.session_state["data_site"][option["variable"]] = data_sites_db.get(
                option["variable"], 0.0
            )


def display_affectations(data_sites_db: Dict, sre_renovation_m2: float):
    """Main function to display and process affectations."""
    st.markdown(
        '<span style="font-size:1.2em;">**Affectations**</span>', 
        unsafe_allow_html=True
    )

    selected_affectations = st.multiselect(
        "Affectation(s):",
        [option["label"] for option in AFFECTATION_OPTIONS],
        default=get_selected_affectations(data_sites_db),
    )

    display_affectation_inputs(data_sites_db, selected_affectations, sre_renovation_m2)
    default_affectations(data_sites_db)

    # Only validate if there are selected affectations
    if selected_affectations:
        # Get only the fields that are actually selected
        fields_to_validate = [
            option["variable"] 
            for option in AFFECTATION_OPTIONS 
            if option["label"] in selected_affectations
        ]
        
        # Run the validation
        validate_percentage_sum(
            data_dict=st.session_state["data_site"],
            field_names=fields_to_validate
        )
