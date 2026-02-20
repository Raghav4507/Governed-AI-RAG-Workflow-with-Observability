from contextlib import contextmanager
import psycopg
from psycopg.types.json import Jsonb
from .config import DB_CONFIG


@contextmanager
def get_conn():
    conn = psycopg.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def insert_document(title: str, source_path: str) -> str:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (title, source_path)
                VALUES (%s, %s)
                RETURNING id;
                """,
                (title, source_path),
            )
            doc_id = cur.fetchone()[0]
        conn.commit()
    return str(doc_id)


def insert_chunk(document_id: str, chunk_index: int, content: str,
                 metadata: dict, embedding: list):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO doc_chunks (document_id, chunk_index, content, metadata, embedding)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (document_id, chunk_index, content, Jsonb(metadata), embedding),
            )
        conn.commit()


def search_similar_chunks(query_embedding: list, top_k: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT content, metadata, 1 - (embedding <=> %s::vector) AS similarity
                FROM doc_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (query_embedding, query_embedding, top_k),
            )
            rows = cur.fetchall()

    return [
        {"content": r[0], "metadata": r[1], "similarity": float(r[2])}
        for r in rows
    ]


def insert_metric(record: dict):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO rag_metrics (
                    user_query, model, latency_ms,
                    prompt_tokens, completion_tokens, total_tokens,
                    num_chunks, success, error_message, response_sample, extra
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                """,
                (
                    record.get("user_query"),
                    record.get("model"),
                    record.get("latency_ms"),
                    record.get("prompt_tokens"),
                    record.get("completion_tokens"),
                    record.get("total_tokens"),
                    record.get("num_chunks"),
                    record.get("success"),
                    record.get("error_message"),
                    record.get("response_sample"),
                    Jsonb(record.get("extra") or {}),
                ),
            )
        conn.commit()