"""
PersonaAudit - Flask Backend
POST /generate  →  returns password list from generator.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from generator import generate_from_dict

app = Flask(__name__)
CORS(app)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)

    if not data.get("first_name") or not data.get("last_name"):
        return jsonify({"error": "first_name and last_name are required."}), 400

    # Map frontend 'keywords' key to 'additional_keywords' expected by generator
    if "keywords" in data and "additional_keywords" not in data:
        data["additional_keywords"] = data.pop("keywords")

    result = generate_from_dict(data)
    return jsonify(result), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
