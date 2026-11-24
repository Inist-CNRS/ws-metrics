# *countryDetect - Détection du pays et de la ville d’une affiliation*

Ce web service renvoie pour une affiliation donnée le pays, son code ISO et la ville. Plus d'information sont disponible sur la fiche [Istex TDM](https://services.istex.fr/detection-du-pays-dune-affiliation//) associée.

## Données
Le corpus de 373 affiliations uniques a été constitué à partir de deux corpus distincts :
- 273 affiliations du corpus d’Ortolang (HAL, Crossref et PubMed)
- 100 affiliations du corpus "Affiliations des participants à l'ISGC" (projet de recherche NETCONF)

Le corpus sera prochainement disponible sur Ortolang.

## Résultats
Nous obtenons les résultats suivants :
- Pour les villes : 90.5% de précision et 95.6% de rappel pour une f-mesure de 93.0%
- Pour les pays :  99.7% de précision et 100% de rappel pour une f-mesure de 99.9%
- pour les codes pays : 99.5% de précision et 98.1% de rappel pour une f-mesure de 98.8%
(Voir fiche concernant la f-mesure)
