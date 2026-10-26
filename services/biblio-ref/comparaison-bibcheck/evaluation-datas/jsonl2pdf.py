#!/usr/bin/env python3
"""
Script simplifié pour convertir un JSONL de références bibliographiques en PDF.

Les références sont déjà formatées dans le champ 'id' du JSONL.
Le PDF généré contient un faux article avec une section References qui reprend
les références telles quelles depuis le champ 'id'.

Usage:
    python jsonl_to_pdf_simple.py input.jsonl output.pdf
"""

import json
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def create_fake_article():
    """Génère un faux contenu d'article académique."""
    return {
        "title": "Le jeu de données d'évaluation de bibCheck au format PDF",
        "abstract": "Une phrase pour préserver la structure d'un article scientifique ",
        "introduction": """
        Une phrase pour préserver la structure usuelle d'un artcile scientifique
        """
    }

def create_pdf(input_jsonl, output_pdf):
    """Crée un PDF à partir d'un fichier JSONL."""
    # Lit le fichier JSONL
    references = []
    with open(input_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    # On prend directement le champ 'id' qui contient la référence formatée
                    ref_text = data.get('id', '')
                    if ref_text:
                        references.append(ref_text)
                except json.JSONDecodeError as e:
                    print(f"Warning: Impossible de parser la ligne: {line[:100]}... Erreur: {e}")

    if not references:
        print("Erreur: Aucune référence valide trouvée dans le fichier d'entrée.")
        sys.exit(1)

    # Génère le contenu de l'article
    article = create_fake_article()

    # Crée le document PDF
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        alignment=1,  # Centré
        spaceAfter=30,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        leading=18,
        spaceBefore=12,
        spaceAfter=6,
    )

    abstract_style = ParagraphStyle(
        'CustomAbstract',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        spaceBefore=6,
        spaceAfter=12,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        leading=14,
        spaceAfter=6,
    )

    reference_style = ParagraphStyle(
        'CustomReference',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        spaceAfter=8,
        leftIndent=20,
    )

    # Construction du document
    story = []

    # Titre
    story.append(Paragraph(article['title'], title_style))
    story.append(Spacer(1, 0.25*inch))

    # Auteurs
    story.append(Paragraph("Léo Gaillard", styles['Normal']))
    story.append(Paragraph(f"Inist-CNRS (UAR76), Vandoeuvre-lès-Nancy\n01 octobre 2026",
                          styles['Normal']))
    story.append(Spacer(1, 0.5*inch))

    # Résumé
    story.append(Paragraph("Abstract", heading_style))
    story.append(Paragraph(article['abstract'], abstract_style))
    story.append(Spacer(1, 0.25*inch))

    # Introduction
    story.append(Paragraph("1. Introduction", heading_style))
    story.append(Paragraph(article['introduction'], body_style))
    story.append(Spacer(1, 0.25*inch))

    # Références
    story.append(Paragraph("References", heading_style))

    for i, ref in enumerate(references, 1):
        # On ajoute le numéro de référence
        formatted_ref = f"[{i}] {ref}"
        story.append(Paragraph(formatted_ref, reference_style))

    # Génère le PDF
    doc.build(story)
    print(f"PDF créé avec succès ({len(references)} références) : {output_pdf}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python jsonl_to_pdf_simple.py input.jsonl output.pdf")
        print("\nExemple:")
        print("  python jsonl_to_pdf_simple.py references.jsonl article.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    create_pdf(input_file, output_file)