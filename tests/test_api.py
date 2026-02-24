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
