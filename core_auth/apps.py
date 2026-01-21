from django.apps import AppConfig


class CoreAuthConfig(AppConfig):
    """
    Application configuration for the core_auth app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "core_auth"
    verbose_name = "Core Authentication"

    def ready(self):
        """
        Perform initialization when the app is ready.

        This is a good place to import signal handlers.
        """
        pass  # Import signals here if needed in the future
