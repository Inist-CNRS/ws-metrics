import json
import csv

with open("corpus_bibcheck_v7.csv", "w", newline='', encoding='utf-8') as f_out:
    writer = csv.writer(f_out)
    writer.writerow(["line_number", "first_author" ,"expected_result", "has_doi"])

    with open("./corpus_bibcheck_v7.jsonl", "r", encoding='utf-8') as f:
        for line_number, line in enumerate(f, start=1):
            data = json.loads(line.strip())
            writer.writerow([line_number, data["id"][:10]+"...",  data["expected_result"], data["has_doi"]])