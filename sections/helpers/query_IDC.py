import streamlit as st
import requests
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple, Union
from pyproj import Transformer
import pydeck as pdk
import sqlite3
import plotly.express as px
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.DEBUG)

def make_request(offset: int, fields: str, url: str, chunk_size: int, table_name: str, geometry: bool, egid: Union[int, List[int]]) -> Optional[List[Dict]]:
    """
    Make an API request to retrieve data for one or multiple EGIDs.
    Args:
        offset (int): The offset for the data to retrieve.
        fields (str): The fields to include in the response.
        url (str): The API endpoint URL.
        chunk_size (int): The number of records to retrieve in each request.
        table_name (str): The name of the table being processed.
        geometry (bool): Whether to include geometry data in the response.
        egid (Union[int, List[int]]): A single EGID or a list of EGIDs to query.
    Returns:
        Optional[List[Dict]]: A list of dictionaries containing the retrieved data, or None if an error occurred.
    """
    # Construct the where clause based on whether egid is a single value or a list
    if isinstance(egid, list):
        where_clause = f"egid IN ({','.join(map(str, egid))})"
    else:
        where_clause = f"egid={egid}"
    params = {
        'where': where_clause,
        'outFields': fields,
        'returnGeometry': str(geometry).lower(),
        'f': 'json',
        'resultOffset': offset,
        'resultRecordCount': chunk_size
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'features' in data:
            data_df = data['features']
            if geometry:
                result = [{'attributes': d['attributes'], 'geometry': d['geometry']} for d in data_df]
                return result
            else:
                result = [d['attributes'] for d in data_df]

                df = pd.DataFrame(result)

                df = df[[
                        'egid', 'annee', 'indice', 'sre',
                        'adresse', 'npa', 'commune', 'destination',
                        'agent_energetique_1', 'quantite_agent_energetique_1', 'unite_agent_energetique_1',
                        'agent_energetique_2', 'quantite_agent_energetique_2', 'unite_agent_energetique_2',
                        'agent_energetique_3', 'quantite_agent_energetique_3', 'unite_agent_energetique_3',
                        'date_debut_periode', 'date_fin_periode', 'date_saisie',
                        'indice_moy2', 'annees_concernees_moy_2', 'indice_moy3', 'annees_concernees_moy_3',
                        'id_concessionnaire', 'nbre_preneur',
                        ]].sort_values(by=['egid', 'annee'])

                df['date_debut_periode'] = pd.to_datetime(df['date_debut_periode'], unit='ms')
                df['date_fin_periode'] = pd.to_datetime(df['date_fin_periode'], unit='ms')
                df['date_saisie'] = pd.to_datetime(df['date_saisie'], unit='ms')

                df['npa'] = df['npa'].astype('int64')
                df['quantite_agent_energetique_1'] = df['quantite_agent_energetique_1'].astype('float64')
                df['quantite_agent_energetique_2'] = df['quantite_agent_energetique_2'].astype('float64')
                df['quantite_agent_energetique_3'] = df['quantite_agent_energetique_3'].astype('float64')

                # for each pair of egid and annee, keep only the moste recent date_saisie
                df = df.sort_values(by=['egid', 'annee', 'date_saisie'], ascending=[True, True, False])
                df = df.drop_duplicates(subset=['egid', 'annee'], keep='first')

                # convert dataframe to list of dictionaries
                filtered_list = df.to_dict('records')

                return filtered_list
        else:
            logging.warning(f"{table_name} → 'features' key not found in the API response for offset {offset}")
    except requests.exceptions.RequestException as e:
        logging.error(f'{table_name} → An error occurred with {offset}: {e}')
    except json.JSONDecodeError:
        logging.error(f'{table_name} → An error occurred with {offset}, retrying later...')
    return None

@st.cache_data
def convert_geometry_for_streamlit(data: List[Dict]) -> tuple:
    """
    Convert the geometry data from the Swiss LV95 system to WGS84 latitude and longitude,
    create a GeoJSON feature collection, and calculate the centroid of all features.
    """
    transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)
    features = []
    all_points = []

    for item in data:
        if 'geometry' in item and 'rings' in item['geometry']:
            rings = item['geometry']['rings']
            new_rings = []
            for ring in rings:
                new_ring = []
                for point in ring:
                    x, y = point[0], point[1]
                    lon, lat = transformer.transform(x, y)
                    new_ring.append([lon, lat])
                    all_points.append([lon, lat])
                new_rings.append(new_ring)
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": new_rings
                },
                "properties": item['attributes']
            }
            features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    # Calculate the centroid of all points
    centroid = np.mean(all_points, axis=0)

    return geojson, centroid

@st.cache_data
def show_map(data: List[Dict], centroid: Tuple[float, float]) -> None:
    """
    Display a map with the given data and centroid.
    """
    # Calculate color scale based on 'indice'
    color_scale = get_color_scale(data)

    # Create a PyDeck layer
    layer = pdk.Layer(
        "GeoJsonLayer",
        data,
        opacity=0.8,
        stroked=True,
        filled=True,
        extruded=True,
        wireframe=True,
        get_fill_color=color_scale,
        get_line_color=[255, 255, 255],
        get_line_width=2,
        pickable=True,
        auto_highlight=True,
    )

    # Set the initial view state
    view_state = pdk.ViewState(
        latitude=centroid[1],
        longitude=centroid[0],
        zoom=16,
        pitch=45,
        bearing=0
    )

    # Create the deck
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v10",
        tooltip={
            "html": """
                <div style="background-color: rgba(0, 0, 0, 0.7); color: white; padding: 10px; border-radius: 5px;">
                    <h3 style="margin-top: 0;">{egid}</h3>
                    <p><b>Adresse:</b> {adresse}</p>
                    <p><b>SRE:</b> {sre} m²</p>
                </div>
            """,
        }
    )

    # Add a title to the map
    st.title("Building Map")

    # Display the map in Streamlit
    st.pydeck_chart(deck)

    # Add a legend below the map
    add_legend(color_scale)

def get_color_scale(data):
    # Extract 'indice' values
    indices = [feature['properties']['indice'] for feature in data['features']]
    min_indice, max_indice = min(indices), max(indices)

    return f"[255 * ({max_indice} - properties.indice) / {max_indice - min_indice}, " \
           f"255 * (properties.indice - {min_indice}) / {max_indice - min_indice}, 50]"

def add_legend(color_scale):
    st.markdown("### Legend")
    legend_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <div style="width: 200px; height: 20px; background: linear-gradient(to right, rgb(255,0,50), rgb(0,255,50)); margin-right: 10px;"></div>
    </div>
    <div style="display: flex; justify-content: space-between; width: 200px;">
        <span>Low Indice</span>
        <span>High Indice</span>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

@st.cache_data
def show_dataframe(df):
    df = pd.DataFrame(df)

    df = df[[
            'egid', 'annee', 'indice', 'sre',
            'adresse', 'npa', 'commune', 'destination',
            'agent_energetique_1', 'quantite_agent_energetique_1', 'unite_agent_energetique_1',
            'agent_energetique_2', 'quantite_agent_energetique_2', 'unite_agent_energetique_2',
            'agent_energetique_3', 'quantite_agent_energetique_3', 'unite_agent_energetique_3',
            'date_debut_periode', 'date_fin_periode', 'date_saisie',
            'indice_moy2', 'annees_concernees_moy_2', 'indice_moy3', 'annees_concernees_moy_3',
            'id_concessionnaire', 'nbre_preneur',
            ]].sort_values(by=['egid', 'annee'])

    st.dataframe(df)

@st.cache_data
def get_adresses_egid():
    conn = sqlite3.connect('adresses_egid.db')
    c = conn.cursor()
    df_adresses_egid = pd.read_sql_query("SELECT * FROM adresses_egid ORDER BY adresse", conn)
    conn.commit()
    conn.close()
    return df_adresses_egid

@st.cache_data
def create_barplot(data_df):
    df_barplot = pd.DataFrame(data_df)
    df_barplot = df_barplot[['adresse', 'egid', 'annee', 'indice']].sort_values(by=['annee', 'adresse', 'egid'])
    
    # Check if annee has all the years between 2011 and current year
    current_year = datetime.now().year
    years = list(range(2011, current_year + 1))
    adresses_egid = df_barplot[['adresse', 'egid']].drop_duplicates().values.tolist()
    
    # Create a list to store new rows
    new_rows = []
    
    for adresse, egid in adresses_egid:
        for year in years:
            if year not in df_barplot[(df_barplot['adresse'] == adresse) & (df_barplot['egid'] == egid)]['annee'].unique():
                new_rows.append({'adresse': adresse, 'egid': egid, 'annee': year, 'indice': 0})
    
    # Use concat to add new rows
    if new_rows:
        df_new_rows = pd.DataFrame(new_rows)
        df_barplot = pd.concat([df_barplot, df_new_rows], ignore_index=True)
    
    df_barplot = df_barplot.sort_values(by=['annee', 'adresse', 'egid'])
    
    # Create a new column for legend
    df_barplot['adresse_egid'] = df_barplot.apply(lambda row: f"{row['adresse']} - {row['egid']}", axis=1)
    
    fig = px.bar(df_barplot, x='annee', y='indice', color='adresse_egid', barmode='group',
                 labels={'annee': 'Année', 'indice': 'Indice [MJ/m²]'},
                 title='Indice par Année et Adresse')
    
    # Customize the layout
    fig.update_layout(
        xaxis_title='Année',
        yaxis_title='Indice [MJ/m²]',
        legend_title='Adresse - EGID',
        xaxis={'type': 'category'}  # Treat year as categorical
    )
    
    return fig
