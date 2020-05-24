from app.applications.devices.interceptors.ack_handler import HciAckHandler
from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import Event, TxPackWriteCharValue, Type, OpCode, RxMsgAttWriteRsp, \
    STATUS_SUCCESS
from app.middleware.messages import Messages


class WriteInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, complete_cb, conn_handle, handle, value):
        self.data_sender = data_sender
        self.ext_complete_cb = complete_cb
        self.conn_handle = conn_handle
        self.handle = handle
        self.value = value
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus
        ])

    def start(self):
        tx_msg = TxPackWriteCharValue(Type.LinkCtrlCommand,
                                      OpCode.GATT_WriteCharValue,
                                      self.conn_handle,
                                      self.handle,
                                      self.value)
        self.data_sender(tx_msg.buf_str)

    def complete(self, msg=None, data=None):
        self.ext_complete_cb(msg, data)

    def abort(self):
        pass

    def process_incoming_npi_msg(self, hci_msg_rx):
        ack_package = self.handle_ack(hci_msg_rx)

        if self.ack_received() and not ack_package:
            msg_data = RxMsgAttWriteRsp(hci_msg_rx.data)
            if msg_data.status == STATUS_SUCCESS and msg_data.conn_handle == self.conn_handle:
                self.complete(msg=Messages.DEV_WRITE_CHAR_VAL_RESP,
                              data={"conn_handle": self.conn_handle,
                                    "handle": self.handle,
                                    "value": self.value})
