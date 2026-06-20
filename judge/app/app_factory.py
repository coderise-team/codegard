import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.redis_client import create_redis
from app.worker import recover_orphans, worker_loop

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = create_redis()
    await recover_orphans(redis)
    task = asyncio.create_task(worker_loop(redis))
    app.state.worker_task = task
    logger.info("Judge worker started")
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await redis.aclose()
        logger.info("Judge worker stopped")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    @app.get("/health")
    def health():
        task = getattr(app.state, "worker_task", None)
        if task is None or task.done():
            return JSONResponse(status_code=503, content={"status": "down"})
        return {"status": "ok"}

    return app
