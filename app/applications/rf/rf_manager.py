from app.middleware.threads import AppThread


class RfManager(AppThread):
    def on_message(self, msg, data):
        print("RF received ", msg)
