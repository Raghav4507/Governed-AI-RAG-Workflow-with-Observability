import os
from typing import List, Dict
from pypdf import PdfReader
from tqdm import tqdm
from .db import insert_document, insert_chunk
from .embeddings import embed_text

def extract_text_from_pdf(path: str) -> List[Dict]:
    """
    Returns list of {page_number, text}
    """
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({"page": i + 1, "text": text})
    return pages

def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
        if start < 0:
            start = 0
    return [c for c in chunks if c]

def ingest_pdf(path: str, title: str | None = None):
    if title is None:
        title = os.path.basename(path)

    doc_id = insert_document(title=title, source_path=path)
    pages = extract_text_from_pdf(path)

    chunk_index = 0
    for page in tqdm(pages, desc=f"Ingesting {title}"):
        page_text = page["text"]
        if not page_text.strip():
            continue
        chunks = chunk_text(page_text)
        for c in chunks:
            emb = embed_text(c)
            metadata = {"page": page["page"]}
            insert_chunk(
                document_id=doc_id,
                chunk_index=chunk_index,
                content=c,
                metadata=metadata,
                embedding=emb,
            )
            chunk_index += 1

def ingest_folder(folder_path: str):
    for fname in os.listdir(folder_path):
        if not fname.lower().endswith(".pdf"):
            continue
        fpath = os.path.join(folder_path, fname)
        ingest_pdf(fpath)