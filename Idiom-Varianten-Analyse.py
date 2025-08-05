import os
import re
from collections import Counter, defaultdict

# Pfad zu den Ordner mit den .txt-Dateien 
folder_path = r"C:\Users\melis\OneDrive\Dokumente\Uni final\Bachelorarbeit\Experiment\Finale Idiomklammerungen"

# Zähler für geklammerte Bestandteile
bestandteile_counter = Counter()
verbformen = defaultdict(set)
trennbarkeit = []

# Hilfsfunktion für geklammerte Bestandteile extrahieren
def extract_klammern(text):
    return re.findall(r"\[([^\[\]]+)\]", text)

# Trennbarkeit prüfen
def check_trennbarkeit(bestandteile, satz):
    joined = ' '.join(bestandteile).lower()
    clean = satz.lower().replace('[', '').replace(']', '')
    
    if joined in clean:
        return "zusammen"
    elif all(b in clean for b in bestandteile):
        return "getrennt"
    else:
        return "umgestellt"

# Alle Dateien im Ordner analysieren
for file in os.listdir(folder_path):
    if not file.endswith(".txt"):
        continue

    idiom = file.replace(".txt", "")
    with open(os.path.join(folder_path, file), encoding="utf-8") as f:
        content = f.read().strip()

    idiomatische_sätze = content.split("\n\n")[0].split("\n")
    getrennt = zusammen = umgestellt = 0
    bestandteile_gesamt = []

    for satz in idiomatische_sätze:
        satz = satz.strip()
        bestandteile = extract_klammern(satz)
        bestandteile_gesamt.extend(bestandteile)

        # Trennbarkeit prüfen
        trennart = check_trennbarkeit(bestandteile, satz)
        if trennart == "getrennt":
            getrennt += 1
        elif trennart == "zusammen":
            zusammen += 1
        else:
            umgestellt += 1

        # Verbformen sammeln (Flexionen wie ging, geht, werfen, warfen)
        for wort in bestandteile:
            if re.search(r"\b(gegangen|gehen|ging|gingen|geht|warfen|werfen|geworfen|stand|steht|standen|liegen|zieht|zog|gezogen|...)$", wort):
                verbformen[idiom].add(wort.lower())

    # Bestandteile zählen
    bestandteile_counter.update(bestandteile_gesamt)

    # Trennbarkeitsstatistik speichern
    trennbarkeit.append({
        "Idiom": idiom,
        "Idiomsätze": len(idiomatische_sätze),
        "Getrennt": getrennt,
        "Zusammenhängend": zusammen,
        "Umgekehrte Reihenfolge": umgestellt
    })

# Top 20 Bestandteile
print("\nTop 20 häufigste idiomatische Bestandteile:")
for bestandteil, freq in bestandteile_counter.most_common(20):
    print(f"{bestandteil:<15} {freq}")

# Verbformen pro Idiom
print("\nBeispielhafte Verbvariationen je Idiom:")
for idiom, verben in verbformen.items():
    if verben:
        print(f"{idiom:<30} {', '.join(sorted(verben))}")

# Tabelle zur Trennbarkeit
print("\nTrennbarkeitsanalyse:")
print(f"{'Idiom':<30} {'Idiomsätze':<12} {'Getrennt':<10} {'Zusammen':<12} {'Umgestellt':<12}")
for row in trennbarkeit:
    print(f"{row['Idiom']:<30} {row['Idiomsätze']:<12} {row['Getrennt']:<10} {row['Zusammenhängend']:<12} {row['Umgekehrte Reihenfolge']:<12}")