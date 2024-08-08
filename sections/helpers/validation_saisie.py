import streamlit as st
import numpy as np

def validate_input(name, variable, unit):
    if (variable.isnumeric() or variable.replace('.', '', 1).isnumeric()):
        st.text(f"{name} {variable} {unit}")
    else:
        st.warning(f"{name} doit être un chiffre")

def validate_input_affectation(name, variable, unite, sre_renovation_m2):
    try:
        variable = float(variable.replace(',', '.', 1))
        if 0 <= variable <= 100:
            st.text(f"{name} {variable} {unite} → {round(variable * float(sre_renovation_m2) / 100, 2)} m²")
        else:
            st.warning(f"Valeur doit être comprise entre 0 et 100")
    except ValueError:
        st.warning(f"{name} doit être un chiffre")
        variable = 0

def validate_agent_energetique_input(name, value, unit):
    if value is None or value == "":
        st.text(f"{name} doit être un chiffre")
        return 0
    
    try:
        if isinstance(value, (int, float, np.float64)):
            value = float(value)
        else:
            value = float(str(value).replace(',', '.', 1))
        
        if value > 0:
            st.text(f"{name} {value} {unit}")
            return value
        else:
            st.text(f"{name} doit être un chiffre positif")
            return 0
    except ValueError:
        st.text(f"{name} doit être un chiffre")
        return 0


def validate_energie_input(name, variable, unit1, unit2):
    try:
        variable = float(variable.replace(',', '.', 1))
        if variable > 0:
            st.text(f"{name} {variable} {unit1} → {round((variable * 3.6),2)} {unit2}")
        else:
            st.text(f"Valeur doit être positive")
    except ValueError:
        st.text(f"{name} doit être un chiffre")
        variable = 0