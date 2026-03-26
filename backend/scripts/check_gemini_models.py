import google.generativeai as genai
import os

def test_full_prompt():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        api_key = line.split("=")[1].strip()
                        break
    
    if not api_key:
        print("No API key found.")
        return
    
    genai.configure(api_key=api_key)
    print(f"Testing full prompt with key: {api_key[:10]}...")
    
    symptoms = "persistent fever, sore throat, and dry cough for 3 days"
    AVAILABLE_PLANTS = [
        "Aloevera", "Amla", "Amruthaballi", "Ashwagandha", "Bamboo",
        "Betel", "Bhrami", "Bringaraja", "Catharanthus", "Chilly",
        "Coffee", "Curry_Leaf", "Drumstick", "Ginger", "Giloy",
        "Guava", "Hibiscus", "Lemon", "Moringa", "Neem",
        "Peppermint", "Tulsi", "Turmeric"
    ]
    
    model_name = "gemini-1.5-flash"
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""You are a senior Ayurvedic physician with 30 years of clinical experience.
A patient describes: "{symptoms}"
From this list of available medicinal plants only: {", ".join(AVAILABLE_PLANTS)}
Recommend exactly 3 most appropriate plants. Return ONLY raw JSON:
{{
  "recommendations": [
    {{
      "plant": "Tulsi",
      "scientific_name": "Ocimum tenuiflorum",
      "ayurvedic_name": "Tulasi",
      "why": "Brief reason",
      "preparation": "How to prepare",
      "dosage": "Suggested dosage",
      "dosha_effect": "Effect on doshas",
      "active_compounds": "Key compounds",
      "safety": "Safety notes",
      "classical_reference": "Reference"
    }}
  ],
  "lifestyle_advice": "One tip",
  "diet_tip": "One tip",
  "warning": "Medical disclaimer"
}}"""
        print("Sending request...")
        response = model.generate_content(prompt, request_options={"timeout": 60})
        print(f"Success! Response text preview: {response.text[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_full_prompt()
