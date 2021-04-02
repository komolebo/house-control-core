from app.applications.devices.conn_info import DevConnDataHandler
from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.devices.oad.oad_fsm import OadFsm
from app.applications.npi.hci_types import STATUS_SUCCESS
from app.middleware.messages import Messages


class OadInterceptHandler(HciInterceptHandler):
    def __init__(self, data_sender, send_resp, complete_cb, mac, firmware_path):
        self.ext_complete_cb = complete_cb
        self.send_response = send_resp
        self.mac = mac
        conn_handle = DevConnDataHandler.get_handle_by_mac(mac)
        self.oad_fsm = OadFsm(data_sender, self.complete, conn_handle, firmware_path)

    def start(self):
        self.oad_fsm.start()

    def abort(self):
        # TODO: check later
        pass

    def complete(self, msg=None, data=None):
        self.send_response(Messages.OAD_COMPLETE, {"status": STATUS_SUCCESS, "mac": self.mac})
        self.ext_complete_cb()

    def process_incoming_npi_msg(self, hci_msg_rx):
        self.oad_fsm.on_event(hci_msg_rx)
