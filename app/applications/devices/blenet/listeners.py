from abc import abstractmethod

from app.applications.npi.hci_types import Event, RxMsgGapTerminateLink, STATUS_SUCCESS
from app.middleware.messages import Messages


class BaseListenHandler:
    @staticmethod
    @abstractmethod
    def listen(hci_msg, response_cb):
        pass


class DisconnectListenHandler(BaseListenHandler):
    @staticmethod
    def listen(hci_msg, response_cb):
        if hci_msg.get_event() == Event.GAP_TerminateLink:
            msg_data = RxMsgGapTerminateLink(hci_msg.data)
            if msg_data.status == STATUS_SUCCESS:
                response_cb(msg=Messages.DEVICE_DISCONN,
                            data={"reason": msg_data.reason,
                                  "conn_handle": msg_data.conn_handle})


class IndicateListenHandler(BaseListenHandler):
    @staticmethod
    def listen(hci_msg, response_cb):
        pass
