from django.apps import AppConfig

from app.Threads.Dispatcher import Dispatcher, MBox
from app.Threads.ThreadMgr import ThreadMgr


class ApplicationConfig(AppConfig):
    name = 'app'

    def ready(self):
        ThreadMgr.start_threads()
