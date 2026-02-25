import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_normalize_text_endpoint():
    client = APIClient()
    response = client.post(
        reverse("normalize-input"),
        {"inputType": "text", "text": "a) find velocity b) find acceleration"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["subject"] == "physics"
    assert response.data["questionParts"]


@pytest.mark.django_db
def test_decompose_endpoint_without_azure_credentials():
    client = APIClient()
    response = client.post(
        reverse("decompose-question"),
        {
            "sessionId": "abc123",
            "normalizedQuery": {
                "query": "find velocity",
                "subject": "physics",
                "hasDiagram": False,
                "questionParts": ["find velocity"],
            },
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["subgoals"] == ["find velocity"]
    assert response.data["currentIndex"] == 0


@pytest.mark.django_db
def test_connected_workflow_endpoint_returns_structured_statuses():
    client = APIClient()
    response = client.post(
        reverse("tutoring-workflow"),
        {
            "sessionId": "student-101",
            "inputType": "text",
            "text": "a) find velocity b) find acceleration",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "normalizedQuery" in response.data
    assert "decomposed" in response.data
    assert isinstance(response.data["statusTrail"], list)
    assert any(item["keyword"] == "thinking" for item in response.data["statusTrail"])
    assert any(item["keyword"] == "creating subgoals" for item in response.data["statusTrail"])
