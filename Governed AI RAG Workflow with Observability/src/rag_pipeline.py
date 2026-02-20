from typing import Dict, Any
from openai import OpenAI
from .config import (
    OPENAI_API_KEY,
    GENERATION_MODEL,
    TOP_K,
    MAX_CONTEXT_CHARS,
)
from .embeddings import embed_text
from .db import search_similar_chunks
from .governance import enforce_input_policy
from .metrics import track_rag_call

client = OpenAI(api_key=OPENAI_API_KEY)

def build_context(chunks):
    texts = []
    total_chars = 0
    for c in chunks:
        part = f"[Page {c['metadata'].get('page', '?')}]\n{c['content']}\n\n"
        if total_chars + len(part) > MAX_CONTEXT_CHARS:
            break
        texts.append(part)
        total_chars += len(part)
    return "".join(texts)

@track_rag_call
def rag_answer(query: str) -> Dict[str, Any]:
    allowed, msg = enforce_input_policy(query)
    if not allowed:
        # Return “fake” result so metrics still record cleanly
        return {
            "model": None,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "chunks": [],
            "answer": msg,
            "extra": {"blocked_by_policy": True},
        }

    q_emb = embed_text(query)
    chunks = search_similar_chunks(q_emb, TOP_K)
    context = build_context(chunks)

    system_prompt = (
        "You are a helpful assistant answering questions using ONLY the provided context. "
        "If the answer is not in the context, say you do not know."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"Context:\n{context}\n\n"
                f"User question: {query}\n\n"
                "Answer concisely and cite page numbers where relevant."
            ),
        },
    ]

    completion = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=messages,
    )

    choice = completion.choices[0].message
    answer = choice.content

    result = {
        "model": completion.model,
        "usage": {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens,
        },
        "chunks": chunks,
        "answer": answer,
        "extra": {},
    }
    return result