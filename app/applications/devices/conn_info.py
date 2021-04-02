from app.applications.npi.hci_types import Constants


class TypeConnHdlData:
     def __init__(self, dev_type, services, chars):
        self.dev_type = dev_type
        self.services = services
        self.chars = chars


class CharData:
    def __init__(self, handle, uuid, byte_format=True):
        if byte_format:
            self.handle = int.from_bytes(handle, byteorder="little")
            if len(uuid) == Constants.UUID_16BIT_IN_BYTES:
                self.uuid = int.from_bytes(uuid, byteorder="little")
            else:
                # just keep as 16 byte array
                self.uuid = uuid
        else:
            self.handle = handle
            self.uuid = uuid


class CharValueData(CharData):
    def __init__(self, handle, uuid, value):
        super().__init__(handle, uuid, byte_format=False)
        self.value = value


class DevConnDataHandler:
    dev_conn_info = {}  # key -> handle
                        # value -> MAC
    @classmethod
    def add_conn_info(cls, _handle, _mac):
        if isinstance(_mac, (bytes, bytearray)):
            _mac = str(bytes(_mac).hex())
        if _handle in cls.dev_conn_info.keys():
            raise Exception("Connection handle {} is already established".format(_handle))
        cls.dev_conn_info[_handle] = _mac

    @classmethod
    def del_conn_info(cls, _conn_handle=None, _mac=None):
        if _conn_handle is not None and _conn_handle in cls.dev_conn_info.keys():
            cls.dev_conn_info.pop(_conn_handle)
        elif _mac:
            cls.dev_conn_info = {hdl:mac for hdl,mac in cls.dev_conn_info.items() if mac != _mac}

    @classmethod
    def get_handle_by_mac(cls, _mac):
        for handle, mac in cls.dev_conn_info.items():
            if mac == _mac:
                return handle
        return None

    @classmethod
    def get_mac_by_handle(cls, _handle):
        return cls.dev_conn_info[_handle] if _handle in cls.dev_conn_info.keys() else None

    @classmethod
    def is_mac_active(cls, _mac):
        return cls.get_handle_by_mac(_mac) is not None