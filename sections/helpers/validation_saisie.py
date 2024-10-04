import streamlit as st
import numpy as np


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
            st.text(f"Valeur doit être positive")
    except ValueError:
        st.text(f"{name} doit être un chiffre")
        variable = 0
