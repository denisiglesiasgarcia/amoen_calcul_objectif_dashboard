import streamlit as st
import pandas as pd
from datetime import datetime, date
from bson import ObjectId
from typing import Dict, Any


class DataValidator:
    """Handles data validation and type conversion for MongoDB documents"""

    # Define the schema for project data
    SCHEMA = {
        "nom_projet": {"type": str, "required": True},
        "adresse_projet": {"type": str, "required": False},
        "amoen_id": {"type": str, "required": False},
        "sre_renovation_m2": {"type": float, "required": False},
        "sre_extension_surelevation_m2": {"type": float, "required": False},
        "ef_avant_corr_kwh_m2": {"type": float, "required": False},
        "ef_objectif_pondere_kwh_m2": {"type": float, "required": False},
        "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2": {
            "type": float,
            "required": False,
        },
        "facteur_ponderation_moyen": {"type": float, "required": False},
        "atteinte_objectif": {"type": float, "required": False},
        "periode_start": {"type": datetime, "required": False},
        "periode_end": {"type": datetime, "required": False},
        "date_rapport": {"type": datetime, "required": False},
        "periode_nb_jours": {"type": float, "required": False},
        # Percentage fields
        "sre_pourcentage_habitat_collectif": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_habitat_individuel": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_administration": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_ecoles": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_commerce": {
            "type": float,
            "required": False,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_restauration": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_lieux_de_rassemblement": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_hopitaux": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_industrie": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_depots": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_installations_sportives": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_piscines_couvertes": {
            "type": float,
            "required": True,
            "min": 0,
            "max": 100,
        },
        # Energy agents
        "agent_energetique_ef_mazout_kg": {"type": float, "required": False, "min": 0},
        "agent_energetique_ef_mazout_litres": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_mazout_kwh": {"type": float, "required": False, "min": 0},
        "agent_energetique_ef_gaz_naturel_m3": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_gaz_naturel_kwh": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_bois_buches_dur_stere": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_bois_buches_tendre_stere": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_bois_buches_tendre_kwh": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_pellets_m3": {"type": float, "required": False, "min": 0},
        "agent_energetique_ef_pellets_kg": {"type": float, "required": False, "min": 0},
        "agent_energetique_ef_pellets_kwh": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_plaquettes_m3": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_plaquettes_kwh": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_cad_kwh": {"type": float, "required": False, "min": 0},
        "agent_energetique_ef_electricite_pac_kwh": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_electricite_directe_kwh": {
            "type": float,
            "required": False,
            "min": 0,
        },
        "agent_energetique_ef_autre_kwh": {"type": float, "required": False, "min": 0},
    }

    @classmethod
    def validate_and_convert(
        cls, data: Dict[str, Any]
    ) -> tuple[Dict[str, Any], list[str]]:
        """
        Validates and converts data according to schema.

        Args:
            data: Dictionary of data to validate

        Returns:
            Tuple of (converted_data, error_messages)
        """
        converted_data = {}
        errors = []

        # Process all fields according to schema
        for field, field_schema in cls.SCHEMA.items():
            value = data.get(field)

            # Skip if field is not required and value is None or empty
            if not field_schema["required"] and (value is None or value == ""):
                continue

            try:
                # Convert value to correct type
                if value is not None and value != "":
                    if field_schema["type"] == datetime:
                        # Handle different date/datetime types
                        if isinstance(value, datetime):
                            converted_value = value
                        elif isinstance(value, pd.Timestamp):
                            converted_value = value.to_pydatetime()
                        elif isinstance(value, date):  # Add this to handle date objects
                            converted_value = datetime.combine(
                                value, datetime.min.time()
                            )
                        elif isinstance(value, str):
                            try:
                                # Try different date formats
                                try:
                                    converted_value = datetime.strptime(
                                        value, "%Y-%m-%d"
                                    )
                                except ValueError:
                                    converted_value = datetime.strptime(
                                        value, "%Y-%m-%d %H:%M:%S"
                                    )
                            except ValueError:
                                errors.append(f"{field}: format de date invalide")
                                continue
                        else:
                            errors.append(f"{field}: type de date non supporté")
                            continue
                        value = converted_value
                    else:
                        value = field_schema["type"](value)

                    # Check min/max if specified
                    if "min" in field_schema and value < field_schema["min"]:
                        errors.append(
                            f"{field}: valeur inférieure au minimum permis ({field_schema['min']})"
                        )
                    if "max" in field_schema and value > field_schema["max"]:
                        errors.append(
                            f"{field}: valeur supérieure au maximum permis ({field_schema['max']})"
                        )

                    converted_data[field] = value
                elif field_schema["required"]:
                    errors.append(f"{field}: champ requis manquant")

            except (ValueError, TypeError) as e:
                errors.append(f"{field}: erreur de conversion - {str(e)}")

        return converted_data, errors


def update_project_in_mongodb(
    mycol_historique_sites, project_id: str, updated_data: Dict[str, Any]
) -> bool:
    """Update project in MongoDB with type validation"""
    try:
        # Validate and convert data
        converted_data, errors = DataValidator.validate_and_convert(updated_data)

        if errors:
            st.error("Erreurs de validation:")
            for error in errors:
                st.error(f"- {error}")
            return False

        # Add last modified timestamp
        converted_data["last_modified"] = datetime.now()

        # Perform update
        result = mycol_historique_sites.update_one(
            {"_id": ObjectId(project_id)}, {"$set": converted_data}
        )

        if result.matched_count == 0:
            st.error("Projet non trouvé")
            return False

        if result.modified_count == 0:
            st.warning("Aucune modification effectuée")
            return False

        return True

    except Exception as e:
        st.error(f"Error updating project: {str(e)}")
        return False


def insert_project_to_mongodb(
    mycol_historique_sites, project_data: Dict[str, Any]
) -> bool:
    """Insert new project into MongoDB with type validation"""
    try:
        # Validate and convert data
        converted_data, errors = DataValidator.validate_and_convert(project_data)

        if errors:
            st.error("Erreurs de validation:")
            for error in errors:
                st.error(f"- {error}")
            return False

        if mycol_historique_sites.find_one(
            {"nom_projet": converted_data["nom_projet"]}
        ):
            st.error("Un projet avec ce nom existe déjà")
            return False

        # Add timestamps
        converted_data["date_creation"] = datetime.now()
        converted_data["last_modified"] = datetime.now()

        # Perform insert
        result = mycol_historique_sites.insert_one(converted_data)
        return result.inserted_id is not None

    except Exception as e:
        st.error(f"Error inserting project: {str(e)}")
        return False


def delete_project_from_mongodb(mycol_historique_sites, project_id: str) -> bool:
    """Delete project from MongoDB"""
    try:
        result = mycol_historique_sites.delete_one({"_id": ObjectId(project_id)})
        return result.deleted_count > 0
    except Exception as e:
        st.error(f"Error deleting project: {str(e)}")
        return False


def clear_session_state(preserve_keys=None):
    """
    Clear session state while preserving specified keys.

    Args:
        preserve_keys: List of keys to preserve, defaults to auth keys if None
    """
    if preserve_keys is None:
        preserve_keys = ["authentication_status", "username", "name", "_is_logged_in"]

    # Save preserved state
    preserved_state = {
        key: st.session_state[key] for key in preserve_keys if key in st.session_state
    }

    # Clear everything
    st.session_state.clear()

    # Restore preserved state
    for key, value in preserved_state.items():
        st.session_state[key] = value


def display_database_management(mycol_historique_sites, data_admin):
    """Display database management interface with CRUD operations"""
    st.subheader("Base de données")

    # Convert data to DataFrame and sort by project name and date
    df = pd.DataFrame(data_admin)
    if not df.empty:
        # Convert date_rapport to datetime for proper sorting
        df["date_rapport"] = pd.to_datetime(df["date_rapport"])
        df = df.sort_values(["nom_projet", "date_rapport"])

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
            display_df = df.copy()
            if "date_rapport" in display_df.columns:
                display_df["date_rapport"] = display_df["date_rapport"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            if "date_creation" in display_df.columns:
                display_df["date_creation"] = display_df["date_creation"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            if "last_modified" in display_df.columns:
                display_df["last_modified"] = display_df["last_modified"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            st.dataframe(display_df.drop(columns=["_id"]), use_container_width=True)

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
                key="edit_project_select",
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

                with st.form("edit_project_form"):
                    # Create input fields for each column
                    edited_data = {}
                    non_editable = [
                        "_id",
                        "project_identifier",
                        "date_creation",
                        "last_modified",
                    ]

                    for col in df.columns:
                        if col not in non_editable:
                            current_value = project_data[col]
                            key = f"edit_{selected_project}_{col}"

                            if isinstance(current_value, (int, float)):
                                edited_data[col] = st.number_input(
                                    f"{col}",
                                    value=float(current_value),
                                    format="%.6f",
                                    key=key,
                                )
                            elif isinstance(current_value, pd.Timestamp):
                                date_value = st.date_input(
                                    f"{col}",
                                    value=current_value,
                                    key=key,
                                )
                                edited_data[col] = date_value
                            elif isinstance(current_value, bool):
                                edited_data[col] = st.checkbox(
                                    f"{col}",
                                    value=current_value,
                                    key=key,
                                )
                            else:
                                edited_data[col] = st.text_input(
                                    f"{col}",
                                    value=(
                                        str(current_value)
                                        if current_value is not None
                                        else ""
                                    ),
                                    key=key,
                                )

                    if st.form_submit_button("Sauvegarder les modifications"):
                        if update_project_in_mongodb(
                            mycol_historique_sites,
                            str(project_data["_id"]),
                            edited_data,
                        ):
                            st.success(
                                f"Projet {selected_project} mis à jour avec succès!"
                            )
                            st.rerun()

        with tab_add:
            st.write("Ajouter un nouveau projet")
            with st.form("new_project_form"):
                new_project_data = {
                    "nom_projet": st.text_input("Nom du projet (requis)"),
                    "adresse_projet": st.text_input("Adresse du projet"),
                    "amoen_id": st.text_input("AMOén ID"),
                    "sre_renovation_m2": st.number_input(
                        "SRE rénovée (m²)", min_value=0.0
                    ),
                }

                if st.form_submit_button("Ajouter le projet"):
                    if insert_project_to_mongodb(
                        mycol_historique_sites, new_project_data
                    ):
                        st.success("Nouveau projet ajouté avec succès!")
                        st.rerun()

        with tab_delete:
            st.write("Supprimer un projet")

            # Project selection for deletion
            project_to_delete = st.selectbox(
                "Sélectionner le projet à supprimer",
                df["project_identifier"].unique(),
                key="delete_project_select",
            )

            if project_to_delete:
                # Extract project details
                project_name = project_to_delete.split(" (")[0]
                project_date = project_to_delete.split("(")[1].rstrip(")")

                # Get project data
                project_data = df[
                    (df["nom_projet"] == project_name)
                    & (df["date_rapport"].dt.strftime("%d-%m-%Y") == project_date)
                ].iloc[0]

                # Show warning and confirmation
                st.warning("⚠️ Attention: Cette action est irréversible!")
                st.write(
                    f"Vous êtes sur le point de supprimer le projet: {project_name}"
                )
                st.write(f"Date du rapport: {project_date}")

                # Add a confirmation checkbox
                confirm_delete = st.checkbox(
                    "Je confirme vouloir supprimer ce projet", key="confirm_delete"
                )

                if confirm_delete:
                    if st.button(
                        "Supprimer le projet", type="primary", key="delete_button"
                    ):
                        if delete_project_from_mongodb(
                            mycol_historique_sites, str(project_data["_id"])
                        ):
                            st.success(f"Projet {project_name} supprimé avec succès!")
                            st.rerun()
    else:
        st.info("Aucun projet dans la base de données")

    # Reset cached data
    st.write("Pour afficher les modifications réalisées, veuillez réinitialiser les données en cache")
    if st.button(
        "Réinitialiser données en cache", use_container_width=True, type="primary"
    ):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.clear()
        st.rerun()


def check_mongodb_connection(collection) -> bool:
    """Check if MongoDB connection is alive and working"""
    try:
        collection.database.client.admin.command("ping")
        return True
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {str(e)}")
        return False


def check_mongodb_operation(operation_result: bool, operation_name: str) -> None:
    """Log MongoDB operation results"""
    if not operation_result:
        st.error(f"L'opération {operation_name} a échoué")
        st.info("Veuillez vérifier les logs pour plus de détails")
