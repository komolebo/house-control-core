from app.applications.devices.interceptors.ack_handler import HciAckHandler
from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import Event, Type, OpCode, STATUS_SUCCESS, TxPackHciLeSetDataLenReq, \
    RxMsgHciLeGenericReportEvtRsp, TxPackGapUpdateLinkParam, RxMsgGapUpdateLinkParam
from app.middleware.messages import Messages


class LinkParamCfgInterceptHandler(HciInterceptHandler, HciAckHandler):
    INTERVAL_MIN = 0x0006
    INTERVAL_MAX = 0x0006
    CONNECTION_LATENCY = 0
    CONNECTION_TIMEOUT = 0x0032

    def __init__(self, data_sender, send_resp, complete_cb, conn_handle):
        self.ext_complete_cb = complete_cb
        self.data_sender = data_sender
        self.send_response = send_resp
        self.conn_handle = conn_handle
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus
        ])

    def start(self):
        tx_msg = TxPackGapUpdateLinkParam(Type.LinkCtrlCommand,
                                          OpCode.GAP_UpdateLinkParamReq,
                                          self.conn_handle,
                                          self.INTERVAL_MIN,
                                          self.INTERVAL_MAX,
                                          self.CONNECTION_LATENCY,
                                          self.CONNECTION_TIMEOUT)
        self.data_sender(tx_msg.buf_str)

    def complete(self, msg=None, data=None):
        self.send_response(msg, data)
        self.ext_complete_cb()

    def abort(self):
        pass

    def process_incoming_npi_msg(self, hci_msg_rx):
        ack_packet = self.handle_ack(hci_msg_rx)

        if self.ack_received() and not ack_packet:
            if hci_msg_rx.get_event() == Event.GAP_LinkParamUpdate:
                msg_data = RxMsgGapUpdateLinkParam(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.complete(msg=Messages.DEV_LINK_PARAM_CFG_RESP,
                                  data={"conn_handle": self.conn_handle,
                                        "status" : STATUS_SUCCESS})
