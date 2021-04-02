from app.applications.devices.interceptors.ack_handler import HciAckHandler
from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import Event, Type, OpCode, Constants, TxPackGapInitGetPhyParam, \
    STATUS_SUCCESS
from app.middleware.messages import Messages


class AdjustInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, send_resp, complete_cb):
        self.data_sender = data_sender
        self.send_resp = send_resp
        self.ext_complete_cb = complete_cb
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.GAP_HCI_ExtentionCommandStatus
        ])

    def _send_conn_param(self, phy_param_conn):
        tx_msg = TxPackGapInitGetPhyParam(Type.LinkCtrlCommand,
                                          OpCode.GapInit_getPhyParam,
                                          Constants.INIT_PHY_1M,
                                          phy_param_conn)
        self.data_sender(tx_msg.buf_str)

    def start(self):
        self._send_conn_param(Constants.INIT_PHYPARAM_CONN_INT_MIN)
        self._send_conn_param(Constants.INIT_PHYPARAM_CONN_INT_MAX)
        self._send_conn_param(Constants.INIT_PHYPARAM_CONN_LATENCY)
        self._send_conn_param(Constants.INIT_PHYPARAM_SUP_TIMEOUT)

    def complete(self, msg=None, data=None):
        self.send_resp(msg, data)
        self.ext_complete_cb()

    def abort(self):
        pass

    def process_incoming_npi_msg(self, hci_msg_rx):
        self.handle_ack(hci_msg_rx)

        if self.ack_received():
            self.complete(msg=Messages.CENTRAL_ADJUST_RESP,
                          data={"status" : STATUS_SUCCESS})
