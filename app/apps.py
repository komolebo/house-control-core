from django.apps import AppConfig

from app.middleware.dispatcher import Dispatcher, MBox
from app.middleware.messages import Messages
from app.applications.rf.rf_manager import RfManager
from app.applications.wifi.wifi_manager import WifiManager
from house_control.settings import THREAD__WIFI_MNGR, THREAD__RF_MNGR


THREAD_CFG = [
    (THREAD__WIFI_MNGR, WifiManager, MBox.WIFI),
    (THREAD__RF_MNGR, RfManager, MBox.RF),
]


class ThreadMgr:
    threads = []

    @staticmethod
    def start_threads():
        print("starting the threads ", THREAD_CFG)
        for (enabled, app_thread, mbox_id) in THREAD_CFG:
            if enabled:
                mbox = Dispatcher.create_mbox(mbox_id)
                t = app_thread(mbox)
                t.setDaemon(True)
                t.start()
                ThreadMgr.threads.append(t)


class ApplicationConfig(AppConfig):
    name = 'app'

    def ready(self):
        ThreadMgr.start_threads()
        Dispatcher.send_msg(Messages.TEST_MSG, "test msg")
