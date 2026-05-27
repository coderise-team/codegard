import logging

import redis
from django.conf import settings
from schemas import ProblemTestCasePayload, SubmissionRequest

logger = logging.getLogger(__name__)

# Redis connection — reuse single connection pool
_redis_client = None


def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _redis_client


JUDGE_QUEUE_KEY = "judge:queue"


def push_to_judge_queue(submission) -> bool:
    """
    Push a submission to the Redis judge queue.
    Returns True on success, False on failure.
    """
    test_cases = [
        ProblemTestCasePayload(input=tc.input, expected_output=tc.expected_output)
        for tc in submission.problem.test_cases.all()
    ]
    payload = SubmissionRequest(
        submission_id=submission.pk,
        language=submission.language,
        code=submission.code,
        time_limit_ms=submission.problem.time_limit,
        memory_limit_mb=submission.problem.memory_limit,
        test_cases=test_cases,
    )

    try:
        client = get_redis_client()
        client.rpush(JUDGE_QUEUE_KEY, payload.model_dump_json())
        logger.info(f"Submission #{submission.pk} pushed to judge queue.")
        return True
    except redis.RedisError as e:
        logger.error(f"Failed to push submission #{submission.pk} to Redis: {e}")
        return False
