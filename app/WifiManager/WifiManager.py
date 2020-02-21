from time import sleep

from app.middleware.AppThread import AppThread
from house_control.events import send_event_to_front, Notifications


class WifiManager(AppThread):
    def on_message(self, msg, data):
        print("Wifi received ", msg)
        while True:
            sleep(12)
            print("awakened")
            send_event_to_front(Notifications.SENSOR_LIST_CHANGED)
