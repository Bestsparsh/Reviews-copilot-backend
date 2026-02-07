import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

API_KEY = "dev-key-12345"
headers = {"X-API-Key": API_KEY}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_valid_data():
    payload = {
        "reviews": [
            {
                "text": "Great service!",
                "rating": 5,
                "location": "NYC",
                "date": "2025-01-01"
            },
            {
                "text": "Terrible experience",
                "rating": 1,
                "location": "SF",
                "date": "2025-01-02"
            }
        ]
    }
    
    response = client.post("/ingest/", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 2


def test_ingest_invalid_data():
    payload = {
        "reviews": [
            {
                "text": "Missing rating and location",
                "date": "2025-01-01"
            }
        ]
    }
    
    response = client.post("/ingest/", json=payload, headers=headers)
    assert response.status_code == 422


def test_ingest_without_auth():
    payload = {
        "reviews": [
            {
                "text": "Test",
                "rating": 3,
                "location": "LA",
                "date": "2025-01-01"
            }
        ]
    }
    
    response = client.post("/ingest/", json=payload)
    assert response.status_code == 401


def test_get_reviews_with_pagination():
    response = client.get("/reviews?skip=0&limit=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "reviews" in data
    assert "pagination" in data
    assert isinstance(data["reviews"], list)


def test_search_similar_reviews():
    response = client.get("/search?q=service&k=3", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert data["query"] == "service"
    assert isinstance(data["results"], list)


def test_analytics_endpoint():
    response = client.get("/analytics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "topics" in data
    assert "total_reviews" in data
    assert "avg_rating" in data


def test_create_review():
    payload = {
        "text": "Amazing food!",
        "rating": 5,
        "location": "Boston",
        "date": "2025-12-01"
    }
    
    response = client.post("/reviews/", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Amazing food!"
    assert "id" in data
