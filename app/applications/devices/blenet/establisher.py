from app.applications.devices.hci_manager import BaseHciHandler
from app.applications.npi.hci_types import TxPackGapScan, TxPackGapInitConnect, Type, OpCode, Constants, Event, \
    RxMsgGapHciExtentionCommandStatus, STATUS_SUCCESS, RxMsgGapAdvertiserScannerEvent, RxMsgGapInitConnect
from app.middleware.messages import Messages


class EstablishHandler(BaseHciHandler):
    def __init__(self, data_sender, complete_cb, data):
        self.data_sender = data_sender
        self.ext_complete_cb = complete_cb
        self.peer_addr = bytearray(data['data'])
        self.ack_list = [
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.GAP_EstablishLink
        ]

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
        # Assume scan request is sent, collect response
        valid_resp = False

        # if not all ACK received
        if len(self.ack_list):
            if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
                msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.ack_list.remove(msg_data.event)
                    valid_resp = True

            elif hci_msg_rx.get_event() == Event.GAP_EstablishLink:
                msg_data = RxMsgGapInitConnect(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    if msg_data.dev_addr == self.peer_addr:
                        self.ack_list.remove(msg_data.event)
                        valid_resp = True

        # ACK received and current response is not a previous ACK
        if valid_resp and not len(self.ack_list):
            print(self.peer_addr)
            self.complete(msg=Messages.ESTABLISH_CONN_RESP,
                          data={"data": self.peer_addr,
                                "success": STATUS_SUCCESS})
