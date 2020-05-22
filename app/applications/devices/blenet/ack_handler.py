from app.applications.npi.hci_types import STATUS_SUCCESS, RxMsgGapHciExtentionCommandStatus, Event, \
    RxMsgGapTerminateLink


class HciAckHandler:
    def __init__(self, ack_list):
        self.ack_list = ack_list

    def handle_ack(self, hci_msg):
        if len(self.ack_list):
            if hci_msg.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
                msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.ack_list.remove(msg_data.event)
                    return True
        return False

    def ack_received(self):
        return not len(self.ack_list)
