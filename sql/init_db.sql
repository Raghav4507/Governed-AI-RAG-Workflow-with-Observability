-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title           text,
    source_path     text,
    created_at      timestamptz DEFAULT now()
);

-- Chunks table with pgvector
CREATE TABLE IF NOT EXISTS doc_chunks (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     uuid REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index     int NOT NULL,
    content         text NOT NULL,
    metadata        jsonb,
    embedding       vector(1536), -- using text-embedding-3-small (1536 dims)
    created_at      timestamptz DEFAULT now()
);

-- Index for vector similarity
CREATE INDEX IF NOT EXISTS idx_doc_chunks_embedding
ON doc_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_doc_chunks_document_id
ON doc_chunks(document_id);

-- Metrics table for observability
CREATE TABLE IF NOT EXISTS rag_metrics (
    id                  bigserial PRIMARY KEY,
    created_at          timestamptz DEFAULT now(),
    user_query          text,
    model               text,
    latency_ms          int,
    prompt_tokens       int,
    completion_tokens   int,
    total_tokens        int,
    num_chunks          int,
    success             boolean,
    error_message       text,
    response_sample     text,      -- truncated response
    extra               jsonb      -- any extra fields
);

-- Sample INSERTS
INSERT INTO documents (title, source_path)
VALUES ('Sample Manual', '/data/pdfs/sample_manual.pdf');

INSERT INTO doc_chunks (document_id, chunk_index, content, metadata, embedding)
VALUES (
    (SELECT id FROM documents LIMIT 1),
    0,
    'This is a sample chunk for testing.',
    '{"page": 1, "section": "intro"}',
    NULL
);

INSERT INTO rag_metrics (user_query, model, latency_ms, prompt_tokens,
                         completion_tokens, total_tokens, num_chunks,
                         success, error_message, response_sample)
VALUES (
    'What is in the sample manual?',
    'gpt-4.1',
    1200,
    50,
    80,
    130,
    3,
    true,
    NULL,
    'Sample response text ...'
);