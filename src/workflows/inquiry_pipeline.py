from src.extraction.inquiry_extractor import extract_event_info
from src.scoring.scoring_engine import score_event
from src.recommendations.package_recommender import recommend_package
from src.recommendations.addon_recommender import recommend_addons
from src.recommendations.experience_recommender import recommend_experience
from src.recommendations.operational_recommender import recommend_operations
from src.workflows.proposal_builder import build_proposal
from src.workflows.missing_info_checker import check_missing_info
from src.workflows.followup_generator import generate_followup_questions
from src.workflows.lead_status import determine_lead_status
from src.workflows.workflow_router import route_workflow
from src.workflows.workflow_executor import execute_workflow
from src.workflows.response_generator_v2 import generate_client_response
from src.workflows.confidence_engine import calculate_confidence


def process_inquiry(inquiry_text: str) -> dict:
    event_data = extract_event_info(inquiry_text)
    missing_info = check_missing_info(event_data)
    confidence = calculate_confidence(event_data, missing_info)
    followup_questions = generate_followup_questions(missing_info)
    lead_status = determine_lead_status(missing_info)
    workflow = route_workflow(lead_status)
    action = execute_workflow(workflow)
    score = score_event(event_data)

    package_recommendation = recommend_package(event_data, score)
    experience_recommendation = recommend_experience(event_data)
    operational_recommendations = recommend_operations(event_data)
    recommended_addons = recommend_addons(event_data)

    addons = []
    for addon in experience_recommendation["recommended_addons"] + recommended_addons:
        if addon not in addons:
            addons.append(addon)

    proposal = build_proposal(
        event_data,
        experience_recommendation,
        package_recommendation,
        addons
    )
    client_response = generate_client_response(
        event_data,
        package_recommendation,
        addons,
        missing_info,
        lead_status,
        action
    )

    return {
        "event_data": event_data,
        "missing_info": missing_info,
        "confidence": confidence,
        "followup_questions": followup_questions,
        "lead_status": lead_status,
        "workflow": workflow,
        "action": action,
        "score": score,
        "package_recommendation": package_recommendation,
        "experience_recommendation": experience_recommendation,
        "operational_recommendations": operational_recommendations,
        "addons": addons,
        "proposal": proposal,
        "client_response": client_response,
    }