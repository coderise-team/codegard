from fastapi import APIRouter

from schemas.request import SubmissionRequest
from schemas.response import SubmissionResponse

from app.core.runner import run_submission


router = APIRouter()


@router.post("/submit", response_model=SubmissionResponse)
def submit(request: SubmissionRequest):
	return run_submission(request)


