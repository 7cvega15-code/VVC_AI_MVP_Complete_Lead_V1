import streamlit as st

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

st.set_page_config(page_title="VVC AI Lead Assistant", page_icon="✨", layout="wide")

st.title("VVC AI Lead Assistant")
st.caption("AI-assisted lead analysis with explicit business rules and human review")

DEFAULT_INQUIRY = (
    "We are planning an outdoor school dance in Torrance for about 180 students. "
    "The event will be in the evening and we would like printed photos."
)

inquiry = st.text_area("Customer inquiry", value=DEFAULT_INQUIRY, height=130)

if st.button("Analyze Lead", type="primary", use_container_width=True):
    if not inquiry.strip():
        st.warning("Enter a customer inquiry first.")
        st.stop()

    with st.spinner("Analyzing inquiry and applying business rules..."):
        event_data = extract_event_info(inquiry)
        missing_info = check_missing_info(event_data)
        confidence = calculate_confidence(event_data, missing_info)
        followup = generate_followup_questions(missing_info)
        lead_status = determine_lead_status(missing_info)
        workflow = route_workflow(lead_status)
        action = execute_workflow(workflow)
        score = score_event(event_data)
        recommendation = recommend_package(event_data, score)
        experience = recommend_experience(event_data)
        operations = recommend_operations(event_data)
        addons = recommend_addons(event_data)

        final_addons = []
        for addon in experience["recommended_addons"] + addons:
            if addon not in final_addons:
                final_addons.append(addon)

        proposal = build_proposal(event_data, experience, recommendation, final_addons)
        client_response = generate_client_response(
            event_data,
            recommendation,
            final_addons,
            missing_info,
            lead_status,
            action,
        )

    st.subheader("Lead Analysis")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Confidence", f"{confidence['score']}%", confidence["level"])
    c2.metric("Lead Status", lead_status["status"])
    c3.metric("Workflow", workflow.replace("_", " ").title())
    c4.metric("Lead Score", score)

    with st.expander("Structured event data", expanded=True):
        st.json(event_data)

    left, right = st.columns(2)
    with left:
        st.subheader("Missing Information")
        if missing_info:
            for item in missing_info:
                st.write(f"• {item}")
        else:
            st.success("No required information missing.")

        st.subheader("Recommended Experience")
        st.write(f"**{experience['recommended_experience']}**")

        recommended = recommendation["recommended"]
        st.subheader("Recommended Package")
        st.write(f"**{recommended['product_family']} {recommended['tier_name']}**")
        st.write(f"Base price: **${recommended['base_price']}**")
        st.write(f"Included hours: **{recommended['included_hours']}**")

    with right:
        st.subheader("Recommended Add-ons")
        if final_addons:
            for addon in final_addons:
                st.write(f"• {addon}")
        else:
            st.write("No add-ons recommended.")

        st.subheader("Operational Recommendations")
        for item in operations:
            st.write(f"• {item}")

        st.subheader("Workflow Action")
        st.info(str(action))

    st.subheader("Proposal Draft")
    st.text_area("Review before use", value=proposal, height=220, disabled=True)

    if missing_info:
        st.subheader("Follow-up Questions")
        st.write(followup)

    st.subheader("Client Response Draft")
    st.text_area("Human review required", value=client_response, height=220, disabled=True)

    st.caption(
        "MVP / proof of concept. AI is used for inquiry extraction; consequential business logic "
        "remains explicit and reviewable. Client-facing output requires human review."
    )
