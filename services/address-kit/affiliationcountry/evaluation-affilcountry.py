import json
import unicodedata

import pandas as pd
import requests

WS_URL = "https://address-kit.services.istex.fr/v1/affiliationcountry/affilcountry"
HEADERS = {"accept": "application/json", "Content-Type": "application/json"}
FIELDS = {
    "city": "city",
    "country": "country",
    "country_code": "code",
}

def normalize(value):
    """Minuscules, sans accents, sans espaces superflus (Tübingen == tubingen)."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(text.casefold().split())

def ws_affiliations(affiliations):
    """Interroge le WS avec une liste d'affiliations (un seul appel).
    Renvoie un dict {id: value}."""
    data=[]
    for i, affiliation in enumerate(affiliations):
        data.append({"id": str(i), "value": affiliation})
    response = requests.post(WS_URL, headers=HEADERS, json=data, timeout=120)
    response.raise_for_status()
    result = {}
    for item in response.json():
        result[item["id"]] = item.get("value", {})
    return result

def get_ws_results(affiliations, batch_size=50):
    """Renvoie une liste de dicts {city, country, country_code} alignée sur `affiliations`.
    En cas d'erreur sur un lot, les lignes concernées valent 'error'."""
    results = []
    for start in range(0, len(affiliations), batch_size):
        batch = affiliations[start:start + batch_size]
        try:
            by_id = ws_affiliations(batch)
            for i in range(len(batch)):
                value = by_id.get(str(i), {})
                results.append({
                    "city": value.get("city", ""),
                    "country": value.get("country", ""),
                    "country_code": value.get("country_code", ""),
                })
        except Exception as e:
            print(f"Erreur pour le lot {start}-{start + len(batch) - 1}: {e}")
            results.extend({f: "error" for f in FIELDS} for _ in batch)
    return results


def check_result(ws_value, expected):
    """'non trouvé' si le WS ne renvoie rien d'exploitable, sinon True/False."""
    ws_norm = normalize(ws_value)
    if ws_norm in ("n/a", ""):
        return "non trouvé"
    if ws_norm == "error":
        return "error"
    return ws_norm == normalize(expected)

def metrics(series):
    TP = (series == True).sum()
    FP = (series == False).sum()
    FN = (series == "non trouvé").sum()
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return TP, FP, FN, precision, recall, f1


def evaluate(jsonl_path, errors_path="evaluation_errors.txt", batch_size=50):
    """Évalue le WS sur un corpus annoté : affiche les métriques par champ
    et enregistre les erreurs dans un fichier texte."""
    # Lecture du corpus JSONL (une affiliation + sa vérité terrain par ligne)
    with open(jsonl_path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    # Appel du WS par lots ; résultats alignés sur l'ordre du corpus
    affiliations = [r["value"] for r in rows]
    ws_results = get_ws_results(affiliations, batch_size=batch_size)

    errors = []
    # Évaluation séparée pour chaque champ (city, country, country_code)
    for ws_field, corpus_field in FIELDS.items():
        evals = []
        for i, (row, ws) in enumerate(zip(rows, ws_results)):
            # Valeur attendue (le corpus utilise "code" au lieu de "country_code")
            expected = row["expected_result"].get(corpus_field, "")
            # Verdict : True, False, "non trouvé" ou "error"
            verdict = check_result(ws[ws_field], expected)
            evals.append(verdict)
            # Tout ce qui n'est pas True est conservé pour le fichier d'erreurs
            if verdict is not True:
                errors.append(f"[{ws_field}] ligne {i} : {verdict}\n"
                              f"  affiliation : {row['value']}\n"
                              f"  attendu     : {expected}\n"
                              f"  obtenu      : {ws[ws_field]}\n")

        # Calcul et affichage des métriques pour ce champ
        TP, FP, FN, p, r, f1 = metrics(pd.Series(evals))
        print(f"\n== {ws_field} ==")
        print(f"TP={TP}  FP={FP}  FN={FN}")
        print(f"Précision : {p:.4f} | Rappel : {r:.4f} | F-mesure : {f1:.4f}")

    # Écriture de toutes les erreurs dans un fichier texte
    with open(errors_path, "w", encoding="utf-8") as f:
        f.write("\n".join(errors))
    print(f"\n{len(errors)} erreur(s) enregistrée(s) dans : {errors_path}")


if __name__ == "__main__":
    evaluate("merged_corpus_countryDetect.jsonl")  # à modifier selon le nom du fichier à évaluer