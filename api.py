from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.workflows.inquiry_pipeline import process_inquiry


app = FastAPI(title="VVC AI Lead Workflow API")


class InquiryRequest(BaseModel):
    inquiry_text: str


@app.post("/process-inquiry")
def process_inquiry_endpoint(request: InquiryRequest) -> dict:
    if not request.inquiry_text.strip():
        raise HTTPException(
            status_code=400,
            detail="inquiry_text must not be blank.",
        )

    try:
        return process_inquiry(request.inquiry_text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to process inquiry.",
        ) from exc