from app.applications.devices.profiles.profile_uuid import CharUuid
from app.middleware.messages import Messages


class DeviceType:
    motion = "motion"
    gas = "gas"


class DeviceConnData:
     def __init__(self, dev_type, services, chars):
        self.dev_type = dev_type
        self.services = services
        self.chars = chars


class TamperData:
    TAMPER_SET = 0x01
    TAMPER_RELEASED = 0x00
    TAMPER_UNDEFINED = 0xFF

    def __init__(self, tamper_state=TAMPER_UNDEFINED):
        self.tamper_state = tamper_state

    @property
    def tamper_state(self):
        return self.tamper_state

    @tamper_state.setter
    def tamper_state(self, tamper_state):
        if tamper_state in (self.TAMPER_SET, self.TAMPER_RELEASED):
            self.tamper_state = tamper_state
        else:
            self.tamper_state = self.TAMPER_UNDEFINED


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
        self.__state = state

    @property
    def batt_level(self):
        return self.__batt_level

    @batt_level.setter
    def batt_level(self, batt_level):
        if batt_level > 100:
            self.__batt_level = 100
        elif batt_level < 0:
            self.__batt_level = 0
        else:
            self.__batt_level = batt_level


class MotionData(DeviceData, TamperData):
    def __init__(self, dev_type, name, state, battery_level):
        DeviceData.__init__(self, dev_type, name, state, battery_level)
        self.__detect_state = None

    @property
    def detect_state(self):
        return self.__detect_state

    @detect_state.setter
    def detect_state(self, detect_state):
        self.__detect_state = detect_state


class DeviceDataHandler:
    def __init__(self, disc_handler, send_response):
        self.disc_handler = disc_handler
        self.send_response = send_response
        self.device_info = {}

    def add_device(self, conn_handle, dev_type, name):
        if conn_handle in self.device_info.keys():
            print('Device already added!')
        self.device_info[conn_handle] = DeviceData(dev_type, name)

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
