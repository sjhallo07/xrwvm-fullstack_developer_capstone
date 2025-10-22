from flask import Flask, jsonify, request
from urllib.parse import unquote

app = Flask(__name__)

@app.route("/analyze/<path:text>", methods=["GET"])
def analyze_get(text):
    t = unquote(text)
    return jsonify({"sentiment": "neutral", "text": t})

@app.route("/analyze", methods=["POST"])
def analyze_post():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    return jsonify({"sentiment": "neutral", "text": text})
