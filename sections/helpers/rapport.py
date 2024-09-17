from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    Frame,
    PageTemplate,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Line, String, Polygon
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfgen.canvas import Canvas
import io
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date, datetime
import os
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.sankey import Sankey


def graphique_bars_rapport(
    site,
    ef_avant_corr_kwh_m2,
    energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
    ef_objectif_pondere_kwh_m2,
    atteinte_objectif,
    facteur_ponderation_moyen,
    amoen_id,
):

    # Données pour le graphique
    idc_moy_3ans_avant_MJ_m2 = ef_avant_corr_kwh_m2 * 3.6
    ef_objectif_pondere_MJ_m2 = ef_objectif_pondere_kwh_m2 * 3.6
    ef_apres_corr_MJ_m2 = (
        energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
        * 3.6
    )
    baisse_objectif_MJ_m2 = (
        ef_avant_corr_kwh_m2 * 3.6 - ef_objectif_pondere_kwh_m2 * 3.6
    )
    baisse_mesuree_MJ_m2 = (
        ef_avant_corr_kwh_m2 * 3.6
        - energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2
        * 3.6
    )

    # données pour le graphique
    bar_data1 = pd.DataFrame(
        {
            "Nom_projet": [site, site, site],
            "Type": [
                "IDC moy 3 ans avant\n$E_{f,avant,corr}$",
                "Objectif\n$E_{f,obj}*f_{p}$",
                "Conso mesurée après\n$E_{f,après,corr,rénové}*f_{p}$",
            ],
            "Valeur": [
                idc_moy_3ans_avant_MJ_m2,
                ef_objectif_pondere_MJ_m2,
                ef_apres_corr_MJ_m2,
            ],
        }
    )

    # Générer histogramme. taillebin est utilisé pour uniformiser le format de l'histogramme et que les axes
    # correspondent bien à la largeur des barres (bin)
    cm = 1 / 2.54
    sns.set(style="white", rc={"figure.figsize": (30 * cm, 14.2 * cm)})
    # ax1 = sns.catplot(x='Nom_projet', y='Valeur', hue='Type', kind='bar', data=bar_data1)

    ax = sns.barplot(
        y="Valeur",
        x="Type",
        data=bar_data1,
        order=[
            "IDC moy 3 ans avant\n$E_{f,avant,corr}$",
            "Objectif\n$E_{f,obj}*f_{p}$",
            "Conso mesurée après\n$E_{f,après,corr,rénové}*f_{p}$",
        ],
        palette=["#1f77b4", "#ff7f0e", "#2ca02c"],
    )

    sns.despine()

    for i, val in enumerate(bar_data1["Valeur"]):
        ax.text(
            i,
            val + 0.5,
            f"{val:.1f}",
            ha="center",
            va="bottom",
            color="black",
            fontsize=18,
        )

    ####################

    # première flèche
    # find the height of the first and third bars
    first_bar_height = idc_moy_3ans_avant_MJ_m2
    second_bar_height = ef_objectif_pondere_MJ_m2
    # set the x-coordinate for the third bar
    x_coord_second_bar = 0.7  # this depends on the actual x-coordinate of the third bar
    # text for the arrow
    text_arrow_baisse_realisee = (
        "Baisse\nobjectif\n" + str("{:.1f}".format(baisse_objectif_MJ_m2)) + " MJ/m²"
    )
    # add text at the midpoint of the arrow
    midpoint_height = (first_bar_height + second_bar_height) / 2
    # plot the line (arrow without arrowheads)
    ax.annotate(
        "",
        xy=(x_coord_second_bar, second_bar_height),
        xytext=(x_coord_second_bar, first_bar_height),
        arrowprops=dict(arrowstyle="<->", color="moccasin", lw=3),
    )  # increase lw for a thicker line
    # # add the text over the line and centered
    u = ax.text(
        x_coord_second_bar,
        midpoint_height,
        text_arrow_baisse_realisee,
        ha="center",
        va="center",
        rotation=0,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="white", lw=2),
        fontsize=18,
    )

    # deuxième flèche
    # find the height of the first and third bars
    third_bar_height = ef_apres_corr_MJ_m2
    # set the x-coordinate for the third bar
    x_coord_third_bar = 1.7  # this depends on the actual x-coordinate of the third bar
    # text for the arrow
    text_arrow_baisse_realisee = (
        "Baisse\nmesurée\n" + str("{:.1f}".format(baisse_mesuree_MJ_m2)) + " MJ/m²"
    )
    # add text at the midpoint of the arrow
    midpoint_height = (first_bar_height + third_bar_height) / 2
    # plot the line (arrow without arrowheads)
    ax.annotate(
        "",
        xy=(x_coord_third_bar, third_bar_height),
        xytext=(x_coord_third_bar, first_bar_height),
        arrowprops=dict(arrowstyle="->", color="lightgreen", lw=4),
    )  # increase lw for a thicker line
    # add the text over the line and centered
    u = ax.text(
        x_coord_third_bar,
        midpoint_height,
        text_arrow_baisse_realisee,
        ha="center",
        va="center",
        rotation=0,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="lime", lw=2),
        fontsize=18,
    )

    #####################

    # titre de l'histogramme
    title_text = (
        str("{:.1f}".format(atteinte_objectif * 100)) + "% de l'objectif atteint\n"
    )
    title_color = "darkgreen" if atteinte_objectif * 100 >= 85 else "red"
    plt.title(
        title_text,
        weight="bold",
        color=title_color,
        loc="center",
        pad=15,
        fontsize=20,
        y=0.925,
    )
    plt.subplots_adjust(
        top=0.945, bottom=0.17, left=0.06, right=0.97, hspace=0.2, wspace=0.2
    )

    # titre pour l'abscisse X
    # plt.xlabel("\nBaisse d'énergie finale minimum pour obtenir la subvention = 85% * " +
    #         str('{:.1f}'.format(baisse_objectif_MJ_m2)) + " = " +
    #         str('{:.1f}'.format(baisse_objectif_MJ_m2*0.85)) + ' MJ/m² \n$E_{f,après,corr}*f_{p}$ maximum pour obtenir la subvention ($(E_{f,après,corr}*f_{p})_{max→subv.}$) = ' +
    #         str('{:.1f}'.format(idc_moy_3ans_avant_MJ_m2)) + " - " +
    #         str('{:.1f}'.format(baisse_objectif_MJ_m2*0.85)) + " = " +
    #         str('{:.1f}'.format(idc_moy_3ans_avant_MJ_m2 - baisse_objectif_MJ_m2*0.85)) + " MJ/m²\nPourcentage de l'objectif atteint = " +
    #         str('{:.1f}'.format(baisse_mesuree_MJ_m2)) + " / " +
    #         str('{:.1f}'.format(baisse_objectif_MJ_m2))+ " * 100 = " +
    #         str('{:.1f}'.format(atteinte_objectif*100)) + "%",
    #         loc='left', size=18)

    formula_atteinte_objectif_titre = r"$Atteinte\ objectif=$"
    formula_atteinte_objectif_titre_pourcent = r"$=$"

    formula_atteinte_objectif = r"$\frac{{\Delta E_{{f,réel}}}}{{\Delta E_{{f,visée}}}} = \frac{{E_{{f,avant,corr}} - E_{{f,après,corr,rénové}}*f_{{p}}}}{{E_{{f,avant,corr}} - E_{{f,obj}}*f_{{p}}}}=$"

    formula_atteinte_objectif_num = r"$\frac{{{} - {}}}{{{} - {}}}$".format(
        round(idc_moy_3ans_avant_MJ_m2, 1),
        round(ef_apres_corr_MJ_m2, 1),
        round(idc_moy_3ans_avant_MJ_m2, 1),
        round(ef_objectif_pondere_MJ_m2, 1),
    )

    formula_atteinte_objectifs_pourcent = r"${} \%$".format(
        round(atteinte_objectif * 100, 1)
    )

    xlabel_sep_x = 0.25
    xlabel_sep_y = -0.17
    xlabel_level1 = -0.3
    xlabel_level2 = xlabel_level1 + xlabel_sep_y

    u1_titre = plt.text(
        0,
        xlabel_level1,
        formula_atteinte_objectif_titre,
        ha="left",
        va="center",
        transform=ax.transAxes,
        fontsize=18,
    )
    u2_titre = plt.text(
        0.89,
        xlabel_level1,
        formula_atteinte_objectif_titre_pourcent,
        ha="left",
        va="center",
        transform=ax.transAxes,
        fontsize=18,
    )
    u1 = plt.text(
        0.22,
        xlabel_level1,
        formula_atteinte_objectif,
        ha="left",
        va="center",
        transform=ax.transAxes,
        fontsize=24,
    )
    u2 = plt.text(
        0.73,
        xlabel_level1,
        formula_atteinte_objectif_num,
        ha="left",
        va="center",
        transform=ax.transAxes,
        fontsize=24,
    )
    u3 = plt.text(
        0.92,
        xlabel_level1,
        formula_atteinte_objectifs_pourcent,
        ha="left",
        va="center",
        transform=ax.transAxes,
        fontsize=20,
    )

    # display(formula_atteinte_objectif)
    # plt.xlabel(formula_atteinte_objectif,
    #         loc='left', size=14)

    # remove xlabel
    plt.xlabel("")

    # titre pour l'ordonnée Y
    plt.ylabel("[MJ/m²/an]", fontsize=18)

    # fontsize xticks/yticks
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    # sauvegarder graphique
    plt.savefig("01_bar_chart.png", dpi=600, bbox_inches="tight")

    # nettoyage
    plt.close()


def repartition_renove_sureleve(
    sre_renovation_m2,
    sre_extension_surelevation_m2,
    repartition_energie_finale_partie_renovee_chauffage,
    repartition_energie_finale_partie_renovee_ecs,
    repartition_energie_finale_partie_surelevee_chauffage,
    repartition_energie_finale_partie_surelevee_ecs,
    ef_avant_corr_kwh_m2,
    ef_objectif_pondere_kwh_m2,
    energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
):
    cm = 1 / 2.54
    fig, (ax1, ax2) = plt.subplots(
        1,
        2,
        figsize=(30 * cm, 14.2 * cm),
        dpi=100,
        gridspec_kw={"width_ratios": [1, 1.5]},
    )

    # Define the reduced building dimensions
    building_width_reno = 1  # Smaller width
    building_height_reno = 2  # Smaller height
    building_width_sur = building_width_reno
    building_height_sur = 1
    floor_height = 3
    floors_reno = building_height_reno // floor_height

    # Define custom colors
    color_reno = "#2ecc71"  # A softer green
    color_sur = "#3498db"  # A softer blue
    color_tout = "#34495e"  # A dark gray
    color_txt_reno = "forestgreen"
    color_txt_sur = "royalblue"

    # Create custom color gradients
    cmap_reno = LinearSegmentedColormap.from_list("", ["#ffffff", color_reno])
    cmap_sur = LinearSegmentedColormap.from_list("", ["#ffffff", color_sur])

    # Define the building coordinates
    building_x = 0
    building_y = 0

    # Text
    texte_alignement_droite = 0.05
    texte_hauteur_sous_titre = 0.15
    texte_hauteur_texte_info = 0.30

    # Rénovation
    floors_reno_rectangle = patches.Rectangle(
        (building_x, building_y),
        building_width_reno,
        building_height_reno,
        facecolor=cmap_reno(0.3),
        edgecolor=color_reno,
        linewidth=2,
    )
    ax2.add_patch(floors_reno_rectangle)

    # Surélévation
    added_part = patches.Rectangle(
        (building_x, building_y + building_height_reno),
        building_width_sur,
        building_height_sur,
        facecolor=cmap_sur(0.3),
        edgecolor=color_sur,
        linewidth=2,
    )
    ax2.add_patch(added_part)

    # Data for text and Sankey
    sre_total = sre_renovation_m2 + sre_extension_surelevation_m2

    INPUT = (
        repartition_energie_finale_partie_renovee_chauffage
        + repartition_energie_finale_partie_renovee_ecs
        + repartition_energie_finale_partie_surelevee_chauffage
        + repartition_energie_finale_partie_surelevee_ecs
    )

    assert INPUT == 100

    repartition_energie_finale_partie_surelevee = (
        repartition_energie_finale_partie_surelevee_chauffage
        + repartition_energie_finale_partie_surelevee_ecs
    )
    repartition_energie_finale_partie_renovee = (
        repartition_energie_finale_partie_renovee_chauffage
        + repartition_energie_finale_partie_renovee_ecs
    )

    # Text on the right for Rénovation
    ax2.text(
        texte_alignement_droite,  # Adjusted position
        building_height_reno - texte_hauteur_sous_titre,
        "Rénovation",
        rotation=0,
        verticalalignment="center",
        fontsize=12,
        fontweight="bold",
        color=color_txt_reno,
    )
    ax2.text(
        texte_alignement_droite,  # Additional text
        building_height_reno - texte_hauteur_texte_info,
        r"$SRE_{renovation} = $"
        f"${sre_renovation_m2}\ m²$"
        "\n"
        r"$E_{f,avant,corr} = $"
        f"${ef_avant_corr_kwh_m2*3.6}\ MJ/m²$"
        "\n"
        r"$E_{f,obj} * f_p = $"
        f"${ef_objectif_pondere_kwh_m2*3.6}\ MJ/m²$"
        "\n"
        r"$E_{f,après,corr,rénové} * f_p = $"
        f"${energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2*3.6}\ MJ/m²$"
        "\n",
        rotation=0,
        verticalalignment="top",
        fontsize=12,
        color=color_txt_reno,
    )

    # Text on the right for Surélévation
    ax2.text(
        texte_alignement_droite,
        building_height_reno + building_height_sur - texte_hauteur_sous_titre,
        "Surélévation",
        rotation=0,
        verticalalignment="center",
        fontsize=12,
        fontweight="bold",
        color=color_txt_sur,
    )
    ax2.text(
        texte_alignement_droite,  # Additional text
        building_height_reno + building_height_sur - texte_hauteur_texte_info,
        r"$SRE_{surelevation} = $" + f"${sre_extension_surelevation_m2}\ m²$",
        rotation=0,
        verticalalignment="top",
        fontsize=12,
        color=color_txt_sur,
    )

    # Adjust the plot limits to accommodate the text
    ax2.set_xlim(-0.1, building_width_reno + 0.5)
    ax2.set_ylim(-0.1, building_height_reno + building_height_sur + 0.1)

    # Remove axes
    ax2.axis("off")

    # Sankey diagram
    ax1.axis("off")

    sankey = Sankey(
        ax=ax1,
        scale=1 / INPUT,
        head_angle=180,
        shoulder=0,
        gap=0.2,
        radius=0.1,
        unit="%",
        format="%.1f",
        offset=0.4,
    )

    trunk_length0 = 0.50
    trunk_length1 = 0.50
    trunk_length2 = trunk_length1

    flows_s1 = [
        100,
        -repartition_energie_finale_partie_renovee,
        -repartition_energie_finale_partie_surelevee,
    ]
    flows_surelevation = [
        -repartition_energie_finale_partie_surelevee_chauffage,
        -repartition_energie_finale_partie_surelevee_ecs,
    ]
    flows_renovation = [
        -repartition_energie_finale_partie_renovee_chauffage,
        -repartition_energie_finale_partie_renovee_ecs,
    ]

    # Main flow
    s0 = sankey.add(
        flows=flows_s1,
        labels=["Energie\nfinale", None, None],
        orientations=[0, -1, 1],
        trunklength=trunk_length0,
        rotation=0,
        fc="salmon",
        color="salmon",
        alpha=0.5,
    )

    # Surélévation subflow
    s1 = sankey.add(
        flows=[repartition_energie_finale_partie_surelevee] + flows_surelevation,
        labels=["Surélévation", "ECS", "Chauffage"],
        orientations=[0, -1, -1],
        prior=0,
        connect=(2, 0),
        trunklength=trunk_length1,
        fc=color_sur,
        color=color_sur,
        alpha=0.5,
    )

    # Rénovation subflow
    s2 = sankey.add(
        flows=[repartition_energie_finale_partie_renovee] + flows_renovation,
        labels=["Rénovation", "ECS", "Chauffage"],
        orientations=[0, 1, 1],
        prior=0,
        connect=(1, 0),
        trunklength=trunk_length2,
        fc=color_reno,
        color=color_reno,
        alpha=0.5,
    )

    sankey.finish()

    fig.suptitle(
        "Répartition entre partie rénovée et surélevée",
        fontsize=16,
        fontweight="bold",
    )

    # Texts

    fig.text(
        0.63,
        -0.04,
        "Subvention bonus AMOén applicable\n" + "uniquement à la partie rénovée.",
        horizontalalignment="center",
        fontsize=11,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", edgecolor=color_reno, facecolor="none"),
    )

    title_sankey = f"{repartition_energie_finale_partie_renovee}% de l'énergie finale\n est dédiée à la rénovation"
    fig.text(
        0.20,
        -0.01,
        title_sankey,
        horizontalalignment="center",
        fontsize=10,
        fontweight="bold",
    )

    fig.text(
        0.07,
        -0.55,
        "Il est important de noter que la subvention ne concerne que la partie rénovée du bâtiment,\n"
        + "excluant ainsi toute extension ou surélévation.\n"
        + "\n"
        + "L'énergie finale après travaux climatiquement corrigée pondérée ("
        + r"$E_{f,après,corr,rénové} * f_p$"
        + ") représente\n"
        + "selon la méthodologie AMOén la quantité d'énergie finale consommée par la partie rénovée.\n"
        + r"$E_{f,après,corr,rénové} * f_p$"
        + " est essentiel pour vérifier le pourcentage d'atteinte de l'objectif de performance énergétique.\n"
        + "\n"
        + "L'IDC déclaré par le/la concessionaire va prendre en compte la totalité du bâtiment (partie rénovée \n"
        + "et surélévation/extension). Cela représente donc 100% de l'énergie finale et toute la SRE du bâtiment.\n"
        + "\n"
        + "L'IDC et "
        + r"$E_{f,après,corr,rénové} * f_p$"
        + " seront donc différents car ils ne prennent pas en compte les mêmes SRE\n"
        + "ni la même quantité d'énergie finale.",
        horizontalalignment="left",
        fontsize=10,
    )

    plt.tight_layout()

    # sauvegarder graphique
    plt.savefig("02_reno_sur.png", dpi=600, bbox_inches="tight")

    # nettoyage
    plt.close()


def header(canvas, doc):
    # Get the directory of the current script (rapport.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the path to the images folder
    img_folder = os.path.join(current_dir, "img")

    canvas.saveState()

    # Add images
    img_path_eco21 = os.path.join(img_folder, "eco21.png")
    img_path_etat = os.path.join(img_folder, "etat.jpg")
    img_path_hepia = os.path.join(img_folder, "hepia.jpg")
    try:
        scale1 = 2
        canvas.drawImage(
            img_path_eco21,
            1.5 * cm,
            27 * cm,
            width=1.88 * cm * scale1,
            height=1 * cm * scale1,
            preserveAspectRatio=True,
            mask="auto",
        )
        scale2 = 2
        canvas.drawImage(
            img_path_etat,
            6 * cm,
            27 * cm,
            width=1.88 * cm * scale2,
            height=1 * cm * scale2,
            preserveAspectRatio=True,
            mask="auto",
        )
        scale3 = 1.15
        canvas.drawImage(
            img_path_hepia,
            15 * cm,
            27.2 * cm,
            width=3.92 * cm * scale3,
            height=1 * cm * scale3,
            preserveAspectRatio=True,
            mask="auto",
        )
    except Exception as e:
        print(f"Error processing image: {e}")
    canvas.restoreState()


def footer(canvas, doc):
    canvas.saveState()
    # Add your footer content here
    canvas.setFont("Helvetica", 8)
    canvas.drawString(doc.leftMargin, doc.bottomMargin - 0.75 * cm, f"Page {doc.page}")
    canvas.drawRightString(
        doc.width + doc.leftMargin,
        doc.bottomMargin - 0.75 * cm,
        f"Généré le {datetime.now().strftime('%Y-%m-%d')}",
    )
    canvas.restoreState()


def generate_pdf(data):
    buffer = io.BytesIO()
    # Create the document with a custom page size that leaves room for header and footer
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=3 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1 * cm,
        rightMargin=1 * cm,
    )

    # Create frames for the content
    content_frame = Frame(
        doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal"
    )

    # Create a custom PageTemplate
    template = PageTemplate(
        id="test",
        frames=content_frame,
        onPage=lambda canvas, doc: (header(canvas, doc), footer(canvas, doc)),
    )

    # Add the template to the document
    doc.addPageTemplates([template])

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Center", alignment=1))
    styles.add(ParagraphStyle(name="SmallCenter", alignment=1, fontSize=8))
    elements = []

    # elements.append(Spacer(1, 0.5*cm))

    # Title
    title_report = f"Rapport " + data["nom_projet"]
    elements.append(Paragraph(title_report, styles["Title"]))
    elements.append(Spacer(1, 0.5 * cm))

    # Project details
    project_admin = [
        [
            Paragraph("<b>Informations administratives</b>", styles["Heading4"]),
            "",
        ],  # Title row
        [Paragraph("", styles["Normal"]), ""],  # Empty row
        [Paragraph("Adresse:", styles["Normal"]), data["adresse_projet"]],
        [Paragraph("AMOén:", styles["Normal"]), data["amoen_id"]],
    ]
    project_admin_table = Table(project_admin, colWidths=[150, 350])
    project_admin_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (1, 1), colors.lightgrey),
                ("SPAN", (0, 0), (1, 1)),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(project_admin_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Surfaces
    project_surfaces = [
        [Paragraph("<b>Surfaces</b>", styles["Heading3"]), ""],  # Title row
        [Paragraph("", styles["Normal"]), ""],  # Empty row
    ]
    if data["sre_extension_surelevation_m2"] > 0.0:
        # Define a custom style for italic text
        italic_style = ParagraphStyle(
            name="Italic",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",  # Use 'Helvetica-Oblique' for italic text
            fontSize=10,  # Adjust font size as needed
            alignment=TA_LEFT,
        )

        # Create the paragraph with mixed styles
        project_surfaces.append(
            [
                Paragraph("Surface surélévation (m² SRE):", styles["Normal"]),
                Paragraph(
                    f"{data['sre_extension_surelevation_m2']} m² SRE. <i>La SRE surélevée n'est pas sujette à la subvention AMOén</i>"
                ),
            ]
        )

    project_surfaces.append(
        [
            Paragraph("Surface rénovation (m² SRE):", styles["Normal"]),
            f"{data['sre_renovation_m2']} m² SRE",
        ]
    )
    # Add conditional rows for different surface types
    for surface_type, percentage in [
        ("Habitat collectif", data["sre_pourcentage_habitat_collectif"]),
        ("Habitat individuel", data["sre_pourcentage_habitat_individuel"]),
        ("Administration", data["sre_pourcentage_administration"]),
        ("Ecoles", data["sre_pourcentage_ecoles"]),
        ("Commerce", data["sre_pourcentage_commerce"]),
        ("Restauration", data["sre_pourcentage_restauration"]),
        ("Lieux de rassemblement", data["sre_pourcentage_lieux_de_rassemblement"]),
        ("Hopitaux", data["sre_pourcentage_hopitaux"]),
        ("Industrie", data["sre_pourcentage_industrie"]),
        ("Depots", data["sre_pourcentage_depots"]),
        ("Installations sportives", data["sre_pourcentage_installations_sportives"]),
        ("Piscines couvertes", data["sre_pourcentage_piscines_couvertes"]),
    ]:
        if percentage > 0.0:
            project_surfaces.append(
                [
                    f"{surface_type} (%):",
                    f"{percentage} % de la surface rénovée soit {(percentage/100*data['sre_renovation_m2']):.0f} m² SRE",
                ]
            )

    project_surfaces_table = Table(project_surfaces, colWidths=[150, 350])
    project_surfaces_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (1, 1), colors.lightgrey),
                ("SPAN", (0, 0), (1, 1)),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(project_surfaces_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Conso énergie après travaux
    project_energie = [
        [
            Paragraph("<b>Consommation après travaux</b>", styles["Heading3"]),
            "",
        ],  # Title row
        [Paragraph("", styles["Normal"]), ""],  # Empty row
    ]
    # Add conditional rows for different energy types
    for energy_type, value, unit in [
        ("Mazout", data["agent_energetique_ef_mazout_kg"], "kg"),
        ("Mazout", data["agent_energetique_ef_mazout_litres"], "litres"),
        ("Mazout", data["agent_energetique_ef_mazout_kwh"], "kWh"),
        ("Gaz naturel", data["agent_energetique_ef_gaz_naturel_m3"], "m³"),
        ("Gaz naturel", data["agent_energetique_ef_gaz_naturel_kwh"], "kWh"),
        (
            "Bois (buches dures)",
            data["agent_energetique_ef_bois_buches_dur_stere"],
            "stères",
        ),
        (
            "Bois (buches tendres)",
            data["agent_energetique_ef_bois_buches_tendre_stere"],
            "stères",
        ),
        (
            "Bois (buches tendres)",
            data["agent_energetique_ef_bois_buches_tendre_kwh"],
            "kWh",
        ),
        ("Pellets", data["agent_energetique_ef_pellets_m3"], "m³"),
        ("Pellets", data["agent_energetique_ef_pellets_kg"], "kg"),
        ("Pellets", data["agent_energetique_ef_pellets_kwh"], "kWh"),
        ("Plaquettes", data["agent_energetique_ef_plaquettes_m3"], "m³"),
        ("Plaquettes", data["agent_energetique_ef_plaquettes_kwh"], "kWh"),
        ("CAD", data["agent_energetique_ef_cad_kwh"], "kWh"),
        ("Electricité PAC", data["agent_energetique_ef_electricite_pac_kwh"], "kWh"),
        (
            "Electricité directe",
            data["agent_energetique_ef_electricite_directe_kwh"],
            "kWh",
        ),
        ("Autre", data["agent_energetique_ef_autre_kwh"], "kWh"),
    ]:
        if value > 0.0:
            project_energie.append(
                [
                    f"{energy_type} ({unit}):",
                    f"{value:.1f} {unit} du {data['periode_start'].date()} au {data['periode_end'].date()}",
                ]
            )

    project_energie_table = Table(project_energie, colWidths=[150, 350])
    project_energie_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (1, 1), colors.lightgrey),
                ("SPAN", (0, 0), (1, 1)),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(project_energie_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Energy data table with an additional "Dénomination" column
    project_results = [
        [
            Paragraph("<b>Atteinte de l'objectif</b>", styles["Heading3"]),
            "",
            "",
            "",
        ],  # Title row
        [
            Paragraph("<b>Variable</b>", styles["Normal"]),
            Paragraph("<b>Dénomination</b>", styles["Normal"]),
            Paragraph("<b>kWh/m²/an</b>", styles["Normal"]),
            Paragraph("<b>MJ/m²/an</b>", styles["Normal"]),
        ],
        [
            f"IDC moyen 3 ans avant travaux ({data['annees_calcul_idc_avant_travaux']})",
            "Ef,avant,corr",
            f"{data['ef_avant_corr_kwh_m2']:.1f}",
            f"{data['ef_avant_corr_kwh_m2']*3.6:.1f}",
        ],
        [
            "EF pondéré corrigé clim. après travaux",
            "Ef,après,corr,rénové*fp",
            f"{data['energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2']:.1f}",
            f"{data['energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2']*3.6:.1f}",
        ],
        [
            "Objectif en énergie finale",
            "Ef,obj*fp",
            f"{data['ef_objectif_pondere_kwh_m2']:.1f}",
            f"{data['ef_objectif_pondere_kwh_m2']*3.6:.1f}",
        ],
        [
            "Baisse mesurée",
            "∆Ef,réel",
            f"{data['ef_avant_corr_kwh_m2'] - data['energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2']:.1f}",
            f"{(data['ef_avant_corr_kwh_m2'] - data['energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2'])*3.6:.1f}",
        ],
        [
            "Baisse objectif",
            "∆Ef,visée",
            f"{data['delta_ef_visee_kwh_m2']:.1f}",
            f"{data['delta_ef_visee_kwh_m2']*3.6:.1f}",
        ],
    ]

    # Adjust column widths for the additional column
    project_results_table = Table(project_results, colWidths=[260, 115, 65, 60])

    # Update the table style for the additional column
    project_results_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, 1),
                    colors.white,
                ),  # Background for header row
                ("TEXTCOLOR", (0, 0), (-1, 1), colors.black),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),  # Left-align first column
                ("ALIGN", (1, 0), (1, -1), "LEFT"),  # Left-align second column
                ("ALIGN", (2, 0), (-1, -1), "CENTER"),  # Center-align other columns
                ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),  # Font size for title row
                ("FONTSIZE", (0, 1), (-1, 1), 10),  # Font size for header row
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),  # Padding for title row
                (
                    "BACKGROUND",
                    (0, 2),
                    (-1, -1),
                    colors.white,
                ),  # Background for data rows
                (
                    "TEXTCOLOR",
                    (0, 2),
                    (-1, -1),
                    colors.black,
                ),  # Text color for data rows
                ("FONTNAME", (0, 2), (-1, -1), "Helvetica"),  # Font for data rows
                ("FONTSIZE", (0, 2), (-1, -1), 10),  # Font size for data rows
                ("TOPPADDING", (0, 0), (-1, -1), 3),  # Padding adjustments
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),  # Table grid
                ("SPAN", (0, 0), (-1, 0)),  # Merge cells in title row
            ]
        )
    )

    # Add the table to the document
    elements.append(project_results_table)
    elements.append(Spacer(1, 1.0 * cm))

    # Bar chart
    graphique_bars_rapport(
        data["nom_projet"],
        data["ef_avant_corr_kwh_m2"],
        data[
            "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
        ],
        data["ef_objectif_pondere_kwh_m2"],
        data["atteinte_objectif"],
        data["facteur_ponderation_moyen"],
        data["amoen_id"],
    )
    elements.append(Image("01_bar_chart.png", width=510, height=280))
    elements.append(Spacer(1, 0.5 * cm))

    if data["sre_extension_surelevation_m2"] > 0.0:
        elements.append(PageBreak())
        elements.append(Spacer(1, 0.5 * cm))
        repartition_renove_sureleve(
            data["sre_renovation_m2"],
            data["sre_extension_surelevation_m2"],
            data["repartition_energie_finale_partie_renovee_chauffage"],
            data["repartition_energie_finale_partie_renovee_ecs"],
            data["repartition_energie_finale_partie_surelevee_chauffage"],
            data["repartition_energie_finale_partie_surelevee_ecs"],
            data["ef_avant_corr_kwh_m2"],
            data["ef_objectif_pondere_kwh_m2"],
            data[
                "energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2"
            ],
        )
        elements.append(Image("02_reno_sur.png", width=510, height=510))
    # elements.append(PageBreak())
    # elements.append(Spacer(1, 0.5*cm))

    doc.build(
        elements,
        onFirstPage=lambda canvas, doc: (header(canvas, doc), footer(canvas, doc)),
        onLaterPages=lambda canvas, doc: (header(canvas, doc), footer(canvas, doc)),
    )
    buffer.seek(0)

    # Save the PDF to a file
    today = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_filename = f"{data['amoen_id']} - {data['nom_projet']} - {today}.pdf"
    with open(output_filename, "wb") as f:
        f.write(buffer.getvalue())

    return buffer, output_filename
