import time
from functools import wraps
from .db import insert_metric


def track_rag_call(func):
    """
    Decorator to measure latency + token usage for a RAG call
    and store it in rag_metrics table.
    Assumes the wrapped function returns a dict like:
    {
        "model": str or None,
        "usage": {
            "prompt_tokens": int,
            "completion_tokens": int,
            "total_tokens": int
        },
        "chunks": list,
        "answer": str,
        "extra": dict
    }
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        # Try to read query from kwargs or first positional arg
        user_query = kwargs.get("query") or (args[0] if args else None)
        extra = {}

        try:
            result = func(*args, **kwargs)
            end = time.time()
            latency_ms = int((end - start) * 1000)

            usage = result.get("usage", {}) or {}
            model = result.get("model")
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            num_chunks = len(result.get("chunks", []))
            response_text = result.get("answer", "")
            response_sample = response_text[:255] if response_text else None

            extra.update(result.get("extra", {}) or {})

            insert_metric(
                {
                    "user_query": user_query,
                    "model": model,
                    "latency_ms": latency_ms,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "num_chunks": num_chunks,
                    "success": True,
                    "error_message": None,
                    "response_sample": response_sample,
                    "extra": extra,
                }
            )

            return result

        except Exception as e:
            end = time.time()
            latency_ms = int((end - start) * 1000)

            insert_metric(
                {
                    "user_query": user_query,
                    "model": None,
                    "latency_ms": latency_ms,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "num_chunks": 0,
                    "success": False,
                    "error_message": str(e),
                    "response_sample": None,
                    "extra": extra,
                }
            )
            # Re-raise so FastAPI sees the error
            raise

    return wrapper