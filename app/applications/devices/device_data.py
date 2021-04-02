from django.forms import model_to_dict

from app.applications.devices.conn_info import DevConnDataHandler
from app.models.models import Sensor


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


class DeviceProfileData:
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


class MotionData(DeviceProfileData, TamperData):
    def __init__(self, name, state=None, battery_level=None):
        DeviceProfileData.__init__(self, DeviceTypeInfo.motion, name, state, battery_level)
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


class DevDataHandler:
    devices = []
    to_update_d = {}

    @classmethod
    def __init__(cls):
        cls.devices = Sensor.objects.all()

    @classmethod
    def _data_wrapper(cls, obj):
        obj = model_to_dict(obj)
        obj['active'] = DevConnDataHandler.is_mac_active(obj['mac'])
        obj['to_update'] = True if obj['mac'] in cls.to_update_d.keys() else False
        return obj

    @classmethod
    def get_dev(cls, _mac, _serializable=False):
        obj = next(x for x in cls.devices if x.mac == _mac)
        return cls._data_wrapper(obj) if _serializable else obj

    @classmethod
    def get_dev_list(cls, _serializable=False):
        return [cls._data_wrapper(x) if _serializable else x for x in cls.devices]

    @classmethod
    def read_dev(cls, _mac, _serializable=False):
        obj = Sensor.objects.get(mac=_mac)
        return cls._data_wrapper(obj) if _serializable else obj

    @classmethod
    def read_all_dev(cls, _serializable=False):
        cls.devices = Sensor.objects.all()
        return [cls._data_wrapper(x) if _serializable else x for x in cls.devices]

    @classmethod
    def add_dev(cls, _mac, _name, _type, _location):
        if not Sensor.objects.filter(mac=_mac).exists():
            dev = Sensor(name = _name,
                         type = _type,
                         location = _location,
                         mac = _mac)
            dev.save()
            cls.read_all_dev()

    @classmethod
    def upd_dev(cls, _mac, _name=None, _location=None, _state=None):
        dev = Sensor.objects.get(mac=_mac)
        dev.location = dev.location if _location is None else _location
        dev.name = dev.name if _name is None else _name
        dev.state = dev.state if _state is None else _state
        dev.save()
        cls.read_all_dev()

    @classmethod
    def rem_dev(cls, _mac):
        filtered = Sensor.objects.filter(mac=_mac)
        if isinstance(filtered, list):
            [device.delete() for device in filtered]  # in case of several devices with same MAC
        else:
            filtered.delete()
        if _mac in cls.to_update_d.keys():
            cls.to_update_d.pop(_mac)
        cls.read_all_dev()

    @classmethod
    def upd_dev_tamper(cls, _mac, _tamper):
        dev = next(x for x in cls.devices if x.mac == _mac)
        dev.tamper = int.from_bytes(_tamper, byteorder='little') > 0
        dev.save()

    @classmethod
    def upd_dev_state(cls, _mac, _state):
        dev = next(x for x in cls.devices if x.mac == _mac)
        dev.state = int.from_bytes(_state, byteorder='little') > 0
        dev.save()

    @classmethod
    def upd_dev_status(cls, _mac, _status):
        dev = next(x for x in cls.devices if x.mac == _mac)
        dev.status = int.from_bytes(_status, byteorder='little') > 0
        dev.save()

    @classmethod
    def upd_dev_battery(cls, _mac, _battery):
        dev = next(x for x in cls.devices if x.mac == _mac)
        _battery = int.from_bytes(_battery, byteorder='little')
        dev.battery = 100 if _battery > 100 else _battery
        dev.save()

    @classmethod
    def set_dev_to_update(cls, _mac, _to_update, _file_path = None):
        if _to_update and _file_path:
            cls.to_update_d[_mac] = _file_path
        elif _mac in cls.to_update_d.keys():
            cls.to_update_d.pop(_mac)
