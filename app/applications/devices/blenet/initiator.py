from time import sleep

from app.applications.devices.hci_manager import BaseHciHandler
from app.applications.npi.hci_types import Event, Type, OpCode, Constants, TxPackGapDeviceInit, \
    RxMsgGapHciExtentionCommandStatus, STATUS_SUCCESS, RxMsgGapDeviceInitDone
from app.middleware.messages import Messages


class InitiatorHandler(BaseHciHandler):
    def __init__(self, data_sender, complete_cb):
        self.ext_complete_cb = complete_cb
        self.data_sender = data_sender
        self.ack_list = [
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.GAP_DeviceInitDone
        ]
        self.central_ip = None

    def start(self):
        tx_msg = TxPackGapDeviceInit(Type.LinkCtrlCommand,
                                     OpCode.Gap_DeviceInit,
                                     Constants.PROFILE_ROLE_CENTRAL,
                                     Constants.ADDRMODE_PUBLIC,
                                     random_addr=bytearray([0, 0, 0, 0, 0, 0]))
        self.data_sender(tx_msg.buf_str)

    def complete(self, msg=None, data=None):
        self.ext_complete_cb(msg, data)

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

            elif hci_msg_rx.get_event() == Event.GAP_DeviceInitDone:
                msg_data = RxMsgGapDeviceInitDone(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.ack_list.remove(msg_data.event)
                    self.central_ip = msg_data.dev_addr
                    valid_resp = True

        # ACK received and current response is not a previous ACK
        if valid_resp and not len(self.ack_list):
            self.complete(msg=Messages.CENTRAL_INIT_RESP,
                          data={"central_ip": self.central_ip,
                                "success": STATUS_SUCCESS})
