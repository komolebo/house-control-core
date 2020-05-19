from app.applications.devices.hci_manager import BaseHciManager
from app.applications.npi.npi_manager import NpiManager
from app.applications.devices.oad.oad_fsm import OadFsm
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages


class OadManager(BaseHciManager):
    def __init__(self, data_sender, complete_cb):
        self.ext_complete_cb = complete_cb
        self.oad_fsm = OadFsm(data_sender, self.complete)

    def start(self):
        self.oad_fsm.start()

    def abort(self):
        # TODO: check later
        pass

    def complete(self, rsp_code=None):
        print('OAD completed')
        Dispatcher.send_msg(Messages.OAD_COMPLETE, {})
        self.ext_complete_cb()

    def process_incoming_npi_msg(self, hci_msg_rx):
        self.oad_fsm.on_event(hci_msg_rx)
