import spacy
import re
from pathlib import Path
import zipfile

nlp = spacy.load("de_core_news_sm")

def extract_idiom_from_filename(filename: Path):
    return [p.lower() for p in filename.stem.split("_")]

def rebracket_line(line: str, idiom_lemmas: list) -> str:
    # Speichere Positionen der bereits geklammerten Tokens
    already_bracketed = set()
    def unbracket_word(match):
        word = match.group(1)
        already_bracketed.add(word)
        return word

    clean_line = re.sub(r"\[([^\[\]]+)\]", unbracket_word, line)
    doc = nlp(clean_line)

    result = []
    for token in doc:
        text = token.text
        lemma = token.lemma_.lower()

        if text in already_bracketed:
            result.append(f"[{text}]")
        elif lemma in idiom_lemmas:
            result.append(f"[{text}]")
        else:
            result.append(text)

    return " ".join(result)

def process_file(file_path: Path, output_dir: Path):
    idiom_lemmas = extract_idiom_from_filename(file_path)

    with file_path.open(encoding="utf-8") as f:
        content = f.read().strip()

    if "\n\n" in content:
        literal_block, idiomatic_block = content.split("\n\n", 1)
    else:
        lines = content.strip().split("\n")
        literal_block = "\n".join(lines[:50])
        idiomatic_block = "\n".join(lines[50:])

    literal_lines = [rebracket_line(l, idiom_lemmas) for l in literal_block.strip().split("\n") if l.strip()]
    idiomatic_lines = [rebracket_line(l, idiom_lemmas) for l in idiomatic_block.strip().split("\n") if l.strip()]

    out_path = output_dir / file_path.name
    with out_path.open("w", encoding="utf-8") as out_f:
        for line in literal_lines:
            out_f.write(line + "\n")
        out_f.write("\n")
        for line in idiomatic_lines:
            out_f.write(line + "\n")

def main(input_dir: Path, output_dir: Path, zip_output: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    for file_path in input_dir.glob("*.txt"):
        process_file(file_path, output_dir)

    with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in output_dir.glob("*.txt"):
            zipf.write(file_path, arcname=file_path.name)

if __name__ == "__main__":
    input_dir = Path("C:/Users/melis/OneDrive/Dokumente/Uni final/Bachelorarbeit/Experiment/idiom_sätze_markiert")
    output_dir = Path("C:/Users/melis/OneDrive/Dokumente/Uni final/Bachelorarbeit/Experiment/idiom_sätze_markiert_output")
    zip_output = Path("C:/Users/melis/OneDrive/Dokumente/Uni final/Bachelorarbeit/Experiment/idiom_output.zip")
    main(input_dir, output_dir, zip_output)