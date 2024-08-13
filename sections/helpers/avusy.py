import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
from bson import ObjectId
import datetime

MONGODB_URI = "mongodb+srv://streamlit:CYEpm33zdXRVsEJk@cluster0.hkkhetq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# BD mongodb
client = MongoClient(MONGODB_URI)
db_sites = client['amoen_ancienne_methodo']
mycol_sites = db_sites["sites"]
mycol_resultats = db_sites["historique"]
mycol_auth = db_sites["authentification"]
mycol_avusy = db_sites["avusy"]

def load_csv_in_pandas():
    # Create a file uploader that accepts multiple CSV files
    csv_files_avusy = st.file_uploader("Choose CSV files", accept_multiple_files=True)

    # Initialize an empty list to hold the DataFrames
    dataframes = []

    columns_long = [
        'time',
        "CRB_AVU10_ELECPAC_ECS_E",
        "CRB_AVU10_ELECPAC_Villas_imm_E",
        "CRB_AVU10_QECS_distribuee_E",
        "CRB_AVU10_QPACCh1_E",
        "CRB_AVU10_QPACCh2_E",
        "CRB_AVU10_QPACECS_E",
        "CRB_AVU10_QPACVillas_E",
        "CRB_AVU10_QPACVImm_E"
    ]

    columns_reduit = [
        'time',
        'Chaleur_Immeuble_ECS',
        'Elec_PAC_Immeuble_Villas',
        'Chaleur_Villas_Chauffage',
        'Chaleur_Immeuble_Chauffage'
    ]

    if csv_files_avusy:
        for file in csv_files_avusy:
            df = pd.read_csv(file, sep=",", skiprows=25, parse_dates=[0])
            col_len = len(df.columns)
            if col_len == 9:
                df.columns = columns_long
                df = df[['time', "CRB_AVU10_ELECPAC_ECS_E", "CRB_AVU10_ELECPAC_Villas_imm_E",
                         "CRB_AVU10_QPACVillas_E", "CRB_AVU10_QPACVImm_E"]]
                # Rename columns
                df = df.rename(columns={
                    "CRB_AVU10_ELECPAC_ECS_E": "Chaleur_Immeuble_ECS",
                    "CRB_AVU10_ELECPAC_Villas_imm_E": "Elec_PAC_Immeuble_Villas",
                    "CRB_AVU10_QPACVillas_E": "Chaleur_Villas_Chauffage",
                    "CRB_AVU10_QPACVImm_E": "Chaleur_Immeuble_Chauffage"
                })
            elif col_len == 5:
                df.columns = columns_reduit

            dataframes.append(df)

        combined_csv = pd.concat(dataframes, ignore_index=True)

        # Tidy up the data
        combined_csv = combined_csv.sort_values(by='time')
        combined_csv = combined_csv.drop_duplicates(subset='time', keep='first')
        combined_csv['time'] = pd.to_datetime(combined_csv['time'])
        combined_csv = combined_csv.reset_index(drop=True)

        # Define the time window around midnight
        start_time = pd.to_datetime('00:00:00').time()
        end_time = pd.to_datetime('00:30:00').time()
        filtered_df = combined_csv[combined_csv['time'].dt.time.between(start_time, end_time)]

        # Keep only the 1st and 15th of every month
        filtered_df = filtered_df[filtered_df['time'].dt.day.isin([1, 15, 30, 31])]

        st.write(filtered_df, combined_csv)

        return filtered_df
    
    # Return an empty DataFrame if no files were uploaded
    return pd.DataFrame(columns=columns_reduit)

def plot_avusy_data(df):
    # Plotting with matplotlib
    if not df.empty:
        # Create a figure and axis for plotting
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot each column in the filtered DataFrame
        ax.plot(df['time'], df['Chaleur_Immeuble_ECS'], label='Chaleur Immeuble ECS')
        ax.plot(df['time'], df['Elec_PAC_Immeuble_Villas'], label='Elec PAC Immeuble Villas')
        ax.plot(df['time'], df['Chaleur_Villas_Chauffage'], label='Chaleur Villas Chauffage')
        ax.plot(df['time'], df['Chaleur_Immeuble_Chauffage'], label='Chaleur Immeuble Chauffage')

        # Set title and labels
        ax.set_title('Filtered Data Line Plot')
        ax.set_xlabel('Time')
        ax.set_ylabel('Values')
        ax.legend()

        # Rotate date labels for better readability
        plt.xticks(rotation=45)

        # Display the plot
        st.pyplot(fig)
    else:
        st.write("No data available to plot.")

def retrieve_existing_data(mycol_avusy):
    documents = list(mycol_avusy.find())
    if documents:
        df_existing = pd.DataFrame(documents)
        df_existing['time'] = pd.to_datetime(df_existing['time'])
    else:
        df_existing = pd.DataFrame(columns=['time', 'Chaleur_Immeuble_ECS', 'Elec_PAC_Immeuble_Villas', 'Chaleur_Villas_Chauffage', 'Chaleur_Immeuble_Chauffage'])
    return df_existing

def find_missing_data(df_existing, df_new):
    merged_df = df_new.merge(df_existing, on=['time', 'Chaleur_Immeuble_ECS', 'Elec_PAC_Immeuble_Villas', 'Chaleur_Villas_Chauffage', 'Chaleur_Immeuble_Chauffage'], how='left', indicator=True)
    missing_data_df = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])
    return missing_data_df

def insert_missing_data(mycol_avusy, df):
    # Remove any potential '_id' columns
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    
    # Convert DataFrame to list of dictionaries
    rows = df.to_dict(orient='records')
    
    try:
        if rows:
            result = mycol_avusy.insert_many(rows)
            st.write(f"{len(result.inserted_ids)} nouvelle(s) valeurs ajoutées à la base de données.")
        else:
            st.write("No new data to insert.")
    except pymongo.errors.BulkWriteError as e:
        st.write(f"BulkWriteError: {e.details}")

def update_existing_data_avusy(mycol_avusy):
    st.markdown('<span style="font-size:1.2em;">**Mise à jour base de données**</span>', unsafe_allow_html=True)
    
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

        if st.button("Insérer les nouvelles données manquantes dans la base de données"):
            insert_missing_data(mycol_avusy, missing_df)
    else:
        st.info("Toutes les données sont déjà dans la base de données.")




def avusy_consommation_energie_dashboard(start_datetime, end_datetime, mycol_avusy):
    # Convert start and end dates to pandas.Timestamp
    start_datetime = pd.Timestamp(start_datetime)
    end_datetime = pd.Timestamp(end_datetime)

    # Find the nearest date to start_datetime in the DataFrame
    try:
        # Query for all documents in the collection and convert the documents to a pandas DataFrame
        df_index = pd.DataFrame(list(mycol_avusy.find()))
        
        nearest_start_date = min(df_index['time'], key=lambda x: abs(x - start_datetime))
        nearest_end_date = min(df_index['time'], key=lambda x: abs(x - end_datetime))
    except ValueError as e:
        st.error(f"Error finding nearest dates: {e}")
        return

    nearest_start_date_days = (nearest_start_date - start_datetime).days
    nearest_end_date_days = (nearest_end_date - end_datetime).days
    number_of_days = (nearest_end_date - nearest_start_date).days

    st.markdown('<span style="font-size:1.2em;">**Dates proches et énergie consommée sur la période**</span>', unsafe_allow_html=True)
    st.markdown(f"""
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
    """, unsafe_allow_html=True)

    required_columns = ['Chaleur_Immeuble_ECS', 'Chaleur_Immeuble_Chauffage', 'Chaleur_Villas_Chauffage', 'Elec_PAC_Immeuble_Villas']
    if not all(col in df_index.columns for col in required_columns):
        st.error(f"The DataFrame does not contain all required columns: {required_columns}")
        return
    try:
        index_chaleur_immeuble_ecs = df_index[df_index['time'] == nearest_end_date]['Chaleur_Immeuble_ECS'].values[0] - \
            df_index[df_index['time'] == nearest_start_date]['Chaleur_Immeuble_ECS'].values[0]
        index_chaleur_immeuble_chauffage = df_index[df_index['time'] == nearest_end_date]['Chaleur_Immeuble_Chauffage'].values[0] - \
            df_index[df_index['time'] == nearest_start_date]['Chaleur_Immeuble_Chauffage'].values[0]
        index_chaleur_villa_chauffage = df_index[df_index['time'] == nearest_end_date]['Chaleur_Villas_Chauffage'].values[0] - \
            df_index[df_index['time'] == nearest_start_date]['Chaleur_Villas_Chauffage'].values[0]

        index_elec_immeuble_villa = df_index[df_index['time'] == nearest_end_date]['Elec_PAC_Immeuble_Villas'].values[0] - \
            df_index[df_index['time'] == nearest_start_date]['Elec_PAC_Immeuble_Villas'].values[0]

        part_chaleur_immeuble_ecs = index_chaleur_immeuble_ecs / (index_chaleur_immeuble_ecs + index_chaleur_immeuble_chauffage + index_chaleur_villa_chauffage)
        part_chaleur_immeuble_chauffage = index_chaleur_immeuble_chauffage / (index_chaleur_immeuble_ecs + index_chaleur_immeuble_chauffage + index_chaleur_villa_chauffage)
        part_chaleur_villa_chauffage = index_chaleur_villa_chauffage / (index_chaleur_immeuble_ecs + index_chaleur_immeuble_chauffage + index_chaleur_villa_chauffage)

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
            col2.metric("Immeuble", f'{int(index_elec_immeuble_villa * part_elec_immeuble)} kWh el', delta=f"{100 * part_elec_immeuble:.1f}%", delta_color="off")
            col3.metric("Villa", f"{int(index_elec_immeuble_villa * (1 - part_elec_immeuble))} kWh el", delta=f"{100 * (1 - part_elec_immeuble):.1f}%", delta_color="off")

            col4, col5, col6 = st.columns(3)
            col4.metric("Chauffage Immeuble", f"{int(index_chaleur_immeuble_chauffage)} kWh th", delta=f"{100 * part_chaleur_immeuble_chauffage:.1f}%", delta_color="off")
            col5.metric("ECS Immeuble", f"{int(index_chaleur_immeuble_ecs)} kWh th", delta=f"{100 * part_chaleur_immeuble_ecs:.1f}%", delta_color="off")
            col6.metric("Chauffage Villa", f"{int(index_chaleur_villa_chauffage)} kWh th", delta=f"{100 * part_chaleur_villa_chauffage:.1f}%", delta_color="off")
    except Exception as e:
        st.error(f"Erreur: {e}")

def avusy_consommation_energie_elec_periode(start_datetime, end_datetime, mycol_avusy):
    # Convert the start and end datetime to pandas Timestamp
    start_datetime = pd.Timestamp(start_datetime)
    end_datetime = pd.Timestamp(end_datetime)
    
    # Retrieve the data from the MongoDB collection and convert it to a DataFrame
    df_index = pd.DataFrame(list(mycol_avusy.find()))
    
    # Check if the 'time' column exists in the dataframe
    if 'time' not in df_index.columns:
        st.error("La colonne 'time' est absente dans les données récupérées.")
        return
    
    # Convert the 'time' column to pandas datetime
    df_index['time'] = pd.to_datetime(df_index['time'])
    
    # Create a new column with only the date part for comparison
    df_index['date'] = df_index['time'].dt.date
    
    # Convert start and end datetime to date
    start_date = start_datetime.date()
    end_date = end_datetime.date()
    
    # Ensure the start date is before the end date
    if start_datetime >= end_datetime:
        st.error("La date de début doit être avant la date de fin.")
        return

    # Find the nearest start and end dates in the dataframe
    nearest_start_date = df_index.loc[df_index['date'] >= start_date, 'time'].min()
    nearest_end_date = df_index.loc[df_index['date'] <= end_date, 'time'].max()
    
    if pd.isnull(nearest_start_date) or pd.isnull(nearest_end_date):
        st.error(f"Pas de données pour les dates spécifiées ({start_date} et {end_date}).")
        return None, None, None
   
    try:
        index_chaleur_immeuble_ecs = df_index.loc[df_index['time'] == nearest_end_date, 'Chaleur_Immeuble_ECS'].values[0] - \
            df_index.loc[df_index['time'] == nearest_start_date, 'Chaleur_Immeuble_ECS'].values[0]
        index_chaleur_immeuble_chauffage = df_index.loc[df_index['time'] == nearest_end_date, 'Chaleur_Immeuble_Chauffage'].values[0] - \
            df_index.loc[df_index['time'] == nearest_start_date, 'Chaleur_Immeuble_Chauffage'].values[0]
        index_chaleur_villa_chauffage = df_index.loc[df_index['time'] == nearest_end_date, 'Chaleur_Villas_Chauffage'].values[0] - \
            df_index.loc[df_index['time'] == nearest_start_date, 'Chaleur_Villas_Chauffage'].values[0]
        index_elec_immeuble_villa = df_index.loc[df_index['time'] == nearest_end_date, 'Elec_PAC_Immeuble_Villas'].values[0] - \
            df_index.loc[df_index['time'] == nearest_start_date, 'Elec_PAC_Immeuble_Villas'].values[0]
        
        total_chaleur = index_chaleur_immeuble_ecs + index_chaleur_immeuble_chauffage + index_chaleur_villa_chauffage
        
        part_chaleur_immeuble_ecs = index_chaleur_immeuble_ecs / total_chaleur if total_chaleur != 0 else 0
        part_chaleur_immeuble_chauffage = index_chaleur_immeuble_chauffage / total_chaleur if total_chaleur != 0 else 0
        part_chaleur_villa_chauffage = index_chaleur_villa_chauffage / total_chaleur if total_chaleur != 0 else 0
        
        part_elec_immeuble = part_chaleur_immeuble_ecs + part_chaleur_immeuble_chauffage
        conso_elec_pac_immeuble = index_elec_immeuble_villa * part_elec_immeuble
        
        return conso_elec_pac_immeuble, nearest_start_date, nearest_end_date
    except Exception as e:
        st.error(f"Erreur lors du calcul : {e}")
        return None, None, None
