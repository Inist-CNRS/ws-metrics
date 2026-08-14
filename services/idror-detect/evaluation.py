import pandas as pd
import requests


def ws_affiliation(affiliation):
    url = "https://affiliations-tools.services.istex.fr/v1/ror/get-id"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = [{"id": affiliation, "value": affiliation}]
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def get_ws_result(affiliation):
    """
    Interrogation du WS.
    Renvoie l'id_ror si trouvé, sinon le status (ex: 'no match found', 'no city found'), ou 'error' en cas d'exception.
    """
    try:
        result = ws_affiliation(affiliation)
        value = result[0]["value"]
        status = value.get("status", "")
        id_ror = value.get("id_ror", "")

        if status in {"no match found", "no city found"} or not id_ror:
            return status
        return id_ror
    except Exception as e:
        print(f"Erreur pour '{affiliation}': {e}")
        return "error"


def check_result(ws_result, label):
    """
    Compare le résultat du WS au label attendu.
    - 'non trouvé' si le WS renvoie un des statuts {"no match found", "no city found"}
    - True si ws_result == label
    - False si ws_result != label
    """
    if ws_result in {"no match found", "no city found"}:
        return "non trouvé"
    return ws_result == label


def evaluate(tsv_path, sep="\t"):
    df = pd.read_csv(tsv_path, sep=sep, dtype=str)

    df["ws_result"] = df["affiliation"].apply(get_ws_result)
    df["evaluation"] = df.apply(lambda row: check_result(row["ws_result"], row["label"]), axis=1)

    TP = (df["evaluation"] == True).sum()
    FP = (df["evaluation"] == False).sum()
    FN = (df["evaluation"] == "non trouvé").sum()

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0)

    print(f"True Positive={TP}  False Positive={FP}  False Negative={FN}")
    print(f"Précision : {precision:.4f}")
    print(f"Rappel    : {recall:.4f}")
    print(f"F-mesure  : {f1:.4f}")

    print(df)
    df.to_csv("evaluation_results.tsv", sep="\t", index=False)
    return df


if __name__ == "__main__":
    evaluate("corpus.tsv") # à modifier selon le nom du fichier à évaluer