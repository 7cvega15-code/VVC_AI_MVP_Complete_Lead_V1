import pytest

from src.scoring.scoring_engine import score_event
from src.recommendations.package_recommender import recommend_package
from src.recommendations.addon_recommender import recommend_addons
from src.workflows.missing_info_checker import check_missing_info
from src.workflows.workflow_router import route_workflow
from src.workflows.workflow_executor import execute_workflow


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
