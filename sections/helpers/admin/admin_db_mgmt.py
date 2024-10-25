# sections/helpers/admin/admin_db_mgmt.py

import streamlit as st
import pandas as pd
from typing import Dict, Any


def update_project_in_mongodb(
    mycol_historique_sites, project_name: str, updated_data: Dict[str, Any]
) -> bool:
    """
    Update project in MongoDB

    Args:
        mycol_historique_sites: MongoDB collection
        project_name (str): Name of the project to update
        updated_data (Dict[str, Any]): New data for the project

    Returns:
        bool: True if update was successful
    """
    try:
        result = mycol_historique_sites.update_one(
            {"nom_projet": project_name}, {"$set": updated_data}
        )
        return result.modified_count > 0
    except Exception as e:
        st.error(f"Error updating project: {str(e)}")
        return False


def insert_project_to_mongodb(
    mycol_historique_sites, project_data: Dict[str, Any]
) -> bool:
    """
    Insert new project into MongoDB

    Args:
        mycol_historique_sites: MongoDB collection
        project_data (Dict[str, Any]): Project data to insert

    Returns:
        bool: True if insertion was successful
    """
    try:
        # Validate required fields
        if not project_data.get("nom_projet"):
            st.error("Le nom du projet est requis")
            return False

        # Check if project already exists
        if mycol_historique_sites.find_one({"nom_projet": project_data["nom_projet"]}):
            st.error("Un projet avec ce nom existe déjà")
            return False

        result = mycol_historique_sites.insert_one(project_data)
        return result.inserted_id is not None
    except Exception as e:
        st.error(f"Error inserting project: {str(e)}")
        return False


def display_database_management(mycol_historique_sites, data_admin: list):
    """
    Display database management interface with CRUD operations

    Args:
        mycol_historique_sites: MongoDB collection
        data_admin (list): List of project data
    """
    st.subheader("Base de données")

    # Convert data to DataFrame and sort by project name
    df = (
        pd.DataFrame(data_admin).sort_values("nom_projet")
        if data_admin
        else pd.DataFrame()
    )

    if df.empty:
        st.warning("Aucun projet trouvé dans la base de données")
        return

    tab_view, tab_edit, tab_add = st.tabs(
        ["Voir les projets", "Modifier un projet", "Ajouter un projet"]
    )

    with tab_view:
        st.write("Liste des projets dans la base de données")
        # Add search/filter functionality
        search_term = st.text_input("Rechercher un projet", key="search_projects")
        filtered_df = (
            df[df["nom_projet"].str.contains(search_term, case=False)]
            if search_term
            else df
        )
        st.dataframe(filtered_df, use_container_width=True)

    with tab_edit:
        st.write("Modifier un projet existant")
        selected_project = st.selectbox(
            "Sélectionner le projet à modifier",
            df["nom_projet"].unique(),
            key="edit_project",
        )

        if selected_project:
            project_data = df[df["nom_projet"] == selected_project].iloc[0]
            edited_data = {}

            # Group related fields together
            st.write("### Informations générales")
            edited_data["nom_projet"] = st.text_input(
                "Nom du projet", value=project_data["nom_projet"], key="edit_nom_projet"
            )

            # Add other field groups as needed...

            if st.button("Sauvegarder les modifications", type="primary"):
                if st.checkbox("Confirmer la modification?"):
                    if update_project_in_mongodb(
                        mycol_historique_sites, selected_project, edited_data
                    ):
                        st.success(f"Projet {selected_project} mis à jour avec succès!")
                        st.rerun()

    with tab_add:
        st.write("Ajouter un nouveau projet")
        with st.form("new_project_form"):
            new_project_data = {}

            # Required fields first
            new_project_data["nom_projet"] = st.text_input(
                "Nom du projet (requis)", key="new_nom_projet"
            )

            # Group other fields logically
            # Add other fields...

            submit = st.form_submit_button("Ajouter le projet")
            if submit:
                if not new_project_data["nom_projet"]:
                    st.error("Le nom du projet est requis")
                elif insert_project_to_mongodb(
                    mycol_historique_sites, new_project_data
                ):
                    st.success("Nouveau projet ajouté avec succès!")
                    st.rerun()
