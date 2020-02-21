from app.middleware.AppThread import AppThread


class RfManager(AppThread):
    def on_message(self, msg, data):
        print("RF received ", msg)
