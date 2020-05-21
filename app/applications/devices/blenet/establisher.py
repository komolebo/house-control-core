from app.applications.devices.blenet.ack_handler import HciAckHandler
from app.applications.devices.hci_manager import HciInterceptHandler
from app.applications.npi.hci_types import TxPackGapInitConnect, Type, OpCode, Constants, Event, \
    STATUS_SUCCESS, RxMsgGapInitConnect
from app.middleware.messages import Messages


class EstablishInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, complete_cb, data):
        self.data_sender = data_sender
        self.ext_complete_cb = complete_cb
        self.peer_addr = bytearray(data["mac"])
        self.device_type = data["type"]
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
        self.ext_complete_cb(msg=msg,
                             data=data)

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
                                            "type": self.device_type})
