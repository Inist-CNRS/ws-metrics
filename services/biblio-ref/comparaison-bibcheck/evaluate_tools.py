import json
import pandas as pd
from sklearn.metrics import classification_report
from collections import defaultdict
import csv

def create_label_dict(corpus_path):
    """Crée un dictionnaire mapping label -> liste d'index ET sépare les index par has_doi."""
    dict_id2label = {
        "found": [],
        "not_found": [],
        "to_be_verified": [],
        "retracted": []
    }
    doi_yes_indices = []
    doi_no_indices = []

    with open(corpus_path, "r") as f:
        for idx, line in enumerate(f):
            data = json.loads(line)
            label = data["expected_result"].replace("feet_of_clay", "found")
            has_doi = data.get("has_doi", "no")  # Valeur par défaut si le champ est absent
            dict_id2label[label].append(idx)
            if has_doi == "yes":
                doi_yes_indices.append(idx)
            else:
                doi_no_indices.append(idx)

    return dict_id2label, doi_yes_indices, doi_no_indices

def constructlist_label_predict(res_file, predict_col_name, csv_sep=";"):
    """Charge un fichier et retourne la colonne de prédiction sous forme de liste."""
    if res_file.endswith('.jsonl'):
        df = pd.read_json(res_file, lines=True)
    elif res_file.endswith('.csv'):
        data = []
        with open(res_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=csv_sep, quotechar='"')
            for row in reader:
                data.append(row)
        df = pd.DataFrame(data)
    elif res_file.endswith('.xlsx'):
        df = pd.read_excel(res_file)
    else:
        raise ValueError("Format de fichier non supporté. Utilisez .jsonl ou .csv")
    return df[predict_col_name].tolist()

def mapping(dict_id2label, prediction, dict_prediction_mapping, add_to_reverse=None):
    """
    1. Filtre les labels selon les CLÉS de prediction_mapping (found/retracted)
    2. Mappe les prédictions vers les labels via l'INVERSE de prediction_mapping
    """
    reverse_mapping = {v: k for k, v in dict_prediction_mapping.items()}
    if add_to_reverse:
        for elt in add_to_reverse:
            reverse_mapping[elt] = add_to_reverse[elt]
    l_pred = []
    l_res = []

    for label, indices in dict_id2label.items():
        if label in dict_prediction_mapping:
            for idx in indices:
                pred = prediction[idx]
                l_pred.append(label)
                l_res.append(reverse_mapping.get(pred, pred))

    return l_pred, l_res

def disp_reports(list_prediction, list_results, title):
    """Affiche l'accuracy globale et par classe avec un titre personnalisé."""
    class_stats = defaultdict(lambda: {"correct": 0, "total": 0})

    for pred, res in zip(list_prediction, list_results):
        class_stats[pred]["total"] += 1
        if pred == res:
            class_stats[pred]["correct"] += 1

    print(f"\n{title}")
    print("Accuracy par classe:")
    print("-" * 40)
    for cls in sorted(class_stats.keys()):
        correct = class_stats[cls]["correct"]
        total = class_stats[cls]["total"]
        accuracy = (correct / total * 100) if total > 0 else 0
        print(f"{cls:20s}: {accuracy:.1f}% ({correct}/{total})")

    total_correct = sum(stats["correct"] for stats in class_stats.values())
    total_all = sum(stats["total"] for stats in class_stats.values())
    global_accuracy = (total_correct / total_all * 100) if total_all > 0 else 0
    print("-" * 40)
    print(f"Accuracy globale : {global_accuracy:.1f}% ({total_correct}/{total_all})\n\n")

def main():
    csv_sep = ";"
    labels_add_to_reverse = None
    



    # # bibcheck - csv
    # print("Tool : bibcheck-csv\n\n")
    # CORPUS_PATH = "evaluation-datas/corpus_bibcheck_v7.jsonl"
    # RES_FILE_PATH = "results/bibcheck/res_bibcheck.jsonl"
    # PREDICT_COL_NAME = "prediction"
    # csv_sep = ";"

    # prediction_mapping = {
    #     "found": "found",
    #     "to_be_verified": "to_be_verified",
    #     # "retracted": "retracted"
    # }







    # # bibcheck-pdf
    # print("Tool : bibcheck-pdf\n\n")
    # CORPUS_PATH = "evaluation-datas/corpus_bibcheck_v7.jsonl"
    # RES_FILE_PATH = "results/bibcheck-pdf/res_bibcheck-pdf_reordered.jsonl"
    # PREDICT_COL_NAME = "value/status"

    # prediction_mapping = {
    #     "found": "found",
    #     "to_be_verified": "to_be_verified",
    #     "retracted": "retracted"
    # }








    # # bibguard
    # print("Tool : Bibguard\n\n")
    # CORPUS_PATH = "evaluation-datas/corpus_bibcheck_v7.jsonl"
    # RES_FILE_PATH = "results/bibguard/res_bibguard.jsonl"
    # PREDICT_COL_NAME = "res_bibguard"

    # prediction_mapping = {
    #     "found": "✅",
    #     "to_be_verified": "⚠️"
    # }








    # # cerca
    # print("Tool : cerca\n\n")
    # CORPUS_PATH = "evaluation-datas/corpus_bibcheck_v7.jsonl"
    # RES_FILE_PATH = "results/cerca/res_cerca.csv"
    # PREDICT_COL_NAME = "Status"

    # prediction_mapping = {
    #     "found": "✅ PASS",
    #     "to_be_verified": "! CHECK"
    # }






    # # checkIfExist
    # print("Tool : checkIfExist\n\n")
    # CORPUS_PATH = "evaluation-datas/corpus_bibcheck_v7.jsonl"
    # RES_FILE_PATH = "results/checkIfExist/res_checkIfExist.xlsx"
    # PREDICT_COL_NAME = "Status"

    # prediction_mapping = {
    #     "found": "Verified",
    #     "to_be_verified": "Mismatch / Error"
    # }
    # labels_add_to_reverse = {"Partial Match": "found"}  # Pour ajouter les `Partial Match` comme found









    # # Hallucinator
    # print("Tool : Hallucinator\n\n")
    # CORPUS_PATH = "evaluation-datas/corpus_bibcheck_v7.jsonl"
    # RES_FILE_PATH = "results/hallucinator/res_hallucinator_reordered.jsonl"
    # PREDICT_COL_NAME = "status_res"

    # prediction_mapping = {
    #     "found": "verified",
    #     "retracted": "retracted",
    #     "to_be_verified": "mismatch"
    # }
    # # Pas de partial match dans notre corpus.
    # labels_add_to_reverse = {"Partial Match": "found"}  # Pour ajouter les `Partial Match` comme found








    # # paperpile
    # print("Tool : paperpile\n\n")
    # CORPUS_PATH = "evaluation-datas/corpus_bibcheck_v7.jsonl"
    # RES_FILE_PATH = "results/paperpile/res_paperpile.csv"
    # PREDICT_COL_NAME = "paperpile_result"
    # csv_sep = ","

    # prediction_mapping = {
    #     "found": "v"
    #     }






    # Charge les données
    dict_id2label, doi_yes_indices, doi_no_indices = create_label_dict(CORPUS_PATH)
    predictions = constructlist_label_predict(RES_FILE_PATH, PREDICT_COL_NAME, csv_sep)

    # Filtre les dict_id2label pour DOI yes/no
    dict_id2label_doi_yes = {label: [idx for idx in indices if idx in doi_yes_indices] for label, indices in dict_id2label.items()}
    dict_id2label_doi_no = {label: [idx for idx in indices if idx in doi_no_indices] for label, indices in dict_id2label.items()}

    # Calcule les prédictions pour chaque cas
    l_pred_all, l_res_all = mapping(dict_id2label, predictions, prediction_mapping, add_to_reverse=labels_add_to_reverse)
    l_pred_doi, l_res_doi = mapping(dict_id2label_doi_yes, predictions, prediction_mapping)
    l_pred_no_doi, l_res_no_doi = mapping(dict_id2label_doi_no, predictions, prediction_mapping)

    # Affiche les 3 rapports
    disp_reports(l_pred_all, l_res_all, "TOUTES LES RÉFÉRENCES")
    disp_reports(l_pred_doi, l_res_doi, "AVEC DOI UNIQUEMENT")
    disp_reports(l_pred_no_doi, l_res_no_doi, "SANS DOI UNIQUEMENT")

if __name__ == "__main__":
    main()