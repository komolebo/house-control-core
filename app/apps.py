from django.apps import AppConfig

from app.Threads.ThreadMgr import ThreadMgr


class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        print('starting APP')
        ThreadMgr.start_threads()
