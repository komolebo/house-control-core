from threading import Timer

from app.applications.npi.hci_types import HciPackageRx


class State:
    def __init__(self, machine, serial_port):
        self.machine = machine
        self.serial_port = serial_port


class NpiReader:
    HCI_TYPE_BYTE_LEN = 1
    HCI_CODE_BYTE_LEN = 1
    HCI_LEN_BYTE_LEN = 1
    READ_TIMEOUT_SEC = 0.3

    def __init__(self, serial):
        self.serial = serial
        self.data_reader = serial.read
        self.read_enable = True

    def cancel_read(self):
        self.read_enable = False
        self.serial.cancel_read()

    def read_package(self):
        while True:
            timeout_handler = Timer(self.READ_TIMEOUT_SEC, self.cancel_read)
            timeout_handler.start()
            type = self.read_type()
            code = self.read_code()
            data_len = self.read_len()
            data = self.read_data(data_len)

            if self.read_enable:
                timeout_handler.cancel()
                return HciPackageRx(type,
                                    code,
                                    data_len,
                                    data)
            else:
                # try to read again on next cycle
                self.read_enable = True

    def read_type(self):
        if self.read_enable:
            buf = self.data_reader(self.HCI_TYPE_BYTE_LEN)
            # print('hci_type: {}'.format(hci_type))
            return int.from_bytes(buf, byteorder='big', signed=False)

    def read_code(self):
        if self.read_enable:
            buf = self.data_reader(self.HCI_CODE_BYTE_LEN)
            return int.from_bytes(buf, byteorder='big', signed=False)

    def read_len(self):
        if self.read_enable:
            buf = self.data_reader(self.HCI_CODE_BYTE_LEN)
            return int.from_bytes(buf, byteorder='big', signed=False)

    def read_data(self, data_len):
        if self.read_enable:
            if data_len:
                return self.data_reader(data_len)
