from fastapi.testclient import TestClient

import api


client = TestClient(api.app)


def test_process_inquiry_returns_pipeline_result(monkeypatch):
    expected_result = {
        "event_data": {"event_type": "school dance"},
        "missing_info": [],
        "client_response": "Draft response",
    }
    monkeypatch.setattr(api, "process_inquiry", lambda inquiry_text: expected_result)

    response = client.post(
        "/process-inquiry",
        json={"inquiry_text": "A school dance inquiry"},
    )

    assert response.status_code == 200
    assert response.json() == expected_result


def test_process_inquiry_rejects_blank_text(monkeypatch):
    def unexpected_pipeline_call(inquiry_text):
        raise AssertionError("The pipeline should not run for blank input")

    monkeypatch.setattr(api, "process_inquiry", unexpected_pipeline_call)

    response = client.post(
        "/process-inquiry",
        json={"inquiry_text": " \t\n "},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "inquiry_text must not be blank."}