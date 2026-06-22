import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHomeRoute:
    def test_home_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_home_returns_expected_message(self, client):
        response = client.get("/")
        assert response.data == b"Loan Risk Backend is Running"


class TestPredictRoute:
    def test_predict_high_risk_below_600(self, client):
        response = client.post("/predict", json={"credit_score": 500})
        data = response.get_json()
        assert response.status_code == 200
        assert data["risk_level"] == "High Risk"
        assert data["risk_percentage"] == 80

    def test_predict_high_risk_at_boundary_599(self, client):
        response = client.post("/predict", json={"credit_score": 599})
        data = response.get_json()
        assert data["risk_level"] == "High Risk"
        assert data["risk_percentage"] == 80

    def test_predict_medium_risk_at_boundary_600(self, client):
        response = client.post("/predict", json={"credit_score": 600})
        data = response.get_json()
        assert data["risk_level"] == "Medium Risk"
        assert data["risk_percentage"] == 50

    def test_predict_medium_risk_mid_range(self, client):
        response = client.post("/predict", json={"credit_score": 650})
        data = response.get_json()
        assert data["risk_level"] == "Medium Risk"
        assert data["risk_percentage"] == 50

    def test_predict_medium_risk_at_boundary_700(self, client):
        response = client.post("/predict", json={"credit_score": 700})
        data = response.get_json()
        assert data["risk_level"] == "Medium Risk"
        assert data["risk_percentage"] == 50

    def test_predict_low_risk_above_700(self, client):
        response = client.post("/predict", json={"credit_score": 701})
        data = response.get_json()
        assert data["risk_level"] == "Low Risk"
        assert data["risk_percentage"] == 20

    def test_predict_low_risk_high_score(self, client):
        response = client.post("/predict", json={"credit_score": 850})
        data = response.get_json()
        assert data["risk_level"] == "Low Risk"
        assert data["risk_percentage"] == 20

    def test_predict_missing_credit_score_defaults_to_zero(self, client):
        response = client.post("/predict", json={})
        data = response.get_json()
        assert data["risk_level"] == "High Risk"
        assert data["risk_percentage"] == 80

    def test_predict_negative_credit_score(self, client):
        response = client.post("/predict", json={"credit_score": -100})
        data = response.get_json()
        assert data["risk_level"] == "High Risk"
        assert data["risk_percentage"] == 80

    def test_predict_zero_credit_score(self, client):
        response = client.post("/predict", json={"credit_score": 0})
        data = response.get_json()
        assert data["risk_level"] == "High Risk"
        assert data["risk_percentage"] == 80

    def test_predict_returns_json_content_type(self, client):
        response = client.post("/predict", json={"credit_score": 700})
        assert response.content_type == "application/json"

    def test_predict_response_contains_required_keys(self, client):
        response = client.post("/predict", json={"credit_score": 700})
        data = response.get_json()
        assert "risk_level" in data
        assert "risk_percentage" in data

    def test_predict_get_method_not_allowed(self, client):
        response = client.get("/predict")
        assert response.status_code == 405
