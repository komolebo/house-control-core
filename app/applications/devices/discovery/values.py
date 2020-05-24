import struct

from app.applications.devices.blenet.ack_handler import HciAckHandler
from app.applications.devices.discovery.chars import CharData
from app.applications.devices.hci_handler import HciInterceptHandler
from app.applications.devices.profiles.profile_data import ProfileTable
from app.applications.devices.profiles.profile_uuid import CharUuid
from app.applications.npi.hci_types import Event, Type, OpCode, \
    TxPackGattReadMultiCharValues, RxMsgAttReadMultiResp, STATUS_SUCCESS
from app.middleware.messages import Messages


class CharValueData(CharData):
    def __init__(self, handle, uuid, value):
        super().__init__(handle, uuid, byte_format=False)
        self.value = value


class ValDiscInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, complete_cb, disc_handler, conn_handle):
        self.conn_handle = conn_handle
        self.data_sender = data_sender
        self.ext_complete_cb = complete_cb
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus
        ])
        self.disc_handler = disc_handler
        self.value_data_list = []

        dev_type = disc_handler.handle_info[conn_handle].dev_type
        self.uuid_list = ProfileTable.char_dev_map[dev_type]
        self.handles = [disc_handler.get_handle_by_uuid(conn_handle, uuid)[0] for uuid in self.uuid_list]

    def start(self):
        handle_buf = [i for sub in [struct.pack('<H', handle) for handle in self.handles] for i in sub]
        tx_msg = TxPackGattReadMultiCharValues(Type.LinkCtrlCommand,
                                               OpCode.GATT_ReadMultiCharValues,
                                               self.conn_handle,
                                               bytearray(handle_buf))
        self.data_sender(tx_msg.buf_str)

    def complete(self, msg=None, data=None):
        self.ext_complete_cb(msg, data)

    def abort(self):
        pass

    def handle_multi_char_resp(self, msg_data):
        # uuid_list = [self.disc_handler.get_uuid_by_handle(handle) for handle in self.handles]
        pos = 0
        for (uuid, handle) in zip(self.uuid_list, self.handles):
            if pos < msg_data.pdu_len:
                char_info = CharUuid.get_data_obj_by_uuid(uuid)
                if char_info.fixed_len:
                    value = msg_data.value[pos : pos + char_info.length]
                else:  # data not fixed, search to next null-terminate char
                    rest_buf_str = msg_data.value[pos:].decode('utf-8')
                    value = rest_buf_str.split('\0')[0]
                char_val_data = CharValueData(handle, uuid, value)
                self.value_data_list.append(char_val_data)
                pos += len(value)

    def process_incoming_npi_msg(self, hci_msg_rx):
        self.handle_ack(hci_msg_rx)

        if self.ack_received():
            if hci_msg_rx.get_event() == Event.ATT_ReadMultiRsp:
                msg_data = RxMsgAttReadMultiResp(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.handle_multi_char_resp(msg_data)
                    self.complete(msg=Messages.DEV_VALUES_DISCOVER_RESP,
                                  data={"conn_handle": self.conn_handle,
                                        "char_value_data": self.value_data_list})
