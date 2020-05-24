from app.applications.devices.interceptors.ack_handler import HciAckHandler
from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import Event, TxPackWriteCharValue, Type, OpCode, Constants, RxMsgAttWriteRsp, \
    STATUS_SUCCESS
from app.middleware.messages import Messages


class CfgDiscInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, complete_cb, conn_handle, ccc_list):
        self.data_sender = data_sender
        self.ext_complete_cb = complete_cb
        self.conn_handle = conn_handle
        self.ccc_list = ccc_list
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus
        ])

    def enable_next_ccc(self):
        if len(self.ccc_list):
            ccc = self.ccc_list[0]
            tx_msg = TxPackWriteCharValue(Type.LinkCtrlCommand,
                                          OpCode.GATT_WriteCharValue,
                                          self.conn_handle,
                                          ccc,
                                          Constants.ENABLE_NOTIFICATION.to_bytes(2, byteorder='little'))
            self.data_sender(tx_msg.buf_str)

    def start(self):
        self.enable_next_ccc()

    def complete(self, msg=None, data=None):
        self.ext_complete_cb(msg, data)

    def abort(self):
        pass

    def process_incoming_npi_msg(self, hci_msg_rx):
        self.handle_ack(hci_msg_rx)

        if self.ack_received():
            if hci_msg_rx.get_event() == Event.ATT_WriteRsp:
                msg_data = RxMsgAttWriteRsp(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.ccc_list.pop(0)
                    self.enable_next_ccc()

        if self.ack_received() and not len(self.ccc_list):
            self.complete(msg=Messages.ENABLE_DEV_IND_RESP,
                          data={"conn_handle": self.conn_handle,
                                "status": STATUS_SUCCESS})
