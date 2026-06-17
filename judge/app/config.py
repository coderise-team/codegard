import socket
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    redis_url: str

    # Identity of this worker instance. Defaults to the container hostname so
    # it stays stable across restarts of the same instance; override via env
    # only if the hostname is not unique per worker.
    worker_id: str = Field(default_factory=socket.gethostname)

    judge_queue_key: str = "judge:queue"
    judge_processing_key: str = "judge:processing"
    judge_results_key: str = "judge:results"
    judge_dead_key: str = "judge:dead"

    worker_poll_timeout: int = 5
    worker_backoff_sec: float = 1.0
    max_attempts: int = 3
    attempts_ttl_sec: int = 3600

    @property
    def processing_key(self) -> str:
        """Per-worker in-flight list, so recover_orphans never touches another
        worker's active submissions."""
        return f"{self.judge_processing_key}:{self.worker_id}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
