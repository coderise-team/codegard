"""Simple in-memory cache for submission results."""

from schemas.response import SubmissionResponse

_submission_cache: dict[int, SubmissionResponse] = {}


def store_result(result: SubmissionResponse) -> None:
    _submission_cache[result.submission_id] = result


def get_result(submission_id: int) -> SubmissionResponse | None:
    return _submission_cache.get(submission_id)


def clear_cache() -> None:
    _submission_cache.clear()

