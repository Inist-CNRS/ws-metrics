# *idRorDetect -  Association d’un identifiant ROR à une adresse d’affiliation*

Ce web service renvoie pour une affiliation donnée son ROR associé et d'autres informations complémentaires.

## Données
Le corpus a été constitué à partir des données d’OpenAlex, en utilisant la requête "climate change". OpenAlex associe à de nombreuses affiliations un ou plusieurs identifiants ROR pour les organismes concernés.

Il comprend 532 affiliations, après un pré-traitement excluant :
- les affiliations dont la ville ne correspond pas à celle du ROR proposé par OpenAlex ;
- les affiliations pour lesquelles plusieurs ROR sont proposés.


## Résultats
Le web service possède une préicsion de 95.21%, un rappel de 89.78% et une f-mesure de 92.43%.
(Voir fiche concernant la f-mesure)

