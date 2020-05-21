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

# Central reset-init-adjust section
        Messages.CENTRAL_RESET: [
            MBox.DEV
        ],
        Messages.CENTRAL_RESET_RESP: [
            MBox.DEV
        ],
        Messages.CENTRAL_INIT: [
            MBox.DEV
        ],
        Messages.CENTRAL_INIT_RESP: [
            MBox.DEV
        ],
        Messages.CENTRAL_ADJUST: [
            MBox.DEV
        ],
        Messages.CENTRAL_ADJUST_RESP: [
            # TODO: front, system
            MBox.DEV
        ],

# OAD section
        Messages.OAD_START: [
            MBox.DEV
        ],
        Messages.OAD_ABORT: [
            MBox.DEV
        ],
        Messages.OAD_COMPLETE: [
            # TODO: front
        ],

# Scan section
        Messages.SCAN_DEVICE: [
            MBox.DEV
        ],
        Messages.SCAN_DEVICE_ABORT: [
            MBox.DEV
        ],
        Messages.SCAN_DEVICE_RESP: [
            # TODO: front
        ],

# Establish connection section
        Messages.ESTABLISH_CONN: [
            MBox.DEV
        ],
        Messages.ESTABLISH_CONN_ABORT: [
            MBox.DEV
        ],
        Messages.ESTABLISH_CONN_RESP: [
            # TODO: front
        ],

# Discovery section
        Messages.DEV_SVC_DISCOVER: [
            MBox.DEV
        ],
        Messages.DEV_SVC_DISCOVER_RESP: [
            # TODO: front
        ],
        Messages.DEV_CHAR_DISCOVER: [
            MBox.DEV
        ],
        Messages.DEV_CHAR_DISCOVER_RESP: [
            # TODO: front
        ],

# Terminate connection section
        Messages.TERMINATE_CONN: [
            MBox.DEV
        ],
        Messages.TERMINATE_CONN_RESP: [
            # TODO: front
        ],
        Messages.DEVICE_DISCONN: [
            MBox.DEV
            # TODO: front
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
        Messages.CENTRAL_RESET: [],
        Messages.CENTRAL_RESET_RESP: ["status"],
        Messages.CENTRAL_INIT: [],
        Messages.CENTRAL_INIT_RESP: ["central_ip", "status"],
        Messages.CENTRAL_ADJUST: [],
        Messages.CENTRAL_ADJUST_RESP: ["status"],
        Messages.OAD_START: [],
        Messages.OAD_ABORT: [],
        Messages.OAD_COMPLETE: ["status"],
        Messages.SCAN_DEVICE: [],
        Messages.SCAN_DEVICE_ABORT: [],
        Messages.SCAN_DEVICE_RESP: ["data", "status"],
        Messages.ESTABLISH_CONN: ["data"],
        Messages.ESTABLISH_CONN_ABORT: [],
        Messages.ESTABLISH_CONN_RESP: ["data", "status"],
        Messages.TERMINATE_CONN: ["conn_handle"],
        Messages.TERMINATE_CONN_RESP: ["status"],
        Messages.DEVICE_DISCONN: ["conn_handle", "reason"],
        Messages.DEV_SVC_DISCOVER: ["conn_handle"],
        Messages.DEV_SVC_DISCOVER_RESP: ["conn_handle", "services", "status"],
        Messages.DEV_CHAR_DISCOVER: ["conn_handle"],
        Messages.DEV_CHAR_DISCOVER_RESP: ["conn_handle", "chars", "status"]
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
