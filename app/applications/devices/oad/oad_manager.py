from app.applications.npi.npi_manager import NpiManager
from app.applications.devices.oad.oad_fsm import OadFsm
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages


class OadManager:
    def __init__(self, data_sender):
        self.oad_fsm = OadFsm(data_sender, self.complete_oad)
        self.oad_active = False

    def start_oad(self):
        self.oad_active = True
        self.oad_fsm.start()

    def abort_oad(self):
        # TODO: check later
        pass

    def complete_oad(self, rsp_code=None):
        self.oad_active = False
        print('OAD completed')
        Dispatcher.send_msg(Messages.OAD_COMPLETE, {})

    def process_oad_msg(self, npi_msg):
        self.oad_fsm.on_event(npi_msg)
