import streamlit as st
import pandas as pd
from typing import Dict, Any


def update_project_in_mongodb(
    mycol_historique_sites, project_name: str, updated_data: Dict[str, Any]
) -> bool:
    """Update project in MongoDB"""
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
    """Insert new project into MongoDB"""
    try:
        if not project_data.get("nom_projet"):
            st.error("Le nom du projet est requis")
            return False

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

    def display_defrag_db():
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
            st.dataframe(df, key="view_projects_df")

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

                # Create input fields for each column
                edited_data = {}
                for col in df.columns:
                    if col not in ["_id", "project_identifier"]:
                        current_value = project_data[col]
                        key = f"edit_{selected_project}_{col}"  # Make key unique per project and field

                        if isinstance(current_value, (int, float)):
                            edited_data[col] = st.number_input(
                                f"{col}",
                                value=float(current_value),
                                format="%.15f",
                                step=1e-10,
                                key=key,
                            )
                        elif isinstance(current_value, bool):
                            edited_data[col] = st.checkbox(
                                f"{col}", value=current_value, key=key
                            )
                        elif isinstance(current_value, pd.Timestamp):
                            date_value = st.date_input(
                                f"{col}", value=current_value, key=key
                            )
                            edited_data[col] = date_value.strftime("%Y-%m-%d")
                        else:
                            edited_data[col] = st.text_input(
                                f"{col}", value=str(current_value), key=key
                            )

                if st.button("Sauvegarder les modifications", key="save_edit_button"):
                    try:
                        from bson import ObjectId

                        query = {"_id": ObjectId(project_data["_id"])}
                        result = mycol_historique_sites.update_one(
                            query, {"$set": edited_data}
                        )

                        if result.matched_count > 0:
                            if result.modified_count > 0:
                                st.success(
                                    f"Projet {selected_project_identifier} mis à jour avec succès!"
                                )
                            else:
                                st.warning(
                                    "Document trouvé mais aucune modification n'a été effectuée"
                                )
                        else:
                            st.error("Aucun document trouvé correspondant aux critères")

                    except Exception as e:
                        st.error(f"Erreur lors de la mise à jour: {str(e)}")

        with tab_add:
            st.write("Ajouter un nouveau projet")
            with st.form(key="new_project_form"):
                new_project_data = {}
                new_project_data["nom_projet"] = st.text_input(
                    "Nom du projet (requis)", key="new_project_name"
                )

                submit = st.form_submit_button("Ajouter le projet")
                if submit:
                    if not new_project_data["nom_projet"]:
                        st.error("Le nom du projet est requis")
                    elif insert_project_to_mongodb(
                        mycol_historique_sites, new_project_data
                    ):
                        st.success("Nouveau projet ajouté avec succès!")

    display_defrag_db()

    if st.button(
        "Sauvegarder et actualiser",
        key="save_refresh_button",
        use_container_width=True,
        type="primary",
    ):
        st.success("Données validées")
        st.rerun()
