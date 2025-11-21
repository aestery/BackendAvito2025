from fastapi import APIRouter, HTTPException
from app.models.user import Reviewer, ReviewerCreate
import app.service as svc

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/reviewers", response_model=list[Reviewer])
async def list_reviewers():
    return svc.list_reviewers()

@router.post("/reviewers", response_model=Reviewer, status_code=201)
async def create_reviewer(body: ReviewerCreate):
    return svc.create_reviewer(body)

@router.get("/reviewers/{id}", response_model=Reviewer)
async def get_reviewer(id: int):
    reviewer = svc.get_reviewer(id)
    if not reviewer:
        raise HTTPException(status_code=404, detail="Reviewer not found")
    return reviewer
