import streamlit as st
import pandas as pd
from datetime import datetime, date
from bson import ObjectId
from typing import Dict, Any
from sections.helpers.save_excel_streamlit import display_dataframe_with_excel_download
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)


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
            "form_type": "text",
            "label": "Adresse du projet",
            "help": "Si plusieurs adresses, séparez-les par des points-virgules par exemple: 'Chemin Dr-Adolphe-PASTEUR 23;Chemin Dr-Adolphe-PASTEUR 25;Chemin Dr-Adolphe-PASTEUR 27'. Le format d'adresse doit être celui de SITG.",
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
        "travaux_start": {
            "type": datetime,
            "required": True,
            "form_type": "date",
            "label": "Date de début des travaux",
            "default": datetime(1900, 1, 1),
        },
        "travaux_end": {
            "type": datetime,
            "required": True,
            "form_type": "date",
            "label": "Date de fin des travaux",
            "default": datetime(1900, 12, 31),
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
            "type": int,
            "required": False,
            "form_type": "number",
            "step": 1,
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

            elif form_type == "number":
                # Initialize default value
                default_value = 0.0
                if current_value is not None:
                    try:
                        # Check if value is NaN
                        if isinstance(current_value, float) and pd.isna(current_value):
                            default_value = 0.0
                        else:
                            default_value = float(current_value)
                    except (ValueError, TypeError):
                        st.warning(f"Invalid number value for {label}: {current_value}")
                        default_value = 0.0

                # Convert all numeric parameters to float for consistency
                try:
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
                except (ValueError, TypeError):
                    st.warning(f"Invalid numeric parameters for {label}")
                    min_value = 0.0
                    max_value = None
                    step = 1.0

                # Special handling for integer-like values
                if schema.get("format", "%.2f") == "%.0f":
                    try:
                        # Convert to int if the format suggests we want integers
                        default_value = (
                            int(default_value) if not pd.isna(default_value) else 0
                        )
                        min_value = (
                            int(min_value)
                            if min_value is not None and not pd.isna(min_value)
                            else None
                        )
                        max_value = (
                            int(max_value)
                            if max_value is not None and not pd.isna(max_value)
                            else None
                        )
                        step = int(step) if not pd.isna(step) else 1
                    except (ValueError, TypeError):
                        st.warning(
                            f"Error converting to integer for {label}, using defaults"
                        )
                        default_value = 0
                        min_value = 0
                        max_value = None
                        step = 1

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
                    if current_value is not None and not pd.isna(current_value):
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
                    value=(
                        str(current_value)
                        if current_value and not pd.isna(current_value)
                        else ""
                    ),
                    help=help_text,
                )

        except Exception as e:
            st.error(f"Error creating form field for {label}: {str(e)}")
            return None

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

    @classmethod
    def handle_datetime_fields(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Properly handle datetime fields according to schema.
        """
        df = df.copy()

        # Get all datetime fields from schema
        datetime_fields = [
            field
            for field, schema in cls.SCHEMA.items()
            if schema.get("type") == datetime
        ]

        # Convert datetime fields
        for field in datetime_fields:
            if field in df.columns:
                try:
                    # Convert to datetime if it's not already
                    if df[field].dtype != "datetime64[ns]":
                        df[field] = pd.to_datetime(df[field], errors="coerce")
                except Exception as e:
                    logger.warning(f"Error converting {field} to datetime: {str(e)}")

        return df

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
                # Handle empty values
                if value is None or value == "":
                    if field_schema.get("required", False):
                        errors.append(f"{field}: champ requis manquant")
                    continue

                # Special handling for datetime fields
                if field_schema["type"] == datetime:
                    value = cls._convert_to_datetime(value, field, errors)
                    if value is not None:
                        converted_data[field] = value
                    continue

                # Convert other types
                try:
                    value = field_schema["type"](value)
                except (ValueError, TypeError) as e:
                    errors.append(f"{field}: erreur de conversion - {str(e)}")
                    continue

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

            except Exception as e:
                errors.append(f"{field}: erreur de traitement - {str(e)}")

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

    # Add general usage instructions
    with st.expander("ℹ️ Instructions d'utilisation", expanded=True):
        st.markdown(
            """
        ### Comment utiliser cette interface:
        1. **Voir les projets**: Consultez tous les projets existants
        2. **Modifier un projet**: Effectuez des changements sur un projet existant
        3. **Ajouter un projet**: Créez un nouveau projet
        4. **Supprimer un projet**: Supprimez définitivement un projet
        
        ⚠️ **Attention**: 
        - Toute modification ou suppression est **définitive**
        - Vérifiez toujours les informations avant de valider
        - En cas de doute, contactez votre administrateur/trice
        """
        )

    if not check_mongodb_connection(mycol_historique_sites):
        st.error(
            "❌ Impossible de se connecter à la base de données. Veuillez réessayer plus tard ou contacter votre administrateur/trice."
        )
        return

    try:
        # Convert data to DataFrame and sort by project name and date
        df = pd.DataFrame(data_admin)
        if df.empty:
            st.info(
                "📝 La base de données est vide. Utilisez l'onglet 'Ajouter un projet' pour commencer."
            )
            df = DataValidator.handle_datetime_fields(df)
            return

        # Convert date fields to datetime for proper sorting
        for date_field in ["date_rapport", "date_creation", "last_modified"]:
            if date_field in df.columns:
                df[date_field] = pd.to_datetime(df[date_field], errors="coerce")

        # Ensure required columns exist
        required_columns = ["nom_projet", "date_rapport", "_id"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(
                f"❌ Structure de données invalide. Colonnes manquantes: {', '.join(missing_columns)}"
            )
            st.warning("Contactez votre administrateur/trice système.")
            return

        # Sort with handling for null values
        df = df.sort_values(
            ["nom_projet", "date_rapport", "last_modified"],
            ascending=[True, True, False],
            na_position="last",
        )

        tab_view, tab_edit, tab_add, tab_delete = st.tabs(
            [
                "👀 Voir les projets",
                "✏️ Modifier un projet",
                "➕ Ajouter un projet",
                "🗑️ Supprimer un projet",
            ]
        )

        with tab_view:
            st.write("📋 Liste des projets dans la base de données")
            st.info(
                "ℹ️ Utilisez la barre de recherche en haut à droite pour trouver un projet spécifique"
            )
            display_df = df.copy()
            date_columns = ["date_rapport", "date_creation", "last_modified"]
            for col in date_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            display_dataframe_with_excel_download(
                display_df.drop(columns=["_id"]), "dataframe.xslx"
            )

        with tab_edit:
            st.write("✏️ Modifier un projet existant")
            st.warning(
                "⚠️ Assurez-vous de bien vérifier toutes les informations avant de sauvegarder les modifications"
            )

            # Create project identifier with safe handling of null dates
            def create_project_identifier(row):
                try:
                    date_str = (
                        row["date_rapport"].strftime("%d-%m-%Y %H:%M:%S")
                        if pd.notnull(row["date_rapport"])
                        else "Date non définie"
                    )
                    return f"{row['nom_projet']} ({date_str})"
                except (AttributeError, ValueError) as e:
                    return f"{row['nom_projet']} (Date invalide)"

            df["project_identifier"] = df.apply(create_project_identifier, axis=1)

            st.info(
                "💡 Le format du projet est: Nom du projet (Date et heure du rapport)"
            )
            selected_project_identifier = st.selectbox(
                "Sélectionner le projet à modifier",
                df["project_identifier"].unique(),
                key="edit_project_select",
            )

            if selected_project_identifier:
                try:
                    # Extract project name and datetime
                    selected_project = selected_project_identifier.split(" (")[0]
                    selected_datetime = selected_project_identifier.split("(")[
                        1
                    ].rstrip(")")

                    # Find the matching project with proper null handling
                    mask = df["nom_projet"] == selected_project
                    if (
                        selected_datetime != "Date non définie"
                        and selected_datetime != "Date invalide"
                    ):
                        mask &= (
                            df["date_rapport"].dt.strftime("%d-%m-%Y %H:%M:%S")
                            == selected_datetime
                        )

                    if not any(mask):
                        st.error("❌ Projet non trouvé dans la base de données")
                        return

                    project_data = df[mask].iloc[0]

                    with st.form("edit_project_form"):
                        st.info(
                            "📝 Modifiez les champs souhaités puis cliquez sur 'Sauvegarder'"
                        )
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

                        st.warning(
                            "⚠️ Vérifiez bien toutes les informations avant de sauvegarder"
                        )
                        if st.form_submit_button("💾 Sauvegarder les modifications"):
                            with st.spinner("⏳ Validation en cours..."):
                                if update_project_in_mongodb(
                                    mycol_historique_sites,
                                    str(project_data["_id"]),
                                    edited_data,
                                ):
                                    st.success(
                                        f"✅ Projet {selected_project} mis à jour avec succès!"
                                    )
                                    time.sleep(1)
                                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur lors de la modification du projet: {str(e)}")
                    st.info(
                        "💡 Si l'erreur persiste, contactez votre administrateur/trice"
                    )

        with tab_add:
            st.write("➕ Ajouter un nouveau projet")
            st.info(
                "📝 Remplissez tous les champs requis (*) pour créer un nouveau projet"
            )

            with st.form("new_project_form"):
                new_project_data = {}
                st.warning("⚠️ Les champs marqués d'un astérisque (*) sont obligatoires")

                for field, schema in DataValidator.SCHEMA.items():
                    if schema.get("required", True):
                        st.markdown(f"**{schema.get('label', field)}** *")
                        new_project_data[field] = DataValidator.create_form_field(
                            field, schema
                        )

                st.warning(
                    "⚠️ Vérifiez bien toutes les informations avant de créer le projet"
                )
                if st.form_submit_button("➕ Ajouter le projet"):
                    with st.spinner("⏳ Création en cours..."):
                        if insert_project_to_mongodb(
                            mycol_historique_sites, new_project_data
                        ):
                            st.success("✅ Nouveau projet ajouté avec succès!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de la création du projet")
                            st.info(
                                "💡 Vérifiez que tous les champs obligatoires sont remplis correctement"
                            )

        with tab_delete:
            st.write("🗑️ Supprimer un projet")
            st.error(
                "⚠️ ATTENTION: La suppression d'un projet est définitive et irréversible!"
            )

            project_to_delete = st.selectbox(
                "Sélectionner le projet à supprimer",
                df["project_identifier"].unique(),
                key="delete_project_select",
            )

            if project_to_delete:
                try:
                    project_name = project_to_delete.split(" (")[0]
                    project_datetime = project_to_delete.split("(")[1].rstrip(")")

                    # Find the matching project with proper null handling
                    mask = df["nom_projet"] == project_name
                    if (
                        project_datetime != "Date non définie"
                        and project_datetime != "Date invalide"
                    ):
                        mask &= (
                            df["date_rapport"].dt.strftime("%d-%m-%Y %H:%M:%S")
                            == project_datetime
                        )

                    if not any(mask):
                        st.error("❌ Projet non trouvé")
                        return

                    project_data = df[mask].iloc[0]

                    st.error(
                        """
                    ⚠️ ATTENTION: 
                    - Cette action est IRRÉVERSIBLE
                    - Toutes les données du projet seront PERDUES
                    - Cette action ne peut pas être annulée
                    """
                    )

                    st.write(
                        f"🗑️ Vous êtes sur le point de supprimer le projet: **{project_name}**"
                    )
                    st.write(f"📅 Date et heure du rapport: **{project_datetime}**")

                    confirm_delete = st.checkbox(
                        "✅ Je confirme vouloir supprimer ce projet et je comprends que cette action est irréversible",
                        key="confirm_delete",
                    )

                    if confirm_delete:
                        if st.button(
                            "🗑️ Supprimer définitivement le projet",
                            type="primary",
                            key="delete_button",
                        ):
                            with st.spinner("⏳ Suppression en cours..."):
                                if delete_project_from_mongodb(
                                    mycol_historique_sites, str(project_data["_id"])
                                ):
                                    st.success(
                                        f"✅ Projet {project_name} supprimé avec succès!"
                                    )
                                    time.sleep(1)
                                    st.rerun()
                    else:
                        st.info(
                            "💡 Cochez la case de confirmation pour activer le bouton de suppression"
                        )

                except Exception as e:
                    st.error(f"❌ Erreur lors de la suppression du projet: {str(e)}")
                    st.info(
                        "💡 Si l'erreur persiste, contactez votre administrateur/trice"
                    )

    except Exception as e:
        st.error(f"❌ Une erreur inattendue est survenue: {str(e)}")
        st.info("💡 Si l'erreur persiste, contactez votre administrateur/trice")
        return

    # Reset cached data
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "🔄 Actualiser",
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
            "🔁 Réinitialiser complètement",
            use_container_width=True,
            type="secondary",
            help="Réinitialise complètement l'application et déconnecte l'utilisateur",
        ):
            st.warning("⚠️ Cette action va vous déconnecter!")
            time.sleep(2)
            st.cache_data.clear()
            st.cache_resource.clear()
            st.session_state.clear()
            st.rerun()

    # Add footer with support information
    st.markdown("---")
    st.info(
        "💡 En cas de problème ou de question, contactez votre administrateur/trice système"
    )
