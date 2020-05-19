from mailbox import Message
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
            sleep(3)
            print("awakened")
            send_notification_to_front(Notifications.SENSOR_LIST_CHANGED, {1: "1", 2: "2"})

            # if count == 2:
            #     print ('OAD START')
            #     Dispatcher.send_msg(Messages.OAD_START, {})

            if count == 0:
                print ('SCAN START')
                Dispatcher.send_msg(Messages.SCAN_DEVICE_REQ, {})

            count += 1
