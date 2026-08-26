# *idRorDetect -  Association d’un identifiant ROR à une adresse d’affiliation*

Ce web service renvoie pour une affiliation donnée son ROR associé et d'autres informations complémentaires. Plus d'information sont disponible sur la fiche [Istex TDM](https://services.istex.fr/associer-un-identifiant-ror-a-une-adresse-daffiliation/) associée.

## Données
Le corpus a été constitué à partir des données d’OpenAlex, en utilisant la requête "climate change". OpenAlex associe à de nombreuses affiliations un ou plusieurs identifiants ROR pour les organismes concernés.

Il comprend 532 affiliations, après un pré-traitement excluant :
- les affiliations dont la ville ne correspond pas à celle du ROR proposé par OpenAlex ;
- les affiliations pour lesquelles plusieurs ROR sont proposés.

Le corpus sera prochainement disponible sur Ortolang.

## Résultats
Le web service possède une préicsion de 95.42%, un rappel de 89.80% et une f-mesure de 92.53%.
(Voir fiche concernant la f-mesure)

