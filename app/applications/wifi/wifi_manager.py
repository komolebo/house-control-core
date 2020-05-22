from time import sleep

from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.middleware.threads import AppThread
from house_control.events import send_notification_to_front, Notifications


class WifiManager(AppThread):
    def on_message(self, msg, data):
        print("Wifi received ", msg)

        count = 0
        while True:
            sleep(6)
            print("awakened")
            send_notification_to_front(Notifications.SENSOR_LIST_CHANGED, {1: "1", 2: "2"})

            if count == 0:
                Dispatcher.send_msg(Messages.CENTRAL_RESET, {})

            # if count == 2:
            #     Dispatcher.send_msg(Messages.SCAN_DEVICE, {})

            if count == 1:
                Dispatcher.send_msg(Messages.ESTABLISH_CONN, {'mac': [0xD1, 0x35, 0xDA, 0xF2, 0xF8, 0xF0],
                                                              'type': "motion"})

            # if count == 4:
            #     Dispatcher.send_msg(Messages.DEV_SVC_DISCOVER, {"conn_handle": 0})
            # if count == 6:
            #     Dispatcher.send_msg(Messages.TERMINATE_CONN, {"conn_handle": 0})

            # if count == 4:
            #     print ('OAD START')
            #     Dispatcher.send_msg(Messages.OAD_START, {})

            count += 1
