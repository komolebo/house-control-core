from app.Threads.AppThread import AppThread


class WifiManager(AppThread):
    def on_message(self, msg):
        print("Wifi received ", msg)
