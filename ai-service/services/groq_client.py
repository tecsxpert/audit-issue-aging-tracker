import os
import time
import requests
from dotenv import load_dotenv

# Load .env from root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

API_KEY = os.getenv("GROQ_API_KEY")

class GroqClient:

    def __init__(self):
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

    def generate_response(self, prompt):
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        retries = 3
        backoff = 2  # seconds

        for attempt in range(retries):
            try:
                response = requests.post(self.url, headers=self.headers, json=data)

                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]

                else:
                    print(f"❌ API Error {response.status_code}: {response.text}")

            except Exception as e:
                print(f"❌ Exception on attempt {attempt+1}: {str(e)}")

            # retry delay
            time.sleep(backoff * (attempt + 1))

        # fallback response
        return "AI service temporarily unavailable. Please try again later."