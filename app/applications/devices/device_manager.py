from app.applications.npi.npi_manager import NpiManager
from app.applications.devices.oad.oad_fsm import OadFsm
from app.applications.devices.oad.oad_manager import OadManager
from app.applications.npi.npi_manager import NpiManager
from app.middleware.messages import Messages
from app.middleware.threads import AppThread


class DeviceManager(OadManager):
    def __init__(self):
        self.npi = NpiManager('/dev/ttyUSB0')
        data_sender = lambda data: self.npi.send_binary_data(data)
        super().__init__(data_sender)

    def scan_devices(self):
        pass

    def process_npi_msg(self, npi_msg):
        if self.oad_active:
            self.process_oad_msg(npi_msg)


class DeviceApp(AppThread, DeviceManager):
    def __init__(self, mbox):
        AppThread.__init__(self, mbox)
        DeviceManager.__init__(self)

    def on_message(self, msg, data):
        if msg is Messages.NPI_RX_MSG:
            print('Received NPI msg')
            self.process_npi_msg(data["data"])
        elif msg is Messages.OAD_START:
            self.start_oad()
        elif msg is Messages.OAD_ABORT:
            self.abort_oad()
        elif msg is Messages.SCAN_DEVICE_REQ:
            self.scan_devices()
