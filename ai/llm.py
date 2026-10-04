import os
import ollama
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "180"))


def generate_response(prompt):
    """Generate a compact LLM response for the Investigation Agent.

    Llama 3 is running locally on CPU, so this function avoids unnecessary
    output and keeps the model loaded between requests. The Agent/LangGraph
    architecture is unchanged.
    """
    if not prompt or not prompt.strip():
        print("[LLM] Empty prompt received.")
        return None

    try:
        print(f"[LLM] Generating FIR response with {MODEL_NAME}...")

        client = ollama.Client(
            host="http://127.0.0.1:11434",
            timeout=OLLAMA_TIMEOUT
        )

        response = client.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.0,
                "top_p": 0.8,
                "num_predict": 120,
                "num_ctx": 2048,
                "repeat_penalty": 1.05
            },
            keep_alive="10m"
        )

        content = response.get("message", {}).get("content", "")

        if not content:
            print("[LLM] Ollama returned an empty response.")
            return None

        print("[LLM] Response received successfully.")
        return content.strip()

    except Exception as e:
        print(f"[LLM] Ollama request failed: {e}")
        return None
