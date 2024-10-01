# Onglets

Cette section décrit les différents onglets de l'outil.

---

## Introduction

L'écran d'accueil de l'[outil de calcul](https://amoen-calcul.streamlit.app/)
permet de se connecter à l'outil. Pour cela, il faut renseigner un nom
d'utilisateur et un mot de passe. Vous devriez avoir reçu ces informations par courriel.

![Login de l'outil](01_login.png)

Une fois connecté, vous arrivez sur l'écran principal de l'outil.

![Vue d'ensemble de l'outil](02_vue_ensemble.png)

Celui-ci est composé de plusieurs onglets:

![Onglets](03_onglets.png)

| Onglet | Objectif |
| ------ | -------- |
| [0 Readme](#0-readme) | Rappel des différences entre la méthodologie AMOén et le calcul IDC. Recommendation de 6 mois de donneés minimium pour le calcul de l'atteinte de l'objectif. Lien vers le Github de l'outil. |
| [1 Données du site](#1-données-du-site) | Données concernant le site ou l'on souhaite calculer l'atteinte de l'objectif. |
| [2 Note de calcul](#2-note-de-calcul) | Détail de tous les calculs réalisés. |
| [3 Résultats](#3-résultats) | Résultats du calcul de l'atteinte de l'objectif. |
| [4 Historique](#4-historique) | Historique IDC pour le site sélectionné. Historique des calculs de l'atteinte de l'objectif précédents. |
| [5 Générer rapport](#5-générer-rapport) | Génération du rapport PDF. |
| 6 Admin | Vue réservée aux administrateurs de l'outil. |

---

## 0 Readme

Cet onglet contient:

- un rappel des différences entre la méthodlogie AMOén et le calcul IDC
- la recommendation d'avoir au moins 6 mois de données pour le calcul de
l'atteinte de l'objectif
- le lien vers le Github de l'outil est également disponible

---

## 1 Données du site

Cet onglet contient les informations nécessaires au calcul de l'atteinte de
l'objectif. La première partie est préremplie lors de la sélection du projet et
la deuxième partie est à compléter par l'AMOén.

### Chargement des données de base du projet

`Sélectionner projet` permet de voir une liste des projets assignés et d'en
sélectionner un. Les données de tous les champs de cette partie sont alors
automatiquement renseignées. Par exemple, dans la vidéo ci-dessous, le projet
"Avusy 10-10A" a été sélectionné.

<video width="900"  controls>
    <source src="https://github.com/user-attachments/assets/8d9f3a86-1e47-4c49-8336-4938cf1569cf" type="video/mp4">
</video>

### Elements à renseigner

!!! important
    **Il est nécessaire de renseigner tous les champs pour pouvoir réaliser le calcul.**

<video width="900"  controls>
    <source src="https://github.com/user-attachments/assets/899db28c-006b-4cf7-8921-cdfab82a973c" type="video/mp4">
</video>

Comme on peut le voir dans la vidéo ci-dessus, il faut renseigner les données suivantes:

- Dates de début et fin de la période de calcul. Il est recommandé d'avoir au
moins 6 mois de données pour le calcul de l'atteinte de l'objectif. Les dates
peuvent être remplies manuellement ou en utilisant le calendrier.

- Affectations (souvent rempli automatiquement). Les affectations peuvent être
sélectionnés dans la liste déroulante. Il est possible de renseigner plusieurs
affectations. La somme des affectations doit être égale à 100%.

- Agents énergétiques utilisés et quantités.

Pour valider les sélections, il faut soit appuyer sur `Enter ↵` soit cliquer
en dehors de la cellule.

!!! warning "IMPORTANT"
    **Le bouton `Sauvegarder` permet de valider les données renseignées. Sans cela,
    les données renseignées sont perdues.**

### Surélévations

!!! note
    Voir la section [Surélévations](sections/surelevation.md) pour plus d'informations sur
    les spécificités des surélévations.

---

## 2 Note de calcul

Cet onglet contient le détail de tous les calculs réalisés. Il est divisé
en plusieurs sections:

- Période sélectionnée: Celle-ci indique le début et la fin de la période de calcul.

- Calculs effectués pour la période sélectionnée: Indique les calculs réalisés
avec des commentaires. Inclus aussi une référence à la cellule Excel correspondante.

- Agents énergétiques: Liste des agents énergétiques utilisés pour le calcul
avec le détail du calcul du facteur de pondération utilisé.

- Données météo station Genève-Cointrin pour la période sélectionnée: données
météo utilisées pour le calcul des degrés-jours.

<details class="example" markdown="1">
<summary>Cliquer pour voir un example</summary>

![alt text](07_note_calcul1.png)

</details>

---

## 3 Résultats

Cet onglet contient les résultats du calcul de l'atteinte de l'objectif.

### Synthèse des résultats

La première section *Synthèse des résultats* indique le pourcentage d'atteinte
de l'objectif. Si ce pourcentage est supérieur ou égal à 85%, l'objectif est atteint.
Si ce pourcentage est inférieur à 85%, l'objectif n'est pas atteint.

<details class="example" markdown="1">

<summary>Cliquer pour voir un example</summary>

![Synthèse des résultats](08_resultats_synthèse.png)

</details>

### Graphiques

La deuxième section *Graphiques* contient le graphique qui résume les résultats
du calcul.

Il est possible de sauvegarder ce graphique en faisant clic sur le bouton droit
de la souris et en sélectionnant *Enregistrer l'image sous...*.

<details class="example" markdown="1">

<summary>Cliquer pour voir un example</summary>

![Graphique résultats](09_resultats_graphique.png)

</details>

---

## 4 Historique

Cet onglet contient l'historique des résultats obtenus et l'IDC pour le site sélectionné.

### Plan

Si l'on sélectionne la case `Afficher la carte`, on peut voir le plan de
situation du site.

<details class="example" markdown="1">

<summary>Cliquer pour voir un example</summary>

![Plan de situation](10_historique_plan.png)

</details>

Cette option est désactivée par défaut pour des raisons de performance.

### Historique IDC

Cette section contient un historique des IDC pour le site sélectionné.

<details class="example" markdown="1">

<summary>Cliquer pour voir un example</summary>

![Historique IDC](11_historique_idc.gif)

</details>

Si l'on coche la case `Afficher les données IDC`, on peut voir les données
utilisées pour ce graphique.

### Historique résultats méthodologie AMOén

Cette section contient un historique de l'atteinte de l'objectif pour le site sélectionné.
Les résultats sont classés par date de calcul.

<details class="example" markdown="1">

<summary>Cliquer pour voir un example</summary>

![Historique atteinte objectifs AMOén](12_historique_resultats_amoen.png)

</details>

Si l'on coche la case `Afficher les données historiques`, on peut voir toutes les
données utilisées pour le calcul de l'atteinte des objectifs pour chaque période.

---

## 5 Générer rapport

Cet onglet permet de générer un rapport PDF avec les résultats du calcul de
l'atteinte de l'objectif. La vidéo ci-dessous détaille le processus.

<video width="900"  controls>
    <source src="https://github.com/user-attachments/assets/225a7075-a524-4613-9449-c69f31b88f1f" type="video/mp4">
</video>