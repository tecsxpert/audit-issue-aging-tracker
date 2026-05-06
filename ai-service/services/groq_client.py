import json
import os
import re
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

    def generate_recommendations(self, issue):
        prompt = f"""
You are a professional audit expert.

Provide exactly 3 actionable recommendations for the given audit issue.

Make responses:
- Specific to auditing context
- Practical and implementable

STRICT RULES:
- Return ONLY JSON
- High, Medium, Low priority (in order)
- Each description max 1 line

Format:
[
  {{"action_type":"Fix","description":"","priority":"High"}},
  {{"action_type":"Improve","description":"","priority":"Medium"}},
  {{"action_type":"Monitor","description":"","priority":"Low"}}
]

Audit Issue:
{issue}
"""

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        def make_default_recommendations():
            return [
                {
                    "action_type": "Fix",
                    "description": "Review the issue and apply an immediate correction to control processes.",
                    "priority": "High"
                },
                {
                    "action_type": "Improve",
                    "description": "Update the audit workflow to prevent this type of issue in the future.",
                    "priority": "Medium"
                },
                {
                    "action_type": "Monitor",
                    "description": "Track the implemented changes and verify they remain effective.",
                    "priority": "Low"
                }
            ]

        def extract_json_array(text):
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if not match:
                return None
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, list) and len(parsed) == 3:
                    return parsed
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
            return None

        retries = 3
        timeout = 10
        backoff = 2

        for attempt in range(1, retries + 1):
            try:
                response = requests.post(
                    self.url,
                    headers=self.headers,
                    json=payload,
                    timeout=timeout
                )

                if response.status_code != 200:
                    print(f"❌ API Error {response.status_code} on attempt {attempt}: {response.text}")
                else:
                    choice_text = response.text
                    parsed = extract_json_array(choice_text)
                    if parsed is not None:
                        return parsed
                    print("❌ Failed to extract a valid JSON recommendation array from API response.")

            except requests.RequestException as e:
                print(f"❌ Request exception on attempt {attempt}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error on attempt {attempt}: {e}")

            if attempt < retries:
                sleep_time = backoff * attempt
                print(f"⏳ Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)

        print("⚠️ All retries exhausted. Returning fallback recommendations.")
        return make_default_recommendations()
