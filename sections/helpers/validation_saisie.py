# /sections/helpers/validation_saisie.py

import streamlit as st
from sections.helpers.sanitize_mongo import get_rounded_float


def validate_input(name, variable, unit):
    if variable.isnumeric() or variable.replace(".", "", 1).isnumeric():
        st.text(f"{name} {variable} {unit}")
    else:
        st.warning(f"{name} doit être un chiffre")


def validate_energie_input(name, variable, unit1, unit2):
    try:
        variable = float(variable.replace(",", ".", 1))
        if variable > 0:
            st.text(f"{name} {variable} {unit1} → {round((variable * 3.6),2)} {unit2}")
        else:
            st.text("Valeur doit être positive")
    except ValueError:
        st.text(f"{name} doit être un chiffre")
        variable = 0


def validate_percentage_sum(data_dict, field_names, expected_sum=100.0, round_digits=2):
    """
    Validates that the sum of specified percentage fields equals an expected value and displays a warning if needed.

    Args:
        data_dict (dict): Dictionary containing the percentage values
        field_names (list): List of field names to sum
        expected_sum (float): Expected sum of percentages (default: 100.0)
        round_digits (int): Number of decimal places to round to (default: 2)
    """
    try:
        # Get values for each field and convert to float
        values = [float(get_rounded_float(data_dict, field)) for field in field_names]

        # Calculate sum and round to specified digits
        actual_sum = round(sum(values), round_digits)

        # Check if sum matches expected value and display warning if needed
        if actual_sum != expected_sum:
            st.warning(
                f"La somme des pourcentages doit être égale à {expected_sum}% ({actual_sum:.2f}%)"
            )

    except Exception as e:
        st.warning(f"Problème dans la somme des pourcentages: {str(e)}")
