from pathlib import Path
import html
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

st.set_page_config(page_title="VVC AI Lead Assistant", page_icon="✦", layout="wide")

LOGO = Path("assets/vvc_logo.png")

st.markdown("""
<style>
:root {
  --ink:#1a1a1a;
  --accent:#6b4fa0;
  --body:#444;
  --body2:#333;
  --muted:#666;
  --quiet:#888;
  --lav:#f3f0fa;
  --white:#fff;
}
.block-container {max-width: 1480px; padding-top: 1rem; padding-bottom: 2rem;}
[data-testid="stHeader"] {background:transparent;}
h1,h2,h3,h4 {letter-spacing:-.02em;color:var(--ink);}
.hero-title {font-size:2.65rem;font-weight:800;line-height:1.05;margin:.15rem 0 .35rem;color:var(--ink);}
.hero-title span {color:var(--accent);}
.hero-sub {color:var(--muted);font-size:1rem;margin-bottom:.8rem;}
.ai-pill {display:inline-block;background:var(--lav);color:var(--accent);border-radius:999px;padding:4px 10px;font-size:.72rem;font-weight:800;letter-spacing:.04em;}
.flow {display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:.8rem;}
.flow-step {border:1px solid var(--lav);border-radius:12px;padding:8px 12px;background:var(--white);font-size:.82rem;color:var(--body);}
.flow-step b {color:var(--ink);}
.flow-arrow {color:var(--accent);font-weight:800;}
.card {border:1px solid var(--lav);border-radius:16px;padding:16px 18px;background:var(--white);height:100%;}
.card-title {font-weight:750;font-size:.92rem;color:var(--ink);margin-bottom:10px;}
.chip {display:inline-block;border:1px solid var(--lav);border-radius:9px;padding:6px 10px;margin:3px 4px 3px 0;background:var(--white);font-size:.83rem;color:var(--body2);}
.section-title {font-size:1.25rem;font-weight:800;color:var(--ink);margin:1rem 0 .55rem;}
.guardrail {border:1px solid var(--accent);background:var(--lav);border-radius:12px;padding:12px 16px;margin:.7rem 0 1rem;color:var(--body2);}
.guardrail b {color:var(--ink);}
.brand-note {border:1px solid var(--lav);background:var(--lav);border-radius:9px;padding:10px 12px;color:var(--body);font-size:.86rem;margin-top:10px;}
.missing-note {border:1px solid var(--lav);background:var(--lav);border-radius:9px;padding:10px 12px;color:var(--body);font-size:.84rem;margin-top:10px;}
.route {background:var(--lav);color:var(--accent);border-radius:8px;padding:8px 10px;font-weight:800;}
.footer {text-align:center;color:var(--quiet);font-size:.75rem;margin-top:1.2rem;}
.output-card {border:1px solid var(--lav);background:var(--lav);border-radius:14px;padding:16px 18px;min-height:330px;height:100%;display:flex;flex-direction:column;}
.output-card-title {font-size:1rem;font-weight:800;color:var(--ink);margin-bottom:4px;}
.output-card-sub {font-size:.78rem;color:var(--quiet);margin-bottom:12px;min-height:18px;}
.output-card-body {background:var(--white);border:1px solid var(--white);border-radius:10px;padding:15px 16px;color:var(--body);font-size:.9rem;line-height:1.5;white-space:pre-wrap;flex:1;}
div.stButton > button[kind="primary"] {background:var(--accent);border:0;border-radius:10px;font-weight:750;color:var(--white);}
div.stButton > button[kind="primary"]:hover {background:var(--ink);color:var(--white);}
[data-testid="stMetric"] {border:1px solid var(--lav);border-radius:16px;padding:14px 16px;background:var(--white);min-height:125px;}
[data-testid="stMetricLabel"] {font-weight:700;color:var(--body2);}
[data-testid="stMetricValue"] {color:var(--accent);}
[data-testid="stMetricDelta"] {color:var(--muted)!important;background:var(--lav);border-radius:999px;padding:2px 6px;width:max-content;}
textarea {border-radius:10px!important;}
</style>
""", unsafe_allow_html=True)

# Header
logo_col, title_col = st.columns([1.15, 7.2], vertical_alignment="center")
with logo_col:
    if LOGO.exists():
        st.image(str(LOGO), width=185)
    else:
        st.markdown("<div style='font-size:2rem;font-weight:800;color:#6b4fa0'>VVC</div><div style='font-size:.72rem;letter-spacing:.16em;color:#444'>PHOTOBOOTH VENTURES</div>", unsafe_allow_html=True)
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
    if event_data.get("event_type"): bits.append("◦ " + str(event_data["event_type"]).title())
    if event_data.get("guest_count"): bits.append(f"◦ {event_data['guest_count']} Guests")
    if event_data.get("location"): bits.append("◦ " + str(event_data["location"]))
    if event_data.get("outdoor_event"): bits.append("◦ Outdoor")
    if event_data.get("night_event"): bits.append("◦ Evening")
    if event_data.get("wants_prints"): bits.append("◦ Prints Requested")
    with snapshot:
        chips = "".join(f'<span class="chip">{x}</span>' for x in bits)
        st.markdown(f'<div class="card"><div class="card-title">Lead snapshot</div>{chips}</div>', unsafe_allow_html=True)
    with conf: st.metric("Confidence", f"{confidence['score']}%", confidence["level"])
    with status: st.metric("Lead Status", lead_status["status"], "More information needed" if missing_info else "Ready for review", delta_color="off")
    with leadscore: st.metric("Lead Score", score, "Out of 100", delta_color="off")

    if missing_info:
        st.markdown('<div class="guardrail">✦ &nbsp; <b>Recommended next action: FOLLOW UP BEFORE QUOTING</b><br><span style="font-size:.84rem;color:#666">An internal preliminary recommendation can be calculated, but client-facing pricing is held until required event details are confirmed.</span></div>', unsafe_allow_html=True)

    missing_col, rec_col = st.columns([1, 1.2])
    with missing_col:
        rows = "".join(f"<div style='margin:7px 0'>• &nbsp; {x}</div>" for x in missing_info) if missing_info else "✓ No required information missing"
        st.markdown(f'<div class="card"><div class="card-title">Missing information</div>{rows}<div class="missing-note">These details are needed to confirm availability, recommend the right package, and provide accurate pricing.</div></div>', unsafe_allow_html=True)
    recommended = recommendation["recommended"]
    with rec_col:
        duration_text = f"{recommended['included_hours']} hours • " if not missing_info or "Duration" not in missing_info else ""
        st.markdown(f'<div class="card"><div class="card-title">✦ &nbsp; Preliminary recommendation</div><div style="color:#6b4fa0;font-weight:800;font-size:1.05rem">{recommended["product_family"]} {recommended["tier_name"]}</div><div style="margin-top:8px;color:#333">{duration_text}${recommended["base_price"]} base price</div><div class="brand-note">Internal starting recommendation based on known lead attributes such as guest count, print preference, and event type. Final duration and pricing remain subject to confirmation and human review.</div></div>', unsafe_allow_html=True)

    d1,d2,d3,d4 = st.columns(4)
    with d1:
        st.markdown(f'<div class="card"><div class="card-title">Decision support</div><small style="color:#666">Recommended experience</small><div class="route" style="margin-top:8px">{experience["recommended_experience"]}</div></div>', unsafe_allow_html=True)
    with d2:
        items = "".join(f"<div style='margin:5px 0;color:#444'>✓ &nbsp; {x}</div>" for x in final_addons)
        st.markdown(f'<div class="card"><div class="card-title">Suggested add-ons</div>{items or "None recommended"}</div>', unsafe_allow_html=True)
    with d3:
        items = "".join(f"<div style='margin:5px 0;color:#444'>• &nbsp; {x}</div>" for x in operations)
        st.markdown(f'<div class="card"><div class="card-title">Operational considerations</div>{items}</div>', unsafe_allow_html=True)
    with d4:
        friendly_route = "FOLLOW-UP REQUIRED" if missing_info else "READY FOR HUMAN REVIEW"
        st.markdown(f'<div class="card"><div class="card-title">Workflow route</div><div class="route">{friendly_route}</div><div style="font-size:.82rem;margin-top:9px;color:#666">The workflow protects against premature client-facing quotes.</div></div>', unsafe_allow_html=True)

    question_map = {
        "Event Date": "What is the event date?",
        "Start Time": "What time should we plan to arrive / start?",
        "Duration": "How many hours would you like the booth for?",
        "Venue": "What is the exact venue name and address?",
    }
    questions = [question_map.get(x, f"Please confirm: {x}") for x in missing_info]
    if questions:
        followup_text = "Hi,\n\nThank you for your interest in VVC Photobooths!\n\nTo help us recommend the best package and provide an accurate quote, could you please share:\n\n" + "\n".join(f"{i}. {q}" for i,q in enumerate(questions,1)) + "\n\nOnce we have these details, we'll send over the best recommendation and pricing for your event.\n\nThanks so much!\n— VVC Photobooths"
    else:
        followup_text = "All required details are present. The recommendation is ready for human review."

    safe_followup = html.escape(followup_text)
    safe_response = html.escape(str(client_response))
    f1,f2 = st.columns(2)
    with f1:
        st.markdown(f'<div class="output-card"><div class="output-card-title">Review-ready follow-up</div><div class="output-card-sub">Questions generated from missing required information.</div><div class="output-card-body">{safe_followup}</div></div>', unsafe_allow_html=True)
    with f2:
        st.markdown(f'<div class="output-card"><div class="output-card-title">Client response draft</div><div class="output-card-sub">Human review required before sending.</div><div class="output-card-body">{safe_response}</div></div>', unsafe_allow_html=True)

    with st.expander("View AI extraction (structured data)"):
        st.json(event_data)
    with st.expander("View decision logic (rules & workflow)"):
        st.write({"lead_status": lead_status, "workflow": workflow, "system_action": action, "lead_score": score})
        st.caption("Technical routing details are available for auditability but intentionally kept out of the primary business view.")
    with st.expander("View internal preliminary proposal"):
        st.text_area("Internal proposal", value=proposal, height=200, disabled=True, label_visibility="collapsed")

    st.markdown('<div class="footer">VVC AI Lead Assistant &nbsp; • &nbsp; AI extracts inquiry details &nbsp; • &nbsp; Business rules remain explicit and reviewable &nbsp; • &nbsp; Client-facing output requires human review</div>', unsafe_allow_html=True)
