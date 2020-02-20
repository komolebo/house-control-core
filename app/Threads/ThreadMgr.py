import threading

from app.RfManager.RfManager import RfManager
from app.Threads.Dispatcher import Dispatcher, MBox
from app.WifiManager.WifiManager import WifiManager
from house_control.settings import *


# register here new threads
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



