# Utilisation du script evaluate_tools.py

## Données d'entrées

Elles sont toutes dans le dossier `evaluation-datas`. Les scripts utilisés pour obtenir les données au format .pdf et .txt sont également donnés dans ce dossier.

## Données de sorties

Pour chaque logiciel `abc`, le fichier résultat correspondant se trouve dans le dossier correspondant `results/{abc}`. Chaque dossier contient également un fichier `res-{abc}.txt` des résultats obtenus.

## scripts d'évaluation

Pour bibCheck et Hallcinator, les scripts utilisés pour obtenir les fichiers résultats sont dans le dossier `evaluation-scripts`. Ils donnent des rapports de classifications et, pour bibcheck, des matrices de confusions. Les autres logiciels ont été obtenus via une interface web en septembre-octobre 2026.

## Script d'évaluation

Pour rejouer les résultats, il est possible de décommenter les lignes correspondantes au logiciel testés dans le script `evaluate_tools.py`. Une simple exécution du script permet ainsi d'obtenir en sortie standard les résultats.

Exemple : pour obtenir les résultats sur bibcheck pdf il faut décommenter les lignes suivantes :

```python3
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
```

Pour obtenir

```python3
    # bibcheck-pdf
    print("Tool : bibcheck-pdf\n\n")
    CORPUS_PATH = "evaluation-datas/corpus_bibcheck_v7.jsonl"
    RES_FILE_PATH = "results/bibcheck-pdf/res_bibcheck-pdf_reordered.jsonl"
    PREDICT_COL_NAME = "value/status"

    prediction_mapping = {
        "found": "found",
        "to_be_verified": "to_be_verified",
        "retracted": "retracted"
    }
```

Conseil : sur certains éditeurs, le racourci clavier `ctrl` maintenu puis `k` puis `u` décommente plusieurs lignes.
Réciproquement, `ctrl` maintenu puis `k` puis `c` commente des lignes.