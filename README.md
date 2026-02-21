# Governed-AI-RAG-Workflow-with-Observability
Overview

This project implements a production-ready, governed Retrieval-Augmented Generation (RAG) system that ingests PDF documents, performs semantic retrieval using vector embeddings stored in Supabase (PostgreSQL + pgvector), applies governance guardrails, generates responses using GPT-4.1, and logs performance + token metrics for observability through a BI dashboard.

The system demonstrates full AI workflow engineering — from ingestion to monitoring — with a focus on safety, performance tracking, and production-minded design.

Key Capabilities

PDF ingestion and text extraction

Chunking with metadata (page numbers)

Embedding generation using OpenAI

Vector storage using Supabase (pgvector)

Cosine similarity Top-K retrieval

Governance guardrails:

Profanity filtering

OpenAI moderation enforcement

GPT-4.1 grounded response generation

Token usage & latency tracking

Structured metrics logging

BI dashboard visualization (Looker Studio)

Architecture Overview
Ingestion Flow

PDF → Text Extraction → Chunking → Embedding → Supabase pgvector

Query Flow

User Query
→ Governance Check (Profinity + Moderation)
→ Query Embedding
→ Vector Similarity Search (Top-K)
→ Curated Context
→ GPT-4.1 Generation
→ Response

Observability Flow

Each request logs:

Latency (ms)

Prompt tokens

Completion tokens

Total tokens

Number of retrieved chunks

Success / failure

Error messages (if any)

Metrics are stored in rag_metrics and visualized in a BI dashboard.

Tech Stack

Python 3.11

FastAPI

OpenAI API (GPT-4.1, Embeddings, Moderation)

Supabase (PostgreSQL + pgvector)

psycopg

Looker Studio (Dashboard)

Project Structure
governed-rag-workflow/
│
├── src/
│   ├── api.py
│   ├── rag_pipeline.py
│   ├── ingest_pdfs.py
│   ├── db.py
│   ├── metrics.py
│   └── config.py
│
├── run_ingest.py
├── test_db.py
├── requirements.txt
├── .env.example
├── README.md
└── architecture_diagram.png (optional)
Setup Instructions
1. Create Environment
conda create -n rag-env python=3.11
conda activate rag-env
pip install -r requirements.txt
2. Configure Environment Variables

Copy the example file:

cp .env.example .env

Update .env with:

OpenAI API key

Supabase database credentials

3. Ingest PDF Documents

Place PDF files inside:

data/pdfs/

Run ingestion:

python run_ingest.py

This will:

Extract text

Generate embeddings

Store vectors in Supabase

4. Start API Server
uvicorn src.api:app --host 127.0.0.1 --port 8000

Open Swagger UI:

http://127.0.0.1:8000/docs

Use /ask endpoint to query documents.

Governance Design

The system enforces safety through:

Regex-based profanity detection

OpenAI moderation model (omni-moderation-latest)

Blocking unsafe queries

Logging violations into metrics table

This ensures responsible AI behavior before generation occurs.

Observability & Metrics

Each request captures:

Latency (ms)

Prompt tokens

Completion tokens

Total tokens

Retrieval depth (num_chunks)

Success/failure

Error message (if applicable)

These metrics are stored in Supabase and visualized in a BI dashboard to monitor performance and token efficiency.

Design Decisions

Used text-embedding-3-small (1536 dimensions) to remain compatible with pgvector ivfflat index limit and optimize cost.

Top-K retrieval set to 5 to balance relevance and token efficiency.

Decorator-based metrics tracking for clean separation of concerns.

Environment-driven configuration for production-readiness.

Vector similarity search using cosine distance.

Limitations & Future Improvements

No reranking layer

No semantic caching

No hybrid keyword + vector search

No streaming responses

No authentication layer

These could be added to further production-harden the system.

Summary

This project demonstrates a governed, production-style RAG workflow capable of:

Transforming PDFs into a searchable vector knowledge base

Retrieving relevant context using semantic similarity

Generating grounded responses with GPT-4.1

Enforcing governance guardrails

Monitoring performance and token usage via BI visualization
