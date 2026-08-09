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

st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem;}
.hero {padding: 0.2rem 0 1.1rem 0;}
.hero h1 {margin-bottom: .2rem;}
.eyebrow {font-size:.78rem; letter-spacing:.12em; text-transform:uppercase; font-weight:700; opacity:.65;}
.summary-card {border:1px solid rgba(128,128,128,.22); border-radius:16px; padding:18px 20px; margin:.5rem 0 1rem 0;}
.summary-title {font-size:1.2rem; font-weight:700; margin-bottom:.4rem;}
.chips {line-height:2.2;}
.chip {display:inline-block; border:1px solid rgba(128,128,128,.28); border-radius:999px; padding:2px 10px; margin:2px 5px 2px 0; font-size:.88rem;}
.guardrail {border-left:5px solid #f0a202; background:rgba(240,162,2,.08); border-radius:10px; padding:14px 16px; margin:.7rem 0 1.2rem 0;}
.small-note {font-size:.88rem; opacity:.72;}
div.stButton > button {border-radius:10px; font-weight:700;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">Applied AI • Decision Intelligence</div><h1>VVC AI Lead Assistant</h1></div>', unsafe_allow_html=True)
st.caption("Turns an unstructured customer inquiry into structured lead intelligence, governed recommendations, and a review-ready response.")

DEFAULT_INQUIRY = (
    "We are planning an outdoor school dance in Torrance for about 180 students. "
    "The event will be in the evening and we would like printed photos."
)

inquiry = st.text_area("Customer inquiry", value=DEFAULT_INQUIRY, height=120)

if st.button("Analyze Lead", type="primary", use_container_width=True):
    if not inquiry.strip():
        st.warning("Enter a customer inquiry first.")
        st.stop()

    with st.spinner("Extracting lead details and applying business rules..."):
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

    st.markdown("### AI understood the inquiry")
    summary_bits = []
    if event_data.get("event_type"):
        summary_bits.append(str(event_data["event_type"]).title())
    if event_data.get("guest_count"):
        summary_bits.append(f"{event_data['guest_count']} Guests")
    if event_data.get("location"):
        summary_bits.append(str(event_data["location"]))
    if event_data.get("outdoor_event"):
        summary_bits.append("Outdoor")
    if event_data.get("night_event"):
        summary_bits.append("Evening")
    if event_data.get("wants_prints"):
        summary_bits.append("Prints Requested")

    chips = "".join(f'<span class="chip">{bit}</span>' for bit in summary_bits)
    st.markdown(f'<div class="summary-card"><div class="summary-title">Lead snapshot</div><div class="chips">{chips}</div></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Confidence", f"{confidence['score']}%", confidence["level"])
    c2.metric("Lead Status", lead_status["status"])
    c3.metric("Lead Score", score)

    if missing_info:
        st.markdown(
            '<div class="guardrail"><b>Recommended next action: FOLLOW UP BEFORE QUOTING</b><br>'
            '<span class="small-note">The system can calculate an internal preliminary recommendation, but client-facing pricing is held until required event details are confirmed.</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.success("Required lead information is complete. Recommendation can proceed to human review.")

    left, right = st.columns([1, 1])
    with left:
        st.markdown("#### Missing information")
        if missing_info:
            icons = {"Event Date": "📅", "Start Time": "🕐", "Duration": "⏱️", "Venue": "📍"}
            for item in missing_info:
                st.write(f"{icons.get(item, '•')} {item}")
        else:
            st.write("✓ No required information missing")

    recommended = recommendation["recommended"]
    with right:
        st.markdown("#### Preliminary recommendation")
        st.write(f"**{recommended['product_family']} {recommended['tier_name']}**")
        st.write(f"{recommended['included_hours']} hours • ${recommended['base_price']} base price")
        st.caption("Internal recommendation — subject to confirmation and human review.")

    with st.expander("View AI extraction"):
        st.json(event_data)

    st.markdown("### Decision support")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("#### Recommended experience")
        st.write(f"**{experience['recommended_experience']}**")
        st.markdown("#### Operational considerations")
        for item in operations:
            st.write(f"• {item}")
    with d2:
        st.markdown("#### Suggested add-ons")
        if final_addons:
            for addon in final_addons:
                st.write(f"• {addon}")
        else:
            st.write("No add-ons recommended.")
        st.markdown("#### Workflow route")
        st.write(f"**{workflow.replace('_', ' ').title()}**")
        st.caption(f"System action: {action}")

    if missing_info:
        st.markdown("### Review-ready follow-up")
        st.info("The workflow asks for missing information instead of sending a final quote.")
        st.write(followup)
    else:
        st.markdown("### Proposal draft")
        st.text_area("Review before use", value=proposal, height=200, disabled=True)

    st.markdown("### Client response draft")
    st.text_area("Human review required before sending", value=client_response, height=220, disabled=True)

    with st.expander("View internal preliminary proposal"):
        st.caption("Generated for internal decision support. Not client-ready while required information is missing.")
        st.text_area("Internal draft", value=proposal, height=200, disabled=True, label_visibility="collapsed")

    st.caption(
        "MVP / proof of concept • AI extracts inquiry details • Business rules remain explicit and reviewable • Client-facing output requires human review"
    )
