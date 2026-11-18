from requests_ratelimiter import LimiterSession
from datetime import date
import json
import os
import time
from requests.exceptions import ChunkedEncodingError, ConnectionError, Timeout

session = LimiterSession(per_second=5)

entities_to_keep = ["diseases"]


to_keep_in_corpus = []
for elt in entities_to_keep:
    to_keep_in_corpus.append(f"B-{elt}")
    to_keep_in_corpus.append(f"I-{elt}")

def keep_entity(entity,to_keep_in_corpus=to_keep_in_corpus):
    if entity in to_keep_in_corpus:
        return True
    return False


def read_corpus(file_path):
    with open(file_path, 'r') as f:
        current_entity = []
        annotations = []
        current_label = None
        words = []
        sentences = []
        all_entities = []
        for line in f:
            line = line.strip()
            if not line:
                if len(words)>0:
                    sentences.append(" ".join(words).replace(" .","."))
                    words = []
                if current_entity:
                    annotations.append((' '.join(current_entity), current_label))
                    current_entity = []
                    current_label = None
                all_entities.append(annotations)
                annotations = []

            else:
                #word, label = line.split() remplacé par *ligne en-dessous*
                word, label = line.split()[0], line.split()[-1]
                words.append(word)
                if label != 'O':
                    if not keep_entity(label):
                        continue
                    if not current_entity:
                        current_entity = [word]
                        current_label = label.split('-')[1]
                    else:
                        if label.split("-")[1] == current_label:
                            current_entity.append(word)
                        else:
                            annotations.append((' '.join(current_entity), current_label))
                            current_entity = [word]
                            current_label = label.split('-')[1]
                else:
                    if current_entity:
                        annotations.append((' '.join(current_entity), current_label))
                    current_entity = []
                    current_label = None
        if current_entity:
            annotations.append((' '.join(current_entity), current_label))
        if len(words)>0:
            sentences.append(" ".join(words).replace(" .","."))
            words = []
        all_entities.append(annotations)
    return all_entities, sentences

URL_SERVICE = "https://diseases-ner.services.istex.fr/v1/diseases/tagger"
TAILLE_LOT = 50   # si ça coupe encore : 20 ; si ça passe bien : 100

def post_avec_retry(data, essais=3):
    for n in range(essais):
        try:
            r = session.post(URL_SERVICE, data=data, timeout=600)
            r.raise_for_status()
            return r
        except (ChunkedEncodingError, ConnectionError, Timeout):
            if n == essais - 1:
                raise
            print(f"Connexion coupée, nouvelle tentative ({n + 2}/{essais})...")
            time.sleep(5 * (n + 1))


### Comment changer brique là pour utiliser mon modèle au lieu de WS
def extract_model_entities(sentences, number_test, test = False):
    id=0
    to_send = []
    for sentence in sentences:
        to_send.append({"id":id,"value":sentence})
        id+=1
        if test and id == number_test:
            break
    with open("disease-entry.json", "w") as f_out:
        f_out.write(json.dumps(to_send))
        
        
# Envoi par lots, dans l'ordre, pour garder l'alignement avec les annotations
    content = []
    for debut in range(0, len(to_send), TAILLE_LOT):
        lot = to_send[debut:debut + TAILLE_LOT]
        response = post_avec_retry(json.dumps(lot))
        content.extend(response.json())
        print(f"{min(debut + TAILLE_LOT, len(to_send))}/{len(to_send)} phrases traitées")


    to_check = entities_to_keep
    output = []
    for sentence in content:
        sentence = sentence["value"]
        entities = []
        for entity in to_check:
            if len(sentence[entity]) == 0:
                continue
            else :
                for res in sentence[entity]:
                    entities.append((res,entity))
        output.append(entities)
    with open("disease-tag-output.json", "w") as f_out:
        f_out.write(json.dumps(output))

    return output

def evaluate_ner_model(annotations, predictions):
    truely_predicted = 0
    total_predicted = 0
    total_true = 0
    
    for true, pred in zip(annotations, predictions):
        true_set = set(true)
        pred_set = set(pred)
        
        total_predicted += len(pred_set)
        total_true += len(true_set)

        for entities in true_set:
        
            if entities in pred_set:
                truely_predicted += 1

    precision = truely_predicted / total_predicted if total_predicted > 0 else 1
    recall = truely_predicted / total_true if total_true > 0 else 1
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return precision, recall, f1_score

def ajouter_resultat(nb_lignes, precision, rappel, f1, fichier="resultats.md"):
    if not os.path.exists(fichier):
        with open(fichier, "w", encoding="utf-8") as f:
            f.write("# Résultats des évaluations diseaseTag\n\n")
            f.write("| Date | Nombre de lignes | Précision | Rappel | F1-score |\n")
            f.write("|------|-----------------:|----------:|-------:|---------:|\n")
    with open(fichier, "a", encoding="utf-8") as f:
        f.write(f"| {date.today().strftime('%d/%m/%Y')} | {nb_lignes} | "
                f"{precision:.4f} | {rappel:.4f} | {f1:.4f} |\n")


# Debut evalutation

annotations_file = 'Europe_PMC_corpus/data/test.conll'
# Si = True, teste uniquement sur le nombre de PHRASES indiqué dans "number_test".
# Si test = False, lance le code sur tout le corpus
test = True
number_test = 5000

if test:
    annotations, sentences = read_corpus(annotations_file)
    predictions = extract_model_entities(sentences,number_test=number_test,test=True)
    annotations = annotations[:number_test]
    precision, recall, f1 = evaluate_ner_model(annotations, predictions)
    print(annotations[:20])
    print(predictions[:20])
    print(f"Précision: {precision:.4f}")
    print(f"Rappel: {recall:.4f}")
    print(f"F1-score: {f1:.4f}")
    print(len(sentences), len(annotations)) # affiche le nombre de phrases du corpus

    ajouter_resultat(number_test, precision, recall, f1)
    exit()

annotations, sentences = read_corpus(annotations_file)
predictions = extract_model_entities(sentences, number_test=0, test=True)
precision, recall, f1 = evaluate_ner_model(annotations, predictions)

print(f"Précision: {precision:.4f}")
print(f"Rappel: {recall:.4f}")
print(f"F1-score: {f1:.4f}")
ajouter_resultat("tout le corpus", precision, recall, f1)