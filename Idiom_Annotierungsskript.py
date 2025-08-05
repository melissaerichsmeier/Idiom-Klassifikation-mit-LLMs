import spacy
from spacy.matcher import Matcher
import re
from pathlib import Path
import zipfile
from itertools import product
from collections import defaultdict

# lade deutsches Sprachmodell von spaCy
nlp = spacy.load("de_core_news_sm")

# Setzt einen spaCy-Matcher für das Idiom „auf den Zug aufspringen“ auf.
# Diese Konstruktion ist zu flexibel für einfache Regeln, daher wird ein individueller Matcher verwendet.
def setup_aufspringen_matcher(nlp):
    matcher = Matcher(nlp.vocab)
    matcher.add("AUF_ZUG_AUFSPRINGEN", [[
        {"LEMMA": {"in": ["springen", "aufspringen"]}},
        {"LOWER": "auf"},
        {"LOWER": "den", "OP": "?"},
        {"IS_ALPHA": True, "OP": "*"},
        {"TEXT": {"REGEX": r".*zug$"}},
        {"LOWER": "auf", "OP": "?"}
    ]])
    return matcher

# Enthält fest definierte Regeln für bekannte Idiome.
# Jede Regel ist eine Liste von Bestandteilen, wobei das letzte Element jeweils eine Liste möglicher Verbformen ist.
IDIOM_RULES = {
    "am_ball_bleiben": [["am", "ball", ["bleiben", "bleib", "bleibt", "blieb", "blieben", "geblieben"]]],
    "am_boden_liegen": [["am", "boden", ["liegen", "lag", "lagen", "gelegen"]]],
    "am_pranger_stehen": [["an", "dem", "pranger", ["stehen", "steht", "stand", "standen"]]],
    "an_glanz_verlieren": [["an", "glanz", ["verlieren", "verlor", "verliert"]]],
    "an_land_ziehen": [["an", "land", ["ziehen", "zog", "zogen", "gezogen"]]],
    "auf_achse_sein": [["auf", "achse", ["sein", "ist", "bin", "war", "waren"]]],
    "auf_dem_abstellgleis_stehen": [["auf", "dem", "abstellgleis", ["stehen", "steht", "stand"]]],
    "auf_dem_tisch_liegen": [["auf", "dem", "tisch", ["liegen", "liegt", "lag"]]],
    "auf_den_arm_nehmen": [["auf", "den", "arm", ["nehmen", "nimmt", "nahm"]]],
    "auf_den_zug_aufspringen": [["auf", "den", "zug", ["aufspringen", "sprang", "springen", "aufzuspringen", "sprangen"]]],
    "auf_der_ersatzbank_sitzen": [["auf", "der", "ersatzbank", ["sitzen", "sitzt", "saß"]]],
    "auf_der_straße_stehen": [["auf", "der", "straße", ["stehen", "steht", "stand"]]],
    "auf_der_strecke_bleiben": [["auf", "der", "strecke", ["bleiben", "bleibt", "blieb"]]],
    "das_handtuch_werfen": [["das", "handtuch", ["werfen", "wirft", "warf"]]],
    "den_atem_anhalten": [["den", "atem", ["anhalten", "hält", "halte", "hielt", "anhielten"]]],
    "den_bogen_überspannen": [["den", "bogen", ["überspannen", "überspannt", "überspannte", "überspanntem"]]],
    "den_faden_verlieren": [["den", "faden", ["verlieren", "verlor"]]],
    "den_kürzeren_ziehen": [["den", "kürzeren", ["ziehen", "zog", "zieh"]]],
    "die_fäden_ziehen": [["die", "fäden", ["ziehen", "zog"]]],
    "die_koffer_packen": [["die", "koffer", ["packen", "packte", "packten"]]],
    "die_kurve_kriegen": [["die", "kurve", ["kriegen", "kriegte"]]],
    "die_notbremse_ziehen": [["die", "notbremse", ["ziehen", "zog"]]],
    "ein_auge_zudrücken": [["ein", "auge", ["zudrücken", "drückt", "drückte", "zugedrückt"]]],
    "ein_zelt_aufschlagen": [["ein", "zelt", ["aufschlagen", "schlug", "schlugen", "aufgeschlagen"]]],
    "eine_brücke_bauen": [["eine", "brücke", ["bauen", "baut"]]],
    "eine_rechnung_begleichen": [["eine", "rechnung", ["begleichen", "beglich", "beglichen"]]],
    "einen_nerv_treffen": [["einen", "nerv", ["treffen", "traf"]]],
    "einen_zahn_zulegen": [["einen", "zahn", ["zulegen", "legte", "legten"]]],
    "im_blut_haben": [["im", "blut", ["haben", "hat"]]],
    "im_regen_stehen": [["im", "regen", ["stehen", "stand"]]],
    "im_sande_verlaufen": [["im", "sande", ["verlaufen", "verliefen"]]],
    "im_schatten_stehen": [["im", "schatten", ["stehen", "stand"]]],
    "in_den_keller_gehen": [["in", "den", "keller", ["gehen", "ging"]]],
    "in_der_luft_hängen": [["in", "der", "luft", ["hängen", "hing", "hingen"]]],
    "in_eine_sackgasse_geraten": [["in", "eine", "sackgasse", ["geraten", "geriet"]]],
    "in_fahrt_kommen": [["in", "fahrt", ["kommen", "kam"]]],
    "in_schieflage_geraten": [["in", "schieflage", ["geraten", "geriet"]]],
    "ins_rennen_gehen": [["ins", "rennen", ["gehen", "ging"]]],
    "ins_wasser_fallen": [["ins", "wasser", ["fallen", "fiel"]]],
    "kein_auge_zutun": [["kein", "auge", ["zutun", "tat", "taten", "zutut", "zugemacht", "zugedrückt"]]],
     # Spezialfall: „kurztreten“ mit mehreren möglichen Zusammensetzungen und Flexionsformen
    "kurztreten": [
    [["kurztreten", "kürzertreten", "kürzerzutreten"]],
    [["tritt", "trat", "trete"], ["kürzer"]],
    [["kürzer"], ["treten"]],
    [["kürzer"]],
],
    "luft_holen": [["luft", ["holen", "holte"]]],
    "mit_dem_feuer_spielen": [["mit", "dem", "feuer", ["spielen", "spielte"]]],
    "unter_strom_stehen": [["unter", "strom", ["stehen", "steht", "stand"]]],
    "über_bord_gehen": [["über", "bord", ["gehen", "ging"]]],
    "über_bord_werfen": [["über", "bord", ["werfen", "warf"]]],
    "über_die_bühne_gehen": [["über", "die", "bühne", ["gehen", "ging"]]],
    "von_bord_gehen": [["von", "bord", ["gehen", "ging"]]],
    "vor_der_tür_stehen": [["vor", "der", "tür", ["stehen", "stand"]]]
}

# Liest zusätzliche idiomatische Muster aus einer Datei mit Beispielsätzen, z. B. von Hand annotierte Klammerungen.
def parse_beispielsaetze(file_path: Path):
    idiom_patterns = defaultdict(list)
    
    with file_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tokens = re.findall(r'\[(.+?)\]', line.lower())
            if len(tokens) >= 2:
                key = "_".join(tokens)
                pattern = [[token] for token in tokens]  # jede Komponente einzeln als Liste
                idiom_patterns[key].append(pattern)
    return idiom_patterns

# Hilfsfunktion: Extrahiert den Idiom-Schlüssel aus dem Dateinamen
def extract_idiom_key_from_filename(filename: Path) -> str:
    return filename.stem.lower()

# Vergleicht ein spaCy-Dokument mit einem gegebenen Idiommuster und gibt die besten Token-Positionen zurück.
def match_best_idiom_instance(doc, idiom_pattern):
    positions = {}
    # Suche potenzielle Übereinstimmungen pro Pattern-Element
    for i, token in enumerate(doc):
        lower = token.text.lower()
        lemma = token.lemma_.lower()
        for j, part in enumerate(idiom_pattern):
            if isinstance(part, list):
                if lower in part or lemma in part:
                    positions.setdefault(j, []).append(i)
                elif any(re.fullmatch(rf"{p}.*", lower) for p in part):
                    positions.setdefault(j, []).append(i)
            else:
                if lower == part:
                    positions.setdefault(j, []).append(i)

    # Wenn nicht alle Teile erkannt wurden → kein Match
    if len(positions) < len(idiom_pattern):
        return set()

    # Generiere alle Kombinationen und finde die kürzeste Spanne 
    all_combos = product(*[positions[k] for k in range(len(idiom_pattern))])
    best_set = set()
    best_span = float("inf")

    for combo in all_combos:
        if len(set(combo)) < len(combo):
            continue
        span = max(combo) - min(combo)
        if span < best_span:
            best_span = span
            best_set = set(combo)

    return best_set

# Überarbeitet eine Zeile durch Erkennung und Klammerung idiomatischer Bestandteile
def rebracket_line(line: str, idiom_key: str) -> str:
    doc = nlp(re.sub(r"\[|\]", "", line))
    idiom_patterns = IDIOM_RULES.get(idiom_key, [])
    idiom_token_indexes = set()

    # Teste alle Muster für das Idiom
    for pattern in idiom_patterns:
        idiom_token_indexes |= match_best_idiom_instance(doc, pattern)

    # Spezialfall mit zusätzlichem Matcher (z. B. "auf den Zug aufspringen")
    if idiom_key == "auf_den_zug_aufspringen":
        matcher = setup_aufspringen_matcher(nlp)
        matches = matcher(doc)
        for _, start, end in matches:
            span = doc[start:end]
            for token in span:
                if token.lemma_ in ["springen", "aufspringen"] and token.pos_ == "VERB":
                    idiom_token_indexes.add(token.i)
                elif token.text.lower() in ["auf", "den"]:
                    idiom_token_indexes.add(token.i)
                elif re.search(r"zug$", token.text.lower()):
                    idiom_token_indexes.add(token.i)

    # Rückgabe: Neue Zeile mit geklammerten Tokens
    return " ".join(
        [f"[{t.text}]" if i in idiom_token_indexes else t.text for i, t in enumerate(doc)]
    )

# Verarbeitet eine einzelne .txt-Datei: trennt idiomatische & literale Sätze, bearbeitet sie, speichert sie neu
def process_file(file_path: Path, output_dir: Path):
    idiom_key = extract_idiom_key_from_filename(file_path)

    with file_path.open(encoding="utf-8") as f:
        content = f.read().strip()

    # Trenne Literal- und Idiom-Block
    if "\n\n" in content:
        literal_block, idiomatic_block = content.split("\n\n", 1)
    else:
        lines = content.strip().split("\n")
        literal_block = "\n".join(lines[:50])
        idiomatic_block = "\n".join(lines[50:])

    # Bearbeite beide Blöcke separat
    literal_lines = [rebracket_line(l, idiom_key) for l in literal_block.strip().split("\n") if l.strip()]
    idiomatic_lines = [rebracket_line(l, idiom_key) for l in idiomatic_block.strip().split("\n") if l.strip()]

    # Schreibe Ergebnisse in neue Datei
    out_path = output_dir / file_path.name
    with out_path.open("w", encoding="utf-8") as out_f:
        for line in literal_lines:
            out_f.write(line + "\n")
        out_f.write("\n")
        for line in idiomatic_lines:
            out_f.write(line + "\n")

# Hauptfunktion: wendet Regeln an, verarbeitet alle Dateien und erstellt ein ZIP-Archiv mit Ergebnissen
def main(input_dir: Path, output_dir: Path, zip_output: Path, beispiel_path: Path = None):
    # Falls zusätzliche Muster vorhanden sind, erweitere IDIOM_RULES
    if beispiel_path and beispiel_path.exists():
        extra_patterns = parse_beispielsaetze(beispiel_path)
        for key, patterns in extra_patterns.items():
            if key in IDIOM_RULES:
                IDIOM_RULES[key].extend(patterns)
            else:
                IDIOM_RULES[key] = patterns

    # Verarbeite alle Dateien im Eingabeverzeichnis
    output_dir.mkdir(parents=True, exist_ok=True)
    for file_path in input_dir.glob("*.txt"):
        process_file(file_path, output_dir)

    # Erstelle ZIP-Datei mit allen Ergebnisdateien
    with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in output_dir.glob("*.txt"):
            zipf.write(file_path, arcname=file_path.name)

# Starte das Skript: Setze Pfade, rufe Hauptfunktion auf
if __name__ == "__main__":
    input_dir = Path("C:/Users/melis/OneDrive/Dokumente/Uni final/Bachelorarbeit/Experiment/idiom_sätze_markiert")
    output_dir = Path("C:/Users/melis/OneDrive/Dokumente/Uni final/Bachelorarbeit/Experiment/idiom_sätze_markiert_output")
    zip_output = Path("C:/Users/melis/OneDrive/Dokumente/Uni final/Bachelorarbeit/Experiment/idiom_output.zip")
    beispiel_path = Path("C:/Users/melis/OneDrive/Dokumente/Uni final/Bachelorarbeit/Experiment/beispielsätze.txt")
    
    main(input_dir, output_dir, zip_output, beispiel_path)