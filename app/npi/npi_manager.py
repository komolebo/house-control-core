import serial


class HciPackageRx:
    HCI_RX_EVENT_BYTE_LEN = 0x02

    def __init__(self, type, code, len, data):
        self.type = type
        self.code = code
        self.len = len
        self.data = data

    def get_event(self):
        if self.data:
            event = self.data[0:self.HCI_RX_EVENT_BYTE_LEN]
            return int.from_bytes(event, byteorder='little', signed=False)
        return None

    def as_output(self):
        str = ""
        str += hex(self.type)
        str += ' '
        str += hex(self.code)
        str += ' '
        str += hex(self.len)
        str += ' '
        for ch in self.data:
            str += hex(ch)
            str += ' '
        return str

    def is_valid(self):
        if not self.len:
            return False
        return True


class State:
    def __init__(self, machine, serial_port):
        self.machine = machine
        self.serial_port = serial_port


class StateReadType(State):
    HCI_TYPE_BYTE_LEN = 1

    def __init__(self, machine, serial_port):
        super().__init__(machine, serial_port)
        self.hci_type = 0

    def execute(self):
        buf = self.serial_port.read(self.HCI_TYPE_BYTE_LEN)
        hci_type = int.from_bytes(buf, byteorder='big', signed=False)
        self.hci_type = hci_type
        self.machine.read_code()


class StateReadCode(State):
    HCI_CODE_BYTE_LEN = 1

    def __init__(self, machine, serial_port):
        super().__init__(machine, serial_port)
        self.hci_code = 0

    def execute(self):
        buf = self.serial_port.read(self.HCI_CODE_BYTE_LEN)
        hci_code = int.from_bytes(buf, byteorder='big', signed=False)
        self.hci_code = hci_code
        self.machine.read_len()


class StateReadLen(State):
    HCI_LEN_BYTE_LEN = 1

    def __init__(self, machine, serial_port):
        super().__init__(machine, serial_port)
        self.msg_len = 0

    def execute(self):
        buf = self.serial_port.read(self.HCI_LEN_BYTE_LEN)
        msg_len = int.from_bytes(buf, byteorder='big', signed=False)
        self.msg_len = msg_len
        self.machine.read_data(msg_len)


class StateReadData(State):
    def __init__(self, machine, serial_port):
        super().__init__(machine, serial_port)
        self.msg_data = None

    def execute(self, len):
        if len:
            data = self.serial_port.read(len)
            self.msg_data = data
        # no other transitions


class Machine:
    def __init__(self, tty_port):
        self.read_type_state = StateReadType(self, tty_port)
        self.read_code_state = StateReadCode(self, tty_port)
        self.read_len_state = StateReadLen(self, tty_port)
        self.read_data_state = StateReadData(self, tty_port)

    def read_type(self):
        self.read_type_state.execute()

    def read_code(self):
        self.read_code_state.execute()

    def read_len(self):
        self.read_len_state.execute()

    def read_data(self, len):
        self.read_data_state.execute(len)

    def start_machine(self):
        self.read_type()

    def execute(self):
        self.start_machine()
        # return HciPackageRx(Machine.hci_type,
        #                     Machine.hci_code,
        #                     Machine.msg_len,
        #                     Machine.msg_data)

        return HciPackageRx(self.read_type_state.hci_type,
                            self.read_code_state.hci_code,
                            self.read_len_state.msg_len,
                            self.read_data_state.msg_data)


class NpiManager:
    def __init__(self, tty_port):
        self.ser = serial.Serial(
            port=tty_port,
            baudrate=115200,
            # parity=serial.PARITY_NONE,
            # stopbits=serial.STOPBITS_ONE,
            # bytesize=serial.EIGHTBITS,
            # timeout=0)
        )
        self.machine = Machine(self.ser)

    def process_next_msg(self):
        return self.machine.execute()

    def send_binary_data(self, byte_array):
        print_msg = ''
        for ch in byte_array:
            print_msg += hex(ch)
            print_msg += ' '
        print("DUMP TX: ", print_msg)
        self.ser.write(byte_array)

    def send_msg(self, hci_msg):
        msg = bytearray()
        msg.append(hci_msg.type)
        msg.append(hci_msg.code)
        msg.append(hci_msg.msg_len)
        if hci_msg.msg_len:
            msg += bytearray(hci_msg.msg_data)
        self.ser.write(msg)
