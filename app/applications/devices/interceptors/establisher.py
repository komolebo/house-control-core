from app.applications.devices.interceptors.ack_handler import HciAckHandler
from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import TxPackGapInitConnect, Type, OpCode, Constants, Event, \
    STATUS_SUCCESS, RxMsgGapInitConnect
from app.middleware.messages import Messages


class EstablishInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, send_resp, complete_cb, data):
        self.data_sender = data_sender
        self.send_response = send_resp
        self.ext_complete_cb = complete_cb
        self.device_type = data["type"]
        self.device_name = data["name"]
        self.peer_addr = bytes.fromhex(data["mac"])
        self.device_location = data["location"]
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus,
        ])

    def start(self):
        tx_msg = TxPackGapInitConnect(Type.LinkCtrlCommand,
                                      OpCode.GapInit_connect,
                                      Constants.PEER_ADDRTYPE_PUBLIC_OR_PUBLIC_ID,
                                      self.peer_addr,
                                      Constants.INIT_PHY_1M,
                                      timeout=0)
        self.data_sender(tx_msg.buf_str)

    def complete(self, msg=None, data=None):
        self.send_response(msg, data)
        self.ext_complete_cb()

    def abort(self):
        pass

    def process_incoming_npi_msg(self, hci_msg_rx):
        # if not all ACK received
        self.handle_ack(hci_msg_rx)

        if self.ack_received():
            if hci_msg_rx.get_event() == Event.GAP_EstablishLink:
                msg_data = RxMsgGapInitConnect(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    if msg_data.dev_addr == self.peer_addr:
                        self.complete(msg=Messages.ESTABLISH_CONN_RESP,
                                      data={"mac": self.peer_addr,
                                            "conn_handle": msg_data.conn_handle,
                                            "status": STATUS_SUCCESS,
                                            "type": self.device_type,
                                            "name": self.device_name,
                                            "location": self.device_location})