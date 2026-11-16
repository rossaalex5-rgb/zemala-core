import os
from google import genai
from google.genai import types

client = genai.Client()

ZEMALA_SYSTEM_PROMPT = """
Du bist ZEMALA. Deine Tonalität ist radikal pragmatisch, ikonisch, selbstbewusst und absolut präzise.
0-Latenz-Vollzug. Jede Intention ist sofort als technischer Befehl zu werten.
"""

config = types.GenerateContentConfig(
    system_instruction=ZEMALA_SYSTEM_PROMPT,
    temperature=0.2,
    max_output_tokens=1024
)

def run_zemala_instance(user_input: str):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_input,
            config=config
        )
        return response.text
    except Exception as e:
        return f"Pipeline-Sicherung aktiv. Fehler abgefangen: {str(e)}"

if __name__ == "__main__":
    import sys
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Status prüfen."
    print(run_zemala_instance(prompt))
