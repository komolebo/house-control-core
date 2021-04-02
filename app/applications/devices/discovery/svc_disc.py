from app.applications.devices.interceptors.ack_handler import HciAckHandler
from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import Event, Type, OpCode, Constants, TxPackGattDiscoverAllPrimaryServices, STATUS_SUCCESS, RxMsgAttReadByGrpTypeRsp
from app.middleware.messages import Messages


class SvcDiscInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, send_resp, complete_cb, conn_handle):
        self.ext_complete_cb = complete_cb
        self.data_sender = data_sender
        self.send_response = send_resp
        self.conn_handle = conn_handle
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus
        ])
        self.svc_list = []

    def handle_svc_resp(self, svc_resp):
        item_len = svc_resp.length
        item_num = (svc_resp.pdu_len - 1) // item_len
        uuid_len = item_len - 2 * Constants.HANDLE_BYTE_LEN

        for i in range(item_num):
            pos = item_len * i + 2 * Constants.HANDLE_BYTE_LEN
            svc_uuid = svc_resp.value[pos : pos + uuid_len]

            if len(svc_uuid) == Constants.GAP_ADTYPE_16BIT_MORE:
                svc_uuid = int.from_bytes(svc_uuid, byteorder='little')

            self.svc_list.append(svc_uuid)

    def start(self):
        tx_msg = TxPackGattDiscoverAllPrimaryServices(Type.LinkCtrlCommand,
                                                      OpCode.GATT_DiscAllPrimaryServices,
                                                      self.conn_handle)
        self.data_sender(tx_msg.buf_str)

    def complete(self, msg=None, data=None):
        self.send_response(msg, data)
        self.ext_complete_cb()

    def abort(self):
        pass

    def process_incoming_npi_msg(self, hci_msg_rx):
        self.handle_ack(hci_msg_rx)

        if self.ack_received():
            if hci_msg_rx.get_event() == Event.ATT_ReadByGrpTypeRsp:
                msg_data = RxMsgAttReadByGrpTypeRsp(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.handle_svc_resp(msg_data)
                elif msg_data.status == Constants.BLE_PROCEDURE_COMPLETE:
                    self.complete(msg=Messages.DEV_SVC_DISCOVER_RESP,
                                  data={"conn_handle": self.conn_handle,
                                        "status" : STATUS_SUCCESS,
                                        "services": self.svc_list})
