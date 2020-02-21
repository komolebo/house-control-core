from time import sleep

from app.middleware.threads import AppThread
from house_control.events import send_notification_to_front, Notifications


class WifiManager(AppThread):
    def on_message(self, msg, data):
        print("Wifi received ", msg)
        while True:
            sleep(6)
            print("awakened")
            send_notification_to_front(Notifications.SENSOR_LIST_CHANGED, {1: "1", 2: "2"})
