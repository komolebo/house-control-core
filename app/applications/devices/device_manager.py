from django.forms.models import model_to_dict

from app.applications.devices.device_connection import DevConnHandler, DevConnManager
from app.applications.devices.discovery.mtu_cfg import MtuCfgInterceptHandler
from app.applications.devices.interceptors.adjuster import AdjustInterceptHandler
from app.applications.devices.interceptors.establisher import EstablishInterceptHandler
from app.applications.devices.interceptors.writer import WriteInterceptHandler
from app.applications.devices.device_data import DevDataHandler
from app.applications.devices.device_data_collect import DeviceIndicationHandler
from app.applications.devices.discovery.indicator import CfgDiscInterceptHandler
from app.applications.devices.interceptors.initiator import InitInterceptHandler
from app.applications.devices.interceptors.listeners import DisconnectListenHandler, NotifyListenHandler
from app.applications.devices.interceptors.resetter import ResetInterceptHandler
from app.applications.devices.interceptors.scanner import ScanInterceptHandler
from app.applications.devices.interceptors.terminator import TerminateInterceptHandler
from app.applications.devices.discovery.char_disc import CharDiscInterceptHandler
from app.applications.devices.discovery.discovery import DiscoveryManager, DiscoveryHandler
from app.applications.devices.discovery.svc_disc import SvcDiscInterceptHandler
from app.applications.devices.discovery.value_disc import ValDiscInterceptHandler
from app.applications.devices.oad.oad_handler import OadInterceptHandler
from app.applications.devices.profiles.profile_uuid import CharUuid
from app.applications.frontier.front_update import FrontUpdateHandler
from app.applications.frontier.signals import FrontSignals
from app.applications.npi.hci_types import STATUS_SUCCESS
from app.applications.npi.npi_manager import NpiManager
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.middleware.nrc import RespCode
from app.middleware.threads import AppThread

from app.models import models
from app.models.models import Sensor


class DeviceManager:
    def __init__(self):
        self.npi = NpiManager()
        self.data_sender = lambda data: self.npi.send_binary_data(data)
        self.npi_interceptor = None
        self.disc_manager = DiscoveryManager()
        self.disc_handler = DiscoveryHandler()
        self.dev_indication_handler = DeviceIndicationHandler(self.disc_handler, self.send_response)

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
        DevDataHandler.__init__()

    def on_message(self, msg, data):
        if msg is Messages.NPI_RX_MSG:
            self.process_npi_msg(data["data"])

        elif msg is Messages.DEV_INDICATION:
            self.dev_indication_handler.process_indication(conn_handle=data["conn_handle"],
                                                           handle=data["handle"],
                                                           value=data["value"])
            FrontUpdateHandler.notify_front(FrontSignals.DEV_NOTIFY_DATA, data={})

# ------ CRUD operations ------------------------------------------------------------------
        if msg is Messages.DEV_INFO_READ:
            mac = data['mac']
            dev = DevDataHandler.read_dev(mac)
            FrontUpdateHandler.notify_front(FrontSignals.DEV_READ_RESP, data=dev)

        elif msg is Messages.DEV_INFO_READ_LIST:
            all_devices = DevDataHandler.get_dev_list()
            # populate conn handle info
            for dev in all_devices:
                dev['active'] = DevConnHandler.is_mac_active(dev['mac'])
                print(dev)
            FrontUpdateHandler.notify_front(FrontSignals.DEV_READ_LIST_RESP, data=all_devices)

        elif msg is Messages.DEV_INFO_ADD:
            mac = data['mac']
            if isinstance(mac, (bytes, bytearray)):
                mac = str(bytes(mac).hex())
            DevDataHandler.add_dev(mac, data['name'], data['type'], data['location'])
            FrontUpdateHandler.notify_front(FrontSignals.DEV_ADD_ACK, {'mac': mac})

        elif msg is Messages.DEV_INFO_REM:
            mac = data['mac']
            DevDataHandler.rem_dev(mac)
            FrontUpdateHandler.notify_front(FrontSignals.DEV_REM_ACK, {'data': mac})

        elif msg is Messages.DEV_INFO_UPD:
            mac = data['mac']
            new_state = data['state']
            conn_handle = DevConnHandler.get_handle_by_mac(mac)
            uuid_handle = self.disc_handler.get_handle_by_uuid(conn_handle, CharUuid.CS_MODE.uuid)[0]
            sensor_cfg_update = new_state != DevDataHandler.get_dev(mac)

            DevDataHandler.upd_dev(mac, data['name'], data['location'], data['state'])
            if sensor_cfg_update:
                Dispatcher.send_msg(Messages.DEV_WRITE_CHAR_VAL, {'conn_handle': conn_handle,
                                                                  'handle': uuid_handle,
                                                                  'value': bytes([new_state])})
            FrontUpdateHandler.notify_front(FrontSignals.DEV_UPD_ACK, {'data': mac})

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

        elif msg is Messages.CENTRAL_ADJUST_RESP:
            DevConnManager.scan_start_schedule()

#-------------------------------------------------------------------------------------------
#------ Do here mutually exclusive GATT procedures -----------------------------------------
        elif msg is Messages.OAD_START:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.OAD_COMPLETE, {"status": RespCode.BUSY})
            else:
                self.npi_interceptor = OadInterceptHandler(self.data_sender, self.send_response)
                self.npi_interceptor.start()
        elif msg is Messages.OAD_ABORT:
            self.npi_interceptor.abort()

        elif msg is Messages.DEV_WRITE_CHAR_VAL:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.DEV_WRITE_CHAR_VAL_RESP, {"status": RespCode.BUSY,
                                                                       "conn_handle": None,
                                                                       "handle": None,
                                                                       "value": None})
            else:
                self.npi_interceptor = WriteInterceptHandler(self.data_sender, self.send_response,
                                                             data["conn_handle"], data["handle"], data["value"])
                self.npi_interceptor.start()

        elif msg is Messages.SCAN_DEVICE:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.SCAN_DEVICE_RESP, {"data" : 0, "status": RespCode.BUSY})
            else:
                self.npi_interceptor = ScanInterceptHandler(self.data_sender, self.send_response)
                self.npi_interceptor.start()
        elif msg is Messages.SCAN_DEVICE_ABORT:
            self.npi_interceptor.abort()

        elif msg is Messages.SCAN_DEVICE_RESP:
            if data["status"] is STATUS_SUCCESS:
                # connect lost devices again
                DevConnManager.process_scan_resp(scan_list=data["data"])

                # notify front of scanned unknown devices
                known_dev_list = [x['mac'] for x in DevDataHandler.read_all_dev()]
                # print("known dev list", known_dev_list)
                unknown_scan_list = [x for x in data["data"] if x.mac not in known_dev_list]
                # print("unknown dev list", unknown_scan_list)
                json_scan_list = [x.to_json() for x in unknown_scan_list]
                FrontUpdateHandler.notify_front(FrontSignals.DEV_SCAN_RESP, {'data': json_scan_list})


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
                self.dev_indication_handler.add_device(data["conn_handle"], data["type"], data["name"])
                DevConnHandler.add_conn_info(data["conn_handle"], data["mac"])
                FrontUpdateHandler.notify_front(FrontSignals.DEV_CONN_RESP, {})
                Dispatcher.send_msg(Messages.DEV_INFO_ADD, data)

        elif msg is Messages.TERMINATE_CONN:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.TERMINATE_CONN_RESP, {"status": RespCode.BUSY})
            else:
                self.npi_interceptor = TerminateInterceptHandler(self.data_sender,
                                                                 self.send_response,
                                                                 data["conn_handle"])
                self.npi_interceptor.start()
        elif msg is Messages.DEVICE_DISCONN:
            DevConnHandler.del_conn_info(_conn_handle=data["conn_handle"])
            FrontUpdateHandler.notify_front(FrontSignals.DEV_DISCONN, {})

        elif msg is Messages.DEV_MTU_CFG:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.DEV_MTU_CFG_RESP, {"conn_handle": data["conn_handle"],
                                                                "status": RespCode.BUSY})
            else:
                self.npi_interceptor = MtuCfgInterceptHandler(self.data_sender,
                                                              self.send_response,
                                                              data["conn_handle"])
                self.npi_interceptor.start()

        elif msg is Messages.DEV_MTU_CFG_RESP:
            if data["status"] == RespCode.SUCCESS:
                self.disc_manager.handle_mtu_cfg(data["conn_handle"])
#------- Discovery section -----------------------------------------------------------------
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

        elif msg is Messages.ENABLE_DEV_INDICATION:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.ENABLE_DEV_IND_RESP, {"status": RespCode.BUSY,
                                                                   "conn_handle": data["conn_handle"]})
            else:
                ccc_list = self.disc_handler.get_handle_by_uuid(data["conn_handle"],CharUuid.GATT_CCC_UUID)
                self.npi_interceptor = CfgDiscInterceptHandler(self.data_sender,
                                                               self.send_response,
                                                               data["conn_handle"],
                                                               ccc_list)
                self.npi_interceptor.start()
        elif msg is Messages.ENABLE_DEV_IND_RESP:
            if data["status"] == RespCode.SUCCESS:
                self.disc_manager.handle_ccc_enabled(data["conn_handle"])
        elif msg is Messages.DEV_VALUES_DISCOVER:
            if self.npi_interceptor:
                Dispatcher.send_msg(Messages.DEV_VALUES_DISCOVER_RESP, {"status": RespCode.BUSY,
                                                                        "conn_handle": data["conn_handle"],
                                                                        "char_value_data": []})
            else:
                self.npi_interceptor = ValDiscInterceptHandler(self.data_sender, self.send_response, self.disc_handler,
                                                               data["conn_handle"])
                self.npi_interceptor.start()
        elif msg is Messages.DEV_VALUES_DISCOVER_RESP:
            self.dev_indication_handler.process_val_disc_resp(data["conn_handle"], data["char_value_data"])
#------------------------------------------------------------------------------------------
