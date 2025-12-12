from dotenv import load_dotenv
import os
import google.generativeai as genai

# load .env file
load_dotenv()

# Load env var
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

MODEL = "models/gemini-flash-latest"   # ✔ correct model path

print([m.name for m in genai.list_models()])
# print(MODEL)

def call_gemini(prompt: str, json_mode: bool = False):
    try:
        model = genai.GenerativeModel(MODEL)

        if json_mode:
            response = model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json"
                }
            )
        else:
            response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        return f"Gemini error: {e}"
    
