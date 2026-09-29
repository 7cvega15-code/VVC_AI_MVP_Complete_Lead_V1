import pytest

from src.scoring.scoring_engine import score_event
from src.recommendations.package_recommender import recommend_package
from src.recommendations.addon_recommender import recommend_addons
from src.workflows.missing_info_checker import check_missing_info
from src.workflows.workflow_router import route_workflow
from src.workflows.workflow_executor import execute_workflow
from src.workflows import inquiry_pipeline


def test_missing_info_checker_detects_required_fields():
    event_data = {
        "event_type": "wedding",
        "guest_count": 150,
        "location": "Pasadena"
    }

    missing = check_missing_info(event_data)

    assert "Event Date" in missing
    assert "Start Time" in missing
    assert "Duration" in missing
    assert "Venue" in missing


def test_workflow_router_maps_lead_status_correctly():
    assert route_workflow({"status": "COMPLETE"}) == "FULL_PROPOSAL"
    assert route_workflow({"status": "PARTIAL"}) == "PRELIMINARY_PROPOSAL"
    assert route_workflow({"status": "INCOMPLETE"}) == "FOLLOWUP_ONLY"
    assert route_workflow({"status": "UNKNOWN"}) == "FOLLOWUP_ONLY"


def test_workflow_executor_maps_workflow_to_action_strings():
    assert execute_workflow("FULL_PROPOSAL") == "SHOW_PROPOSAL"
    assert execute_workflow("PRELIMINARY_PROPOSAL") == "SHOW_PROPOSAL_AND_QUESTIONS"
    assert execute_workflow("OTHER") == "SHOW_QUESTIONS_ONLY"


def test_scoring_engine_higher_score_for_strong_lead():
    strong_lead = {
        "event_type": "wedding",
        "guest_count": 180,
        "wants_prints": True
    }
    weak_lead = {
        "event_type": "school dance",
        "guest_count": 20,
        "wants_prints": False
    }

    assert score_event(strong_lead) > score_event(weak_lead)


def test_package_recommender_recommends_luxe_for_prints_requested():
    event_data = {
        "event_type": "wedding",
        "wants_prints": True
    }
    score = 10

    recommendation = recommend_package(event_data, score)
    assert recommendation["recommended"]["product_family"] == "The Luxe"


def test_addon_recommender_returns_addons_for_relevant_event_type():
    event_data = {"event_type": "wedding"}
    addons = recommend_addons(event_data)

    assert isinstance(addons, list)
    assert len(addons) > 0
    assert "Custom Magnets" in addons


def test_process_inquiry_returns_pipeline_results_without_openai(monkeypatch):
    event_data = {
        "event_type": "school dance",
        "guest_count": 180,
        "wants_prints": True,
        "location": "Torrance",
        "event_date": "2026-10-10",
        "start_time": "7:00 PM",
        "duration": "4 hours",
        "venue": "Torrance High School",
        "outdoor_event": True,
        "night_event": True,
        "needs_power": True,
    }
    monkeypatch.setattr(
        inquiry_pipeline,
        "extract_event_info",
        lambda inquiry_text: event_data,
    )

    result = inquiry_pipeline.process_inquiry("A school dance inquiry")

    assert set(result) == {
        "event_data",
        "missing_info",
        "confidence",
        "followup_questions",
        "lead_status",
        "workflow",
        "action",
        "score",
        "package_recommendation",
        "experience_recommendation",
        "operational_recommendations",
        "addons",
        "proposal",
        "client_response",
    }
    assert result["event_data"] == event_data
    assert result["missing_info"] == []
    assert result["workflow"] == "FULL_PROPOSAL"
    assert len(result["addons"]) == len(set(result["addons"]))
    assert result["proposal"]
    assert result["client_response"]
