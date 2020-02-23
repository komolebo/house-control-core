from queue import Queue

from app.middleware.mailbox import MBox
from app.middleware.messages import Messages


class Subscriptions:
    subscribers_info = {

        Messages.TEST_MSG: [
            MBox.WIFI,
            MBox.RF
        ],

        Messages.TEST_MSG2: [
            MBox.WIFI,
            MBox.RF
        ],

        Messages.SENSOR_REMOVED_FROM_FRONT: [
            MBox.DEV_HANDLER
        ],

        Messages.DEVICE_LOST_COMM: [
            MBox.DEV_HANDLER
        ],

        Messages.CLEAR_DEVICE_LOST_COMM: [
            MBox.DEV_HANDLER
        ]
    }


class Validation:
    validation_info = {
        Messages.TEST_MSG: ['id', 'message'],
        Messages.TEST_MSG2: ['id'],
        Messages.SENSOR_REMOVED_FROM_FRONT: ['id'],
        Messages.DEVICE_LOST_COMM: ["id"],
        Messages.CLEAR_DEVICE_LOST_COMM: ["id"]
    }

    @classmethod
    def is_msg_data_valid(cls, msg_id, data):
        if type(data) is not dict:
            raise Exception("Message {} type is not dictionary".format(msg_id))
        if msg_id not in cls.validation_info.keys():
            raise Exception("Message {} is not defined in validation".format(msg_id))
        return set(data).issubset(set(cls.validation_info[msg_id]))


class Dispatcher:
    mbox_table = {}

    @classmethod
    def create_mbox(cls, mbox):
        cls.mbox_table[mbox] = Queue()
        return cls.mbox_table[mbox]

    @classmethod
    def __put_msg_in_mbox(cls, mbox_id, data):
        if mbox_id not in cls.mbox_table.keys():
            mbox_name = MBox.get_name_by_enum_id(mbox_id)
            print("::: Mbox {} not registered, message is going to be ignored".format(mbox_name))
            return
        cls.mbox_table[mbox_id].put(data)

    @classmethod
    def send_msg(cls, msg_id, data):
        if not Validation.is_msg_data_valid(msg_id, data):
            msg_name = Messages.get_name_by_enum_id(msg_id)
            raise Exception("Message {} is not validated, incorrect keys detected".format(msg_name))

        if msg_id in Subscriptions.subscribers_info:
            [cls.__put_msg_in_mbox(mbox, (msg_id, data)) for mbox in Subscriptions.subscribers_info[msg_id]]
