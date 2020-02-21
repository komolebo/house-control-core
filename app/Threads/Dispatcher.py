from queue import Queue

from enum import auto, Enum


class MBox:
    WIFI = 0
    RF = 1


class Messages(Enum):
    TEST_MSG = auto()
    TEST_MSG2 = auto()


class Subscriptions:
    subscribers_info = {

        Messages.TEST_MSG: [
            MBox.WIFI,
            MBox.RF
        ],

        Messages.TEST_MSG2: [
            MBox.WIFI,
            MBox.RF
        ]
    }

class Dispatcher:
    mbox_table = {}

    @classmethod
    def create_mbox(cls, mbox):
        cls.mbox_table[mbox] = Queue()
        return cls.mbox_table[mbox]

    @classmethod
    def put_msg_in_mbox(cls, mbox, data):
        cls.mbox_table[mbox].put(data)

    @classmethod
    def send_msg(cls, msg_id, data):
        if msg_id in Subscriptions.subscribers_info:
            [cls.put_msg_in_mbox(mbox, (msg_id, data)) for mbox in Subscriptions.subscribers_info[msg_id]]