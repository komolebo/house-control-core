from queue import Queue

class MBox:
    WIFI = 0
    RF = 1


class Dispatcher:
    mbox_table = {}

    @staticmethod
    def create_mbox(mbox_id):
        Dispatcher.mbox_table[mbox_id] = Queue()
        return Dispatcher.mbox_table[mbox_id]

    @staticmethod
    def send_msg(mbox_id, data):
        Dispatcher.mbox_table[mbox_id].put(data)
