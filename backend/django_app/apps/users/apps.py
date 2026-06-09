from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "apps.users"

    def ready(self) -> None:
        import apps.users.signals  # noqa: F401  (registers avatar cleanup signals)
