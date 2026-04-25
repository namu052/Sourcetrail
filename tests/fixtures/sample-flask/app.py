from flask import Flask, jsonify

from services import get_health_payload

app = Flask(__name__)


@app.get("/health")
def health() -> object:
    return jsonify(get_health_payload())
