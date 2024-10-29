import streamlit as st
import pandas as pd
from datetime import datetime, date
from bson import ObjectId
from typing import Dict, Any
import time


class DataValidator:
    """Handles data validation and type conversion for MongoDB documents"""

    # Define the schema for project data with form configurations
    SCHEMA = {  # Changed from tuple to dictionary
        "nom_projet": {
            "type": str,
            "required": True,
            "form_type": "text",
            "label": "Nom du projet",
            "help": "Nom unique du projet",
        },
        "adresse_projet": {
            "type": str,
            "required": True,
            "form_type": "text_area",
            "label": "Adresse du projet",
            "help": "Adresse complète du projet (rue, numéro, NPA, ville)",
        },
        "amoen_id": {
            "type": str,
            "required": True,
            "form_type": "text",
            "label": "AMOén ID",
        },
        "sre_renovation_m2": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min_value": 0,
            "step": 0.1,
            "format": "%.2f",
            "label": "SRE rénovée (m²)",
        },
        "ef_avant_corr_kwh_m2": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min_value": 0,
            "step": 0.1,
            "format": "%.2f",
            "label": "Ef avant corr (kWh/m²)",
        },
        "periode_start": {
            "type": datetime,
            "required": False,
            "form_type": "date",
            "label": "Date de début période",
        },
        "periode_end": {
            "type": datetime,
            "required": False,
            "form_type": "date",
            "label": "Date de fin période",
        },
        "date_rapport": {
            "type": datetime,
            "required": False,
            "form_type": "date",
            "label": "Date du rapport",
        },
        "periode_nb_jours": {
            "type": float,
            "required": False,
            "form_type": "number",
            "step": 1,
            "format": "%.0f",
            "label": "Nombre de jours de la période",
        },
        # Percentage fields
        "sre_pourcentage_habitat_collectif": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_habitat_individuel": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_administration": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_ecoles": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_commerce": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_restauration": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_lieux_de_rassemblement": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_hopitaux": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_industrie": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_depots": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_installations_sportives": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        "sre_pourcentage_piscines_couvertes": {
            "type": float,
            "required": True,
            "form_type": "number",
            "min": 0,
            "max": 100,
        },
        # Energy agents
        "agent_energetique_ef_mazout_kg": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_mazout_litres": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_mazout_kwh": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_gaz_naturel_m3": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_gaz_naturel_kwh": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_bois_buches_dur_stere": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_bois_buches_tendre_stere": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_bois_buches_tendre_kwh": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_pellets_m3": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_pellets_kg": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_pellets_kwh": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_plaquettes_m3": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_plaquettes_kwh": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_cad_kwh": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_electricite_pac_kwh": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_electricite_directe_kwh": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
        "agent_energetique_ef_autre_kwh": {
            "type": float,
            "required": False,
            "form_type": "number",
            "min": 0,
        },
    }

    @classmethod
    def create_form_field(cls, key: str, schema: dict, current_value: Any = None):
        """Creates the appropriate form field based on schema definition"""
        form_type = schema.get("form_type", "text")
        label = schema.get("label", key)
        help_text = schema.get("help", "")

        try:
            if form_type == "text":
                return st.text_input(
                    label,
                    value="" if current_value is None else str(current_value),
                    help=help_text,
                )

            elif form_type == "text_area":
                return st.text_area(
                    label,
                    value="" if current_value is None else str(current_value),
                    help=help_text,
                )

            elif form_type == "number":
                # Initialize default value
                default_value = 0.0
                if current_value is not None:
                    try:
                        default_value = float(current_value)
                    except (ValueError, TypeError):
                        st.warning(f"Invalid number value for {label}: {current_value}")

                # Convert all numeric parameters to float for consistency
                min_value = (
                    float(schema.get("min_value", 0))
                    if schema.get("min_value") is not None
                    else None
                )
                max_value = (
                    float(schema.get("max_value"))
                    if schema.get("max_value") is not None
                    else None
                )
                step = float(schema.get("step", 1.0))

                # Special handling for integer-like values
                if schema.get("format", "%.2f") == "%.0f":
                    # Convert to int if the format suggests we want integers
                    default_value = int(default_value)
                    min_value = int(min_value) if min_value is not None else None
                    max_value = int(max_value) if max_value is not None else None
                    step = int(step)

                return st.number_input(
                    label,
                    min_value=min_value,
                    max_value=max_value,
                    value=default_value,
                    step=step,
                    format=schema.get("format", "%.2f"),
                    help=help_text,
                )

            elif form_type == "date":
                try:
                    default_date = datetime.now()
                    if current_value is not None:
                        if isinstance(current_value, pd.Timestamp):
                            default_date = current_value.to_pydatetime()
                        elif isinstance(current_value, datetime):
                            default_date = current_value
                        elif isinstance(current_value, str):
                            default_date = datetime.strptime(current_value, "%Y-%m-%d")
                except (ValueError, TypeError):
                    st.warning(f"Invalid date value for {label}: {current_value}")
                    default_date = datetime.now()

                date_value = st.date_input(label, value=default_date, help=help_text)
                return datetime.combine(date_value, datetime.min.time())

            else:
                return st.text_input(
                    label,
                    value=str(current_value) if current_value else "",
                    help=help_text,
                )

        except Exception as e:
            st.error(f"Error creating form field for {label}: {str(e)}")
            return None

    @classmethod
    def validate_and_convert(
        cls, data: Dict[str, Any]
    ) -> tuple[Dict[str, Any], list[str]]:
        """Validates and converts data according to schema."""
        converted_data = {}
        errors = []

        # Check required fields first
        for field, schema in cls.SCHEMA.items():
            if schema.get("required", False) and field not in data:
                errors.append(f"{field}: champ requis manquant")

        # Process all fields according to schema
        for field, value in data.items():
            if field not in cls.SCHEMA:
                continue  # Skip fields not in schema

            field_schema = cls.SCHEMA[field]

            try:
                # Convert value to correct type
                if value is not None and value != "":
                    if field_schema["type"] == datetime:
                        value = cls._convert_to_datetime(value, field, errors)
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
                elif field_schema.get("required", False):
                    errors.append(f"{field}: champ requis manquant")

            except (ValueError, TypeError) as e:
                errors.append(f"{field}: erreur de conversion - {str(e)}")

        # Validate percentage fields sum to 100%
        percentage_fields = [
            f for f in converted_data.keys() if f.startswith("sre_pourcentage_")
        ]
        if percentage_fields:
            total = sum(converted_data.get(f, 0) for f in percentage_fields)
            if abs(total - 100) > 0.01:  # Allow small floating point differences
                errors.append(
                    f"La somme des pourcentages doit être 100% (actuellement {total}%)"
                )

        return converted_data, errors

    @staticmethod
    def _convert_to_datetime(value, field: str, errors: list) -> datetime:
        """Helper method to convert values to datetime"""
        if isinstance(value, datetime):
            return value
        elif isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        elif isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        elif isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                try:
                    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    errors.append(f"{field}: format de date invalide")
                    return None
        else:
            errors.append(f"{field}: type de date non supporté")
            return None


def check_mongodb_connection(collection) -> bool:
    """Check if MongoDB connection is alive and working"""
    try:
        collection.database.client.admin.command("ping")
        return True
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {str(e)}")
        return False


def update_project_in_mongodb(
    mycol_historique_sites, project_id: str, updated_data: Dict[str, Any]
) -> bool:
    """Update project in MongoDB with type validation"""
    try:
        if not check_mongodb_connection(mycol_historique_sites):
            return False

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
        if not check_mongodb_connection(mycol_historique_sites):
            return False

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
        if not check_mongodb_connection(mycol_historique_sites):
            return False

        result = mycol_historique_sites.delete_one({"_id": ObjectId(project_id)})
        if result.deleted_count == 0:
            st.error("Projet non trouvé")
            return False
        return True
    except Exception as e:
        st.error(f"Error deleting project: {str(e)}")
        return False


def clear_session_state(preserve_keys=None):
    """Clear session state while preserving specified keys."""
    if preserve_keys is None:
        preserve_keys = ["authentication_status", "username", "name", "_is_logged_in"]

    preserved_state = {
        key: st.session_state[key] for key in preserve_keys if key in st.session_state
    }
    st.session_state.clear()
    for key, value in preserved_state.items():
        st.session_state[key] = value


def display_database_management(mycol_historique_sites, data_admin):
    """Display database management interface with CRUD operations"""
    st.subheader("Base de données")

    if not check_mongodb_connection(mycol_historique_sites):
        return

    try:
        # Convert data to DataFrame and sort by project name and date
        df = pd.DataFrame(data_admin)
        if df.empty:
            st.info("Aucun projet dans la base de données")
            return

        # Convert date fields to datetime for proper sorting
        for date_field in ["date_rapport", "date_creation", "last_modified"]:
            if date_field in df.columns:
                df[date_field] = pd.to_datetime(df[date_field])

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
            date_columns = ["date_rapport", "date_creation", "last_modified"]
            for col in date_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(display_df.drop(columns=["_id"]), use_container_width=True)

        with tab_edit:
            st.write("Modifier un projet existant")
            df["project_identifier"] = df.apply(
                lambda x: f"{x['nom_projet']} ({x['date_rapport'].strftime('%d-%m-%Y')})",
                axis=1,
            )

            selected_project_identifier = st.selectbox(
                "Sélectionner le projet à modifier",
                df["project_identifier"].unique(),
                key="edit_project_select",
            )

            if selected_project_identifier:
                # Extract project name and date
                selected_project = selected_project_identifier.split(" (")[0]
                selected_date = selected_project_identifier.split("(")[1].rstrip(")")

                # Get the specific project data
                project_data = df[
                    (df["nom_projet"] == selected_project)
                    & (df["date_rapport"].dt.strftime("%d-%m-%Y") == selected_date)
                ].iloc[0]

                with st.form("edit_project_form"):
                    edited_data = {}
                    non_editable = [
                        "_id",
                        "project_identifier",
                        "date_creation",
                        "last_modified",
                    ]

                    for col in df.columns:
                        if col not in non_editable and col in DataValidator.SCHEMA:
                            current_value = project_data[col]
                            schema = DataValidator.SCHEMA[col]
                            edited_data[col] = DataValidator.create_form_field(
                                col, schema, current_value
                            )

                    if st.form_submit_button("Sauvegarder les modifications"):
                        with st.spinner("Validation en cours..."):
                            if update_project_in_mongodb(
                                mycol_historique_sites,
                                str(project_data["_id"]),
                                edited_data,
                            ):
                                st.success(
                                    f"Projet {selected_project} mis à jour avec succès!"
                                )
                                time.sleep(1)
                                st.rerun()

        with tab_add:
            st.write("Ajouter un nouveau projet")
            with st.form("new_project_form"):
                new_project_data = {}
                for field, schema in DataValidator.SCHEMA.items():
                    if schema.get(
                        "required", True
                    ):  # Show all fields that are required
                        new_project_data[field] = DataValidator.create_form_field(
                            field, schema
                        )

                if st.form_submit_button("Ajouter le projet"):
                    with st.spinner("Création en cours..."):
                        if insert_project_to_mongodb(
                            mycol_historique_sites, new_project_data
                        ):
                            st.success("Nouveau projet ajouté avec succès!")
                            time.sleep(1)
                            st.rerun()

        with tab_delete:
            st.write("Supprimer un projet")
            project_to_delete = st.selectbox(
                "Sélectionner le projet à supprimer",
                df["project_identifier"].unique(),
                key="delete_project_select",
            )

            if project_to_delete:
                project_name = project_to_delete.split(" (")[0]
                project_date = project_to_delete.split("(")[1].rstrip(")")

                project_data = df[
                    (df["nom_projet"] == project_name)
                    & (df["date_rapport"].dt.strftime("%d-%m-%Y") == project_date)
                ].iloc[0]

                st.warning("⚠️ Attention: Cette action est irréversible!")
                st.write(
                    f"Vous êtes sur le point de supprimer le projet: {project_name}"
                )
                st.write(f"Date du rapport: {project_date}")

                confirm_delete = st.checkbox(
                    "Je confirme vouloir supprimer ce projet", key="confirm_delete"
                )

                if confirm_delete:
                    if st.button(
                        "Supprimer le projet", type="primary", key="delete_button"
                    ):
                        with st.spinner("Suppression en cours..."):
                            if delete_project_from_mongodb(
                                mycol_historique_sites, str(project_data["_id"])
                            ):
                                st.success(
                                    f"Projet {project_name} supprimé avec succès!"
                                )
                                time.sleep(1)
                                st.rerun()

    except Exception as e:
        st.error(f"Une erreur est survenue: {str(e)}")
        return

    # Reset cached data
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Actualiser",
            use_container_width=True,
            type="primary",
            help="Actualise les données en conservant la session",
        ):
            st.cache_data.clear()
            st.cache_resource.clear()
            clear_session_state()
            st.rerun()

    with col2:
        if st.button(
            "Réinitialiser complètement",
            use_container_width=True,
            type="secondary",
            help="Réinitialise complètement l'application et déconnecte l'utilisateur",
        ):
            st.warning("⚠️ Cette action va vous déconnecter!")
            st.cache_data.clear()
            st.cache_resource.clear()
            st.session_state.clear()
            st.rerun()
