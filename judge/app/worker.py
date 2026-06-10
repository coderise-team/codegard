import asyncio
import logging

from pydantic import ValidationError
from redis.asyncio import Redis
from schemas.request import SubmissionRequest
from schemas.response import SubmissionResponse, VerdictEnum

from app.config import settings
from app.core.runner import run_submission

logger = logging.getLogger(__name__)


def _attempts_key(submission_id: int) -> str:
    return f"judge:attempts:{submission_id}"


def _internal_failure(submission_id: int) -> SubmissionResponse:
    return SubmissionResponse(
        submission_id=submission_id,
        verdict=VerdictEnum.RE,
        error_message="Internal judge error",
    )


async def _finish(redis: Redis, raw: str, response: SubmissionResponse) -> None:
    await redis.rpush(settings.judge_results_key, response.model_dump_json())
    await redis.lrem(settings.judge_processing_key, 1, raw)
    await redis.delete(_attempts_key(response.submission_id))


async def handle_one(redis: Redis, raw: str) -> None:
    try:
        request = SubmissionRequest.model_validate_json(raw)
    except ValidationError:
        logger.exception("Malformed submission payload, dropping: %.200s", raw)
        await redis.rpush(settings.judge_dead_key, raw)
        await redis.lrem(settings.judge_processing_key, 1, raw)
        return

    attempts = await redis.incr(_attempts_key(request.submission_id))
    await redis.expire(_attempts_key(request.submission_id), settings.attempts_ttl_sec)
    if attempts > settings.max_attempts:
        logger.error(
            "Submission #%s exceeded %s attempts → dead-letter",
            request.submission_id, settings.max_attempts,
        )
        await redis.rpush(settings.judge_dead_key, raw)
        await _finish(redis, raw, _internal_failure(request.submission_id))
        return

    try:
        response = await asyncio.to_thread(run_submission, request)
    except Exception:
        logger.exception("run_submission failed for #%s", request.submission_id)
        response = _internal_failure(request.submission_id)
    await _finish(redis, raw, response)


async def recover_orphans(redis: Redis) -> None:
    count = 0
    while await redis.lmove(
        settings.judge_processing_key,
        settings.judge_queue_key,
        src="LEFT",
        dest="LEFT",
    ) is not None:
        count += 1
    if count:
        logger.warning("Recovered %s orphaned submission(s) from processing", count)


async def worker_loop(redis: Redis) -> None:
    while True:
        raw = await redis.blmove(
            settings.judge_queue_key,
            settings.judge_processing_key,
            settings.worker_poll_timeout,
            src="LEFT",
            dest="RIGHT",
        )
        if raw is None:
            continue
        try:
            await handle_one(redis, raw)
        except Exception:
            logger.exception("Unexpected error handling submission")