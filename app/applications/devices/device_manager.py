from app.applications.devices.blenet.adjuster import AdjustInterceptHandler
from app.applications.devices.blenet.establisher import EstablishInterceptHandler
from app.applications.devices.device_data import DeviceDataHandler
from app.applications.devices.discovery.indicator import IndicateInterceptHandler
from app.applications.devices.blenet.initiator import InitInterceptHandler
from app.applications.devices.blenet.listeners import DisconnectListenHandler, NotifyListenHandler
from app.applications.devices.blenet.resetter import ResetInterceptHandler
from app.applications.devices.blenet.scanner import ScanInterceptHandler
from app.applications.devices.blenet.terminator import TerminateInterceptHandler
from app.applications.devices.discovery.chars import CharDiscInterceptHandler
from app.applications.devices.discovery.discovery import DiscoveryManager
from app.applications.devices.discovery.svc import SvcDiscInterceptHandler
from app.applications.devices.oad.oad_handler import OadInterceptHandler
from app.applications.devices.profiles.profile_uuid import CharUuid
from app.applications.npi.npi_manager import NpiManager
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.middleware.nrc import RespCode
from app.middleware.threads import AppThread


class DeviceManager:
    def __init__(self):
        self.npi = NpiManager() # '/dev/ttyUSB0')
        self.data_sender = lambda data: self.npi.send_binary_data(data)
        self.npi_interceptor = None
        self.disc_manager = DiscoveryManager()
        self.device_data_handler = DeviceDataHandler(self.disc_manager, self.send_response)

    def process_npi_msg(self, npi_msg):
        if self.npi_interceptor:
            self.npi_interceptor.process_incoming_npi_msg(npi_msg)
        # listeners task place
        DisconnectListenHandler.listen(npi_msg, self.send_response)
        NotifyListenHandler.listen(npi_msg, self.send_response, self.data_sender)

    def send_response(self, msg=None, data=None):
        self.npi_interceptor = None
        Dispatcher.send_msg(msg, data)

    def handle_device_data_change(self, conn_handle, value, handle):
        pass


class DeviceApp(AppThread, DeviceManager):
    def __init__(self, mbox):
        AppThread.__init__(self, mbox)
        DeviceManager.__init__(self)

    def on_message(self, msg, data):
        if msg is Messages.NPI_RX_MSG:
            self.process_npi_msg(data["data"])

        elif msg is Messages.DEV_DATA_CHANGE:
            self.device_data_handler.process_data_change(conn_handle=data["conn_handle"],
                                                         handle=data["handle"],
                                                         value=data["value"])

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

#------ Do here mutually exclusive GATT procedures -----------------------------------------
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
                Dispatcher.send_msg(Messages.ESTABLISH_CONN_RESP, {"conn_handle": 0xFFFF,
                                                                   "status": RespCode.BUSY,
                                                                   "mac": 0,
                                                                   "type": None,
                                                                   "name": None})
            else:
                self.npi_interceptor = EstablishInterceptHandler(self.data_sender, self.send_response, data)
                self.npi_interceptor.start()
        elif msg is Messages.ESTABLISH_CONN_ABORT:
            self.npi_interceptor.abort()
        elif msg is Messages.ESTABLISH_CONN_RESP:
            if data["status"] is RespCode.SUCCESS:
                self.disc_manager.handle_new_conn(data["conn_handle"], data["type"])
                self.device_data_handler.add_device(data["conn_handle"], data["type"], data["name"])

        elif msg is Messages.TERMINATE_CONN:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.TERMINATE_CONN_RESP, {"status": RespCode.BUSY})
            else:
                self.npi_interceptor = TerminateInterceptHandler(self.data_sender,
                                                                 self.send_response,
                                                                 data["conn_handle"])
                self.npi_interceptor.start()

        elif msg is Messages.DEV_SVC_DISCOVER:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.DEV_SVC_DISCOVER_RESP, {"status": RespCode.BUSY,
                                                                    "services": [],
                                                                    "conn_handle": data["conn_handle"]})
            else:
                self.npi_interceptor = SvcDiscInterceptHandler(self.data_sender,
                                                               self.send_response,
                                                               data["conn_handle"])
                self.npi_interceptor.start()
        elif msg is Messages.DEV_SVC_DISCOVER_RESP:
            if data["status"] == RespCode.SUCCESS:
                self.disc_manager.handle_svc_report(data["conn_handle"], data["services"])

        elif msg is Messages.DEV_CHAR_DISCOVER:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.DEV_CHAR_DISCOVER_RESP, {"status": RespCode.BUSY,
                                                                      "chars": [],
                                                                      "conn_handle": data["conn_handle"]})
            else:
                self.npi_interceptor = CharDiscInterceptHandler(self.data_sender,
                                                                self.send_response,
                                                                data["conn_handle"])
                self.npi_interceptor.start()
        elif msg is Messages.DEV_CHAR_DISCOVER_RESP:
            if data["status"] == RespCode.SUCCESS:
                self.disc_manager.handle_char_report(data["conn_handle"], data["chars"])

        elif msg is Messages.ENABLE_DEV_IND:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.ENABLE_DEV_IND_RESP, {"status": RespCode.BUSY,
                                                                   "conn_handle": data["conn_handle"]})
            else:
                self.npi_interceptor = IndicateInterceptHandler(self.data_sender,
                                                                self.send_response,
                                                                data["conn_handle"],
                                                                self.disc_manager.get_handle_by_uuid(data["conn_handle"],
                                                                                                CharUuid.GATT_CCC_UUID))
                self.npi_interceptor.start()
        elif msg is Messages.ENABLE_DEV_IND_RESP:
            if data["status"] == RespCode.SUCCESS:
                self.disc_manager.handle_ccc_enabled(data["conn_handle"])

#------------------------------------------------------------------------------------------