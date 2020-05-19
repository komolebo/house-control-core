from app.applications.npi.npi_manager import NpiManager
from app.applications.devices.oad.oad_fsm import OadFsm
from app.applications.devices.oad.oad_manager import OadManager
from app.applications.npi.npi_manager import NpiManager
from app.middleware.messages import Messages
from app.middleware.threads import AppThread


class DeviceManager(OadManager):
    def __init__(self):
        npi = NpiManager('/dev/ttyUSB0')
        data_sender = lambda data: npi.send_binary_data(data)
        super().__init__(data_sender)

    def process_npi_msg(self, npi_msg):
        if self.oad_active:
            self.process_oad_msg(npi_msg)


class DeviceApp(AppThread, DeviceManager):
    def on_message(self, msg, data):
        if msg is Messages.NPI_RX_MSG:
            self.process_npi_msg(data["data"])
        elif msg is Messages.OAD_START:
            self.start_oad()
        elif msg is Messages.OAD_ABORT:
            self.abort_oad()
# if __name__ == '__main__':
#     npi = NpiManager('/dev/ttyUSB0')
#     oadFsm = OadFsm()
#
#     oadFsm.start()
#
#     while True:
#         npi_msg = npi.process_next_msg()
#         print("DUMP RX: ", npi_msg.as_output())
#         oadFsm.on_event(npi_msg)
