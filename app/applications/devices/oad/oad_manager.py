from app.applications.npi.npi_manager import NpiManager
from app.applications.devices.oad.oad_fsm import OadFsm


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

    def complete_oad(self, rsp_code):
        self.oad_active = False

    def process_oad_msg(self, npi_msg):
        self.oad_fsm.on_event(npi_msg)
