from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from src.workflows.inquiry_pipeline import process_inquiry
from src.workflows.review_store import load_review_items, save_review_items


app = FastAPI(title="VVC AI Lead Workflow API")
REVIEW_QUEUE_PATH = Path(__file__).resolve().parent / "data" / "review_queue.json"


class InquiryRequest(BaseModel):
    inquiry_text: str


class ReviewDecisionRequest(BaseModel):
    reviewer: str
    decision_notes: str | None = None


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.post("/process-inquiry")
def process_inquiry_endpoint(request: InquiryRequest) -> dict:
    if not request.inquiry_text.strip():
        raise HTTPException(
            status_code=400,
            detail="inquiry_text must not be blank.",
        )

    try:
        result = process_inquiry(request.inquiry_text)
        created_at = _utc_timestamp()
        review_item = {
            "review_id": str(uuid4()),
            "inquiry_text": request.inquiry_text,
            "event_data": result["event_data"],
            "missing_info": result["missing_info"],
            "confidence": result["confidence"],
            "lead_status": result["lead_status"],
            "workflow": result["workflow"],
            "action": result["action"],
            "score": result["score"],
            "package_recommendation": result["package_recommendation"],
            "experience_recommendation": result["experience_recommendation"],
            "operations_recommendation": result["operational_recommendations"],
            "addon_recommendations": result["addons"],
            "proposal": result["proposal"],
            "client_response": result["client_response"],
            "status": "pending",
            "created_at": created_at,
            "reviewed_at": None,
            "reviewer": None,
            "decision_notes": None,
            "audit": [
                {
                    "action": "created",
                    "timestamp": created_at,
                    "reviewer": None,
                    "notes": "Draft created from inquiry processing",
                }
            ],
        }
        review_items = load_review_items(REVIEW_QUEUE_PATH)
        review_items.append(review_item)
        save_review_items(REVIEW_QUEUE_PATH, review_items)
        return review_item
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to create review item.",
        ) from exc


@app.get("/review-items")
def get_review_items(
    status: Literal["pending", "approved", "rejected"] | None = Query(default=None),
) -> list[dict]:
    try:
        review_items = load_review_items(REVIEW_QUEUE_PATH)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to load review items.",
        ) from exc

    if status is not None:
        review_items = [item for item in review_items if item["status"] == status]
    return review_items


def _record_decision(
    review_id: str,
    decision: Literal["approved", "rejected"],
    request: ReviewDecisionRequest,
) -> dict:
    if not request.reviewer.strip():
        raise HTTPException(status_code=400, detail="reviewer must not be blank.")

    try:
        review_items = load_review_items(REVIEW_QUEUE_PATH)
        for item in review_items:
            if item["review_id"] != review_id:
                continue

            if item["status"] != "pending":
                raise HTTPException(
                    status_code=409,
                    detail="Review item has already been decided.",
                )

            reviewed_at = _utc_timestamp()
            reviewer = request.reviewer.strip()
            item["status"] = decision
            item["reviewed_at"] = reviewed_at
            item["reviewer"] = reviewer
            item["decision_notes"] = request.decision_notes
            item["audit"].append(
                {
                    "action": decision,
                    "timestamp": reviewed_at,
                    "reviewer": reviewer,
                    "notes": request.decision_notes,
                }
            )
            save_review_items(REVIEW_QUEUE_PATH, review_items)
            return item

        raise HTTPException(status_code=404, detail="Review item not found.")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to update review item.",
        ) from exc


@app.post("/review-items/{review_id}/approve")
def approve_review_item(review_id: str, request: ReviewDecisionRequest) -> dict:
    return _record_decision(review_id, "approved", request)


@app.post("/review-items/{review_id}/reject")
def reject_review_item(review_id: str, request: ReviewDecisionRequest) -> dict:
    return _record_decision(review_id, "rejected", request)