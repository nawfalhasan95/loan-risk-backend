import os
import functools

from flask import Flask, request, jsonify

app = Flask(__name__)

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",")
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS if o.strip()]

API_KEY = os.environ.get("API_KEY")


# ---------------------------------------------------------------------------
# Security helpers
# ---------------------------------------------------------------------------

def _add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains"
    )
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    return response


app.after_request(_add_security_headers)


def _add_cors_headers(response):
    origin = request.headers.get("Origin", "")
    if ALLOWED_ORIGINS and origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, X-API-Key"
        )
        response.headers["Access-Control-Max-Age"] = "600"
    return response


app.after_request(_add_cors_headers)


def require_api_key(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not API_KEY:
            return f(*args, **kwargs)
        key = request.headers.get("X-API-Key", "")
        if key != API_KEY:
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return "Loan Risk Backend is Running"


@app.route("/predict", methods=["POST"])
@require_api_key
def predict():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "invalid JSON body"}), 400

    credit_score = data.get("credit_score")
    if credit_score is None:
        return jsonify({"error": "credit_score is required"}), 400

    if not isinstance(credit_score, (int, float)):
        return jsonify({"error": "credit_score must be a number"}), 400

    credit_score = int(credit_score)
    if credit_score < 300 or credit_score > 850:
        return jsonify({"error": "credit_score must be between 300 and 850"}), 400

    if credit_score < 600:
        risk_level = "High Risk"
        risk_percentage = 80
    elif credit_score <= 700:
        risk_level = "Medium Risk"
        risk_percentage = 50
    else:
        risk_level = "Low Risk"
        risk_percentage = 20

    return jsonify({
        "risk_level": risk_level,
        "risk_percentage": risk_percentage,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
