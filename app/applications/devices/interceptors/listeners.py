from abc import abstractmethod

from app.applications.npi.hci_types import Event, RxMsgGapTerminateLink, STATUS_SUCCESS, \
    RxMsgAttHandleValueNotification, TxPackAttHandleValueConfirmation, Type, OpCode
from app.middleware.messages import Messages


class BaseListenHandler:
    @staticmethod
    @abstractmethod
    def listen(hci_msg, complete_cb):
        pass

class BaseListenAckHandler:
    @staticmethod
    @abstractmethod
    def listen(hci_msg, complete_cb, data_sender):
        pass


class DisconnectListenHandler(BaseListenHandler):
    @staticmethod
    def listen(hci_msg, complete_cb):
        if hci_msg.get_event() == Event.GAP_TerminateLink:
            msg_data = RxMsgGapTerminateLink(hci_msg.data)
            if msg_data.status == STATUS_SUCCESS:
                complete_cb(msg=Messages.DEVICE_DISCONN,
                            data={"reason": msg_data.reason,
                                  "conn_handle": msg_data.conn_handle})


class NotifyListenHandler(BaseListenAckHandler):
    @staticmethod
    def listen(hci_msg, complete_cb, data_sender):
        if hci_msg.get_event() == Event.ATT_HandleValueNotification:
            msg_data = RxMsgAttHandleValueNotification(hci_msg.data)
            if msg_data.status == STATUS_SUCCESS:
                # send ACK
                ack_msg = TxPackAttHandleValueConfirmation(Type.LinkCtrlCommand,
                                                           OpCode.ATT_HandleValueConfirmation,
                                                           msg_data.conn_handle)
                data_sender(ack_msg.buf_str)

                # process data
                complete_cb(msg=Messages.DEV_INDICATION,
                            data={"conn_handle": msg_data.conn_handle,
                                  "handle": msg_data.handle,
                                  "value": msg_data.value})
