from fastapi import APIRouter, HTTPException, Depends
from app.models.tags import Tags
from app.models.error_response import ErrorCode
from app.routers.errors import ErrorResponse
from app.services.dependencies import get_pull_request_service
from app.services.pull_requests import PullRequestService


router = APIRouter(prefix="/pullRequest", tags=[Tags.PULL_REQUESTS])

@router.post("/create", status_code=201)
async def create_pull_request(
    pull_request_id: str, 
    pull_request_name: str, 
    author_id: str,
    service: PullRequestService = Depends(get_pull_request_service)
    ):
    """Создаёт PR и автоматически назначает до 2 ревьюверов из команды автора"""
    result, error = await service.create_pull_request(
        author_id, pull_request_id, pull_request_name
        )

    if error == ErrorCode.NOT_FOUND:
        return ErrorResponse(
            status_code=404,
            code=error.value,
            message="user, team or request is not found"
        )
    
    if error == ErrorCode.PR_EXISTS:
        return ErrorResponse(
            status_code=409,
            code=error.value,
            message="PR id already exists"
        )
    
    return {"pr": result}

@router.post("/merge", status_code=200)
async def set_pr_as_merged(
    pull_request_id: str, 
    service: PullRequestService = Depends(get_pull_request_service)):
    """Помечает PR как MERGED (идемпотентная операция)"""
    result, error = await service.merge_pull_request(pull_request_id)

    if error == ErrorCode.NOT_FOUND:
        return ErrorResponse(
            status_code=404,
            code=error.value,
            message="PR not found"
        )
    
    return {"pr": result}

@router.post("/reassign", status_code=200)
async def reassign_reviewer(
    pull_request_id: str, 
    old_user_id: str,
    service: PullRequestService = Depends(get_pull_request_service)):
    """Переназначить конкретного ревьювера на другого из его команды"""
    result, error, new_reviewer = await service.reassign_reviwer(pull_request_id, old_user_id)

    if error == ErrorCode.NOT_FOUND:
        return ErrorResponse(
            status_code=404,
            code=error.value,
            message="user, team or request is not found"
        )
    
    if error == ErrorCode.PR_MERGED:
        return ErrorResponse(
            status_code=409,
            code=error.value,
            message="cannot reassign on merged PR"
        )
    
    if error == ErrorCode.NOT_ASSIGNED:
        return ErrorResponse(
            status_code=409,
            code=error.value,
            message="reviewer is not assigned to this PR"
        )
    
    if error == ErrorCode.NO_CANDIDATE:
        return ErrorResponse(
            status_code=409,
            code=error.value,
            message="no active replacement candidate in team"
        )
    
    return {"pr": result, "replaced_by": new_reviewer} 
