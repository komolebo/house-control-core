from time import sleep

from app.Threads.AppThread import AppThread
from house_control.events import send_event_to_front, Notification


class WifiManager(AppThread):
    def on_message(self, msg):
        print("Wifi received ", msg)

        sleep(12)
        print("awakened")
        send_event_to_front(Notification.SENSOR_LIST_CHANGED)
