# Documentation

Cette documentation a pour but de présenter l'outil de calcul de la méthodologie AMOén et de décrire comment l'utiliser.

## Table of Contents

- [Introduction](#introduction)
- [Onglets](#onglets)

## Introduction

L'écran d'accueil de l'[outil de calcul](https://amoen-calcul.streamlit.app/) permet de se connecter à l'outil. Pour cela, il faut renseigner un nom d'utilisateur et un mot de passe. Vous devriez avoir reçu ces informations par courriel.

![Login de l'outil](01_login.png)

Une fois connecté, vous arrivez sur l'écran principal de l'outil.

![Vue d'ensemble de l'outil](02_vue_ensemble.png)

Celui-ci est composé de plusieurs onglets:

- **0 Readme**: Rappel des différences entre la méthodologie AMOén et le calcul IDC. Recommendation de 6 mois de donneés minimium pour le calcul de l'atteinte de l'objectif. Lien vers le Github de l'outil.

- **1 Données du site**: Données concernant le site ou l'on souhaite calculer l'atteinte de l'objectif.

- **2 Note de calcul**: Détail de tous les calculs réalisés.

- **3 Résultats**: Résultats du calcul de l'atteinte de l'objectif.

- **4 Historique**: Historique IDC pour le site sélectionné. Historique des calculs de l'atteinte de l'objectif précédents.

- **5 Générer rapport**: Génération du rapport PDF.

- **6 Admin**: Vue réservée aux administrateurs de l'outil.

![Onglets](03_onglets.png)

## Onglets

### 0 Readme

Cet onglet contient:

- un rappel des différences entre la méthodlogie AMOén et le calcul IDC
- la recommendation d'avoir au moins 6 mois de données pour le calcul de l'atteinte de l'objectif
- le lien vers le Github de l'outil est également disponible

### 1 Données du site

Cet onglet contient les informations nécessaires au calcul de l'atteinte de l'objectif. L'image ci-dessous permet d'avoir un aperçu des données à renseigner.

![Données à renseigner](04_donnees_site1.png)

Dans **Chargement des données de base du projet** on peut sélectionner un projet. Les données de tous les champs sont alors automatiquement renseignées. Par exemple dans l'image ci-dessous, le projet "Avusy 10-10A" a été sélectionné.

![Sélectionner un projet -exemple](05_donnees_site2.png)

Les éléments qui ne sont pas renseignées se trouvent dans la section **Elements à renseigner**. Il est nécessaire de les renseigner pour pouvoir continuer.

![Elements à renseigner](06_donnes_site3.png)

Comme on peut le voir dans l'image ci-dessus, il est nécessaire de renseigner les données suivantes:

- Dates de début et fin de la période de calcul

- Affectations (souvent rempli automatiquement)

- Agents énergétiques utilisés

**Le bouton *Sauvegarder* permet de valider les données renseignées. Sans cela les données renseignées sont perdues.**

### 2 Note de calcul

Cet onglet contient le détail de tous les calculs réalisés.

![alt text](07_note_calcul1.png)

Il contient plusieurs sections:

- Période sélectionnée: Celle-ci indique le début et la fin de la période de calcul.

- Calculs effectués pour la période sélectionnée: Indique les calculs réalisés avec des commentaires. Inclus aussi une référence à la cellule Excel correspondante.

- Agents énergétiques: Liste des agents énergétiques utilisés pour le calcul avec le détail du calcul du facteur de pondération utilisé.

- Données météo station Genève-Cointrin pour la période sélectionnée: données météo utilisées pour le calcul des degrés-jours.


### 3 Résultats

Cet onglet contient les résultats du calcul de l'atteinte de l'objectif.

![Synthèse des résultats](08_resultats_synthèse.png)

La première section *Synthèse des résultats* indique le pourcentage d'atteinte de l'objectif. Si ce pourcentage est supérieur ou égal à 85%, l'objectif est atteint. Si ce pourcentage est inférieur à 85%, l'objectif n'est pas atteint.