import threading


class AppThread(threading.Thread):
    def __init__(self, mbox):
        super().__init__()
        self.mbox = mbox

    def on_message(self, msg):
        raise NotImplementedError()

    def run(self):
        while True:
            msg = self.mbox.get()
            self.on_message(msg)