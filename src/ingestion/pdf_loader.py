
from pathlib import Path
from pypdf import PdfReader

PDF_FOLDER = Path("data/pdfs")
OUTPUT_FOLDER = Path("data/processed/pdf_text")


def extract_pdf_text(pdf_path):
    reader = PdfReader(str(pdf_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(
            f"\n--- Page {page_number} ---\n{text}"
        )

    return "\n".join(pages), len(reader.pages)


def main():
    PDF_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    pdf_files = list(PDF_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {PDF_FOLDER.resolve()}")
        print("Add a college PDF to this folder and run the script again.")
        return

    for pdf_path in pdf_files:
        try:
            text, page_count = extract_pdf_text(pdf_path)

            output_path = OUTPUT_FOLDER / f"{pdf_path.stem}.txt"
            output_path.write_text(text, encoding="utf-8")

            print(f"PDF: {pdf_path.name}")
            print(f"Pages: {page_count}")
            print(f"Extracted characters: {len(text)}")
            print(f"Saved text: {output_path}")
            print("-" * 40)

        except Exception as error:
            print(f"Failed to process {pdf_path.name}: {error}")

    print("PDF ingestion completed.")


if __name__ == "__main__":
    main()
