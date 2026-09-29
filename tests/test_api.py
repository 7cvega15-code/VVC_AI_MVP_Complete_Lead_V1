import pytest
from fastapi.testclient import TestClient

import api


PIPELINE_RESULT = {
    "event_data": {"event_type": "school dance", "guest_count": 180},
    "missing_info": ["Event Date"],
    "confidence": {"score": 90, "level": "HIGH"},
    "lead_status": {"status": "PARTIAL", "message": "Needs follow-up."},
    "workflow": "PRELIMINARY_PROPOSAL",
    "action": "SHOW_PROPOSAL_AND_QUESTIONS",
    "score": 60,
    "package_recommendation": {"recommended": {"tier_name": "Signature"}},
    "experience_recommendation": {"recommended_experience": "Spark"},
    "operational_recommendations": ["Check power access"],
    "addons": ["Prints"],
    "proposal": "Draft proposal",
    "client_response": "Draft response",
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "REVIEW_QUEUE_PATH", tmp_path / "review_queue.json")
    return TestClient(api.app)


def mock_pipeline(monkeypatch):
    monkeypatch.setattr(
        api,
        "process_inquiry",
        lambda inquiry_text: PIPELINE_RESULT,
    )


def create_pending_item(client, monkeypatch):
    mock_pipeline(monkeypatch)
    response = client.post(
        "/process-inquiry",
        json={"inquiry_text": "A school dance inquiry"},
    )
    assert response.status_code == 200
    return response.json()


def test_process_inquiry_creates_pending_review_item(client, monkeypatch):
    item = create_pending_item(client, monkeypatch)

    assert item["review_id"]
    assert item["inquiry_text"] == "A school dance inquiry"
    assert item["event_data"] == PIPELINE_RESULT["event_data"]
    assert item["missing_info"] == ["Event Date"]
    assert item["confidence"] == PIPELINE_RESULT["confidence"]
    assert item["status"] == "pending"
    assert item["created_at"]
    assert item["reviewed_at"] is None
    assert item["reviewer"] is None
    assert item["decision_notes"] is None
    assert item["audit"] == [
        {
            "action": "created",
            "timestamp": item["created_at"],
            "reviewer": None,
            "notes": "Draft created from inquiry processing",
        }
    ]
    assert api.REVIEW_QUEUE_PATH.exists()


def test_get_review_items_returns_and_filters_items(client, monkeypatch):
    item = create_pending_item(client, monkeypatch)

    all_items = client.get("/review-items")
    pending_items = client.get("/review-items", params={"status": "pending"})
    approved_items = client.get("/review-items", params={"status": "approved"})

    assert all_items.status_code == 200
    assert all_items.json() == [item]
    assert pending_items.json() == [item]
    assert approved_items.json() == []


def test_approve_review_item_updates_status_and_audit(client, monkeypatch):
    item = create_pending_item(client, monkeypatch)

    response = client.post(
        f"/review-items/{item['review_id']}/approve",
        json={"reviewer": "Alex", "decision_notes": "Reviewed and approved."},
    )
    approved = response.json()

    assert response.status_code == 200
    assert approved["status"] == "approved"
    assert approved["reviewed_at"]
    assert approved["reviewer"] == "Alex"
    assert approved["decision_notes"] == "Reviewed and approved."
    assert approved["audit"][-1] == {
        "action": "approved",
        "timestamp": approved["reviewed_at"],
        "reviewer": "Alex",
        "notes": "Reviewed and approved.",
    }


def test_reject_review_item_updates_status_and_audit(client, monkeypatch):
    item = create_pending_item(client, monkeypatch)

    response = client.post(
        f"/review-items/{item['review_id']}/reject",
        json={"reviewer": "Alex", "decision_notes": "Needs revision."},
    )
    rejected = response.json()

    assert response.status_code == 200
    assert rejected["status"] == "rejected"
    assert rejected["reviewed_at"]
    assert rejected["reviewer"] == "Alex"
    assert rejected["decision_notes"] == "Needs revision."
    assert rejected["audit"][-1] == {
        "action": "rejected",
        "timestamp": rejected["reviewed_at"],
        "reviewer": "Alex",
        "notes": "Needs revision.",
    }


@pytest.mark.parametrize("decision", ["approve", "reject"])
def test_unknown_review_id_returns_404(client, decision):
    response = client.post(
        f"/review-items/unknown-id/{decision}",
        json={"reviewer": "Alex"},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("first_decision", "second_decision"),
    [
        ("approve", "approve"),
        ("approve", "reject"),
        ("reject", "approve"),
        ("reject", "reject"),
    ],
)
def test_final_review_item_cannot_be_decided_again(
    client,
    monkeypatch,
    first_decision,
    second_decision,
):
    item = create_pending_item(client, monkeypatch)
    decision_data = {"reviewer": "Alex"}

    first_response = client.post(
        f"/review-items/{item['review_id']}/{first_decision}",
        json=decision_data,
    )
    second_response = client.post(
        f"/review-items/{item['review_id']}/{second_decision}",
        json=decision_data,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409


def test_process_inquiry_rejects_blank_text(client, monkeypatch):
    def unexpected_pipeline_call(inquiry_text):
        raise AssertionError("The pipeline should not run for blank input")

    monkeypatch.setattr(api, "process_inquiry", unexpected_pipeline_call)
    response = client.post(
        "/process-inquiry",
        json={"inquiry_text": " \t\n "},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "inquiry_text must not be blank."}