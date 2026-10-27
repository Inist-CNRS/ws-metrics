#!/usr/bin/env python3

import json
import sklearn.metrics as skl
import matplotlib.pyplot as plt
import numpy as np
import sys
from sklearn.metrics import classification_report
import pandas as pd
import requests

def call_bibcheck(data):
    try:
        url = f"http://localhost:31976/v1/validate"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        data = response.json()
        return data[0]["value"]
    except Exception as e:
        sys.stderr.write(str(e))
        return []


results = []
predictions = []
results_doi = []
predictions_doi = []

for line in sys.stdin:
    data = json.loads(line)
    ref_biblio = data["id"]
    res = call_bibcheck([{"value": ref_biblio}])
    prediction = res["status"]
    label = data["expected_result"]
    
    if prediction == "feet_of_clay":
        prediction = "found"
        print("Feet of clay detected !: ", data["id"], "\n")


    # # seek errors
    if prediction == "error_service":
        # continue
        print("Erreur service: ", data["id"], "\n")
        
    if prediction != "retracted" and label == "retracted":
        print("Retracté non trouvé: ", data["id"])

    if prediction == "found" and label == "to_be_verified" and data["has_doi"] == "yes":
        sys.stderr.write(json.dumps(res))
        sys.stderr.write("\n")


    if data["has_doi"] == "yes":
        predictions_doi.append(prediction)
        results_doi.append(label)
    else:
        predictions.append(prediction)
        results.append(label)
    
    # print(prediction)
    # print(label)
    # print("-------------")


labels = ["found", "to_be_verified", "retracted", "not_found"]

# create matrix of references that do NOT contains doi
results_no_doi = [r for r, p in zip(results, predictions)]
predictions_no_doi = [p for r, p in zip(results, predictions)]
print(len(predictions_no_doi))
print(len(results_no_doi))

cm_no_doi = skl.confusion_matrix(results_no_doi, predictions_no_doi, labels=labels)
with np.errstate(divide='ignore', invalid='ignore'):
    cm_no_doi_normalized = cm_no_doi.astype('float') / cm_no_doi.sum(axis=1, keepdims=True)
    cm_no_doi_normalized = np.nan_to_num(cm_no_doi_normalized)  # replace NaN by 0

disp_no_doi = skl.ConfusionMatrixDisplay(confusion_matrix=cm_no_doi_normalized, display_labels=labels)
disp_no_doi.plot(cmap='Blues', values_format=".2f")
plt.gcf().subplots_adjust(left=0.21) # without it, we cant see ylabel (to low marge)
plt.title("Confusion Matrix - references without DOI")
plt.xlabel("Predicted label", fontweight='bold')
plt.ylabel("True label", fontweight='bold')
plt.savefig("confusion_matrix.png")
plt.close()



# create matrix of references that contains doui
results_doi = [r for r, p in zip(results_doi, predictions_doi)]
predictions_doi = [p for r, p in zip(results_doi, predictions_doi)]
print(len(predictions_doi))
print(len(results_doi))

cm_doi = skl.confusion_matrix(results_doi, predictions_doi, labels=labels)
with np.errstate(divide='ignore', invalid='ignore'):
    cm_doi_normalized = cm_doi.astype('float') / cm_doi.sum(axis=1, keepdims=True)
    cm_doi_normalized = np.nan_to_num(cm_doi_normalized)

disp_doi = skl.ConfusionMatrixDisplay(confusion_matrix=cm_doi_normalized, display_labels=labels)
disp_doi.plot(cmap='Blues', values_format=".2f")
plt.gcf().subplots_adjust(left=0.21) # without it, we cant see ylabel (to low marge)
plt.title("Confusion Matrix - references that contain DOI")
plt.xlabel("Predicted label", fontweight='bold')
plt.ylabel("True label", fontweight='bold')
plt.savefig("confusion_matrix_doi.png")
plt.close()



results_combined = results_doi + results
predictions_combined = predictions_doi + predictions
print(len(predictions_combined))
print(len(results_combined))

# labels that's will be shown for doi + no doi in last matrix

cm_combined = skl.confusion_matrix(results_combined, predictions_combined, labels=labels)
with np.errstate(divide='ignore', invalid='ignore'):
    cm_combined_normalized = cm_combined.astype('float') / cm_combined.sum(axis=1, keepdims=True)
    cm_combined_normalized = np.nan_to_num(cm_combined_normalized)

disp_combined = skl.ConfusionMatrixDisplay(confusion_matrix=cm_combined_normalized, display_labels=labels)
disp_combined.plot(cmap='Blues', values_format=".2f")
plt.gcf().subplots_adjust(left=0.21) # without it, we cant see ylabel (to low marge)
plt.title("Confusion Matrix - all references")
plt.xlabel("Predicted label", fontweight='bold')
plt.ylabel("True label", fontweight='bold')
plt.savefig("confusion_matrix_all.png")
plt.close()


# Precision, rappel et f-mesure
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

print_metrics_table(
    results_no_doi,
    predictions_no_doi,
    labels,
    title="Metrics — references without DOI"
)
print_metrics_table(
    results_doi,
    predictions_doi,
    labels,
    title="Metrics — references with DOI"
)
print_metrics_table(
    results_combined,
    predictions_combined,
    labels,
    title="Metrics — all references"
)