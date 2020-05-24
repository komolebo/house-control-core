from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.devices.oad.oad_fsm import OadFsm
from app.applications.npi.hci_types import STATUS_SUCCESS
from app.middleware.messages import Messages


class OadInterceptHandler(HciInterceptHandler):
    def __init__(self, data_sender, complete_cb):
        self.ext_complete_cb = complete_cb
        self.oad_fsm = OadFsm(data_sender, self.complete)

    def start(self):
        self.oad_fsm.start()

    def abort(self):
        # TODO: check later
        pass

    def complete(self, msg=None, data=None):
        self.ext_complete_cb(Messages.OAD_COMPLETE, {"status": STATUS_SUCCESS})

    def process_incoming_npi_msg(self, hci_msg_rx):
        self.oad_fsm.on_event(hci_msg_rx)
