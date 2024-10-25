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

        # Create a combined identifier for selection
        df["project_identifier"] = df.apply(
            lambda x: f"{x['nom_projet']} ({x['date_rapport'].strftime('%d-%m-%Y')})",
            axis=1,
        )

        # Project selection with date
        selected_project_identifier = st.selectbox(
            "Sélectionner le projet à modifier",
            df["project_identifier"].unique(),
            key="edit_project",
        )

        if selected_project_identifier:
            # Extract project name and date from the selection
            selected_project = selected_project_identifier.split(" (")[0]
            selected_date = selected_project_identifier.split("(")[1].rstrip(")")

            # Get the specific project data
            project_data = df[
                (df["nom_projet"] == selected_project)
                & (df["date_rapport"].dt.strftime("%d-%m-%Y") == selected_date)
            ].iloc[0]

            # Create input fields for each column
            edited_data = {}
            for col in df.columns:
                if col not in [
                    "_id",
                    "project_identifier",
                ]:  # Skip MongoDB ID and our custom identifier
                    current_value = project_data[col]

                    # Handle different data types
                    if isinstance(current_value, (int, float)):
                        edited_data[col] = st.number_input(
                            f"{col}", value=float(current_value), key=f"edit_{col}"
                        )
                    elif isinstance(current_value, bool):
                        edited_data[col] = st.checkbox(
                            f"{col}", value=current_value, key=f"edit_{col}"
                        )
                    elif isinstance(current_value, pd.Timestamp):
                        edited_data[col] = st.date_input(
                            f"{col}", value=current_value, key=f"edit_{col}"
                        )
                    else:
                        edited_data[col] = st.text_input(
                            f"{col}", value=str(current_value), key=f"edit_{col}"
                        )

            if st.button("Sauvegarder les modifications"):
                try:
                    # Update MongoDB document using both name and date for precise matching
                    result = mycol_historique_sites.update_one(
                        {
                            "nom_projet": selected_project,
                            "date_rapport": project_data["date_rapport"].strftime(
                                "%Y-%m-%d"
                            ),
                        },
                        {"$set": edited_data},
                    )
                    if result.modified_count > 0:
                        st.success(
                            f"Projet {selected_project_identifier} mis à jour avec succès!"
                        )
                        st.rerun()
                    else:
                        st.error("Erreur lors de la mise à jour du projet")
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")

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
