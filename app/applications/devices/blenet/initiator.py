from app.applications.devices.blenet.ack_handler import HciAckHandler
from app.applications.devices.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import Event, Type, OpCode, Constants, TxPackGapDeviceInit, \
    STATUS_SUCCESS, RxMsgGapDeviceInitDone
from app.middleware.messages import Messages


class InitInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, complete_cb):
        self.ext_complete_cb = complete_cb
        self.data_sender = data_sender
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus,
        ])
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
        self.handle_ack(hci_msg_rx)

        if self.ack_received():
        # if not all ACK received
            if hci_msg_rx.get_event() == Event.GAP_DeviceInitDone:
                msg_data = RxMsgGapDeviceInitDone(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.central_ip = msg_data.dev_addr
                    self.complete(msg=Messages.CENTRAL_INIT_RESP,
                                  data={"central_ip": self.central_ip,
                                        "status": STATUS_SUCCESS})
