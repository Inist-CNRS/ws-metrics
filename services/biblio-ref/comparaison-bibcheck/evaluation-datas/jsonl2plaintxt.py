#!/usr/bin/env python3
"""
Script simplifié pour convertir un JSONL de références bibliographiques en PDF.

Les références sont déjà formatées dans le champ 'id' du JSONL.
Le PDF généré contient un faux article avec une section References qui reprend
les références telles quelles depuis le champ 'id'.

Usage:
    python jsonl_to_pdf_simple.py input.jsonl output.pdf
"""

import json
import sys    


def create_plaintext(input_jsonl, output_pdf):
    with open(input_jsonl, "r") as f:
        corpus_jsonl = f.readlines()
        with open(output_file, "w") as f_out:
            for i, line in enumerate(corpus_jsonl):
                line = json.loads(line)
                f_out.write(f"[{i+1}] {line["id"].replace("\n", " ").replace("  ", " ")}\n")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python jsonl_to_pdf_simple.py input.jsonl output.pdf")
        print("\nExemple:")
        print("  python jsonl_to_pdf_simple.py references.jsonl article.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    create_plaintext(input_file, output_file)