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
    PageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Line, String, Polygon
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
import io
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date, datetime
import os

def graphique_bars_rapport(site,
                            ef_avant_corr_kwh_m2,
                            energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2,
                            ef_objectif_pondere_kwh_m2,
                            atteinte_objectif,
                            facteur_ponderation_moyen,
                            amoen_id):

    # Données pour le graphique
    idc_moy_3ans_avant_MJ_m2 = ef_avant_corr_kwh_m2*3.6
    ef_objectif_pondere_MJ_m2 = ef_objectif_pondere_kwh_m2*3.6
    ef_apres_corr_MJ_m2 = energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2*3.6
    baisse_objectif_MJ_m2 = ef_avant_corr_kwh_m2*3.6 - ef_objectif_pondere_kwh_m2*3.6
    baisse_mesuree_MJ_m2 = ef_avant_corr_kwh_m2*3.6 - energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2*3.6

    # données pour le graphique
    bar_data1 = pd.DataFrame({
        'Nom_projet': [site,
                        site,
                        site],
        'Type': ['IDC moy 3 ans avant\n$IDC_{moy3ans}$',
                    'Objectif\n$E_{f,obj}*f_{p}$',
                    'Conso mesurée après\n$E_{f,après,corr}*f_{p}$'],
        'Valeur': [idc_moy_3ans_avant_MJ_m2,
                    ef_objectif_pondere_MJ_m2,
                    ef_apres_corr_MJ_m2]
    })

    # Générer histogramme. taillebin est utilisé pour uniformiser le format de l'histogramme et que les axes
    # correspondent bien à la largeur des barres (bin)
    cm = 1 / 2.54
    sns.set (style='white',rc={"figure.figsize":(30* cm, 14.2 * cm)})
    # ax1 = sns.catplot(x='Nom_projet', y='Valeur', hue='Type', kind='bar', data=bar_data1)
    
    ax = sns.barplot (y="Valeur",
                        x="Type",
                        data=bar_data1,
                        order=['IDC moy 3 ans avant\n$IDC_{moy3ans}$',"Objectif\n$E_{f,obj}*f_{p}$",'Conso mesurée après\n$E_{f,après,corr}*f_{p}$'],
                        palette=['#1f77b4', '#ff7f0e', '#2ca02c'])
    
    sns.despine()

    for i, val in enumerate(bar_data1['Valeur']):
        ax.text(i, val + 0.5, f"{val:.1f}", ha='center', va='bottom', color='black', fontsize=18)

    ####################

    # première flèche
    # find the height of the first and third bars
    first_bar_height = idc_moy_3ans_avant_MJ_m2
    second_bar_height = ef_objectif_pondere_MJ_m2
    # set the x-coordinate for the third bar
    x_coord_second_bar = 0.7  # this depends on the actual x-coordinate of the third bar
    # text for the arrow
    text_arrow_baisse_realisee = "Baisse\nobjectif\n"+str('{:.1f}'.format(baisse_objectif_MJ_m2)) + " MJ/m²"
    # add text at the midpoint of the arrow
    midpoint_height = (first_bar_height + second_bar_height) / 2
    # plot the line (arrow without arrowheads)
    ax.annotate("", xy=(x_coord_second_bar, second_bar_height), xytext=(x_coord_second_bar, first_bar_height),
                arrowprops=dict(arrowstyle="<->", color='moccasin', lw=3))  # increase lw for a thicker line
    # # add the text over the line and centered
    u = ax.text(x_coord_second_bar, midpoint_height, text_arrow_baisse_realisee, ha='center', va='center', rotation=0,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="white", lw=2), fontsize=18)

    # deuxième flèche
    # find the height of the first and third bars
    third_bar_height = ef_apres_corr_MJ_m2
    # set the x-coordinate for the third bar
    x_coord_third_bar = 1.7  # this depends on the actual x-coordinate of the third bar
    # text for the arrow
    text_arrow_baisse_realisee = "Baisse\nmesurée\n"+str('{:.1f}'.format(baisse_mesuree_MJ_m2)) + " MJ/m²"
    # add text at the midpoint of the arrow
    midpoint_height = (first_bar_height + third_bar_height) / 2
    # plot the line (arrow without arrowheads)
    ax.annotate("", xy=(x_coord_third_bar, third_bar_height), xytext=(x_coord_third_bar, first_bar_height),
                arrowprops=dict(arrowstyle="->", color='lightgreen', lw=4))  # increase lw for a thicker line
    # add the text over the line and centered
    u = ax.text(x_coord_third_bar, midpoint_height, text_arrow_baisse_realisee, ha='center', va='center', rotation=0,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="lime", lw=2), fontsize=18)

    #####################

    # titre de l'histogramme
    title_text = str('{:.1f}'.format(atteinte_objectif*100)) + "% de l'objectif atteint\n"
    title_color = 'darkgreen' if atteinte_objectif*100 >= 85 else 'red'
    plt.title(title_text, weight='bold', color=title_color, loc='center', pad=15, fontsize=20, y=0.925)
    plt.subplots_adjust (top=.945, bottom=.17, left=.06, right=.97, hspace=.2, wspace=.2)


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
    
    
    formula_atteinte_objectif_titre = r"$Atteinte\ objectif \ [-]=$"
    formula_atteinte_objectif_titre_pourcent = r"$Atteinte\ objectif \ [\%]=$"

    formula_atteinte_objectif = r"$\frac{{\Delta E_{{f,réel}}}}{{\Delta E_{{f,visée}}}} = \frac{{E_{{f,avant,corr}} - E_{{f,après,corr,rénové}}*f_{{p}}}}{{E_{{f,avant,corr}} - E_{{f,obj}}*f_{{p}}}}=$"

    formula_atteinte_objectif_num = r"$\frac{{{} - {}*{}}}{{{} - {}*{}}}$".format(
        round(idc_moy_3ans_avant_MJ_m2,1),
        round(ef_apres_corr_MJ_m2, 1),
        facteur_ponderation_moyen,
        round(idc_moy_3ans_avant_MJ_m2,1),
        round(ef_objectif_pondere_MJ_m2,1),
        facteur_ponderation_moyen,
    )

    formula_atteinte_objectifs_pourcent = r"${} \%$".format(
        round(atteinte_objectif*100, 1)
    )

    xlabel_sep_x = 0.25
    xlabel_sep_y = -0.17
    xlabel_level1 = -0.3
    xlabel_level2 = xlabel_level1 + xlabel_sep_y

    u1_titre = plt.text(0, xlabel_level1, formula_atteinte_objectif_titre, ha='left', va='center', transform=ax.transAxes, fontsize=18)
    u2_titre = plt.text(0, xlabel_level2, formula_atteinte_objectif_titre_pourcent, ha='left', va='center', transform=ax.transAxes, fontsize=18)
    u1 = plt.text(0.27, xlabel_level1, formula_atteinte_objectif, ha='left', va='center', transform=ax.transAxes, fontsize=24)
    u2 = plt.text(0.78, xlabel_level1, formula_atteinte_objectif_num, ha='left', va='center', transform=ax.transAxes, fontsize=24)
    u3 = plt.text(0.27, xlabel_level2, formula_atteinte_objectifs_pourcent, ha='left', va='center', transform=ax.transAxes, fontsize=20)


    # display(formula_atteinte_objectif)
    # plt.xlabel(formula_atteinte_objectif,
    #         loc='left', size=14)

    # remove xlabel
    plt.xlabel('')

    # titre pour l'ordonnée Y
    plt.ylabel("[MJ/m²/an]", fontsize=18)

    # fontsize xticks/yticks
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    
    # sauvegarder graphique
    plt.savefig ('01_bar_chart.png', dpi=600, bbox_inches='tight')

    # nettoyage
    plt.close()


def header(canvas, doc):
    # Get the directory of the current script (rapport.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the path to the images folder
    img_folder = os.path.join(current_dir, 'img')

    canvas.saveState()

    # Add images
    img_path_eco21 = os.path.join(img_folder, 'eco21.png')
    img_path_etat = os.path.join(img_folder, 'etat.jpg')
    img_path_hepia = os.path.join(img_folder, 'hepia.jpg')
    try:
        scale1 = 2
        canvas.drawImage(img_path_eco21, 1.5*cm, 27*cm, width=1.88*cm*scale1, height=1*cm*scale1, preserveAspectRatio=True, mask='auto')
        scale2 = 2
        canvas.drawImage(img_path_etat, 6*cm, 27*cm, width=1.88*cm*scale2, height=1*cm*scale2, preserveAspectRatio=True, mask='auto')
        scale3 = 1.15
        canvas.drawImage(img_path_hepia, 15*cm, 27.2*cm, width=3.92*cm*scale3, height=1*cm*scale3, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"Error processing image: {e}")
    canvas.restoreState()

def footer(canvas, doc):
    canvas.saveState()
    # Add your footer content here
    canvas.setFont('Helvetica', 8)
    canvas.drawString(doc.leftMargin, doc.bottomMargin - 0.75*cm, f"Page {doc.page}")
    canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 0.75*cm, f"Généré le {datetime.now().strftime('%Y-%m-%d')}")
    canvas.restoreState()

def generate_pdf(data):
    buffer = io.BytesIO()
    # Create the document with a custom page size that leaves room for header and footer
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            topMargin=3*cm,
                            bottomMargin=1.5*cm,
                            leftMargin=1*cm, rightMargin=1*cm)
    
    # Create frames for the content
    content_frame = Frame(doc.leftMargin, doc.bottomMargin, 
                        doc.width, doc.height,
                        id='normal')
    
    # Create a custom PageTemplate
    template = PageTemplate(id='test', frames=content_frame,
                            onPage=lambda canvas, doc: (header(canvas, doc), footer(canvas, doc)))
    
    # Add the template to the document
    doc.addPageTemplates([template])
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))
    styles.add(ParagraphStyle(name='SmallCenter', alignment=1, fontSize=8))
    styles.add(ParagraphStyle(name='SmallText', parent=styles['Normal'], fontSize=8))
    elements = []

    # elements.append(Spacer(1, 0.5*cm))

    # Title
    title_report = f"Rapport " + data['nom_projet']
    elements.append(Paragraph(title_report, styles['Title']))
    elements.append(Spacer(1, 0.5*cm))
    
    # Project details
    project_admin = [
        [Paragraph("<b>Informations administratives</b>", styles['Heading4']), ''],  # Title row
        [Paragraph("", styles['SmallText']), ''], # Empty row
        [Paragraph("Adresse:", styles['SmallText']), data['adresse_projet']],
        [Paragraph("AMOén:", styles['SmallText']), data['amoen_id']],
    ]
    project_admin_table = Table(project_admin, colWidths=[150, 350])
    project_admin_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (1,1), colors.lightgrey),
        ('SPAN',(0,0),(1,1)),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(project_admin_table)
    elements.append(Spacer(1, 0.5*cm))

    # Surfaces
    project_surfaces = [
        [Paragraph("<b>Surfaces</b>", styles['Heading3']), ''],  # Title row
        [Paragraph("", styles['Normal']), ''], # Empty row
        [Paragraph("Surface rénovée (m² SRE):", styles['Normal']), f"{data['sre_renovation_m2']} m² SRE"],
    ]
    # Add conditional rows for different surface types
    for surface_type, percentage in [
        ('Habitat collectif', data['sre_pourcentage_habitat_collectif']),
        ('Habitat individuel', data['sre_pourcentage_habitat_individuel']),
        ('Administration', data['sre_pourcentage_administration']),
        ('Ecoles', data['sre_pourcentage_ecoles']),
        ('Commerce', data['sre_pourcentage_commerce']),
        ('Restauration', data['sre_pourcentage_restauration']),
        ('Lieux de rassemblement', data['sre_pourcentage_lieux_de_rassemblement']),
        ('Hopitaux', data['sre_pourcentage_hopitaux']),
        ('Industrie', data['sre_pourcentage_industrie']),
        ('Depots', data['sre_pourcentage_depots']),
        ('Installations sportives', data['sre_pourcentage_installations_sportives']),
        ('Piscines couvertes', data['sre_pourcentage_piscines_couvertes'])
    ]:
        if percentage > 0.0:
            project_surfaces.append([f"{surface_type} (%):", f"{percentage} % de la surface rénovée soit {(percentage/100*data['sre_renovation_m2']):.0f} m² SRE"])
  
    project_surfaces_table = Table(project_surfaces, colWidths=[150, 350])
    project_surfaces_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (1,1), colors.lightgrey),
        ('SPAN',(0,0),(1,1)),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(project_surfaces_table)
    elements.append(Spacer(1, 0.5*cm))

    # Conso énergie après travaux
    project_energie = [
        [Paragraph("<b>Consommation après travaux</b>", styles['Heading3']), ''],  # Title row
        [Paragraph("", styles['Normal']), ''], # Empty row
        ]
    # Add conditional rows for different energy types
    for energy_type, value, unit in [
        ('Mazout', data['agent_energetique_ef_mazout_kg'], 'kg'),
        ('Mazout', data['agent_energetique_ef_mazout_litres'], 'litres'),
        ('Mazout', data['agent_energetique_ef_mazout_kwh'], 'kWh'),
        ('Gaz naturel', data['agent_energetique_ef_gaz_naturel_m3'], 'm³'),
        ('Gaz naturel', data['agent_energetique_ef_gaz_naturel_kwh'], 'kWh'),
        ('Bois (buches dures)', data['agent_energetique_ef_bois_buches_dur_stere'], 'stères'),
        ('Bois (buches tendres)', data['agent_energetique_ef_bois_buches_tendre_stere'], 'stères'),
        ('Bois (buches tendres)', data['agent_energetique_ef_bois_buches_tendre_kwh'], 'kWh'),
        ('Pellets', data['agent_energetique_ef_pellets_m3'], 'm³'),
        ('Pellets', data['agent_energetique_ef_pellets_kg'], 'kg'),
        ('Pellets', data['agent_energetique_ef_pellets_kwh'], 'kWh'),
        ('Plaquettes', data['agent_energetique_ef_plaquettes_m3'], 'm³'),
        ('Plaquettes', data['agent_energetique_ef_plaquettes_kwh'], 'kWh'),
        ('CAD', data['agent_energetique_ef_cad_kwh'], 'kWh'),
        ('Electricité PAC', data['agent_energetique_ef_electricite_pac_kwh'], 'kWh'),
        ('Electricité directe', data['agent_energetique_ef_electricite_directe_kwh'], 'kWh'),
        ('Autre', data['agent_energetique_ef_autre_kwh'], 'kWh')
    ]:
        if value > 0.0:
            project_energie.append([f"{energy_type} ({unit}):", f"{value:.1f} {unit} du {data['periode_start'].date()} au {data['periode_end'].date()}"])

    project_energie_table = Table(project_energie, colWidths=[150, 350])
    project_energie_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (1,1), colors.lightgrey),
        ('SPAN',(0,0),(1,1)),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(project_energie_table)
    elements.append(Spacer(1, 0.5*cm))

    # Energy data table
    project_results = [
        [Paragraph("<b>Atteinte de l'objectif</b>", styles['Heading3'])],  # Title row
        [Paragraph("<b>Variable</b>", styles['Normal']), Paragraph("<b>kWh/m²/an</b>", styles['Normal']), Paragraph("<b>MJ/m²/an</b>", styles['Normal'])],
        [f"IDC moyen 3 ans avant travaux → (Ef,avant,corr)", f"{data['ef_avant_corr_kwh_m2']:.1f}", f"{data['ef_avant_corr_kwh_m2']*3.6:.1f}"],
        [f"EF pondéré corrigé clim. après travaux → (Ef,après,corr,rénové*fp)", f"{data['energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2']:.1f}", f"{data['energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2']*3.6:.1f}"],
        [f"Objectif en énergie finale (Ef,obj *fp)", f"{data['ef_objectif_pondere_kwh_m2']:.1f}", f"{data['ef_objectif_pondere_kwh_m2']*3.6:.1f}"],
        [f"Baisse ΔEf réalisée → ∆Ef,réel", f"{data['ef_avant_corr_kwh_m2'] - data['energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2']:.1f}", f"{(data['ef_avant_corr_kwh_m2'] - data['energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2'])*3.6:.1f}"],
        [f"Baisse ΔEf visée → ∆Ef,visée", f"{data['delta_ef_visee_kwh_m2']:.1f}", f"{data['delta_ef_visee_kwh_m2']*3.6:.1f}"]
    ]

    project_results_table = Table(project_results, colWidths=[375, 65, 60])
    project_results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),  # Add background to the second row
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Left-align the first column
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),  # Center-align the other columns
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, 1), 10),  # Adjust font size for the second row
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 2), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 2), (-1, -1), colors.black),
        ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 2), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('SPAN', (0, 0), (-1, 0)),  # Merge cells in the first row
    ]))
    elements.append(project_results_table)
    elements.append(Spacer(1, 1.0*cm))

    # Bar chart
    graphique_bars_rapport(data['nom_projet'],
                                        data['ef_avant_corr_kwh_m2'],
                                        data['energie_finale_apres_travaux_climatiquement_corrigee_renovee_pondere_kwh_m2'],
                                        data['ef_objectif_pondere_kwh_m2'],
                                        data['atteinte_objectif'],
                                        data['facteur_ponderation_moyen'],
                                        data['amoen_id'])
    elements.append(Image('01_bar_chart.png', width=510, height=280))
    # elements.append(PageBreak())
    # elements.append(Spacer(1, 0.5*cm))

    doc.build(elements, onFirstPage=lambda canvas, doc: (header(canvas, doc), footer(canvas, doc)),
                    onLaterPages=lambda canvas, doc: (header(canvas, doc), footer(canvas, doc)))
    buffer.seek(0)

    # Save the PDF to a file
    today = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_filename = f"{data['amoen_id']} - {data['nom_projet']} - {today}.pdf"
    with open(output_filename, 'wb') as f:
        f.write(buffer.getvalue())

    return buffer, output_filename
