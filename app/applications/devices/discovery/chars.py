from app.applications.devices.conn_info import CharData
from app.applications.devices.blenet.ack_handler import HciAckHandler
from app.applications.devices.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import Event, Type, OpCode, Constants, STATUS_SUCCESS, \
    TxPackGattDiscoverAllCharsDescs, \
    RxMsgAttFindInfoRsp
from app.middleware.messages import Messages


class CharDiscInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, complete_cb, conn_handle):
        self.ext_complete_cb = complete_cb
        self.data_sender = data_sender
        self.conn_handle = conn_handle
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus
        ])
        self.char_data_list = []

    def start(self):
        tx_msg = TxPackGattDiscoverAllCharsDescs(Type.LinkCtrlCommand,
                                                 OpCode.GATT_DiscAllCharDescs,
                                                 self.conn_handle,
                                                 start_handle=0x0001,
                                                 end_handle=0xFFFF)
        self.data_sender(tx_msg.buf_str)

    def complete(self, msg=None, data=None):
        self.ext_complete_cb(msg, data)

    def abort(self):
        pass

    def handle_char_resp(self, hci_msg):
        if hci_msg.format == Constants.HANDLE_BT_UUID_TYPE_16BIT_FORMAT:
            uuid_len = Constants.UUID_16BIT_IN_BYTES
        else:
            uuid_len = Constants.UUID_128BIT_IN_BYTES
        item_len = uuid_len + Constants.HANDLE_BYTE_LEN
        data_len = hci_msg.pdu_len - Constants.FORMAT_BYTE_LEN
        item_num = data_len // item_len
        for i in range(item_num):
            byte_pos = item_len * i
            handle = hci_msg.data[byte_pos : byte_pos + Constants.HANDLE_BYTE_LEN]
            byte_pos += Constants.HANDLE_BYTE_LEN
            uuid = hci_msg.data[byte_pos : byte_pos + uuid_len]
            self.char_data_list.append(CharData(handle, uuid))

    def process_incoming_npi_msg(self, hci_msg_rx):
        self.handle_ack(hci_msg_rx)

        if self.ack_received():
            if hci_msg_rx.get_event() == Event.ATT_FindInfoRsp:
                msg_data = RxMsgAttFindInfoRsp(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.handle_char_resp(msg_data)
                elif msg_data.status == Constants.BLE_PROCEDURE_COMPLETE:
                    self.complete(msg=Messages.DEV_CHAR_DISCOVER_RESP,
                                  data={"conn_handle": self.conn_handle,
                                        "status" : STATUS_SUCCESS,
                                        "chars": self.char_data_list})
