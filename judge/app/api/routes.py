from fastapi import APIRouter, HTTPException
from schemas.request import SubmissionRequest
from schemas.response import SubmissionResponse

from app.core.runner import run_submission
from app.core.cache import store_result, get_result

router = APIRouter()


@router.post(
    "/submit",
    response_model=SubmissionResponse
)
def submit(request: SubmissionRequest) -> SubmissionResponse:
    result = run_submission(request)
    store_result(result)
    return result


@router.get(
    "/status/{submission_id}",
    response_model=SubmissionResponse
)
def get_status(submission_id: int) -> SubmissionResponse:
    result = get_result(submission_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Submission {submission_id} not found",
        )
    return result


