from django.apps import AppConfig

class ApplicationConfig(AppConfig):
    name = 'app'
    threads = []

    def ready(self):
        from app.main import main
        main()
