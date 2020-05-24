from app.applications.npi.hci_types import Constants


class DeviceConnData:
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
