from src.ingest_pdfs import ingest_folder

if __name__ == "__main__":
    ingest_folder("data/pdfs")
    print("Ingestion complete.")