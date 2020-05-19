from app.applications.devices.blenet.scanner import ScanManager
from app.applications.devices.oad.oad_manager import OadManager
from app.applications.npi.npi_manager import NpiManager
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.middleware.threads import AppThread


class DeviceTypes:
    motion = "motion"
    gas = "gas"


class DeviceManager:
    def __init__(self):
        self.npi = NpiManager('/dev/ttyUSB1')
        self.data_sender = lambda data: self.npi.send_binary_data(data)
        self.npi_interceptor = None

    def process_npi_msg(self, npi_msg):
        if self.npi_interceptor:
            self.npi_interceptor.process_incoming_npi_msg(npi_msg)
        # TODO: process base info here

    def send_response(self, data):
        Dispatcher.send_msg(Messages.SCAN_DEVICE_RESP, {'data': data})
        self.npi_interceptor = None

class DeviceApp(AppThread, DeviceManager):
    def __init__(self, mbox):
        AppThread.__init__(self, mbox)
        DeviceManager.__init__(self)

    def on_message(self, msg, data):
        if msg is Messages.NPI_RX_MSG:
            self.process_npi_msg(data["data"])

        elif msg is Messages.OAD_START:
            self.npi_interceptor = OadManager(self.data_sender, self.send_response)
            self.npi_interceptor.start()
        elif msg is Messages.OAD_ABORT:
            self.npi_interceptor.abort()

        elif msg is Messages.SCAN_DEVICE_REQ:
            self.npi_interceptor = ScanManager(self.data_sender, self.send_response)
            self.npi_interceptor.start()
        elif msg is Messages.SCAN_DEVICE_ABORT:
            self.npi_interceptor.abort()
