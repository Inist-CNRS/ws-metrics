import csv
import json
import sys
import difflib
import numpy as np
from Levenshtein import distance as levenshtein_distance
from scipy.optimize import linear_sum_assignment

"""
Nous avons remarqué que la sortie d'hallucinator pouvait être différente :
Références répétées, ou références manquantes, ...

Nous avons donc décidé d'écrire ce programme pour réordonner les références
et vérifier celles remplacées / supprimées.
"""
# Nous voulons un match exact : à 0
# et on marque l'entrée comme "not_extracted" plutôt que de forcer un mauvais match.
DISTANCE_THRESHOLD = 0.05


def load_jsonl(filepath):
    with open(filepath, 'r') as f:
        return [json.loads(line) for line in f]


def load_csv(filepath):
    with open(filepath, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)


def explain_diff(a, b):
    """Retourne un résumé des différences caractère par caractère entre deux ids."""
    sm = difflib.SequenceMatcher(None, a, b)
    parts = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        a_frag = a[i1:i2]
        b_frag = b[j1:j2]
        if tag == 'replace':
            parts.append(f"remplace '{a_frag}' -> '{b_frag}'")
        elif tag == 'delete':
            parts.append(f"absent chez result: '{a_frag}'")
        elif tag == 'insert':
            parts.append(f"ajouté chez result: '{b_frag}'")
    return "; ".join(parts) if parts else "aucune différence détectée (bizarre si distance > 0)"


def build_distance_matrix(corpus, results, corpus_key, result_key):
    n, m = len(corpus), len(results)
    dist_matrix = np.zeros((n, m))
    for i, c in enumerate(corpus):
        cid = c[corpus_key] or ""
        for j, r in enumerate(results):
            rid = r[result_key] or ""
            d = levenshtein_distance(cid, rid)
            max_len = max(len(cid), len(rid))
            dist_matrix[i, j] = d / max_len if max_len else 0.0
    return dist_matrix


def reorder_results(corpus_path, results_path, output_path=None, threshold=DISTANCE_THRESHOLD,
                     corpus_key='id', result_key='value/reference'):
    corpus = load_jsonl(corpus_path)
    results = load_csv(results_path)

    n, m = len(corpus), len(results)
    dist_matrix = build_distance_matrix(corpus, results, corpus_key, result_key)

    # Assignation OPTIMALE (algorithme de Hungarian / Kuhn-Munkres) au lieu d'un
    # matching glouton : ça évite qu'une entrée "vole" par erreur le résultat
    # qui appartenait en réalité à une autre entrée du corpus.
    row_ind, col_ind = linear_sum_assignment(dist_matrix)
    assigned = dict(zip(row_ind, col_ind))

    ordered_results = [None] * n

    for corpus_idx, corpus_item in enumerate(corpus):
        corpus_id = corpus_item[corpus_key]

        if corpus_idx not in assigned:
            # Il y avait moins de résultats que d'entrées dans le corpus.
            print(f"[NOT_EXTRACTED] Aucun résultat disponible pour assigner à | "
                  f"Corpus: \"{corpus_id}\"", file=sys.stderr)
            ordered_results[corpus_idx] = {
                "id": corpus_id,
                "status_res": "not_extracted",
                "error": "no_result_available"
            }
            continue

        result_idx = assigned[corpus_idx]
        best_distance = dist_matrix[corpus_idx, result_idx]
        result = results[result_idx]

        if best_distance > threshold:
            # Le meilleur candidat dispo est quand même trop éloigné : on ne force
            # pas le match, on marque l'entrée comme non retrouvée.
            print(
                f"[NOT_EXTRACTED] Distance: {best_distance:.4f} (> seuil {threshold}) | "
                f"Corpus: \"{corpus_id}\" | Candidat le plus proche rejeté: \"{result[result_key]}\"",
                file=sys.stderr
            )
            ordered_results[corpus_idx] = {
                "id": corpus_id,
                "status_res": "not_extracted",
                "error": "no_reliable_match_in_results"
            }
            continue

        # On garde toute la ligne CSV (doi, status, mismatches, etc.) + une trace
        # du corpus_id auquel elle a été rattachée, car le "id" du CSV est un PID
        # de document, pas un identifiant de référence individuelle.
        result_out = dict(result)
        result_out['matched_corpus_id'] = corpus_id
        result_out['match_distance'] = round(float(best_distance), 4)
        ordered_results[corpus_idx] = result_out

        if best_distance > 0:
            result_id = result[result_key]
            print(
                f"[REORDER] Distance: {best_distance:.4f}\n"
                f"  Corpus : \"{corpus_id}\"\n"
                f"  Result : \"{result_id}\"\n"
                f"  Diff   : {explain_diff(corpus_id, result_id)}",
                file=sys.stderr
            )

    if output_path:
        with open(output_path, 'w') as f:
            for item in ordered_results:
                f.write(json.dumps(item) + '\n')

    return ordered_results


if __name__ == "__main__":
    CORPUS_PATH = "evaluation-datas/corpus_bibcheck_v7.jsonl"
    RESULTS_PATH = "results/bibcheck-pdf/res_bibcheck-pdf.csv"
    OUTPUT_PATH = "results/bibcheck-pdf/res_bibcheck-pdf_reordered.jsonl"

    ordered = reorder_results(
        CORPUS_PATH, RESULTS_PATH, OUTPUT_PATH,
        corpus_key='id', result_key='value/reference'
    )

    total = len(ordered)
    not_extracted = sum(1 for item in ordered if item.get("status_res") == "not_extracted")
    matched = total - not_extracted
    print(f"✅ Appariement : {matched}/{total} ({matched/total*100:.1f}%)")
    if not_extracted:
        print(f"⚠️  Non retrouvées : {not_extracted}/{total}")