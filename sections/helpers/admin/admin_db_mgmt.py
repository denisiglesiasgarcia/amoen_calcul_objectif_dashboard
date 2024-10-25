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


def display_database_management(mycol_historique_sites, data_admin):
    """Display database management interface with CRUD operations"""
    st.subheader("Base de données")

    # Convert data to DataFrame and sort by project name and date
    df = pd.DataFrame(data_admin)
    # Convert date_rapport to datetime for proper sorting
    df["date_rapport"] = pd.to_datetime(df["date_rapport"])
    df = df.sort_values(["nom_projet", "date_rapport"])

    tab_view, tab_edit, tab_add = st.tabs(
        ["Voir les projets", "Modifier un projet", "Ajouter un projet"]
    )

    with tab_view:
        st.write("Liste des projets dans la base de données")
        st.dataframe(df)

    with tab_edit:
        st.write("Modifier un projet existant")

        # Create a combined identifier for selection
        df['project_identifier'] = df.apply(
            lambda x: f"{x['nom_projet']} ({x['date_rapport'].strftime('%d-%m-%Y')})", 
            axis=1
        )

        # Project selection with date
        selected_project_identifier = st.selectbox(
            "Sélectionner le projet à modifier",
            df['project_identifier'].unique(),
            key="edit_project",
        )

        if selected_project_identifier:
            # Extract project name and date from the selection
            selected_project = selected_project_identifier.split(" (")[0]
            selected_date = selected_project_identifier.split("(")[1].rstrip(")")
            
            # Get the specific project data
            project_data = df[
                (df['nom_projet'] == selected_project) & 
                (df['date_rapport'].dt.strftime('%d-%m-%Y') == selected_date)
            ].iloc[0]

            # Create input fields for each column
            edited_data = {}
            for col in df.columns:
                if col not in ['_id', 'project_identifier']:  # Skip MongoDB ID and our custom identifier
                    current_value = project_data[col]

                    # Handle different data types
                    if isinstance(current_value, (int, float)):
                        edited_data[col] = st.number_input(
                            f"{col}", 
                            value=float(current_value),
                            format="%.15f",  # Show up to 15 decimal places
                            step=1e-10,      # Allow very small increments
                            key=f"edit_{col}"
                        )
                    elif isinstance(current_value, bool):
                        edited_data[col] = st.checkbox(
                            f"{col}", 
                            value=current_value, 
                            key=f"edit_{col}"
                        )
                    elif isinstance(current_value, pd.Timestamp) or 'datetime' in str(type(current_value)).lower():
                        date_value = st.date_input(
                            f"{col}", 
                            value=current_value,
                            key=f"edit_{col}"
                        )
                        # Convert to datetime string for MongoDB
                        edited_data[col] = date_value.strftime("%Y-%m-%d")
                    else:
                        edited_data[col] = st.text_input(
                            f"{col}", 
                            value=str(current_value), 
                            key=f"edit_{col}"
                        )

            if "update_success" not in st.session_state:
                st.session_state.update_success = False

            if st.button("Sauvegarder les modifications"):
                try:
                    from bson import ObjectId
                    
                    # Use _id for querying
                    query = {"_id": ObjectId(project_data['_id'])}
                    
                    # Update MongoDB document
                    result = mycol_historique_sites.update_one(
                        query,
                        {"$set": edited_data}
                    )
                    
                    if result.matched_count > 0:
                        if result.modified_count > 0:
                            st.session_state.update_success = True
                            st.experimental_rerun()
                        else:
                            st.warning("Document trouvé mais aucune modification n'a été effectuée")
                    else:
                        st.error("Aucun document trouvé correspondant aux critères")
                        
                except Exception as e:
                    st.error(f"Erreur lors de la mise à jour: {str(e)}")
                    st.write("Type d'erreur:", type(e).__name__)

            # Show success message if update was successful
            if st.session_state.update_success:
                st.success(f"Projet {selected_project_identifier} mis à jour avec succès!")
                st.session_state.update_success = False

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
