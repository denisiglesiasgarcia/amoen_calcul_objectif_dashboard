# /sections/helpers/validation_saisie.py

import streamlit as st
from sections.helpers.sanitize_mongo import get_rounded_float


def validate_input(name, variable, unit):
    if variable.isnumeric() or variable.replace(".", "", 1).isnumeric():
        st.text(f"{name} {variable} {unit}")
    else:
        st.warning(f"{name} doit être un chiffre")


def validate_input_float(name, variable, unit, text=True, zero=False):
    """
    Validates and formats a float input value.

    Args:
        name (str): Name of the variable for display
        variable: The input value to validate
        unit (str): Unit for display
        text (bool): Whether to display the text output
        zero (bool): Whether to allow zero values

    Returns:
        float: The validated and rounded value, or 0 if invalid
    """
    try:
        variable = float(variable.replace(",", ".", 1))

        if zero:
            # Case when zero is allowed
            if variable >= 0:
                if text:
                    st.text(f"{name} {variable} {unit}")
                return round(variable, 2)
            else:
                st.warning(f"{name} doit être positive ou nulle")
                return 0
        else:
            # Case when zero is not allowed
            if variable > 0:
                if text:
                    st.text(f"{name} {variable} {unit}")
                return round(variable, 2)
            else:
                st.warning(f"{name} doit être positive")
                return 0

    except ValueError:
        st.warning(f"{name} doit être un chiffre")
        return 0


def validate_energie_input(name, variable, unit1, unit2):
    try:
        variable = float(variable.replace(",", ".", 1))
        if variable > 0:
            st.text(f"{name} = {variable} {unit1} → {round((variable * 3.6),2)} {unit2}")
            return variable
        else:
            st.warning(f"{name} doit être positif")
            return 0
    except ValueError:
        st.warning(f"{name} doit être un chiffre")
        return 0


def validate_percentage_sum(data_dict, field_names, expected_sum=100.0, round_digits=2):
    """
    Validates that the sum of specified percentage fields equals an expected value and displays a warning if needed.

    Args:
        data_dict (dict): Dictionary containing the percentage values
        field_names (list): List of field names to sum
        expected_sum (float): Expected sum of percentages (default: 100.0)
        round_digits (int): Number of decimal places to round to (default: 2)

    Returns:
        float: The actual sum of percentages if validation passes, 0 if validation fails
    """
    try:
        # Initialize values list
        values = []

        # Get values for each field and convert to float, handling potential None values
        for field in field_names:
            value = get_rounded_float(data_dict, field)
            if value is None:
                st.warning(f"Champ manquant ou invalide: {field}")
                return 0
            values.append(float(value))

        # Calculate sum and round to specified digits
        actual_sum = round(sum(values), round_digits)

        # Check if sum matches expected value
        if actual_sum != expected_sum:
            st.warning(
                f"La somme des pourcentages doit être égale à {expected_sum}% (actuellement: {actual_sum:.2f}%)"
            )
            return 0

        return actual_sum

    except Exception as e:
        st.warning(f"Problème dans la somme des pourcentages: {str(e)}")
        return 0
