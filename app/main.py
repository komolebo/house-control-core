from app.applications.devices.device_manager import DeviceApp
from app.applications.frontier.front_manager import FrontierApp
from app.applications.npi.npi_manager import NpiApp
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.applications.rf.rf_manager import RfManager
from app.applications.wifi.wifi_manager import WifiManager
from house_control.settings import THREAD__WIFI_MNGR, THREAD__RF_MNGR, THREAD__DEV_APP, THREAD__NPI_APP, \
    THREAD__FRONTIER_APP

THREAD_CFG = [
    (THREAD__WIFI_MNGR, WifiManager),
    (THREAD__RF_MNGR, RfManager),
    (THREAD__DEV_APP, DeviceApp),
    (THREAD__NPI_APP, NpiApp),
    (THREAD__FRONTIER_APP, FrontierApp)
]


def main():
    threads = []

    print("starting the threads ", THREAD_CFG)
    for (enabled, app_thread) in THREAD_CFG:
        if enabled:
            mbox = Dispatcher.create_mbox()
            t = app_thread(mbox)
            t.setDaemon(True)
            t.start()
            threads.append(t)

        Dispatcher.send_msg(Messages.TEST_MSG, {"message": "test msg", "id": 0})
        Dispatcher.send_msg(Messages.NPI_SERIAL_PORT_LISTEN, {})
