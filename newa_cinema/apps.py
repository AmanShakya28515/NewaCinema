from django.apps import AppConfig

class NewaCinemaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newa_cinema'

    def ready(self):
        import newa_cinema.signals  # Import signals here
