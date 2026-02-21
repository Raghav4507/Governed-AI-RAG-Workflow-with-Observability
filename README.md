# Governed-AI-RAG-Workflow-with-Observability
## Overview

This project implements a production-ready, governed Retrieval-Augmented Generation (RAG) system that ingests PDF documents, performs semantic retrieval using vector embeddings stored in Supabase (PostgreSQL + pgvector), applies governance guardrails, generates responses using GPT-4.1, and logs performance + token metrics for observability through a BI dashboard.

The system demonstrates full AI workflow engineering — from ingestion to monitoring — with a focus on safety, performance tracking, and production-minded design.

---
## Key Capabilities

* PDF ingestion and text extraction
* Chunking with metadata (page numbers)
* Embedding generation using OpenAI
* Vector storage using Supabase (pgvector)
* Cosine similarity Top-K retrieval
* Governance guardrails:
  * Profanity filtering
  * OpenAI moderation enforcement
* GPT-4.1 grounded response generation
* Token usage & latency tracking
* Structured metrics logging
* BI dashboard visualization (Looker Studio)

  ---
## Architecture Overview
### Ingestion Flow

PDF → Text Extraction → Chunking → Embedding → Supabase pgvector

### Query Flow

#### User Query
→ Governance Check (Profinity + Moderation) <br />
→ Query Embedding <br />
→ Vector Similarity Search (Top-K) <br />
→ Curated Context <br />
→ GPT-4.1 Generation <br />
→ Response <br />

### Observability Flow

Each request logs:
* Latency (ms) 
* Prompt tokens 
* Completion tokens
* Total tokens
* Number of retrieved chunks
* Success/failure
* Error messages (if any)

Metrics are stored in rag_metrics and visualized in a BI dashboard.

---
## Tech Stack

Python 3.11 <br />
FastAPI <br />
OpenAI API (GPT-4.1, Embeddings, Moderation) <br />
Supabase (PostgreSQL + pgvector) <br />
psycopg <br />
Looker Studio (Dashboard) <br />
