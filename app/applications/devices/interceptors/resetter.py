from threading import Timer

from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import Type, OpCode, Constants, TxPackHciExtResetSystemCmd, Event, \
    RxMsgGapHciExtResetSystemCmdDone, STATUS_SUCCESS
from app.middleware.messages import Messages


class ResetInterceptHandler(HciInterceptHandler):
    RESET_DELAY_SEC = 0.5

    def __init__(self, data_sender, send_response, complete_cb):
        self.data_sender = data_sender
        self.send_response = send_response
        self.ext_complete_cb = complete_cb

    def start(self):
        tx_msg = TxPackHciExtResetSystemCmd(Type.LinkCtrlCommand,
                                            OpCode.HCIExt_ResetSystemCmd,
                                            Constants.CHIP_RESET)
        self.data_sender(tx_msg.buf_str)

    def _complete(self, msg=None, data=None):
        self.send_response(msg, data)
        self.ext_complete_cb()

    def complete(self, msg=None, data=None):
        # send callback after delay to let Host MCU to reset
        Timer(self.RESET_DELAY_SEC,
              self._complete, [msg, data]
        ).start()

    def abort(self):
        pass

    def process_incoming_npi_msg(self, hci_msg_rx):
        if hci_msg_rx.get_event() == Event.HCIExt_ResetSystemCmdDone:
            msg_data = RxMsgGapHciExtResetSystemCmdDone(hci_msg_rx.data)
            if msg_data.status == STATUS_SUCCESS:
                self.complete(msg=Messages.CENTRAL_RESET_RESP,
                              data={"status" : STATUS_SUCCESS})
