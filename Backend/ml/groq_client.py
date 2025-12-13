# ml/groq_client.py
import os
from dotenv import load_dotenv
from groq import Groq

# Load .env
load_dotenv()

# Load Groq API Key
GROQ_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_KEY)

MODEL = "openai/gpt-oss-20b"  # best general-purpose model on Groq
# print(GROQ_KEY)

def call_groq(prompt: str, json_mode: bool = False):
    """
    drop-in replacement for call_gemini()
    returns text output or JSON output depending on json_mode
    """

    try:
        if json_mode:
            # Ask Groq to return JSON
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
        else:
            # Standard text mode
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )

        return completion.choices[0].message.content

    except Exception as e:
        return f"Groq error: {e}"
