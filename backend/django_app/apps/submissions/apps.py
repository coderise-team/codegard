from django.apps import AppConfig


class SubmissionsConfig(AppConfig):
    name = "apps.submissions"

    def ready(self) -> None:
        from . import signals  # noqa: F401
