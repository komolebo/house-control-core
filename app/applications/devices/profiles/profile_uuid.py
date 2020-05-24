class ServiceUuid:
    LED = 0x1110
    BUTTON = 0x1120
    DATA = 0x1130
    CONFIG = 0x1140
    TAMPER = 0x1150


class UuidData:
    def __init__(self, uuid, length, fixed_len=True):
        self.uuid = uuid
        self.length = length
        self.fixed_len = fixed_len


class CharUuid:
# Gatt general UUIDs
    GATT_CHAR_DECL_UUID = 0x2803
    GATT_PRIM_SERV_DECL_UUID = 0x2800
    GATT_CHAR_DESC_UUID = 0x2901
    GATT_CCC_UUID = 0x2902

# Generic device UUIDs
    APPEARANCE_UUID = 0x2A01
    PREFER_CONN_PARAM_UUID = 0x2A04
    SYSTEM_ID_UUID = 0x2A23
    SERIAL_NUM_UUID = 0x2A23

    DEVICE_NAME = UuidData(0x2A00, 21, fixed_len=False)

    BATTERY_LEVEL = UuidData(0x2A19, 1)

# Custom device UUIDs
#     LS_LED1_UUID = 0x1112
#     LS_LED1_LEN = 1
    LS_LED = UuidData(0x1112, 1)

    # BS_BUTTON0_UUID = 0x1121
    # BS_BUTTON0_LEN = 1
    BS_BUTTON0 = UuidData(0x1121, 1)

    # BS_BUTTON1_UUID = 0x1122
    # BS_BUTTON1_LEN = 1
    BS_BUTTON1 = UuidData(0x1122, 1)

    # DS_STATE_UUID = 0x1131
    # DS_STATE_LEN = 1
    DS_STATE = UuidData(0x1131, 1)

    # CS_STATE_UUID = 0x1141
    # CS_STATE_LEN = 1
    CS_STATE = UuidData(0x1141, 1)

    # CS_MODE_UUID = 0x1142
    # CS_MODE_LEN = 1
    CS_MODE = UuidData(0x1142, 1)

    # CS_SENSITIVITY_UUID = 0x1143
    # CS_SENSITIVITY_LEN = 1
    CS_SENSITIVITY = UuidData(0x1143, 1)

    # CS_LED_UUID = 0x1144
    # CS_LED_LEN = 1
    CS_LEN = UuidData(0x1144, 1)

    # TS_STATE_UUID = 0x1151
    # TS_STATE_LEN = 1
    TS_STATE = UuidData(0x1151, 1)

    @classmethod
    def get_data_obj_by_uuid(cls, uuid):
        for uuid_object_name in cls.__dict__.keys():
            uuid_obj = cls.__dict__[uuid_object_name]
            if isinstance(uuid_obj, UuidData) and uuid_obj.uuid == uuid:
                return uuid_obj
        return None
