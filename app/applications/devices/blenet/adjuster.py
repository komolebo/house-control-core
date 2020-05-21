from time import sleep

from app.applications.devices.hci_manager import BaseHciHandler
from app.applications.npi.hci_types import Event, Type, OpCode, Constants, TxPackGapInitGetPhyParam, \
    RxMsgGapHciExtentionCommandStatus, STATUS_SUCCESS
from app.middleware.messages import Messages


class AdjustHandler(BaseHciHandler):
    def __init__(self, data_sender, complete_cb):
        self.data_sender = data_sender
        self.ext_complete_cb = complete_cb
        self.ack_list = [
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.GAP_HCI_ExtentionCommandStatus
        ]

    def _send_conn_param(self, phy_param_conn):
        tx_msg = TxPackGapInitGetPhyParam(Type.LinkCtrlCommand,
                                          OpCode.GapInit_getPhyParam,
                                          Constants.INIT_PHY_1M,
                                          phy_param_conn)
        self.data_sender(tx_msg.buf_str)

    def start(self):
        self._send_conn_param(Constants.INIT_PHYPARAM_CONN_INT_MIN)
        # sleep(1)
        self._send_conn_param(Constants.INIT_PHYPARAM_CONN_INT_MAX)
        # sleep(1)
        self._send_conn_param(Constants.INIT_PHYPARAM_CONN_LATENCY)
        # sleep(1)
        self._send_conn_param(Constants.INIT_PHYPARAM_SUP_TIMEOUT)

    def complete(self, msg=None, data=None):
        self.ext_complete_cb(msg, data)

    def abort(self):
        pass

    def process_incoming_npi_msg(self, hci_msg_rx):
        valid_resp = False

        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)

            if msg_data.status == STATUS_SUCCESS:
                self.ack_list.remove(msg_data.event)
                valid_resp = True

        if valid_resp and not(len(self.ack_list)):
            self.complete(msg=Messages.CENTRAL_ADJUST_RESP,
                          data={"success" : STATUS_SUCCESS})
