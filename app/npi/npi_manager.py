import serial

print("yahoo")


class HciPackageRx:
    HCI_RX_EVENT_BYTE_LEN = 0x02

    def __init__(self, type = 0x0, code = 0x0, len = 0x0, data=None):
        self.type = type
        self.code = code
        self.len = len
        self.data = data

    def get_event(self):
        return self.data[0:self.HCI_RX_EVENT_BYTE_LEN]

    def is_valid(self):
        if not self.len:
            return False
        return True


class State:
    def __init__(self, machine, serial_port):
        self.machine = machine
        self.serial_port = serial_port


class StateReadType(State):
    HCI_TYPE_BYTE_LEN = 2

    def __init__(self, machine, serial_port):
        super().__init__(machine, serial_port)

    def execute(self):
        hci_type = self.serial_port.read(self.HCI_TYPE_BYTE_LEN)
        self.machine.hci_type = hci_type
        self.machine.read_code()


class StateReadCode(State):
    HCI_CODE_BYTE_LEN = 2

    def __init__(self, machine, serial_port):
        super().__init__(machine, serial_port)

    def execute(self):
        hci_code = self.serial_port.read(self.HCI_CODE_BYTE_LEN)
        self.machine.hci_code = hci_code
        self.machine.read_len()


class StateReadLen(State):
    HCI_LEN_BYTE_LEN = 1

    def __init__(self, machine, serial_port):
        super().__init__(machine, serial_port)

    def execute(self):
        msg_len = self.serial_port.read(self.HCI_LEN_BYTE_LEN)
        self.machine.msg_len = msg_len
        self.machine.read_data()


class StateReadData(State):
    def __init__(self, machine, serial_port):
        super().__init__(machine, serial_port)

    def execute(self):
        if self.machine.msg_len:
            data = self.serial_port.read(self.machine.msg_len)
            self.machine.msg_data = data
        # no other transitions


class Machine:
    hci_type = 0
    hci_code = 0
    msg_len = 0
    msg_data = None

    def __init__(self, tty_port):
        self.read_type_state = StateReadType(self, tty_port)
        self.read_code_state = StateReadCode(self, tty_port)
        self.read_len_state = StateReadLen(self, tty_port)
        self.read_data_state = StateReadData(self, tty_port)

    def read_type(self):
        self.read_code_state.execute()

    def read_code(self):
        self.read_code_state.execute()

    def read_len(self):
        self.read_len_state.execute()

    def read_data(self):
        self.read_data_state.execute()

    def start_machine(self):
        self.read_type()

    def execute(self):
        self.start_machine()
        return HciPackageRx(Machine.hci_type,
                            Machine.hci_code,
                            Machine.msg_len,
                            Machine.msg_data)


class NpiManager:
    def __init__(self, tty_port):
        self.ser = serial.Serial(
            port=tty_port,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0)
        self.machine = Machine(self.ser)

    def process_next_msg(self):
        return self.machine.execute()

    def send_binary_data(self, byte_array):
        self.ser.write(byte_array)

    def send_msg(self, hci_msg):
        msg = bytearray()
        msg.append(hci_msg.type)
        msg.append(hci_msg.code)
        msg.append(hci_msg.msg_len)
        if hci_msg.msg_len:
            msg += bytearray(hci_msg.msg_data)
        self.ser.write(msg)
