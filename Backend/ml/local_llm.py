# backend/ml/local_llm.py
import requests
import os
from typing import Optional

# Default Ollama local endpoint
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


def call_local_llm(prompt: str, model: str = "llama3.1", max_tokens: int = 512) -> str:
    """
    Simple wrapper to call local Ollama (or similar) inference endpoint.
    Ensure ollama is running and model is pulled: ollama run <model>
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.1,
        "stream": False
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        # adjust based on ollama response shape - we expect .get("response") or similar
        if isinstance(data, dict):
            # common keys: 'response' or 'result' or 'outputs'
            if "response" in data:
                return data["response"]
            if "result" in data:
                return data["result"]
            if "outputs" in data and data["outputs"]:
                # outputs may be list with text field
                return data["outputs"][0].get("text", str(data))
        return str(data)
    except Exception as e:
        return f"LLM call error: {e}"
