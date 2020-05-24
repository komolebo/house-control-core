from app.applications.devices.conn_info import CharValueData
from app.applications.devices.profiles.profile_uuid import CharUuid
from app.middleware.messages import Messages


class DeviceTypeInfo:
    motion = "motion"
    gas = "gas"


class TamperData:
    TAMPER_SET = 0x01
    TAMPER_RELEASED = 0x00
    TAMPER_UNDEFINED = 0xFF

    def __init__(self, tamper_state=TAMPER_UNDEFINED):
        self.__tamper_state = tamper_state

    @property
    def tamper_state(self):
        return self.__tamper_state

    @tamper_state.setter
    def tamper_state(self, tamper_state):
        if isinstance(tamper_state, bytes):
            tamper_state = int.from_bytes(tamper_state, byteorder='little')

        if tamper_state in (self.TAMPER_SET, self.TAMPER_RELEASED):
            self.__tamper_state = tamper_state
        else:
            self.__tamper_state = self.TAMPER_UNDEFINED
        print('Update tamper value', tamper_state)


class DeviceData:
    STATE_ENABLED = 0x01
    STATE_DISABLED = 0x00
    STATE_UNDEFINED = 0xFF

    def __init__(self, dev_type, name, state=STATE_UNDEFINED, battery_level=100):
        self.dev_type = dev_type
        self.__state = state
        self.__batt_level = battery_level
        self.name = name

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        if isinstance(state, bytes):
            state = int.from_bytes(state, byteorder='little')
        self.__state = state
        print('Update state value', state)

    @property
    def batt_level(self):
        return self.__batt_level

    @batt_level.setter
    def batt_level(self, batt_level):
        if isinstance(batt_level, bytes):
            batt_level = int.from_bytes(batt_level, byteorder='little')

        if batt_level > 100:
            self.__batt_level = 100
        elif batt_level < 0:
            self.__batt_level = 0
        else:
            self.__batt_level = batt_level
        print('Update battery value', batt_level)


class MotionData(DeviceData, TamperData):
    def __init__(self, name, state=None, battery_level=None):
        DeviceData.__init__(self, DeviceTypeInfo.motion, name, state, battery_level)
        self.__detect_state = None

    @property
    def detect_state(self):
        return self.__detect_state

    @detect_state.setter
    def detect_state(self, detect_state):
        if isinstance(detect_state, bytes):
            detect_state = int.from_bytes(detect_state, byteorder='little')
        self.__detect_state = detect_state
        print('Update detect value', detect_state)


class DeviceDataHandler:
    def __init__(self, disc_handler, send_response):
        self.disc_handler = disc_handler
        self.send_response = send_response
        self.device_info = {}

    def add_device(self, conn_handle, dev_type, name):
        if conn_handle in self.device_info.keys():
            print('Device already added!')
        if dev_type == DeviceTypeInfo.motion:
            self.device_info[conn_handle] = MotionData(name)

    def process_data_change(self, conn_handle, handle, value):
        if conn_handle not in self.device_info.keys():
            self.send_response(msg=Messages.ERR_DEV_CONN_NOT_EXIST,
                               data={"conn_handle": conn_handle})
            return
        data_uuid = self.disc_handler.get_uuid_by_handle(conn_handle, handle)
        if data_uuid == CharUuid.CS_MODE.uuid:
            self.device_info[conn_handle].state = value
        elif data_uuid == CharUuid.DS_STATE.uuid:
            self.device_info[conn_handle].detect_state = value
        elif data_uuid == CharUuid.BATTERY_LEVEL.uuid:
            self.device_info[conn_handle].batt_level = value
        elif data_uuid == CharUuid.TS_STATE.uuid:
            self.device_info[conn_handle].tamper_state = value
        elif data_uuid == CharUuid.DEVICE_NAME:
            # TODO: handle device name
            pass

    def process_val_disc_resp(self, conn_handle, char_value_data):
        if conn_handle not in self.device_info.keys():
            self.send_response(msg=Messages.ERR_DEV_CONN_NOT_EXIST,
                               data={"conn_handle": conn_handle})
            return
        for char_val_item in char_value_data:
            if isinstance(char_val_item, CharValueData):
                self.process_data_change(conn_handle, char_val_item.handle, char_val_item.value)
