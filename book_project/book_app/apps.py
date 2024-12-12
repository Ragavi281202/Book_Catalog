from django.apps import AppConfig

class BookAppConfig(AppConfig):
    name = 'book_app'

    def ready(self):
        import book_app.signals