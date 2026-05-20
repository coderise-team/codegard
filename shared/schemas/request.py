from pydantic import BaseModel


class ProblemTestCasePayload(BaseModel):
    input: str
    expected_output: str


class SubmissionRequest(BaseModel):
    submission_id: int
    language: str
    code: str
    time_limit_ms: int
    memory_limit_mb: int
    test_cases: list[ProblemTestCasePayload]
