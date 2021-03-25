from app.applications.devices.interceptors.ack_handler import HciAckHandler
from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import Event, Type, OpCode, Constants, TxPackGattDiscoverAllPrimaryServices, \
    STATUS_SUCCESS, RxMsgAttReadByGrpTypeRsp, TxPackHciLeSetDataLenReq, RxMsgHciLeGenericReportEvtRsp
from app.middleware.messages import Messages


class MtuCfgInterceptHandler(HciInterceptHandler, HciAckHandler):
    TX_OCTETS = 0x00FB
    TX_TIME = 0x0848

    def __init__(self, data_sender, complete_cb, conn_handle):
        self.ext_complete_cb = complete_cb
        self.data_sender = data_sender
        self.conn_handle = conn_handle
        HciAckHandler.__init__(self, [
            Event.HCI_CommandCompleteEvent
        ])
        self.svc_list = []

    def handle_mtu_cfg_resp(self, svc_resp):
        pass
        # item_len = svc_resp.length
        # item_num = (svc_resp.pdu_len - 1) // item_len
        # uuid_len = item_len - 2 * Constants.HANDLE_BYTE_LEN
        #
        # for i in range(item_num):
        #     pos = item_len * i + 2 * Constants.HANDLE_BYTE_LEN
        #     svc_uuid = svc_resp.value[pos : pos + uuid_len]
        #
        #     if len(svc_uuid) == Constants.GAP_ADTYPE_16BIT_MORE:
        #         svc_uuid = int.from_bytes(svc_uuid, byteorder='little')
        #
        #     self.svc_list.append(svc_uuid)

    def start(self):
        tx_msg = TxPackHciLeSetDataLenReq(Type.LinkCtrlCommand,
                                          OpCode.HciLe_SetDataLength,
                                          self.conn_handle,
                                          self.TX_OCTETS,
                                          self.TX_TIME)
        self.data_sender(tx_msg.buf_str)

    def complete(self, msg=None, data=None):
        self.ext_complete_cb(msg, data)

    def abort(self):
        pass

    def process_incoming_npi_msg(self, hci_msg_rx):
        ack_packet = self.handle_ack(hci_msg_rx)

        if self.ack_received() and not ack_packet:
            if hci_msg_rx.code == Event.HCI_LE_GenericReportEvent:
                msg_data = RxMsgHciLeGenericReportEvtRsp(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.handle_mtu_cfg_resp(msg_data)
                    self.complete(msg=Messages.DEV_MTU_CFG_RESP,
                                  data={"conn_handle": self.conn_handle,
                                        "status" : STATUS_SUCCESS})
