from pathlib import Path
import streamlit as st

from src.extraction.inquiry_extractor import extract_event_info
from src.scoring.scoring_engine import score_event
from src.recommendations.package_recommender import recommend_package
from src.recommendations.addon_recommender import recommend_addons
from src.recommendations.experience_recommender import recommend_experience
from src.recommendations.operational_recommender import recommend_operations
from src.workflows.proposal_builder import build_proposal
from src.workflows.missing_info_checker import check_missing_info
from src.workflows.lead_status import determine_lead_status
from src.workflows.workflow_router import route_workflow
from src.workflows.workflow_executor import execute_workflow
from src.workflows.response_generator_v2 import generate_client_response
from src.workflows.confidence_engine import calculate_confidence

st.set_page_config(page_title="VVC AI Lead Assistant", page_icon="✨", layout="wide")

PURPLE = "#4c1d95"
LOGO = Path("assets/vvc_logo.png")

st.markdown("""
<style>
:root { --vvc:#4c1d95; --violet:#6d28d9; --line:#e8e5ef; --soft:#faf9ff; }
.block-container {max-width: 1420px; padding-top: 1.2rem; padding-bottom: 2rem;}
[data-testid="stHeader"] {background:transparent;}
h1,h2,h3,h4 {letter-spacing:-.02em;}
.hero-title {font-size:2.55rem;font-weight:800;line-height:1.05;margin:.15rem 0 .35rem;color:#151225;}
.hero-title span {color:#5b21b6;}
.hero-sub {color:#696476;font-size:1rem;margin-bottom:.8rem;}
.ai-pill {display:inline-block;background:#f1eaff;color:#5b21b6;border-radius:999px;padding:4px 10px;font-size:.72rem;font-weight:800;letter-spacing:.04em;}
.flow {display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:.8rem;}
.flow-step {border:1px solid var(--line);border-radius:12px;padding:8px 12px;background:#fff;font-size:.82rem;}
.flow-step b {color:#231942;}
.flow-arrow {color:#6d28d9;font-weight:800;}
.card {border:1px solid var(--line);border-radius:16px;padding:16px 18px;background:#fff;box-shadow:0 3px 14px rgba(50,35,80,.035);height:100%;}
.card-title {font-weight:750;font-size:.92rem;color:#211a37;margin-bottom:10px;}
.chip {display:inline-block;border:1px solid #e4e0ec;border-radius:9px;padding:6px 10px;margin:3px 4px 3px 0;background:#fff;font-size:.83rem;}
.section-title {font-size:1.25rem;font-weight:800;color:#171225;margin:1rem 0 .55rem;}
.guardrail {border:1px solid #f2d59c;background:#fff9ec;border-radius:12px;padding:12px 16px;margin:.7rem 0 1rem;}
.guardrail b {color:#5d3a00;}
.green-note {border:1px solid #cce9d2;background:#f3fbf5;border-radius:9px;padding:10px 12px;color:#266638;font-size:.86rem;margin-top:10px;}
.missing-note {border:1px solid #ddd4fa;background:#faf8ff;border-radius:9px;padding:10px 12px;color:#4b3b72;font-size:.84rem;margin-top:10px;}
.route {background:#f5f0ff;color:#5b21b6;border-radius:8px;padding:8px 10px;font-weight:800;}
.footer {text-align:center;color:#827c8d;font-size:.75rem;margin-top:1.2rem;}
div.stButton > button[kind="primary"] {background:linear-gradient(90deg,#5b21b6,#a33ee5);border:0;border-radius:10px;font-weight:750;}
[data-testid="stMetric"] {border:1px solid var(--line);border-radius:16px;padding:14px 16px;background:#fff;min-height:125px;}
[data-testid="stMetricLabel"] {font-weight:700;}
[data-testid="stMetricValue"] {color:#4c1d95;}
textarea {border-radius:10px!important;}
</style>
""", unsafe_allow_html=True)

# Header
logo_col, title_col = st.columns([1.05, 7.5], vertical_alignment="center")
with logo_col:
    if LOGO.exists():
        st.image(str(LOGO), width=150)
    else:
        st.markdown("<div style='font-size:2rem;font-weight:800;color:#4c1d95'>VVC</div><div style='font-size:.72rem;letter-spacing:.16em'>PHOTOBOOTH VENTURES</div>", unsafe_allow_html=True)
with title_col:
    st.markdown('<span class="ai-pill">✦ AI-POWERED</span><div class="hero-title">VVC AI <span>Lead Assistant</span></div><div class="hero-sub">AI turns inquiries into intelligence, recommendations, and review-ready responses.</div>', unsafe_allow_html=True)
    st.markdown('<div class="flow"><div class="flow-step"><b>1. Understand</b><br>Extract key details</div><span class="flow-arrow">›</span><div class="flow-step"><b>2. Analyze</b><br>Score & evaluate</div><span class="flow-arrow">›</span><div class="flow-step"><b>3. Recommend</b><br>Suggest best fit</div><span class="flow-arrow">›</span><div class="flow-step"><b>4. Respond</b><br>Draft follow-up</div></div>', unsafe_allow_html=True)

DEFAULT_INQUIRY = "We are planning an outdoor school dance in Torrance for about 180 students. The event will be in the evening and we would like printed photos."
st.markdown('<div class="section-title">Enter customer inquiry</div>', unsafe_allow_html=True)
inquiry = st.text_area("Paste or type the lead inquiry below.", value=DEFAULT_INQUIRY, height=95)

if st.button("✦  Analyze Lead", type="primary", use_container_width=True):
    if not inquiry.strip():
        st.warning("Enter a customer inquiry first.")
        st.stop()

    with st.spinner("Extracting lead details and applying governed business rules..."):
        event_data = extract_event_info(inquiry)
        missing_info = check_missing_info(event_data)
        confidence = calculate_confidence(event_data, missing_info)
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
        client_response = generate_client_response(event_data, recommendation, final_addons, missing_info, lead_status, action)

    st.markdown('<div class="section-title">✦ &nbsp; AI understood the inquiry</div>', unsafe_allow_html=True)
    snapshot, conf, status, leadscore = st.columns([1.8, .9, 1, .9])
    bits = []
    if event_data.get("event_type"): bits.append("🎓 " + str(event_data["event_type"]).title())
    if event_data.get("guest_count"): bits.append(f"👥 {event_data['guest_count']} Guests")
    if event_data.get("location"): bits.append("📍 " + str(event_data["location"]))
    if event_data.get("outdoor_event"): bits.append("☀️ Outdoor")
    if event_data.get("night_event"): bits.append("🌙 Evening")
    if event_data.get("wants_prints"): bits.append("🖨️ Prints Requested")
    with snapshot:
        chips = "".join(f'<span class="chip">{x}</span>' for x in bits)
        st.markdown(f'<div class="card"><div class="card-title">Lead snapshot</div>{chips}</div>', unsafe_allow_html=True)
    with conf: st.metric("Confidence", f"{confidence['score']}%", confidence["level"])
    with status: st.metric("Lead Status", lead_status["status"], "More information needed" if missing_info else "Ready for review", delta_color="off")
    with leadscore: st.metric("Lead Score", score, "Out of 100", delta_color="off")

    if missing_info:
        st.markdown('<div class="guardrail">⚠️ &nbsp; <b>Recommended next action: FOLLOW UP BEFORE QUOTING</b><br><span style="font-size:.84rem;color:#6f6251">An internal preliminary recommendation can be calculated, but client-facing pricing is held until required event details are confirmed.</span></div>', unsafe_allow_html=True)

    missing_col, rec_col = st.columns([1, 1.2])
    with missing_col:
        icons = {"Event Date":"📅", "Start Time":"🕐", "Duration":"⏱️", "Venue":"📍"}
        rows = "".join(f"<div style='margin:7px 0'>{icons.get(x,'•')} &nbsp; {x}</div>" for x in missing_info) if missing_info else "✓ No required information missing"
        st.markdown(f'<div class="card"><div class="card-title">Missing information</div>{rows}<div class="missing-note">These details are needed to confirm availability, recommend the right package, and provide accurate pricing.</div></div>', unsafe_allow_html=True)
    recommended = recommendation["recommended"]
    with rec_col:
        duration_text = f"{recommended['included_hours']} hours • " if not missing_info or "Duration" not in missing_info else ""
        st.markdown(f'<div class="card"><div class="card-title">☆ &nbsp; Preliminary recommendation</div><div style="color:#17833b;font-weight:800;font-size:1.05rem">✦ {recommended["product_family"]} {recommended["tier_name"]}</div><div style="margin-top:8px">{duration_text}${recommended["base_price"]} base price</div><div class="green-note">Internal starting recommendation based on known lead attributes such as guest count, print preference, and event type. Final duration and pricing remain subject to confirmation and human review.</div></div>', unsafe_allow_html=True)

    d1,d2,d3,d4 = st.columns(4)
    with d1:
        st.markdown(f'<div class="card"><div class="card-title">↗ &nbsp; Decision support</div><small>Recommended experience</small><div class="route" style="margin-top:8px">{experience["recommended_experience"]}</div></div>', unsafe_allow_html=True)
    with d2:
        items = "".join(f"<div style='margin:5px 0'>✓ &nbsp; {x}</div>" for x in final_addons)
        st.markdown(f'<div class="card"><div class="card-title">🎁 &nbsp; Suggested add-ons</div>{items or "None recommended"}</div>', unsafe_allow_html=True)
    with d3:
        items = "".join(f"<div style='margin:5px 0'>• &nbsp; {x}</div>" for x in operations)
        st.markdown(f'<div class="card"><div class="card-title">⚙️ &nbsp; Operational considerations</div>{items}</div>', unsafe_allow_html=True)
    with d4:
        friendly_route = "FOLLOW-UP REQUIRED" if missing_info else "READY FOR HUMAN REVIEW"
        st.markdown(f'<div class="card"><div class="card-title">↪ &nbsp; Workflow route</div><div class="route">{friendly_route}</div><div style="font-size:.82rem;margin-top:9px;color:#6f6878">The workflow protects against premature client-facing quotes.</div></div>', unsafe_allow_html=True)

    # Cleaner, client-friendly questions for the portfolio demo.
    question_map = {
        "Event Date": "What is the event date?",
        "Start Time": "What time should we plan to arrive / start?",
        "Duration": "How many hours would you like the booth for?",
        "Venue": "What is the exact venue name and address?",
    }
    questions = [question_map.get(x, f"Please confirm: {x}") for x in missing_info]
    if questions:
        followup_text = "Hi,\n\nThank you for your interest in VVC Photobooths! ✨\n\nTo help us recommend the best package and provide an accurate quote, could you please share:\n\n" + "\n".join(f"{i}. {q}" for i,q in enumerate(questions,1)) + "\n\nOnce we have these details, we'll send over the best recommendation and pricing for your event.\n\nThanks so much!\n— Christina | VVC Photobooths"
    else:
        followup_text = "All required details are present. The recommendation is ready for human review."

    f1,f2 = st.columns(2)
    with f1:
        st.markdown('<div class="section-title" style="font-size:1rem">✉️ &nbsp; Review-ready follow-up</div>', unsafe_allow_html=True)
        st.text_area("Questions to send", value=followup_text, height=250, disabled=True, label_visibility="collapsed")
    with f2:
        st.markdown('<div class="section-title" style="font-size:1rem">👤 &nbsp; Client response draft</div>', unsafe_allow_html=True)
        st.caption("Human review required before sending.")
        st.text_area("Client response", value=client_response, height=225, disabled=True, label_visibility="collapsed")

    with st.expander("View AI extraction (structured data)"):
        st.json(event_data)
    with st.expander("View decision logic (rules & workflow)"):
        st.write({"lead_status": lead_status, "workflow": workflow, "system_action": action, "lead_score": score})
        st.caption("Technical routing details are available for auditability but intentionally kept out of the primary business view.")
    with st.expander("View internal preliminary proposal"):
        st.text_area("Internal proposal", value=proposal, height=200, disabled=True, label_visibility="collapsed")

    st.markdown('<div class="footer">VVC AI Lead Assistant &nbsp; • &nbsp; AI extracts inquiry details &nbsp; • &nbsp; Business rules remain explicit and reviewable &nbsp; • &nbsp; Client-facing output requires human review</div>', unsafe_allow_html=True)
