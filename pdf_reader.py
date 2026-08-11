import faiss
import os
import PyPDF2
import numpy as np
import pickle
import pymupdf
import pytesseract
import sys
from sentence_transformers import SentenceTransformer

OCR_CACHE_FILE = "ocr_cache.pkl"

pytesseract.pytesseract.tesseract_cmd = (
    os.environ.get(
        "TESSERACT_CMD",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
)

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded")


def load_ocr_cache():

    if os.path.exists(OCR_CACHE_FILE):

        with open(OCR_CACHE_FILE, "rb") as f:
            return pickle.load(f)

    return {}


def save_ocr_cache(cache):

    with open(OCR_CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)


def extract_page_text(pdf_path, page_index, ocr_cache, pdf_doc):

    page_number = page_index + 1

    if page_number in ocr_cache:

        return ocr_cache[page_number]

    with open(pdf_path, "rb") as f:

        pdf_reader = PyPDF2.PdfReader(f)

        text = pdf_reader.pages[page_index].extract_text() or ""

    if text.strip() and len(text.strip()) >= 20:

        return text

    print(
        f"Page {page_number} has no text layer, "
        "running OCR..."
    )

    page = pdf_doc[page_index]

    pix = page.get_pixmap(dpi=200)

    temp_path = os.path.join(
        os.environ.get("TEMP", "."),
        f"_ocr_page_{page_number}.png"
    )

    pix.save(temp_path)

    try:

        text = pytesseract.image_to_string(
            temp_path,
            lang="eng"
        ) or ""

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)

    ocr_cache[page_number] = text

    if page_number % 25 == 0:
        print(f"OCR progress: page {page_number}")

    save_ocr_cache(ocr_cache)

    return text


def pdf_to_vectors(pdf_path):

    print(f"\nReading PDF: {pdf_path}")

    with open(pdf_path, "rb") as f:

        pdf_reader = PyPDF2.PdfReader(f)

        total_pages = len(pdf_reader.pages)

        print(f"Total pages: {total_pages}")

    ocr_cache = load_ocr_cache()

    print(f"Loaded OCR cache: {len(ocr_cache)} pages")

    pdf_doc = pymupdf.open(pdf_path)

    page_texts = []

    for page_num in range(total_pages):

        page_text = extract_page_text(
            pdf_path,
            page_num,
            ocr_cache,
            pdf_doc
        )

        page_texts.append({
            "text": page_text,
            "page_number": page_num + 1
        })

    pdf_doc.close()

    chunks = []
    chunk_metadata = []

    chunk_size = 500
    chunk_overlap = 50

    for page in page_texts:

        page_text = page["text"]
        page_number = page["page_number"]

        if not page_text.strip():
            continue

        step = chunk_size - chunk_overlap

        for start in range(
            0,
            len(page_text),
            step
        ):

            chunk_text = page_text[
                start:start + chunk_size
            ]

            if not chunk_text.strip():
                continue

            chunks.append(chunk_text)

            chunk_metadata.append({
                "page_number": page_number,
                "start_position": start
            })

    print(f"Created {len(chunks)} chunks")

    if not chunks:

        print("No text found in PDF.")

        return None, [], []

    print("\nCreating local embeddings...")

    embeddings = embedding_model.encode(
        chunks,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    embeddings = np.array(
        embeddings,
        dtype="float32"
    )

    print(
        f"Vector shape: {embeddings.shape}"
    )

    faiss.normalize_L2(embeddings)

    print("Creating FAISS index...")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(embeddings)

    print("Saving FAISS index...")

    faiss.write_index(
        index,
        "vectors.index"
    )

    print("Saving chunks and metadata...")

    with open("chunks.pkl", "wb") as f:

        pickle.dump(
            {
                "chunks": chunks,
                "metadata": chunk_metadata,
                "total_pages": total_pages
            },
            f
        )

    print("\nVECTOR DATABASE CREATED")

    print("Files created:")

    print("   vectors.index")
    print("   chunks.pkl")

    print(
        f"\nNumber of chunks: {len(chunks)}"
    )

    print(
        f"Vector dimension: "
        f"{embeddings.shape[1]}"
    )

    return (
        embeddings,
        chunks,
        chunk_metadata
    )


if __name__ == "__main__":

    pdf_file = sys.argv[1] if len(sys.argv) > 1 else "documents/history_world.pdf"

    embeddings, chunks, metadata = pdf_to_vectors(
        pdf_file
    )

    print("\nSetup completed!")