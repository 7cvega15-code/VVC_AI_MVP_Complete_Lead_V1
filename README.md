# VVC_AI_MVP_Complete_Lead_V1

## Overview

This project is a Python MVP for an AI-assisted event intelligence and recommendation engine for VVC Photobooths.

It demonstrates how to convert freeform customer inquiries into structured event data, score lead value, recommend packages and add-ons from config-driven business rules, and support human review with proposal and response generation.

## Status

MVP / proof of concept. The current version demonstrates core lead interpretation, scoring, recommendation, and workflow-routing logic. It is not intended as a production booking system yet.

## What it demonstrates

- AI-assisted event inquiry interpretation using OpenAI
- Config-driven package, add-on, and experience recommendation logic
- Lead scoring and workflow routing based on event attributes
- Separation of LLM extraction from deterministic business rules
- Human-in-the-loop proposal and client response support

## Architecture

- `app.py`: demo entry point that runs the pipeline on a sample inquiry
- `src/extraction/inquiry_extractor.py`: LLM-based extraction of event details
- `src/scoring/scoring_engine.py`: scoring logic for lead and package recommendation
- `src/recommendations/`: package, add-on, experience, and operational recommendation modules
- `src/workflows/`: workflow routing, missing-info checks, proposal building, and response generation
- `configs/`: JSON-driven business rules, packages, and add-on metadata
- `tests/test_core_logic.py`: deterministic tests for scoring, routing, recommendations, and missing-info checks
- `examples/demo_leads.json`: fictional sample leads for different workflow demos

## Demo lead examples

The file `examples/demo_leads.json` contains fictional sample leads used to demonstrate different workflow paths:

- `incomplete_wedding_lead` → follow-up questions
- `complete_sweet_16_lead` → full package and add-on recommendation
- `corporate_brand_activation` → business-focused recommendation and upsell logic

## Local setup

1. Create a virtual environment:

```powershell
python -m venv venv
```

2. Activate the environment:

```powershell
venv\Scripts\activate
```

3. Install runtime dependencies:

```powershell
pip install -r requirements.txt
```

4. Add your OpenAI API key to a `.env` file in the project root.

5. Run the demo:

```powershell
python app.py
```

## Testing

Core deterministic business logic can be tested without calling OpenAI.
Dev dependencies are listed in `requirements-dev.txt`.

Install dev dependencies:

```powershell
pip install -r requirements-dev.txt
```

Run tests:

```powershell
python -m pytest tests/test_core_logic.py
```

Current tests cover missing-info detection, workflow routing, workflow execution, scoring, package recommendation, and add-on recommendation.

## Notes

- The project expects an `OPENAI_API_KEY` environment variable to be available.
- Keep `.env` and `venv/` out of version control.
- This is an MVP intended to show how AI extraction and deterministic business rules can work together in a photobooth lead workflow.

## Future enhancements

- Load demo leads from `examples/demo_leads.json` instead of a hardcoded sample inquiry
- Add mocked tests for OpenAI-based extraction
- Add HoneyBook workflow integration
- Add structured proposal output for CRM/email workflows
- Add governance rules for human review before client-facing responses are sent
