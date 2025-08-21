import os
import re
from collections import defaultdict

# Verzeichnis mit den Textdateien
directory = r"C:\Users\melis\OneDrive\Dokumente\Uni final\Bachelorarbeit\Experiment\Finale Idiomklammerungen"

# Idiom, bei den eine einzelne Klammerung erlaubt ist
single_bracket_ok = {"Kurztreten"}

# Hilfsfunktion zum Zählen der öffnenden Klammern
def count_brackets(sentence):
    return sentence.count("[")

# Ergebnisse zwischenspeichern
idiom_stats = defaultdict(lambda: {"total": 0, "problematic": 0})

# Dateien durchgehen
for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        idiom_name = filename.replace(".txt", "")
        with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]
        
        for sentence in lines:
            bracket_count = count_brackets(sentence)
            idiom_stats[idiom_name]["total"] += 1
            if bracket_count == 0 or (bracket_count == 1 and idiom_name not in single_bracket_ok):
                idiom_stats[idiom_name]["problematic"] += 1

# Ergebnisse vorbereiten und sortieren
result_list = []
for idiom, stats in idiom_stats.items():
    total = stats["total"]
    prob = stats["problematic"]
    percent = round(prob / total * 100, 2) if total > 0 else 0
    result_list.append((idiom, prob, total, percent))

# Nach Prozentwert absteigend sortieren
result_list.sort(key=lambda x: x[3], reverse=True)

# Ausgabe formatieren
print(f"{'Idiom':<30} {'Problematisch':>14} {'Gesamt':>10} {'Anteil (%)':>12}")
print("-" * 70)
for idiom, prob, total, percent in result_list:
    print(f"{idiom:<30} {prob:>14} {total:>10} {percent:>12.2f}")
