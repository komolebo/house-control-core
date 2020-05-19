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
            MBox.DEV
        ],

        Messages.DEVICE_LOST_COMM: [
            MBox.DEV
        ],

        Messages.CLEAR_DEVICE_LOST_COMM: [
            MBox.DEV
        ],

        Messages.NPI_SERIAL_PORT_LISTEN: [
            MBox.NPI
        ],

        Messages.NPI_RX_MSG: [
            MBox.DEV
        ],

        Messages.OAD_START: [
            MBox.DEV
        ],
        Messages.OAD_ABORT: [
            MBox.DEV
        ],
        Messages.OAD_COMPLETE: [
            MBox.DEV
        ]
    }


class Validation:
    validation_info = {
        Messages.TEST_MSG: ['id', 'message'],
        Messages.TEST_MSG2: ['id'],
        Messages.SENSOR_REMOVED_FROM_FRONT: ['id'],
        Messages.DEVICE_LOST_COMM: ["id"],
        Messages.CLEAR_DEVICE_LOST_COMM: ["id"],
        Messages.NPI_SERIAL_PORT_LISTEN: [],
        Messages.NPI_RX_MSG: ["data"],
        Messages.OAD_START: [],
        Messages.OAD_ABORT: [],
        Messages.OAD_COMPLETE: []
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
    mbox_num = 0

    @classmethod
    def create_mbox(cls):
        mbox_id = cls.mbox_num
        cls.mbox_num += 1
        cls.mbox_table[mbox_id] = Queue()
        return cls.mbox_table[mbox_id]

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
            print(">> " + Messages.get_name_by_enum_id(msg_id) + " : " + str(data))
            [cls.__put_msg_in_mbox(mbox, (msg_id, data)) for mbox in Subscriptions.subscribers_info[msg_id]]
