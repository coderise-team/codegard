from unittest.mock import AsyncMock, patch

from schemas.request import LanguageEnum, SubmissionRequest
from schemas.response import SubmissionResponse, VerdictEnum

from app.config import Settings
from app.worker import handle_one, recover_orphans

VALID_RAW = SubmissionRequest(
    submission_id=1,
    language=LanguageEnum.PYTHON,
    code="print(1)",
    time_limit_ms=1000,
    memory_limit_mb=128,
    test_cases=[],
).model_dump_json()


def _redis():
    r = AsyncMock()
    r.incr.return_value = 1
    return r


@patch("app.worker.run_submission")
async def test_success_pushes_result_and_clears_processing(mock_run):
    mock_run.return_value = SubmissionResponse(submission_id=1, verdict=VerdictEnum.AC)
    redis = _redis()

    await handle_one(redis, VALID_RAW)

    redis.rpush.assert_awaited_once()
    assert "judge:results" in redis.rpush.await_args.args[0]
    redis.lrem.assert_awaited_once()


@patch("app.worker.run_submission")
async def test_malformed_payload_dead_letters_and_does_not_run(mock_run):
    redis = _redis()

    await handle_one(redis, "{not json")

    mock_run.assert_not_called()
    pushed_keys = [c.args[0] for c in redis.rpush.await_args_list]
    assert any("judge:dead" in k for k in pushed_keys)
    assert all("judge:results" not in k for k in pushed_keys)


@patch("app.worker.run_submission", side_effect=RuntimeError("docker boom"))
async def test_run_failure_yields_terminal_result(mock_run):
    redis = _redis()

    await handle_one(redis, VALID_RAW)

    assert any("judge:results" in c.args[0] for c in redis.rpush.await_args_list)
    redis.lrem.assert_awaited()


@patch("app.worker.run_submission")
async def test_poison_pill_dead_letters_after_max_attempts(mock_run):
    redis = _redis()
    redis.incr.return_value = 99

    await handle_one(redis, VALID_RAW)

    mock_run.assert_not_called()
    assert any("judge:dead" in c.args[0] for c in redis.rpush.await_args_list)


async def test_recover_orphans_requeues_until_empty():
    redis = AsyncMock()
    redis.lmove.side_effect = [VALID_RAW, VALID_RAW, None]

    await recover_orphans(redis)

    assert redis.lmove.await_count == 3


def test_processing_key_is_namespaced_per_worker():
    a = Settings(redis_url="redis://x", worker_id="worker-a")
    b = Settings(redis_url="redis://x", worker_id="worker-b")

    assert a.processing_key == "judge:processing:worker-a"
    assert a.processing_key != b.processing_key
