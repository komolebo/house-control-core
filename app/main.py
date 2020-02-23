from app.applications.devices.devices import DevManager
from app.middleware.dispatcher import Dispatcher, MBox
from app.middleware.messages import Messages
from app.applications.rf.rf_manager import RfManager
from app.applications.wifi.wifi_manager import WifiManager
from house_control.settings import THREAD__WIFI_MNGR, THREAD__RF_MNGR, THREAD__DEV_MNGR


THREAD_CFG = [
    (THREAD__WIFI_MNGR, WifiManager, MBox.WIFI),
    (THREAD__RF_MNGR, RfManager, MBox.RF),
    (THREAD__DEV_MNGR, DevManager, MBox.DEV_HANDLER),
]


def main():
    threads = []

    print("starting the threads ", THREAD_CFG)
    for (enabled, app_thread, mbox_id) in THREAD_CFG:
        if enabled:
            mbox = Dispatcher.create_mbox(mbox_id)
            t = app_thread(mbox)
            t.setDaemon(True)
            t.start()
            threads.append(t)

    Dispatcher.send_msg(Messages.TEST_MSG, {"message": "test msg"})
