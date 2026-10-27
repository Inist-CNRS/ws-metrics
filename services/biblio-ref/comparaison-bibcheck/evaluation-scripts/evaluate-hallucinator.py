import json
from hallucinator import PdfExtractor, Validator, ValidatorConfig
from sklearn.metrics import classification_report
import pandas as pd
import os
from tqdm import tqdm


def print_metrics_table(y_true, y_pred, labels, title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0
    )
    df = pd.DataFrame(report).T
    df = df.loc[labels, ["precision", "recall", "f1-score", "support"]]
    print(df.round(3))

def map_tool_status(validation_result):
    """Mappe un ValidationResult (status global + retraction_info) vers tes labels attendus.

    ATTENTION : ValidationResult.status ne prend que 3 valeurs :
    "verified", "not_found", "author_mismatch".
    Les statuts "match"/"no_match"/"timeout"/"rate_limited"/"error"/"skipped"
    existent uniquement au niveau de chaque base (validation_result.db_results[x].status),
    pas au niveau du résultat global - donc on ne les teste pas ici.
    """
    if validation_result.retraction_info and validation_result.retraction_info.is_retracted:
        return "retracted"

    status = validation_result.status
    if status in ("verified", "author_mismatch"):
        return "found"
    elif status == "not_found":
        return "to_be_verified"
    else:
        return "not_found"

def clean_reference_text(ref_text):
    """Nettoie le texte d'une référence (retire les préfixes [1], (1), etc.)."""
    ref_text = ref_text.strip()
    if ref_text.startswith("["):
        ref_text = ref_text.split("]", 1)[1].strip()
    elif ref_text.startswith("("):
        ref_text = ref_text.split(")", 1)[1].strip()
    return ref_text

def evaluate_bibcheck_tool(corpus_path, pdf_path):
    # chargement du corpus JSONL (pour les labels)
    corpus = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            corpus.append(json.loads(line))
    print(f"Chargé {len(corpus)} références depuis le corpus.")

    # Viens d'halucinator
    ext = PdfExtractor()
    extraction_result = ext.extract(pdf_path)
    extracted_refs = extraction_result.references
    print(f"Extrait {len(extracted_refs)} références depuis le PDF.")

    print("\n🔎 Validation des références avec l'outil...")
    config = ValidatorConfig()
    config.openalex_key = os.getenv("OPENALEX_API_KEY")
    config.crossref_mailto = os.getenv("MAIL")
    config.cache_path = "hallucinator_cache.db"
    validator = Validator(config)

    progress_bar = tqdm(total=len(extracted_refs), desc="Validation des références")

    def on_progress(event):
        if event.event_type == "result":
            progress_bar.update(1)

    validation_results = validator.check(extracted_refs, progress=on_progress)
    progress_bar.close()

    indices_to_keep = [
        i for i, entry in enumerate(corpus)
    ]

    filtered_corpus = [corpus[i] for i in indices_to_keep]
    filtered_extracted_refs = [extracted_refs[i] for i in indices_to_keep]
    filtered_validation_results = [validation_results[i] for i in indices_to_keep]

    print(f"Filtratiojn : {len(filtered_corpus)} références non-hallucinées conservées.")

    # On vérifie que le nombre de références correspond (après filtrage)
    if len(filtered_corpus) != len(filtered_extracted_refs):
        print(f"Attention : Le corpus filtré contient {len(filtered_corpus)} références, mais les références extraites filtrées en contiennent {len(filtered_extracted_refs)}.")
        min_count = min(len(filtered_corpus), len(filtered_extracted_refs))
        print(f" On utilise les {min_count} premières références pour l'évaluation.")
    else:
        min_count = len(filtered_corpus)

    # fichier res
    print("\n Création du fichier res_hallucinator.jsonl...")
    with open("res_hallucinator.jsonl", "w", encoding="utf-8") as f:
        for i in range(min_count):
            ref_text = clean_reference_text(filtered_extracted_refs[i].raw_citation)
            vr = filtered_validation_results[i]
            if vr.retraction_info and vr.retraction_info.is_retracted:
                status = "retracted"
            else:
                status = vr.status  # "verified" | "not_found" | "author_mismatch"
            entry = {
                "id": filtered_corpus[i]["id"],
                "ref_from_pdf": ref_text,
                "status_res": status
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Fichier res_hallucinator.jsonl créé avec {min_count} entrées.")

    # Classif
    labels = ["found", "not_found", "retracted"]
    y_true_all = []
    y_pred_all = []
    y_true_doi = []
    y_pred_doi = []
    y_true_no_doi = []
    y_pred_no_doi = []

    for i in range(min_count):
        expected = filtered_corpus[i]["expected_result"]
        has_doi = filtered_corpus[i]["has_doi"]
        mapped_status = map_tool_status(filtered_validation_results[i])

        # ICI on filtre sur les not_found :
        # Ils moissonent d'autres API et peuvent très bien trouver un not found.
        # Ça les défavoriserait à tord.
        if expected == "not_found":
            continue
        y_true_all.append(expected)
        y_pred_all.append(mapped_status)

        if has_doi == "yes":
            y_true_doi.append(expected)
            y_pred_doi.append(mapped_status)
        else:
            y_true_no_doi.append(expected)
            y_pred_no_doi.append(mapped_status)

    print_metrics_table(y_true_no_doi, y_pred_no_doi, labels, "Métriques : Références SANS DOI")
    print_metrics_table(y_true_doi, y_pred_doi, labels, "Métriques : Références AVEC DOI")
    print_metrics_table(y_true_all, y_pred_all, labels, "Métriques : TOUTES les références")

#main
if __name__ == "__main__":
    evaluate_bibcheck_tool(
        corpus_path="evaluation-datas/corpus_bibcheck_v7.jsonl",
        pdf_path="evaluation-datas/corpus_bibcheck_v7.pdf"
    )