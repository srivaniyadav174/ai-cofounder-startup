
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "AI Co-Founder API is running",
        "version": "1.0.0",
    }


def test_openapi_schema_loads():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "AI Co-Founder"
    assert "/" in schema["paths"]
