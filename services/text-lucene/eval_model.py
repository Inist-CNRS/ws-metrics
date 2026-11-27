#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


OUTPUT_DIR = "./graph/"
TEST_LOCAL = False  # Ne pas toucher sauf pour tester en local
VERBOSE = False


def is_string_in_llm_response(string, llm_response):
    string = string.lower().replace("\"", "").replace("\\", "").replace("(", "").replace(")", "").replace(" ", "")
    llm_response = llm_response.lower().replace("\"", "").replace("\\", "").replace("(", "").replace(")", "").replace(" ", "")
    
    if string in llm_response:
        return True
    
    return False


def get_language_coherence(query):
    """
    retourne 2 si langues pertinentes et cohérentes
    1 si langue cohérente
    0 sinon
    """
    language_corresp = {
        "anglais": "eng",
        "français": "fre",
        "espagnol": "spa",
        "allemand": "ger",
        "italien": "ita"
    }
    if query["language_asked"] == []:
        if is_string_in_llm_response("language.raw:", query["value"]):
            if is_string_in_llm_response(language_corresp[query["query_language"]], query["value"]):
                return 1
            else:
                return 0
        else: 
            return 2
    
    else:
        if not is_string_in_llm_response("language.raw:", query["value"]):
            return 0
        
        return 2


def get_date_coherence(query):
    """
    retourne 1 si dates cohérentes
    0 sinon
    """
    date_min = query["date_min"]
    if not date_min:
        date_min = ""
    date_max = query["date_max"]
    if not date_max:
        date_max = ""

    if not date_min and not date_max:
        if is_string_in_llm_response("publicationDate:[", query["value"]):
            return 0
        else:
            return 1
        
    else:
        if date_min and date_max:
            if is_string_in_llm_response("publicationDate:[", query["value"]) and (is_string_in_llm_response(str(date_min), query["value"]) or is_string_in_llm_response(str(date_min-1), query["value"]) or is_string_in_llm_response(str(date_min+1), query["value"])) and (is_string_in_llm_response(str(date_max), query["value"]) or is_string_in_llm_response(str(date_max-1), query["value"]) or is_string_in_llm_response(str(date_max+1), query["value"])):
                return 1
            else:
                return 0
        if date_min:
            if is_string_in_llm_response("publicationDate:[", query["value"]) and (is_string_in_llm_response(str(date_min), query["value"]) or is_string_in_llm_response(str(date_min-1), query["value"]) or is_string_in_llm_response(str(date_min+1), query["value"])):
                return 1
            else:
                return 0
        else:
            if is_string_in_llm_response("publicationDate:[", query["value"]) and (is_string_in_llm_response(str(date_min), query["value"]) or is_string_in_llm_response(str(date_min-1), query["value"]) or is_string_in_llm_response(str(date_min+1), query["value"])):
                return 1
            else:
                return 0

def get_isarticle_coherence(query):
    """
    retourne 2 si pas d'erreur sur le type de doc
    1 si ajouté
    0 si supprimé / erreur
    """
    if query["only_research_doc"]:
        if is_string_in_llm_response('genre.raw:"research-article"', query["value"]):
            return 2
        else:
            return 0
    else:
        if is_string_in_llm_response('genre.raw:"research-article"', query["value"]):
            return 1
        else:
            return 2


def get_specifickw_coherence(query):
    """
    retourne 2 si ok
    1 cohérent mais champ manquant
    0 si erreur
    """
    if query["use_specific_keywords"]:
        try:
            keywords = query["value"].split("title:(")[1].split(")")[0].replace("  "," ")
            keywords = keywords.split(" ")
            for keyword in keywords:
                if not is_string_in_llm_response(keyword, query["query_saved"]):
                    return 0
            if is_string_in_llm_response("title:", query["value"]) and is_string_in_llm_response("abstract:", query["value"]) and is_string_in_llm_response("subject.value:", query["value"]):
                return 2
            else:
                return 1
        
        except Exception:
            return 0
    else:
        return 2


def get_authors_coherence(query):
    """
    retourne 1 cohérent si ok
    0 si erreur
    """
    if len(query["authors_demanded"]) == 0:
        if is_string_in_llm_response("author.name", query["value"]):
            return 0
        return 1
    else:
        if not is_string_in_llm_response("author.name", query["value"]):
            return 0
        for author in query["authors_demanded"]:
            if not is_string_in_llm_response(author, query["value"]):
                return 0
        return 1


def evaluate(query_to_eval):
    nb_errors = 0
    
    if len(query_to_eval["value"]) < 10:
        return 0

    language_coherence = get_language_coherence(query_to_eval)

    date_coherence = get_date_coherence(query_to_eval)

    isarticle_coherence = get_isarticle_coherence(query_to_eval)

    specifickw_coherence = get_specifickw_coherence(query_to_eval)

    authors_coherence = get_authors_coherence(query_to_eval)

    if language_coherence == 0:
        nb_errors += 1
        sys.stderr.write("Language coherence -1 !\n")
    if language_coherence == 1:
        nb_errors += 0.5
        sys.stderr.write("Language coherence -0.5 !\n")
    if date_coherence == 0:
        nb_errors += 1
        sys.stderr.write("date coherence -1 !\n")
    if isarticle_coherence == 0:
        nb_errors += 1
        sys.stderr.write("isarticle coherence -1 !\n")
    if isarticle_coherence == 1:
        nb_errors += 0.5
        sys.stderr.write("isarticle coherence -0.5 !\n")
    if specifickw_coherence == 0:
        nb_errors += 1
        sys.stderr.write("specific kw coherence -1 !\n")
    if specifickw_coherence == 1:
        nb_errors += 0.5
        sys.stderr.write("specific kw coherence -0.5 !\n")
    if authors_coherence == 0:
        nb_errors += 1
        sys.stderr.write("specific authors coherence -1 !\n")

    if nb_errors == 0:
        return 1
    if nb_errors < 1:
        return 0.9
    if nb_errors < 2:
        return 0.7
    if nb_errors == 2:
        return 0.4
    
    return 0.1


def call_txtlucene_ws(data):
    
    url = "https://text-lucene.services.istex.fr/v1/istex-search"
    if TEST_LOCAL:
        url = "http://localhost:31976/v1/istex-search"
        
    try:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        data = response.json()

        return data[0]
    except Exception:
        return []



def create_charts(data):
    possible_values = [1, 0.9, 0.7, 0.4, 0.1, 0]

    # Création du dossier de sortie
    output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    # 1.Histogramme
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=len(possible_values), edgecolor='black', rwidth=0.8)
    plt.title("Histogramme des valeurs")
    plt.xlabel("Valeurs")
    plt.ylabel("Fréquence")
    plt.xticks(possible_values)
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(f"{output_dir}/histogramme.png", dpi=200, bbox_inches='tight')
    plt.close()

    # 2.Camembert
    plt.figure(figsize=(10, 6))
    counts = [data.count(val) for val in possible_values]
    plt.pie(counts, labels=possible_values, autopct='%1.1f%%', startangle=140)
    plt.title("Répartition des valeurs (Camembert)")
    plt.savefig(f"{output_dir}/camembert.png", dpi=200, bbox_inches='tight')
    plt.close()

    # 3.Boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=data, color='lightblue')
    plt.title("Boxplot des valeurs")
    plt.xlabel("Valeurs")
    plt.savefig(f"{output_dir}/boxplot.png", dpi=200, bbox_inches='tight')
    plt.close()

    # 4.Barplot
    plt.figure(figsize=(10, 6))
    sns.countplot(x=data, order=sorted(possible_values, reverse=True), palette='viridis')
    plt.title("Fréquence des valeurs (Barplot)")
    plt.xlabel("Valeurs")
    plt.ylabel("Fréquence")
    plt.savefig(f"{output_dir}/barplot.png", dpi=200, bbox_inches='tight')
    plt.close()

    # 5.Heatmap (adapté pour une seule série)
    plt.figure(figsize=(10, 6))
    data_matrix = np.array(data).reshape(1, -1)
    sns.heatmap(data_matrix, annot=True, cmap='YlGnBu', xticklabels=False, yticklabels=False)
    plt.title("Heatmap des valeurs")
    plt.savefig(f"{output_dir}/heatmap.png", dpi=200, bbox_inches='tight')
    plt.close()

    print(f"Toutes les visualisations ont été enregistrées dans {output_dir}.", sys.stderr)

    with open(os.path.join(output_dir, "mean.txt"), "w") as f:
        f.write("data_saved = ")
        f.write(str(data))
        f.write("\n\n")
        f.write(f"mean : {np.mean(data)}")
        

def main():
    scores = []
    for line in sys.stdin:
        try:
            query_to_eval = json.loads(line)
            query_to_eval["query_saved"] = query_to_eval["value"]
            
            query_to_eval = call_txtlucene_ws([query_to_eval])
            #La sorite est un jsonl {"value": ...}, s'utilise comme ça pour la suite

        except Exception as e:
            print(str(e), sys.stderr)


        if VERBOSE:
            sys.stdout.write("\n---------------------------------------\n")
            sys.stdout.write(str(query_to_eval))
            sys.stdout.write("\n\n")
            sys.stdout.write(str(query_to_eval["query_saved"]))
            sys.stdout.write("\n")

        scores.append(evaluate(query_to_eval))

    sys.stdout.write("\n---------------------\nScore moyen :" + str(np.mean(scores)) + "\n---------------------\n")
    create_charts(scores)



if __name__ == "__main__":
    main()
