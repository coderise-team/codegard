from enum import Enum

from pydantic import BaseModel


class LanguageEnum(str, Enum):
    PYTHON = "python"


class ProblemTestCasePayload(BaseModel):
    input: str
    expected_output: str


class SubmissionRequest(BaseModel):
    submission_id: int
    language: LanguageEnum
    code: str
    time_limit_ms: int
    memory_limit_mb: int
    test_cases: list[ProblemTestCasePayload]
