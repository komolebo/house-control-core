from app.applications.devices.blenet.adjuster import AdjustHandler
from app.applications.devices.blenet.establisher import EstablishHandler
from app.applications.devices.blenet.initiator import InitiatorHandler
from app.applications.devices.blenet.resetter import ResetHandler
from app.applications.devices.blenet.scanner import ScanHandler
from app.applications.devices.oad.oad_handler import OadHandler
from app.applications.npi.npi_manager import NpiManager
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.middleware.nrc import RespCode
from app.middleware.threads import AppThread


class DeviceTypes:
    motion = "motion"
    gas = "gas"


class DeviceManager:
    def __init__(self):
        self.npi = NpiManager('/dev/ttyUSB0')
        self.data_sender = lambda data: self.npi.send_binary_data(data)
        self.npi_interceptor = None

    def process_npi_msg(self, npi_msg):
        if self.npi_interceptor:
            self.npi_interceptor.process_incoming_npi_msg(npi_msg)
        # TODO: process base info here

    def send_response(self, msg = None, data = None):
        self.npi_interceptor = None
        Dispatcher.send_msg(msg, data)


class DeviceApp(AppThread, DeviceManager):
    def __init__(self, mbox):
        AppThread.__init__(self, mbox)
        DeviceManager.__init__(self)

    def on_message(self, msg, data):
        if msg is Messages.NPI_RX_MSG:
            self.process_npi_msg(data["data"])

# ------ CENTRAL setup procedures ---------------------------------------------------------
        elif msg is Messages.CENTRAL_RESET:
            self.npi_interceptor = ResetHandler(self.data_sender, self.send_response)
            self.npi_interceptor.start()

        elif msg in (Messages.CENTRAL_INIT, Messages.CENTRAL_RESET_RESP):
            self.npi_interceptor = InitiatorHandler(self.data_sender, self.send_response)
            self.npi_interceptor.start()

        elif msg in (Messages.CENTRAL_ADJUST, Messages.CENTRAL_INIT_RESP):
            self.npi_interceptor = AdjustHandler(self.data_sender, self.send_response)
            self.npi_interceptor.start()

#------ Do here mutually exclusive procedures ----------------------------------------------
        if msg is Messages.OAD_START:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.OAD_COMPLETE, {"success": RespCode.BUSY})
            else:
                self.npi_interceptor = OadHandler(self.data_sender, self.send_response)
                self.npi_interceptor.start()
        elif msg is Messages.OAD_ABORT:
            self.npi_interceptor.abort()

        elif msg is Messages.SCAN_DEVICE:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.SCAN_DEVICE_RESP, {"data" : 0, "success": RespCode.BUSY})
            else:
                self.npi_interceptor = ScanHandler(self.data_sender, self.send_response)
                self.npi_interceptor.start()
        elif msg is Messages.SCAN_DEVICE_ABORT:
            self.npi_interceptor.abort()

        elif msg is Messages.ESTABLISH_CONN:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.ESTABLISH_CONN_RESP, {"data": 0, "success": RespCode.BUSY})
            else:
                self.npi_interceptor = EstablishHandler(self.data_sender, self.send_response, data)
                self.npi_interceptor.start()
        elif msg is Messages.ESTABLISH_CONN_ABORT:
            self.npi_interceptor.abort()

#------------------------------------------------------------------------------------------