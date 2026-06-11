from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    redis_url: str

    judge_queue_key: str = "judge:queue"
    judge_processing_key: str = "judge:processing"
    judge_results_key: str = "judge:results"
    judge_dead_key: str = "judge:dead"

    worker_poll_timeout: int = 5
    max_attempts: int = 3
    attempts_ttl_sec: int = 3600


settings = Settings()
