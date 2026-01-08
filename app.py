from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Loan Risk Backend is Running"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    credit_score = data.get("credit_score", 0)

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
        "risk_percentage": risk_percentage
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
