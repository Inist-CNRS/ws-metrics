Ce web service détecte des entités chimiques dans des textes en anglais.
# *chemTag - Extraction d’entités nommées de chimie*

Ce web service détecte des entités nommées de chimie sur des textes en anglais. Plus d'informations en suivant ce lien https://services.istex.fr/detection-dentites-nommees-en-chimie/

## Données
Le corpus BC4CHEMD (issu du défi BioCreative IV CHEMDNER, Krallinger et al., 2015), utilisé pour évaluer le web service chemTag, est accessible sur [ORTOLANG](https://www.ortolang.fr/workspaces/dataset-chemical-extract). L’évaluation s’appuie sur un échantillon de 5 000 phrases du fichier BC4CHEMD/test.conll.

## Résultats
Nous obtenons les résultats suivants :
Précision = 0.9164 
Rappel = 0.9195 
F1-Score = 0.9180

## Script d'évaluation
Le script d'évaluation utilisé est accessible [ici](https://github.com/Inist-CNRS/ws-metrics/tree/main/services/chemTag).