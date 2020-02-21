from django.apps import AppConfig

from app.middleware.Dispatcher import Dispatcher, MBox
from app.middleware.ThreadMgr import ThreadMgr


class ApplicationConfig(AppConfig):
    name = 'app'

    def ready(self):
        ThreadMgr.start_threads()
        Dispatcher.send_msg(MBox.WIFI, "wifi msg")
