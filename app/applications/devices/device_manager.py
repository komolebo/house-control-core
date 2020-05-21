from app.applications.devices.blenet.adjuster import AdjustInterceptHandler
from app.applications.devices.blenet.establisher import EstablishInterceptHandler
from app.applications.devices.blenet.initiator import InitInterceptHandler
from app.applications.devices.blenet.listeners import DisconnectListenHandler
from app.applications.devices.blenet.resetter import ResetInterceptHandler
from app.applications.devices.blenet.scanner import ScanInterceptHandler
from app.applications.devices.blenet.terminator import TerminateInterceptHandler
from app.applications.devices.oad.oad_handler import OadInterceptHandler
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
        # listeners task place
        DisconnectListenHandler.listen(npi_msg, self.send_response)

    def send_response(self, msg=None, data=None):
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
            self.npi_interceptor = ResetInterceptHandler(self.data_sender, self.send_response)
            self.npi_interceptor.start()

        elif msg in (Messages.CENTRAL_INIT, Messages.CENTRAL_RESET_RESP):
            self.npi_interceptor = InitInterceptHandler(self.data_sender, self.send_response)
            self.npi_interceptor.start()

        elif msg in (Messages.CENTRAL_ADJUST, Messages.CENTRAL_INIT_RESP):
            self.npi_interceptor = AdjustInterceptHandler(self.data_sender, self.send_response)
            self.npi_interceptor.start()

#------ Do here mutually exclusive procedures ----------------------------------------------
        elif msg is Messages.OAD_START:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.OAD_COMPLETE, {"status": RespCode.BUSY})
            else:
                self.npi_interceptor = OadInterceptHandler(self.data_sender, self.send_response)
                self.npi_interceptor.start()
        elif msg is Messages.OAD_ABORT:
            self.npi_interceptor.abort()

        elif msg is Messages.SCAN_DEVICE:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.SCAN_DEVICE_RESP, {"data" : 0, "status": RespCode.BUSY})
            else:
                self.npi_interceptor = ScanInterceptHandler(self.data_sender, self.send_response)
                self.npi_interceptor.start()
        elif msg is Messages.SCAN_DEVICE_ABORT:
            self.npi_interceptor.abort()

        elif msg is Messages.ESTABLISH_CONN:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.ESTABLISH_CONN_RESP, {"data": 0, "status": RespCode.BUSY})
            else:
                self.npi_interceptor = EstablishInterceptHandler(self.data_sender, self.send_response, data)
                self.npi_interceptor.start()
        elif msg is Messages.ESTABLISH_CONN_ABORT:
            self.npi_interceptor.abort()

        elif msg is Messages.TERMINATE_CONN:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.TERMINATE_CONN_RESP, {"status": RespCode.BUSY})
            else:
                self.npi_interceptor = TerminateInterceptHandler(self.data_sender,
                                                                 self.send_response,
                                                                 data["conn_handle"])
                self.npi_interceptor.start()

#------------------------------------------------------------------------------------------