import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
import pymongo

# from bson import ObjectId
# import datetime
# import time

MONGODB_URI = "mongodb+srv://streamlit:CYEpm33zdXRVsEJk@cluster0.hkkhetq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# BD mongodb
client = MongoClient(MONGODB_URI)
db_sites = client["amoen_ancienne_methodo"]
mycol_sites = db_sites["sites"]
mycol_resultats = db_sites["historique"]
mycol_auth = db_sites["authentification"]
mycol_avusy = db_sites["avusy"]


def load_csv_in_pandas():
    """
    Load multiple CSV files into pandas DataFrames, process and combine them.
    This function creates a file uploader widget to accept multiple CSV files,
    processes each file to match a specific format, and combines them into a
    single DataFrame. The combined DataFrame is then filtered to include only
    rows within a specific time window around midnight.
    Returns:
        pd.DataFrame: A DataFrame containing the combined and filtered data
        from the uploaded CSV files. If no files are uploaded, returns an
        empty DataFrame with predefined columns.
    """
    # Create a file uploader that accepts multiple CSV files
    csv_files_avusy = st.file_uploader("Choose CSV files", accept_multiple_files=True)

    # Initialize an empty list to hold the DataFrames
    dataframes = []

    columns_long = [
        "time",
        "CRB_AVU10_ELECPAC_ECS_E",
        "CRB_AVU10_ELECPAC_Villas_imm_E",
        "CRB_AVU10_QECS_distribuee_E",
        "CRB_AVU10_QPACCh1_E",
        "CRB_AVU10_QPACCh2_E",
        "CRB_AVU10_QPACECS_E",
        "CRB_AVU10_QPACVillas_E",
        "CRB_AVU10_QPACVImm_E",
    ]

    columns_reduit = [
        "time",
        "Chaleur_Immeuble_ECS",
        "Elec_PAC_Immeuble_Villas",
        "Chaleur_Villas_Chauffage",
        "Chaleur_Immeuble_Chauffage",
    ]

    if csv_files_avusy:
        for file in csv_files_avusy:
            df = pd.read_csv(file, sep=",", skiprows=25, parse_dates=[0])
            col_len = len(df.columns)
            if col_len == 9:
                df.columns = columns_long
                df = df[
                    [
                        "time",
                        "CRB_AVU10_ELECPAC_ECS_E",
                        "CRB_AVU10_ELECPAC_Villas_imm_E",
                        "CRB_AVU10_QPACVillas_E",
                        "CRB_AVU10_QPACVImm_E",
                    ]
                ]
                # Rename columns
                df = df.rename(
                    columns={
                        "CRB_AVU10_ELECPAC_ECS_E": "Chaleur_Immeuble_ECS",
                        "CRB_AVU10_ELECPAC_Villas_imm_E": "Elec_PAC_Immeuble_Villas",
                        "CRB_AVU10_QPACVillas_E": "Chaleur_Villas_Chauffage",
                        "CRB_AVU10_QPACVImm_E": "Chaleur_Immeuble_Chauffage",
                    }
                )
            elif col_len == 5:
                df.columns = columns_reduit

            dataframes.append(df)

        combined_csv = pd.concat(dataframes, ignore_index=True)

        # Tidy up the data
        combined_csv = combined_csv.sort_values(by="time")
        combined_csv = combined_csv.drop_duplicates(subset="time", keep="first")
        combined_csv["time"] = pd.to_datetime(combined_csv["time"])
        combined_csv = combined_csv.reset_index(drop=True)

        # Define the time window around midnight
        start_time = pd.to_datetime("00:00:00").time()
        end_time = pd.to_datetime("00:15:00").time()
        filtered_df = combined_csv[
            combined_csv["time"].dt.time.between(start_time, end_time)
        ]

        st.write(filtered_df, combined_csv)

        return filtered_df

    # Return an empty DataFrame if no files were uploaded
    return pd.DataFrame(columns=columns_reduit)


def plot_avusy_data(df):
    """
    Plots the Avusy data using matplotlib and displays it with Streamlit.
    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data to be plotted.
                           It should have the following columns:
                           - 'time': Timestamps for the x-axis.
                           - 'Chaleur_Immeuble_ECS': Data for Chaleur Immeuble ECS.
                           - 'Elec_PAC_Immeuble_Villas': Data for Elec PAC Immeuble Villas.
                           - 'Chaleur_Villas_Chauffage': Data for Chaleur Villas Chauffage.
                           - 'Chaleur_Immeuble_Chauffage': Data for Chaleur Immeuble Chauffage.
    Returns:
    None
    """
    # Plotting with matplotlib
    if not df.empty:
        # Create a figure and axis for plotting
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot each column in the filtered DataFrame
        ax.plot(df["time"], df["Chaleur_Immeuble_ECS"], label="Chaleur Immeuble ECS")
        ax.plot(
            df["time"], df["Elec_PAC_Immeuble_Villas"], label="Elec PAC Immeuble Villas"
        )
        ax.plot(
            df["time"], df["Chaleur_Villas_Chauffage"], label="Chaleur Villas Chauffage"
        )
        ax.plot(
            df["time"],
            df["Chaleur_Immeuble_Chauffage"],
            label="Chaleur Immeuble Chauffage",
        )

        # Set title and labels
        ax.set_title("Filtered Data Line Plot")
        ax.set_xlabel("Time")
        ax.set_ylabel("Values")
        ax.legend()

        # Rotate date labels for better readability
        plt.xticks(rotation=45)

        # Display the plot
        st.pyplot(fig)
    else:
        st.write("No data available to plot.")


def retrieve_existing_data(mycol_avusy):
    """
    Retrieve existing data from a MongoDB collection and return it as a pandas DataFrame.

    Args:
        mycol_avusy (pymongo.collection.Collection): The MongoDB collection from which to retrieve data.

    Returns:
        pandas.DataFrame: A DataFrame containing the retrieved data. If the collection is empty,
                          returns an empty DataFrame with predefined columns:
                          ['time', 'Chaleur_Immeuble_ECS', 'Elec_PAC_Immeuble_Villas',
                          'Chaleur_Villas_Chauffage', 'Chaleur_Immeuble_Chauffage'].
    """
    documents = list(mycol_avusy.find())
    if documents:
        df_existing = pd.DataFrame(documents)
        df_existing["time"] = pd.to_datetime(df_existing["time"])
    else:
        df_existing = pd.DataFrame(
            columns=[
                "time",
                "Chaleur_Immeuble_ECS",
                "Elec_PAC_Immeuble_Villas",
                "Chaleur_Villas_Chauffage",
                "Chaleur_Immeuble_Chauffage",
            ]
        )
    return df_existing


def find_missing_data(df_existing, df_new):
    """
    Identify and return rows in df_new that are not present in df_existing based on specific columns.

    This function merges df_new with df_existing on the columns 'time', 'Chaleur_Immeuble_ECS',
    'Elec_PAC_Immeuble_Villas', 'Chaleur_Villas_Chauffage', and 'Chaleur_Immeuble_Chauffage'.
    It then filters out the rows that are only present in df_new.

    Parameters:
    df_existing (pd.DataFrame): The existing DataFrame to compare against.
    df_new (pd.DataFrame): The new DataFrame to find missing data from.

    Returns:
    pd.DataFrame: A DataFrame containing rows that are in df_new but not in df_existing.
    """
    merged_df = df_new.merge(
        df_existing,
        on=[
            "time",
            "Chaleur_Immeuble_ECS",
            "Elec_PAC_Immeuble_Villas",
            "Chaleur_Villas_Chauffage",
            "Chaleur_Immeuble_Chauffage",
        ],
        how="left",
        indicator=True,
    )
    missing_data_df = merged_df[merged_df["_merge"] == "left_only"].drop(
        columns=["_merge"]
    )
    return missing_data_df


def insert_missing_data(mycol_avusy, df):
    """
    Inserts missing data from a DataFrame into a MongoDB collection.
    This function removes any '_id' columns from the DataFrame, converts the DataFrame
    into a list of dictionaries, and inserts the data into the specified MongoDB collection.
    If the DataFrame is empty, it will notify that there is no new data to insert.

    Parameters:
    mycol_avusy (pymongo.collection.Collection): The MongoDB collection where data will be inserted.
    df (pandas.DataFrame): The DataFrame containing the data to be inserted.

    Returns:
    None

    Raises:
    pymongo.errors.BulkWriteError: If there is an error during the bulk write operation.
    """
    # Remove any potential '_id' columns
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])

    # Convert DataFrame to list of dictionaries
    rows = df.to_dict(orient="records")

    try:
        if rows:
            result = mycol_avusy.insert_many(rows)
            st.write(
                f"{len(result.inserted_ids)} nouvelle(s) valeurs ajoutées à la base de données."
            )
        else:
            st.write("No new data to insert.")
    except pymongo.errors.BulkWriteError as e:
        st.write(f"BulkWriteError: {e.details}")


def update_existing_data_avusy(mycol_avusy):
    """
    Updates the existing data in the Avusy MongoDB collection.
    This function performs the following steps:
    1. Displays a markdown header for updating the database.
    2. Loads the data from a CSV file into a pandas DataFrame.
    3. Plots the loaded data.
    4. Retrieves existing data from the specified MongoDB collection.
    5. Identifies any missing data by comparing the existing data with the loaded data.
    6. Displays the missing data, if any.
    7. Provides an option to insert the missing data into the MongoDB collection.

    Parameters:
    mycol_avusy (pymongo.collection.Collection): The MongoDB collection where the Avusy data is stored.

    Returns:
    None
    """
    st.markdown(
        '<span style="font-size:1.2em;">**Mise à jour base de données**</span>',
        unsafe_allow_html=True,
    )

    # Load the data
    filtered_df = load_csv_in_pandas()

    # plot data
    plot_avusy_data(filtered_df)

    # Retrieve existing data from MongoDB
    df_existing = retrieve_existing_data(mycol_avusy)

    # Find missing data
    missing_df = find_missing_data(df_existing, filtered_df)

    # Display missing data
    if not missing_df.empty:
        st.info("Nouvelle données qui ne sont pas encore dans la base de données:")
        st.write(missing_df)

        if st.button(
            "Insérer les nouvelles données manquantes dans la base de données"
        ):
            insert_missing_data(mycol_avusy, missing_df)
    else:
        st.info("Toutes les données sont déjà dans la base de données.")


def avusy_consommation_energie_dashboard(start_datetime, end_datetime, mycol_avusy):
    """
    Generates an energy consumption dashboard for the Avusy dataset within a specified date range.

    The function performs the following steps:
    1. Converts the start and end dates to pandas.Timestamp.
    2. Finds the nearest dates in the dataset to the specified start and end dates.
    3. Calculates the number of days between the nearest start and end dates.
    4. Displays the nearest dates and the differences in days using Streamlit markdown.
    5. Checks if the required columns are present in the DataFrame.
    6. Calculates the energy consumption indices for different categories.
    7. Computes the proportions of energy consumption for different categories.
    8. Displays the energy consumption metrics using Streamlit.

    Parameters:
    start_datetime (str or datetime-like): The start date and time for the data range.
    end_datetime (str or datetime-like): The end date and time for the data range.
    mycol_avusy (pymongo.collection.Collection): The MongoDB collection containing the Avusy data.

    Returns:
    None: The function outputs the dashboard directly using Streamlit.

    Raises:
    ValueError: If there is an error finding the nearest dates.
    Exception: If there is an error during the calculation or display of metrics.
    """
    # Convert start and end dates to pandas.Timestamp
    start_datetime = pd.Timestamp(start_datetime)
    end_datetime = pd.Timestamp(end_datetime)

    # Find the nearest date to start_datetime in the DataFrame
    try:
        # Query for all documents in the collection and convert the documents to a pandas DataFrame
        df_index = pd.DataFrame(list(mycol_avusy.find()))

        nearest_start_date = min(
            df_index["time"], key=lambda x: abs(x - start_datetime)
        )
        nearest_end_date = min(df_index["time"], key=lambda x: abs(x - end_datetime))
    except ValueError as e:
        st.error(f"Error finding nearest dates: {e}")
        return

    nearest_start_date_days = (nearest_start_date - start_datetime).days
    nearest_end_date_days = (nearest_end_date - end_datetime).days
    number_of_days = (nearest_end_date - nearest_start_date).days

    st.markdown(
        '<span style="font-size:1.2em;">**Dates proches et énergie consommée sur la période**</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <style>
            .date-info {{
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 10px;
                background-color: #f9f9f9;
                margin-bottom: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .date-info .highlight {{
                color: green;
                font-weight: bold;
            }}
            .date-info .difference {{
                color: blue;
                font-weight: bold;
            }}
        </style>
        <div class="date-info">
            Nearest start date to <span class="highlight">{start_datetime.date()}</span> is <span class="highlight">{nearest_start_date.date()}</span>. 
            Difference: <span class="difference">{nearest_start_date_days} days</span>
        </div>
        <div class="date-info">
            Nearest end date to <span class="highlight">{end_datetime.date()}</span> is <span class="highlight">{nearest_end_date.date()}</span>. 
            Difference: <span class="difference">{nearest_end_date_days} days</span>
        </div>
        <div class="date-info">
            Number of days between <span class="highlight">{nearest_start_date.date()}</span> and 
            <span class="highlight">{nearest_end_date.date()}</span> is <span class="difference">{number_of_days} days</span>
        </div>
    """,
        unsafe_allow_html=True,
    )

    required_columns = [
        "Chaleur_Immeuble_ECS",
        "Chaleur_Immeuble_Chauffage",
        "Chaleur_Villas_Chauffage",
        "Elec_PAC_Immeuble_Villas",
    ]
    if not all(col in df_index.columns for col in required_columns):
        st.error(
            f"The DataFrame does not contain all required columns: {required_columns}"
        )
        return
    try:
        index_chaleur_immeuble_ecs = (
            df_index[df_index["time"] == nearest_end_date][
                "Chaleur_Immeuble_ECS"
            ].values[0]
            - df_index[df_index["time"] == nearest_start_date][
                "Chaleur_Immeuble_ECS"
            ].values[0]
        )
        index_chaleur_immeuble_chauffage = (
            df_index[df_index["time"] == nearest_end_date][
                "Chaleur_Immeuble_Chauffage"
            ].values[0]
            - df_index[df_index["time"] == nearest_start_date][
                "Chaleur_Immeuble_Chauffage"
            ].values[0]
        )
        index_chaleur_villa_chauffage = (
            df_index[df_index["time"] == nearest_end_date][
                "Chaleur_Villas_Chauffage"
            ].values[0]
            - df_index[df_index["time"] == nearest_start_date][
                "Chaleur_Villas_Chauffage"
            ].values[0]
        )

        index_elec_immeuble_villa = (
            df_index[df_index["time"] == nearest_end_date][
                "Elec_PAC_Immeuble_Villas"
            ].values[0]
            - df_index[df_index["time"] == nearest_start_date][
                "Elec_PAC_Immeuble_Villas"
            ].values[0]
        )

        part_chaleur_immeuble_ecs = index_chaleur_immeuble_ecs / (
            index_chaleur_immeuble_ecs
            + index_chaleur_immeuble_chauffage
            + index_chaleur_villa_chauffage
        )
        part_chaleur_immeuble_chauffage = index_chaleur_immeuble_chauffage / (
            index_chaleur_immeuble_ecs
            + index_chaleur_immeuble_chauffage
            + index_chaleur_villa_chauffage
        )
        part_chaleur_villa_chauffage = index_chaleur_villa_chauffage / (
            index_chaleur_immeuble_ecs
            + index_chaleur_immeuble_chauffage
            + index_chaleur_villa_chauffage
        )

        part_elec_immeuble = part_chaleur_immeuble_ecs + part_chaleur_immeuble_chauffage

        container = st.container(border=True)
        with container:

            st.write(
                """
                <style>
                [data-testid="stMetricDelta"] svg {
                    display: none;
                }
                [data-testid="stMetricValue"] {
                    font-size: 18px;
                }
                [data-testid="stMetricLabel"] {
                    font-size: 14px;
                }
                [data-testid="stMetricDelta"] {
                    font-size: 14px;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns(3)
            col1.metric("Immeuble+Villa", f"{int(index_elec_immeuble_villa)} kWh el")
            col2.metric(
                "Immeuble",
                f"{int(index_elec_immeuble_villa * part_elec_immeuble)} kWh el",
                delta=f"{100 * part_elec_immeuble:.1f}%",
                delta_color="off",
            )
            col3.metric(
                "Villa",
                f"{int(index_elec_immeuble_villa * (1 - part_elec_immeuble))} kWh el",
                delta=f"{100 * (1 - part_elec_immeuble):.1f}%",
                delta_color="off",
            )

            col4, col5, col6 = st.columns(3)
            col4.metric(
                "Chauffage Immeuble",
                f"{int(index_chaleur_immeuble_chauffage)} kWh th",
                delta=f"{100 * part_chaleur_immeuble_chauffage:.1f}%",
                delta_color="off",
            )
            col5.metric(
                "ECS Immeuble",
                f"{int(index_chaleur_immeuble_ecs)} kWh th",
                delta=f"{100 * part_chaleur_immeuble_ecs:.1f}%",
                delta_color="off",
            )
            col6.metric(
                "Chauffage Villa",
                f"{int(index_chaleur_villa_chauffage)} kWh th",
                delta=f"{100 * part_chaleur_villa_chauffage:.1f}%",
                delta_color="off",
            )
    except Exception as e:
        st.error(f"Erreur: {e}")


def display_counter_indices(mycol_avusy):
    """
    Display counter indices from the database between two selected dates.

    Parameters:
    mycol_avusy (pymongo.collection.Collection): MongoDB collection containing the counter data
    """
    st.markdown(
        '<span style="font-size:1.2em;">**Affichage des index des compteurs**</span>',
        unsafe_allow_html=True,
    )

    # Get all data from MongoDB to find min and max dates
    df = pd.DataFrame(list(mycol_avusy.find()))
    if df.empty:
        st.error("Aucune donnée trouvée dans la base de données.")
        return

    try:
        # Convert time column to datetime
        df["time"] = pd.to_datetime(df["time"])

        # Get min and max dates from the database
        min_date = df["time"].min()
        max_date = df["time"].max()

        # Create two columns for date selection
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Date de début",
                min_value=min_date.date(),
                max_value=max_date.date(),
                value=min_date.date(),
            )

        with col2:
            end_date = st.date_input(
                "Date de fin",
                min_value=min_date.date(),
                max_value=max_date.date(),
                value=max_date.date(),
            )

        if start_date and end_date:
            if start_date > end_date:
                st.error("La date de début doit être antérieure à la date de fin.")
                return

            # Convert dates to datetime for comparison
            start_mask = df["time"].dt.date == start_date
            end_mask = df["time"].dt.date == end_date

            start_data = df[start_mask].iloc[0] if not df[start_mask].empty else None
            end_data = df[end_mask].iloc[0] if not df[end_mask].empty else None

            if start_data is not None and end_data is not None:
                # Create a container with a border
                container = st.container(border=True)
                with container:
                    st.markdown("### Valeurs des index")

                    # Create columns for start and end dates
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**Date**")
                        st.write(f"Début: {start_date}")
                        st.write(f"Fin: {end_date}")

                    with col2:
                        st.markdown("**Index de début**")
                        st.write(
                            f"Chaleur Immeuble ECS: {start_data['Chaleur_Immeuble_ECS']:.1f}"
                        )
                        st.write(
                            f"Chaleur Immeuble Chauffage: {start_data['Chaleur_Immeuble_Chauffage']:.1f}"
                        )
                        st.write(
                            f"Chaleur Villas Chauffage: {start_data['Chaleur_Villas_Chauffage']:.1f}"
                        )
                        st.write(
                            f"Elec PAC Immeuble Villas: {start_data['Elec_PAC_Immeuble_Villas']:.1f}"
                        )

                    with col3:
                        st.markdown("**Index de fin**")
                        st.write(
                            f"Chaleur Immeuble ECS: {end_data['Chaleur_Immeuble_ECS']:.1f}"
                        )
                        st.write(
                            f"Chaleur Immeuble Chauffage: {end_data['Chaleur_Immeuble_Chauffage']:.1f}"
                        )
                        st.write(
                            f"Chaleur Villas Chauffage: {end_data['Chaleur_Villas_Chauffage']:.1f}"
                        )
                        st.write(
                            f"Elec PAC Immeuble Villas: {end_data['Elec_PAC_Immeuble_Villas']:.1f}"
                        )

                    # Calculate and display differences
                    st.markdown("### Différences d'index")
                    diff_container = st.container(border=True)
                    with diff_container:
                        dcol1, dcol2 = st.columns(2)
                        with dcol1:
                            st.markdown("**Consommation sur la période**")
                            st.write(
                                f"Chaleur Immeuble ECS: {end_data['Chaleur_Immeuble_ECS'] - start_data['Chaleur_Immeuble_ECS']:.1f} kWh"
                            )
                            st.write(
                                f"Chaleur Immeuble Chauffage: {end_data['Chaleur_Immeuble_Chauffage'] - start_data['Chaleur_Immeuble_Chauffage']:.1f} kWh"
                            )
                            st.write(
                                f"Chaleur Villas Chauffage: {end_data['Chaleur_Villas_Chauffage'] - start_data['Chaleur_Villas_Chauffage']:.1f} kWh"
                            )
                            st.write(
                                f"Elec PAC Immeuble Villas: {end_data['Elec_PAC_Immeuble_Villas'] - start_data['Elec_PAC_Immeuble_Villas']:.1f} kWh"
                            )

                        with dcol2:
                            # Calculate daily averages
                            days_diff = (end_date - start_date).days
                            if days_diff > 0:
                                st.markdown("**Moyenne journalière**")
                                st.write(
                                    f"Chaleur Immeuble ECS: {(end_data['Chaleur_Immeuble_ECS'] - start_data['Chaleur_Immeuble_ECS'])/days_diff:.1f} kWh/jour"
                                )
                                st.write(
                                    f"Chaleur Immeuble Chauffage: {(end_data['Chaleur_Immeuble_Chauffage'] - start_data['Chaleur_Immeuble_Chauffage'])/days_diff:.1f} kWh/jour"
                                )
                                st.write(
                                    f"Chaleur Villas Chauffage: {(end_data['Chaleur_Villas_Chauffage'] - start_data['Chaleur_Villas_Chauffage'])/days_diff:.1f} kWh/jour"
                                )
                                st.write(
                                    f"Elec PAC Immeuble Villas: {(end_data['Elec_PAC_Immeuble_Villas'] - start_data['Elec_PAC_Immeuble_Villas'])/days_diff:.1f} kWh/jour"
                                )

            else:
                st.warning("Pas de données disponibles pour les dates sélectionnées.")

    except Exception as e:
        st.error(f"Une erreur s'est produite: {str(e)}")


def avusy_consommation_energie_elec_periode(start_datetime, end_datetime, mycol_avusy):
    """
    Calculate the electrical energy consumption for a given period from a MongoDB collection.

    Parameters:
    start_datetime (str or datetime-like): The start date and time of the period.
    end_datetime (str or datetime-like): The end date and time of the period.
    mycol_avusy (pymongo.collection.Collection): The MongoDB collection containing the data.

    Returns:
    tuple: A tuple containing:
        - conso_elec_pac_immeuble (float or None): The calculated electrical energy consumption for the period.
        - nearest_start_date (Timestamp or None): The nearest start date found in the data.
        - nearest_end_date (Timestamp or None): The nearest end date found in the data.

    Notes:
    - The function retrieves data from the MongoDB collection and converts it to a pandas DataFrame.
    - It checks for the existence of the 'time' column and converts it to pandas datetime.
    - It ensures the start date is before the end date.
    - It calculates the energy consumption for different categories and returns the total electrical energy consumption.
    - If any error occurs during the calculation, it logs the error and returns None for all values.
    """
    # Convert the start and end datetime to pandas Timestamp
    start_datetime = pd.Timestamp(start_datetime)
    end_datetime = pd.Timestamp(end_datetime)

    # Retrieve the data from the MongoDB collection and convert it to a DataFrame
    df_index = pd.DataFrame(list(mycol_avusy.find()))

    # Check if the 'time' column exists in the dataframe
    if "time" not in df_index.columns:
        st.error("La colonne 'time' est absente dans les données récupérées.")
        return

    # Convert the 'time' column to pandas datetime
    df_index["time"] = pd.to_datetime(df_index["time"])

    # Create a new column with only the date part for comparison
    df_index["date"] = df_index["time"].dt.date

    # Convert start and end datetime to date
    start_date = start_datetime.date()
    end_date = end_datetime.date()

    # Ensure the start date is before the end date
    if start_datetime >= end_datetime:
        st.error("La date de début doit être avant la date de fin.")
        return

    # Find the nearest start and end dates in the dataframe
    nearest_start_date = df_index.loc[df_index["date"] >= start_date, "time"].min()
    nearest_end_date = df_index.loc[df_index["date"] <= end_date, "time"].max()

    if pd.isnull(nearest_start_date) or pd.isnull(nearest_end_date):
        st.error(
            f"Pas de données pour les dates spécifiées ({start_date} et {end_date})."
        )
        return None, None, None

    try:
        index_chaleur_immeuble_ecs = (
            df_index.loc[
                df_index["time"] == nearest_end_date, "Chaleur_Immeuble_ECS"
            ].values[0]
            - df_index.loc[
                df_index["time"] == nearest_start_date, "Chaleur_Immeuble_ECS"
            ].values[0]
        )
        index_chaleur_immeuble_chauffage = (
            df_index.loc[
                df_index["time"] == nearest_end_date, "Chaleur_Immeuble_Chauffage"
            ].values[0]
            - df_index.loc[
                df_index["time"] == nearest_start_date, "Chaleur_Immeuble_Chauffage"
            ].values[0]
        )
        index_chaleur_villa_chauffage = (
            df_index.loc[
                df_index["time"] == nearest_end_date, "Chaleur_Villas_Chauffage"
            ].values[0]
            - df_index.loc[
                df_index["time"] == nearest_start_date, "Chaleur_Villas_Chauffage"
            ].values[0]
        )
        index_elec_immeuble_villa = (
            df_index.loc[
                df_index["time"] == nearest_end_date, "Elec_PAC_Immeuble_Villas"
            ].values[0]
            - df_index.loc[
                df_index["time"] == nearest_start_date, "Elec_PAC_Immeuble_Villas"
            ].values[0]
        )

        total_chaleur = (
            index_chaleur_immeuble_ecs
            + index_chaleur_immeuble_chauffage
            + index_chaleur_villa_chauffage
        )

        part_chaleur_immeuble_ecs = (
            index_chaleur_immeuble_ecs / total_chaleur if total_chaleur != 0 else 0
        )
        part_chaleur_immeuble_chauffage = (
            index_chaleur_immeuble_chauffage / total_chaleur
            if total_chaleur != 0
            else 0
        )
        # part_chaleur_villa_chauffage = (
        #     index_chaleur_villa_chauffage / total_chaleur if total_chaleur != 0 else 0
        # )

        part_elec_immeuble = part_chaleur_immeuble_ecs + part_chaleur_immeuble_chauffage
        conso_elec_pac_immeuble = index_elec_immeuble_villa * part_elec_immeuble

        return conso_elec_pac_immeuble, nearest_start_date, nearest_end_date
    except Exception as e:
        st.error(f"Erreur lors du calcul : {e}")
        return None, None, None
