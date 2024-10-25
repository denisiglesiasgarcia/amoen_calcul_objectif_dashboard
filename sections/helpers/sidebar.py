# /sections/helpers/sidebar.py

import streamlit as st

def add_sidebar_links():
    # Custom CSS for the buttons including Font Awesome - now embedded within the HTML
    st.sidebar.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <div class="sidebar-section">
            <style>
                .sidebar-section {
                    margin: 20px 0;
                }
                .sidebar-link {
                    display: inline-block;
                    width: 100%;
                    padding: 8px 16px;
                    margin: 8px 0;
                    text-align: left;
                    background-color: transparent;
                    color: inherit !important;
                    border-radius: 4px;
                    text-decoration: none;
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    transition: all 0.3s;
                }
                .sidebar-link:hover {
                    background-color: rgba(49, 51, 63, 0.1);
                    border-color: rgba(49, 51, 63, 0.2);
                    color: inherit !important;
                    text-decoration: none;
                }
                .sidebar-link i {
                    margin-right: 8px;
                    width: 20px;
                    text-align: center;
                    color: inherit !important;
                }
                hr {
                    margin: 20px 0;
                }
            </style>
            <a href="https://denisiglesiasgarcia.github.io/amoen_calcul_objectif_dashboard/"
               class="sidebar-link"
               target="_blank">
                <i class="fas fa-book"></i> Documentation
            </a>
            <a href="https://github.com/denisiglesiasgarcia/amoen_calcul_objectif_dashboard/tree/main"
               class="sidebar-link"
               target="_blank">
                <i class="fab fa-github"></i> GitHub Repository
            </a>
            <a href="https://pa.eco21.ch/accueil"
                class="sidebar-link"
                target="_blank">
                <i class="fas fa-link"></i> Applications SIG-éco21
            </a>
            <hr>
        </div>
    """,
        unsafe_allow_html=True,
    )
