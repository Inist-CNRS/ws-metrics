import sys
import json

with open("res_cleaned.txt", "r") as f:
    for line in f.readlines():
        id, value = line.split("                     ")
        id = id.strip()
        if "❌" in value:
            value = "❌"
        elif "⚠️" in value:
            value = "⚠️"
        elif "✅" in value:
            value = "✅"
        else:
            sys.stderr.write(f"Ni une X, ni un V ni un ! . Vérifier la sorte {id}")
        output = {"id": id, "res_bibguard": value}
        sys.stdout.write(json.dumps(output))
        sys.stdout.write("\n")