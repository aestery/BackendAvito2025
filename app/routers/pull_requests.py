from fastapi import (
    APIRouter, 
    Depends
)
from app.models.tags import Tags
from app.models.error_response import ErrorCode
from app.models.pull_requests import (
    PrCreateSchema,
    PrMergeSchema,
    PrReassignSchema
)
from app.routers.errors import ErrorResponse
from app.services.dependencies import get_pull_request_service
from app.services.pull_requests import PullRequestService


router = APIRouter(prefix="/pullRequest", tags=[Tags.PULL_REQUESTS])

@router.post("/create", status_code=201)
async def create_pull_request(
    schema: PrCreateSchema,
    service: PullRequestService = Depends(get_pull_request_service)
    ):
    """Создаёт PR и автоматически назначает до 2 ревьюверов из команды автора"""
    result, error = await service.create_pull_request(
        schema.author_id, 
        schema.pull_request_id, 
        schema.pull_request_name
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
    schema: PrMergeSchema, 
    service: PullRequestService = Depends(get_pull_request_service)):
    """Помечает PR как MERGED (идемпотентная операция)"""
    result, error = await service.merge_pull_request(schema.pull_request_id)

    if error == ErrorCode.NOT_FOUND:
        return ErrorResponse(
            status_code=404,
            code=error.value,
            message="PR not found"
        )
    
    return {"pr": result}

@router.post("/reassign", status_code=200)
async def reassign_reviewer(
    schema: PrReassignSchema,
    service: PullRequestService = Depends(get_pull_request_service)):
    """Переназначить конкретного ревьювера на другого из его команды"""
    result, error, new_reviewer = await service.reassign_reviwer(
        schema.pull_request_id, 
        schema.old_user_id
        )

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
