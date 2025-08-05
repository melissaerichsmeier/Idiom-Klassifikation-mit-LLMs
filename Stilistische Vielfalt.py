import os
import re
from collections import Counter

# Verzeichnis mit den Textdateien
input_dir = r"C:\Users\melis\OneDrive\Dokumente\Uni final\Bachelorarbeit\Experiment\Finale Idiomklammerungen"

# Hilfsfunktionen
def classify_sentence_start(sentence):
    sentence = sentence.strip()
    if re.match(r"(?i)^(der|die|das)\s+[A-ZÄÖÜ]", sentence):
        return "Der/Die/Das + Substantiv"
    elif re.match(r"(?i)^(er|sie)\s", sentence):
        return "Er/Sie"
    elif re.match(r"(?i)^ich\s", sentence):
        return "Ich"
    elif re.match(r"(?i)^es\s", sentence):
        return "Es"
    elif re.match(r"(?i)^plötzlich\b", sentence):
        return "Plötzlich"
    elif re.match(r"(?i)^(wenn|während|obwohl|als|falls)\b", sentence):
        return "Nebensatz"
    else:
        return "Sonstiger Anfang"

def detect_question_or_exclamation(sentence):
    if sentence.strip().endswith("?"):
        return "Frage"
    elif sentence.strip().endswith("!"):
        return "Ausruf"
    return "Normal"

def detect_tempus(sentence):
    präsens = re.search(r"\b(gehe|geht|sehen|steht|liegt|wirft|kommt|nimmt|ist|bleibt|zieht)\b", sentence)
    präteritum = re.search(r"\b(ging|sah|stand|lag|warf|kam|nahm|war|blieb|zog)\b", sentence)
    konjunktiv = re.search(r"\b(hätte|wäre|würde|könnte|sollte|möge|wollte|dürfte)\b", sentence)
    if konjunktiv:
        return "Konjunktiv"
    elif präteritum:
        return "Präteritum"
    elif präsens:
        return "Präsens"
    return "Unbestimmt"

# Zähler
start_counter = Counter()
sentence_type_counter = Counter()
tempus_counter = Counter()

# Verarbeitung aller Dateien
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as f:
            lines = f.readlines()
            idiom_sentences = [line.strip() for line in lines if line.strip()]
            for sentence in idiom_sentences:
                # Satzanfang
                start_type = classify_sentence_start(sentence)
                start_counter[start_type] += 1

                # Satzart
                sentence_type = detect_question_or_exclamation(sentence)
                sentence_type_counter[sentence_type] += 1

                # Tempus/Modus
                tempus = detect_tempus(sentence)
                tempus_counter[tempus] += 1

# Ergebnisse anzeigen
print("\n1. Satzstruktur-Muster")
for key, val in start_counter.most_common():
    print(f"{key:<30}{val}")

print("\n2. Frage- und Ausrufesätze")
print(f"{'Fragen':<20}{sentence_type_counter.get('Frage', 0)}")
print(f"{'Ausrufe':<20}{sentence_type_counter.get('Ausruf', 0)}")

print("\n3. Tempus- und Modus-Analyse")
for key, val in tempus_counter.items():
    print(f"{key:<20}{val}")