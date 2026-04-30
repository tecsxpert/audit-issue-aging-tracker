from flask import Flask, request, jsonify
from services.groq_client import GroqClient
from datetime import datetime

app = Flask(__name__)
client = GroqClient()


@app.route("/describe", methods=["POST"])
def describe():

    data = request.get_json()

    # ✅ Input validation
    if not data or "issue" not in data:
        return jsonify({"error": "Invalid input: 'issue' field required"}), 400

    issue = data["issue"]

    if not isinstance(issue, str) or len(issue.strip()) < 5:
        return jsonify({"error": "Issue must be a valid string (min 5 chars)"}), 400

    try:
        # ✅ Call GroqClient
        ai_response = client.generate_response(issue)

        # ✅ Structured JSON response
        return jsonify({
            "description": ai_response,
            "generated_at": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)