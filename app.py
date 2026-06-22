import logging
import os

from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error.description)}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(error):
    logger.exception("Unhandled server error")
    return jsonify({"error": "Internal server error"}), 500


@app.route("/")
def home():
    return "Loan Risk Backend is Running"


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if data is None:
        logger.warning("Received request with invalid or missing JSON body")
        return jsonify({"error": "Request body must be valid JSON"}), 400

    if "credit_score" not in data:
        return jsonify({"error": "Missing required field: credit_score"}), 400

    credit_score = data["credit_score"]

    if not isinstance(credit_score, (int, float)):
        return jsonify({"error": "credit_score must be a number"}), 400

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
    raw_port = os.environ.get("PORT", "10000")
    try:
        port = int(raw_port)
    except ValueError:
        logger.error("Invalid PORT value %r, falling back to 10000", raw_port)
        port = 10000

    app.run(host="0.0.0.0", port=port)
