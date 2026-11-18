# *diseaseTag - Extraction d’entités nommées de maladies*

Ce web service détecte des entités nommées de maladies sur des textes en anglais. Plus d'informations en suivant ce lien https://services.istex.fr/detection-dentites-nommees-de-maladies/

## Données
Le corpus BC5CDR-disease (BioCreative V Chemical Disease Relation), utilisé pour évaluer le web service diseaseTag, est accessible sur [ORTOLANG](https://www.ortolang.fr/market/corpora/dataset-disease-extract). L’évaluation s’appuie sur un échantillon de 4 797 phrases, le fichier BC5CDR-disease-IOB_test.conll.

## Résultats
Nous obtenons les résultats suivants :
Précision = 0,82
Rappel = 0,86
F1-score = 0,84

## Script d'évaluation
Le script d'évaluation utilisé est accessible [ici](https://github.com/Inist-CNRS/ws-metrics/tree/main/services/disease-tag).