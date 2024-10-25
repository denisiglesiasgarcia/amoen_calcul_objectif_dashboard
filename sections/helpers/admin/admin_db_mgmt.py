import streamlit as st
import pandas as pd
from datetime import datetime
from bson import ObjectId
from typing import Dict, Any, Optional, List, Tuple
from pymongo.results import UpdateResult, InsertOneResult, DeleteResult


def check_mongodb_connection(collection) -> bool:
    """
    Check if MongoDB connection is alive and working.

    Args:
        collection: MongoDB collection

    Returns:
        Boolean indicating if connection is working
    """
    try:
        # Ping the database
        collection.database.client.admin.command("ping")
        return True
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return False


def validate_project_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate project data before database operations.

    Args:
        data: Dictionary containing project data

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data.get("nom_projet"):
        return False, "Le nom du projet est requis"

    # Check numeric fields
    numeric_fields = [
        "sre_renovation_m2",
        "ef_avant_corr_kwh_m2",
        "ef_objectif_pondere_kwh_m2",
    ]
    for field in numeric_fields:
        if field in data and data[field] is not None:
            try:
                float(data[field])
            except ValueError:
                return False, f"Le champ {field} doit être un nombre"

    return True, ""


def verify_update_result(
    result: UpdateResult, expected_changes: int = 1
) -> Tuple[bool, str]:
    """
    Verify the result of a MongoDB update operation.

    Args:
        result: MongoDB UpdateResult object
        expected_changes: Number of documents expected to be modified

    Returns:
        Tuple of (success, message)
    """
    if result.matched_count == 0:
        return False, "Aucun document trouvé pour la mise à jour"
    if result.matched_count != expected_changes:
        return (
            False,
            f"Nombre incorrect de documents trouvés: {result.matched_count} (attendu: {expected_changes})",
        )
    if result.modified_count == 0:
        return False, "Document trouvé mais aucune modification effectuée"
    if result.modified_count != expected_changes:
        return (
            False,
            f"Nombre incorrect de documents modifiés: {result.modified_count} (attendu: {expected_changes})",
        )
    return True, "Mise à jour effectuée avec succès"


def verify_insert_result(result: InsertOneResult) -> Tuple[bool, str]:
    """
    Verify the result of a MongoDB insert operation.

    Args:
        result: MongoDB InsertOneResult object

    Returns:
        Tuple of (success, message)
    """
    if not result.inserted_id:
        return False, "Échec de l'insertion du document"
    return True, "Document inséré avec succès"


def verify_delete_result(
    result: DeleteResult, expected_deletes: int = 1
) -> Tuple[bool, str]:
    """
    Verify the result of a MongoDB delete operation.

    Args:
        result: MongoDB DeleteResult object
        expected_deletes: Number of documents expected to be deleted

    Returns:
        Tuple of (success, message)
    """
    if result.deleted_count == 0:
        return False, "Aucun document trouvé pour la suppression"
    if result.deleted_count != expected_deletes:
        return (
            False,
            f"Nombre incorrect de documents supprimés: {result.deleted_count} (attendu: {expected_deletes})",
        )
    return True, "Suppression effectuée avec succès"


def format_project_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format and clean project data before database operations.

    Args:
        data: Dictionary containing project data

    Returns:
        Formatted data dictionary
    """
    formatted_data = {}

    for key, value in data.items():
        # Skip None values and empty strings
        if value is None or value == "":
            continue

        # Convert string numbers to float where appropriate
        if isinstance(value, str) and value.replace(".", "").replace("-", "").isdigit():
            try:
                formatted_data[key] = float(value)
                continue
            except ValueError:
                pass

        # Handle dates
        if key in ["periode_start", "periode_end", "date_rapport"]:
            if isinstance(value, str):
                try:
                    formatted_data[key] = datetime.strptime(value, "%Y-%m-%d")
                    continue
                except ValueError:
                    pass
            elif isinstance(value, datetime):
                formatted_data[key] = value
                continue

        formatted_data[key] = value

    return formatted_data


def get_project_by_id(collection, project_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a project by its ObjectId.

    Args:
        collection: MongoDB collection
        project_id: Project ID string

    Returns:
        Project document or None if not found
    """
    try:
        if not check_mongodb_connection(collection):
            return None

        project = collection.find_one({"_id": ObjectId(project_id)})
        if not project:
            st.error("Projet non trouvé")
            return None
        return project
    except Exception as e:
        st.error(f"Error retrieving project: {str(e)}")
        return None


def update_project(collection, project_id: str, data: Dict[str, Any]) -> bool:
    """
    Update an existing project in the database.

    Args:
        collection: MongoDB collection
        project_id: Project ID string
        data: Updated project data

    Returns:
        Boolean indicating success
    """
    try:
        if not check_mongodb_connection(collection):
            return False

        # Validate data
        is_valid, error = validate_project_data(data)
        if not is_valid:
            st.error(error)
            return False

        # Format data
        formatted_data = format_project_data(data)

        # Add last modified timestamp
        formatted_data["last_modified"] = datetime.now()

        # Update document
        result = collection.update_one(
            {"_id": ObjectId(project_id)}, {"$set": formatted_data}
        )

        # Verify the update
        success, message = verify_update_result(result)
        if not success:
            st.error(message)
            return False

        # Double-check the updated document
        updated_doc = get_project_by_id(collection, project_id)
        if not updated_doc:
            st.error("Impossible de vérifier les modifications")
            return False

        # Verify key fields were updated correctly
        for key, value in formatted_data.items():
            if updated_doc.get(key) != value:
                st.error(f"La mise à jour du champ {key} a échoué")
                return False

        return True

    except Exception as e:
        st.error(f"Error updating project: {str(e)}")
        return False


def create_project(collection, data: Dict[str, Any]) -> bool:
    """
    Create a new project in the database.

    Args:
        collection: MongoDB collection
        data: Project data

    Returns:
        Boolean indicating success
    """
    try:
        if not check_mongodb_connection(collection):
            return False

        # Validate data
        is_valid, error = validate_project_data(data)
        if not is_valid:
            st.error(error)
            return False

        # Check for duplicate project name
        existing_project = collection.find_one({"nom_projet": data["nom_projet"]})
        if existing_project:
            st.error("Un projet avec ce nom existe déjà")
            return False

        # Format data
        formatted_data = format_project_data(data)
        formatted_data["date_creation"] = datetime.now()
        formatted_data["last_modified"] = datetime.now()

        # Insert document
        result = collection.insert_one(formatted_data)

        # Verify the insertion
        success, message = verify_insert_result(result)
        if not success:
            st.error(message)
            return False

        # Double-check the inserted document
        inserted_doc = get_project_by_id(collection, str(result.inserted_id))
        if not inserted_doc:
            st.error("Impossible de vérifier l'insertion")
            return False

        # Verify key fields were inserted correctly
        for key, value in formatted_data.items():
            if inserted_doc.get(key) != value:
                st.error(f"L'insertion du champ {key} a échoué")
                collection.delete_one({"_id": result.inserted_id})  # Rollback
                return False

        return True

    except Exception as e:
        st.error(f"Error creating project: {str(e)}")
        return False


def delete_project(collection, project_id: str) -> bool:
    """
    Delete a project from the database.

    Args:
        collection: MongoDB collection
        project_id: Project ID string

    Returns:
        Boolean indicating success
    """
    try:
        if not check_mongodb_connection(collection):
            return False

        # Get project before deletion for verification
        project = get_project_by_id(collection, project_id)
        if not project:
            return False

        # Delete document
        result = collection.delete_one({"_id": ObjectId(project_id)})

        # Verify the deletion
        success, message = verify_delete_result(result)
        if not success:
            st.error(message)
            return False

        # Double-check the deletion
        deleted_check = get_project_by_id(collection, project_id)
        if deleted_check:
            st.error("La suppression n'a pas été effectuée correctement")
            return False

        return True

    except Exception as e:
        st.error(f"Error deleting project: {str(e)}")
        return False


def display_database_management(collection, data_admin: List[Dict[str, Any]]):
    """
    Display the database management interface.

    Args:
        collection: MongoDB collection
        data_admin: List of all project documents
    """
    st.subheader("Gestion de la base de données")

    # Check database connection
    if not check_mongodb_connection(collection):
        st.error("Impossible de se connecter à la base de données")
        return

    # Convert data to DataFrame for display
    df = pd.DataFrame(data_admin)
    if not df.empty:
        # Convert dates to datetime
        date_columns = ["date_rapport", "date_creation", "last_modified"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        df = df.sort_values(["nom_projet", "date_rapport"])

    # Create tabs for different operations
    tab_view, tab_edit, tab_add, tab_delete = st.tabs(
        [
            "Voir les projets",
            "Modifier un projet",
            "Ajouter un projet",
            "Supprimer un projet",
        ]
    )

    with tab_view:
        st.write("Liste des projets dans la base de données")
        if not df.empty:
            # Format dates for display
            display_df = df.copy()
            for col in date_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(display_df.drop(columns=["_id"]), use_container_width=True)
        else:
            st.info("Aucun projet dans la base de données")

    with tab_edit:
        st.write("Modifier un projet existant")
        if not df.empty:
            # Create project selector
            df["project_identifier"] = df.apply(
                lambda x: f"{x['nom_projet']} ({x['date_rapport'].strftime('%Y-%m-%d %H:%M')})",
                axis=1,
            )

            selected_identifier = st.selectbox(
                "Sélectionner le projet à modifier", df["project_identifier"].unique()
            )

            if selected_identifier:
                project_name = selected_identifier.split(" (")[0]
                project_data = df[df["nom_projet"] == project_name].iloc[0]

                with st.form("edit_project_form"):
                    edited_data = {}

                    # Create input fields for editable columns
                    non_editable = [
                        "_id",
                        "project_identifier",
                        "date_creation",
                        "last_modified",
                    ]
                    for col in df.columns:
                        if col not in non_editable:
                            current_value = project_data[col]

                            if isinstance(current_value, (int, float)):
                                edited_data[col] = st.number_input(
                                    f"{col}", value=float(current_value), format="%.6f"
                                )
                            elif isinstance(current_value, pd.Timestamp):
                                edited_data[col] = st.date_input(
                                    f"{col}", value=current_value
                                )
                            else:
                                edited_data[col] = st.text_input(
                                    f"{col}",
                                    value=(
                                        str(current_value)
                                        if current_value is not None
                                        else ""
                                    ),
                                )

                    if st.form_submit_button("Sauvegarder les modifications"):
                        with st.spinner("Mise à jour en cours..."):
                            if update_project(
                                collection, str(project_data["_id"]), edited_data
                            ):
                                st.success(
                                    f"Projet {project_name} mis à jour avec succès!"
                                )
                                st.rerun()
        else:
            st.info("Aucun projet à modifier")

    with tab_add:
        st.write("Ajouter un nouveau projet")
        with st.form("new_project_form"):
            new_project_data = {
                "nom_projet": st.text_input("Nom du projet (requis)"),
                "adresse_projet": st.text_input("Adresse du projet"),
                "amoen_id": st.text_input("AMOén ID"),
                "sre_renovation_m2": st.number_input("SRE rénovée (m²)", min_value=0.0),
            }

            if st.form_submit_button("Ajouter le projet"):
                with st.spinner("Création en cours..."):
                    if create_project(collection, new_project_data):
                        st.success("Nouveau projet ajouté avec succès!")
                        st.rerun()

    with tab_delete:
        st.write("Supprimer un projet")
        if not df.empty:
            project_to_delete = st.selectbox(
                "Sélectionner le projet à supprimer", df["project_identifier"].unique()
            )

            if project_to_delete:
                project_name = project_to_delete.split(" (")[0]
                project_data = df[df["nom_projet"] == project_name].iloc[0]

                st.warning("⚠️ Attention: Cette action est irréversible!")
