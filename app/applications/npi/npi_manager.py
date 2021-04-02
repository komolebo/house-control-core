import serial

from app.applications.npi.npi_reader import NpiReader
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.middleware.threads import AppThread


class NpiManager:
    def __init__(self, tty_port='/dev/ttyUSB1'):
        self.ser = serial.Serial(
            port=tty_port,
            baudrate=115200,
            timeout=0.3
            # parity=serial.PARITY_NONE,
            # stopbits=serial.STOPBITS_ONE,
            # bytesize=serial.EIGHTBITS,
            # timeout=0)
        )
        self.npi_reader = NpiReader(self.ser)

    def listen(self):
        while True:  # always listen
            # npi_msg = self.machine.execute()
            npi_msg = self.npi_reader.read_package()
            print("DUMP RX: ", npi_msg.as_output())
            Dispatcher.send_msg(Messages.NPI_RX_MSG, {'data': npi_msg })

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


class NpiApp(AppThread):
    def __init__(self, mbox):
        super().__init__(mbox)
        self.npi = NpiManager()

        # init central ble host when npi is ready
        Dispatcher.send_msg(Messages.CENTRAL_RESET, {})

    def on_message(self, msg, data):
        if msg is Messages.NPI_SERIAL_PORT_LISTEN:
            self.npi.listen()
