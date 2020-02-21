import threading


class AppThread(threading.Thread):
    def __init__(self, mbox):
        super().__init__()
        self.mbox = mbox

    def on_message(self, msg, data):
        raise NotImplementedError()

    def run(self):
        while True:
            msg, data = self.mbox.get()
            self.on_message(msg, data)