from services.groq_client import GroqClient

client = GroqClient()

response = client.generate_response("Explain audit issue in simple terms")

print("\n=== AI RESPONSE ===\n")
print(response)