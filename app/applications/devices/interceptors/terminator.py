from app.applications.devices.interceptors.ack_handler import HciAckHandler
from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import Type, OpCode, Constants, TxPackGapTerminateLink, \
    Event, STATUS_SUCCESS, RxMsgGapTerminateLink
from app.middleware.messages import Messages


class TerminateInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, send_response, complete_cb, conn_handle):
        self.ext_complete_cb = complete_cb
        self.send_response = send_response
        self.data_sender = data_sender
        self.conn_handle = conn_handle
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus
        ])

    def start(self):
        tx_msg = TxPackGapTerminateLink(Type.LinkCtrlCommand,
                                        OpCode.GAP_TerminateLinkRequest,
                                        self.conn_handle,
                                        Constants.REMOTE_USER_TERMINATED)
        self.data_sender(tx_msg.buf_str)

    def complete(self, msg=None, data=None):
        self.send_response(msg, data)
        self.ext_complete_cb()

    def abort(self):
        pass

    def process_incoming_npi_msg(self, hci_msg_rx):
        self.handle_ack(hci_msg_rx)

        if self.ack_received():
            if hci_msg_rx.get_event() == Event.GAP_TerminateLink:
                msg_data = RxMsgGapTerminateLink(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.complete(msg=Messages.TERMINATE_CONN_RESP,
                                  data={"status" : STATUS_SUCCESS})
