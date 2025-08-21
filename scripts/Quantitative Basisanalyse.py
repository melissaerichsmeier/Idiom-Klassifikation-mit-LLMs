import os
import statistics

def read_sentences(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
    parts = content.split("\n\n")
    idiomatic = [line.strip() for line in parts[0].split("\n") if line.strip()]
    literal = [line.strip() for line in parts[1].split("\n") if line.strip()]
    return idiomatic, literal

def word_count(text):
    return len(text.split())

def analyze_directory(folder_path):
    summary = []
    idiom_shorter = 0
    literal_shorter = 0
    equal_length = 0
    idiom_sentence_lengths = []
    literal_sentence_lengths = []

    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(folder_path, filename)
        idiomatic, literal = read_sentences(filepath)
        
        all_words = sum(word_count(s) for s in idiomatic + literal)
        total_sentences = len(idiomatic) + len(literal)

        idiom_avg = statistics.mean([word_count(s) for s in idiomatic])
        literal_avg = statistics.mean([word_count(s) for s in literal])
        diff = round(abs(idiom_avg - literal_avg), 2)

        if idiom_avg < literal_avg:
            idiom_shorter += 1
        elif idiom_avg > literal_avg:
            literal_shorter += 1
        else:
            equal_length += 1

        idiom_sentence_lengths.append(idiom_avg)
        literal_sentence_lengths.append(literal_avg)

        summary.append({
            "file": filename.replace(".txt", ""),
            "word_count": all_words,
            "idiom_avg": round(idiom_avg, 2),
            "literal_avg": round(literal_avg, 2),
            "diff": diff
        })

    # Gesamtwerte
    all_idiom_avg = round(statistics.mean(idiom_sentence_lengths), 2)
    all_literal_avg = round(statistics.mean(literal_sentence_lengths), 2)

    # Größte Differenz
    max_diff = max(summary, key=lambda x: x["diff"])

    # Ausgabe
    print("1.1 Wortanzahl je Datei:")
    for s in sorted(summary, key=lambda x: x["word_count"], reverse=True):
        print(f'• {s["file"]}: {s["word_count"]} Wörter')
    print("\n1.2 Ø Wörter pro Satz (idiomatisch vs. literal):")
    for s in sorted(summary, key=lambda x: x["idiom_avg"], reverse=True)[:3]:
        print(f'Längste idiomatische Sätze: {s["file"]} – Ø {s["idiom_avg"]}')
    for s in sorted(summary, key=lambda x: x["idiom_avg"])[:3]:
        print(f'Kürzeste idiomatische Sätze: {s["file"]} – Ø {s["idiom_avg"]}')
    for s in sorted(summary, key=lambda x: x["literal_avg"], reverse=True)[:3]:
        print(f'Längste literale Sätze: {s["file"]} – Ø {s["literal_avg"]}')
    for s in sorted(summary, key=lambda x: x["literal_avg"])[:3]:
        print(f'Kürzeste literale Sätze: {s["file"]} – Ø {s["literal_avg"]}')

    print("\n1.3 Durchschnitt über alle Idiome:")
    print(f'• Ø Wörter pro idiomatischem Satz: {all_idiom_avg}')
    print(f'• Ø Wörter pro literalem Satz: {all_literal_avg}')
    print("\nGrößter Unterschied:")
    print(f'- {max_diff["file"]} -> {max_diff["diff"]} Wörter Differenz')
    print("\nVerteilung der durchschnittlichen Satzlängen:")
    print(f'• {idiom_shorter}× idiomatische Sätze kürzer')
    print(f'• {equal_length}× gleich lang')
    print(f'• {literal_shorter}× idiomatische Sätze länger')

folder_path = r"C:\Users\melis\OneDrive\Dokumente\Uni final\Bachelorarbeit\Experiment\Finale Idiomklammerungen"
analyze_directory(folder_path)
