
from pathlib import Path
import json
import re

INPUT_FOLDER = Path("data/processed/pdf_text")
OUTPUT_FOLDER = Path("data/processed/chunks")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def clean_text(text):
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_chunks(text, chunk_size=CHUNK_SIZE,
                      overlap=CHUNK_OVERLAP):
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append({
                "chunk_id": len(chunks) + 1,
                "start_char": start,
                "end_char": end,
                "text": chunk_text
            })

        if end == len(text):
            break

        start = end - overlap

    return chunks


def main():
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    input_files = list(INPUT_FOLDER.glob("*.txt"))

    if not input_files:
        print(f"No extracted text files found in {INPUT_FOLDER}")
        return

    for input_file in input_files:
        text = clean_text(
            input_file.read_text(encoding="utf-8")
        )

        chunks = split_into_chunks(text)

        output_file = OUTPUT_FOLDER / f"{input_file.stem}_chunks.json"
        output_file.write_text(
            json.dumps(chunks, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"Document: {input_file.name}")
        print(f"Characters: {len(text)}")
        print(f"Chunks created: {len(chunks)}")
        print(f"Saved: {output_file}")
        print("-" * 40)

    print("Text chunking completed successfully.")


if __name__ == "__main__":
    main()
