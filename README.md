# VVC AI Lead Workflow MVP

A Python proof of concept for an AI-assisted event lead workflow. The project converts a freeform customer inquiry into structured event data, evaluates lead completeness and confidence, applies configurable business rules, recommends packages and add-ons, routes the workflow, and generates proposal and response drafts for human review.

> **Current status:** MVP / proof of concept. This repository demonstrates the workflow and governance pattern; it is not an autonomous production booking system.

## Business problem

Small event-service businesses spend significant time interpreting inquiries, identifying missing information, matching customers to packages, assembling proposals, and drafting responses. This MVP explores how AI-based extraction can reduce that manual work while keeping key business logic explicit and reviewable.

## What this demonstrates

- OpenAI-based extraction of structured event details from freeform inquiries
- Separation of model inference from deterministic Python business logic
- Lead completeness and confidence signals
- Config-driven package, add-on, experience, and operational recommendations
- Workflow routing for full proposal, preliminary proposal, or follow-up-only paths
- Proposal and client-response draft generation
- Deterministic pytest coverage for core business logic
- Human review before client-facing use

## Current architecture

```text
Customer inquiry
      ↓
OpenAI extraction
      ↓
Structured event data
      ↓
Missing-info check ─────→ Follow-up questions
      ↓
Lead status + confidence signal
      ↓
Scoring + deterministic/config-driven recommendations
      ↓
Package / add-on / experience / operational recommendations
      ↓
Workflow routing by lead completeness
      ↓
Proposal + client-response draft
      ↓
Human review before use
```

### Important implementation boundary

The current MVP **calculates confidence**, but the workflow router does not yet use that score as an automated review gate. Routing is driven by lead completeness/status:

- `COMPLETE` → `FULL_PROPOSAL`
- `PARTIAL` → `PRELIMINARY_PROPOSAL`
- otherwise → `FOLLOWUP_ONLY`

Confidence is currently a diagnostic signal. A future enhancement is to make confidence thresholds an explicit automated route to human review.

## Repository structure

- `app.py`: end-to-end demo entry point
- `src/extraction/inquiry_extractor.py`: OpenAI-based inquiry extraction
- `src/scoring/scoring_engine.py`: lead scoring
- `src/recommendations/`: package, add-on, experience, and operational recommendation logic
- `src/workflows/confidence_engine.py`: confidence calculation
- `src/workflows/missing_info_checker.py`: required-field checks
- `src/workflows/lead_status.py`: completeness/status classification
- `src/workflows/workflow_router.py`: workflow selection
- `src/workflows/workflow_executor.py`: action mapping
- `src/workflows/proposal_builder.py`: proposal construction
- `src/workflows/response_generator_v2.py`: response draft generation
- `configs/`: configurable packages, business rules, add-ons, and experience metadata
- `tests/test_core_logic.py`: deterministic tests for core logic
- `examples/demo_leads.json`: fictional lead scenarios

## Design principles

1. **Use the model where language understanding helps.** Inquiry extraction is the AI-dependent step.
2. **Keep business decisions inspectable.** Package and workflow logic live in Python/configuration rather than opaque model output alone.
3. **Surface uncertainty.** Missing information and confidence are calculated explicitly.
4. **Generate drafts, not autonomous sends.** Client-facing output is intended for review before use.
5. **Test deterministic logic separately from the model.** Core routing and recommendation behavior can be regression-tested without an API call.

## Demo lead examples

`examples/demo_leads.json` contains fictional examples for different workflow paths:

- incomplete wedding inquiry → follow-up path
- complete Sweet 16 inquiry → recommendation/proposal path
- corporate brand activation → business-oriented recommendation path

## Local setup

1. Create a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

2. Install runtime dependencies:

```powershell
pip install -r requirements.txt
```

3. Add your OpenAI API key to a local `.env` file or environment variable. Never commit the key.

4. Run the demo:

```powershell
python app.py
```

## Testing

Install development dependencies:

```powershell
pip install -r requirements-dev.txt
```

Run the deterministic test suite:

```powershell
python -m pytest tests/test_core_logic.py
```

The tests cover missing-information detection, workflow routing/execution, scoring, package recommendations, and add-on recommendations.

## Technology positioning

- **Runtime integration:** OpenAI API for inquiry extraction
- **Language / logic:** Python
- **Version control:** Git / GitHub
- **Development and evaluation aids:** ChatGPT, Claude, Cursor, GitHub Copilot, Visual Studio Code

Claude is not part of the current runtime path shown in this repository; it has been used as a development/evaluation aid.

## Future enhancements

- Use confidence thresholds as an explicit automated human-review routing gate
- Load demo scenarios directly from `examples/demo_leads.json`
- Add mocked tests for the OpenAI extraction layer
- Add structured CRM/email outputs
- Add HoneyBook integration
- Add feedback capture from human review decisions
- Expand governance and audit logging for client-facing workflows

## Portfolio note

This is a hands-on applied AI project built for VVC Photobooth Ventures. The repository is intended to demonstrate practical workflow design, AI/data separation, business-rule governance, testing, and human-in-the-loop thinking without overstating the maturity of the current MVP.