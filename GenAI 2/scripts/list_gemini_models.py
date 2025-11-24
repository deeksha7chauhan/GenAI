# scripts/list_gemini_models.py
import os
import re
import google.generativeai as genai  # uses the "google-generativeai" package

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise SystemExit("Set GOOGLE_API_KEY in your environment first.")

genai.configure(api_key=api_key)

print("Models available to your key:\n")
for m in genai.list_models():
    name = getattr(m, "name", "")
    # google.generativeai returns names like "models/gemini-1.5-flash-8b"
    short = re.sub(r"^models/", "", name)
    methods = getattr(m, "supported_generation_methods", [])
    print(f"- {short}   methods={list(methods)}")



