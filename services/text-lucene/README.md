# textToLuceneQuery - Génération de requête syntaxe Lucene

Ce corpus de test est complétement expérimental : il sert surtout à comparer la validité des requêtes générés par différents modèles / prompt / etc .
Les résultats peuvent être rejoué à partir du corpus donné dans la partie **Données** ci-dessous, en utilisant le script `eval_model.py` comme ceci (possible de régler `VERBOSE` à True pour plus d'infos) :

```sh
python eval_model.py < corpus.jsonl
```

## Données

Le corpus a été généré par LLM et vérifié à la mano. Il est constitué de 110 requêtes distinctes, en language naturelle. Différentes languages sont testées (Anglais, Français, Italien, Espagnol, Allemand)
Le corpus sera prochainement disponible sur Ortolang.

## Création d'une métrique personnalisée

Nous comptons le nombre d'erreur `nbErr`. Les erreurs et oublis n'impactant pas la qualité de la requête augmentent `nbErr` de 1. Les résultats correctes mais non prévu augmentent `nbErr` de 0.5. Nous attribuons ensuite un score `s` de manière discrète en fonction de `nbErr` :

- `s=1` si `nbErr=0`
- `s=0.9` si `nbErr<1`
- `s=0.7` si `nbErr<2`
- `s=0.4` si `nbErr=2`
- `s=0.1` sinon
- Si la requête est non valide, `s=0`, peu importe la valeur de `nbErr`

## Résultats

Étant donné que la métrique est conçue uniquement pour évaluer le web service, toute comparaison hors de ce cadre n'a aucun sens. Pour deux modèles ou prompt distincts, cette métrique permet de dire si on s'est amélioré ou pas, mais pas de quantifié réellement la qualité des résultats.

Le graphique `barplot.png` donne une répartition des résultats sur ce corpus. Le score moyen obtenu est de 0.94