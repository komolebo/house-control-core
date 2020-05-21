from app.applications.npi.hci_types import STATUS_SUCCESS, RxMsgGapHciExtentionCommandStatus, Event


class HciAckHandler:
    def __init__(self, ack_list):
        self.ack_list = ack_list

    def handle_ack(self, hci_msg):
        valid_resp = False

        if len(self.ack_list):
            if hci_msg.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
                msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.ack_list.remove(msg_data.event)
                    valid_resp = True

            elif hci_msg.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
                msg_data = RxMsgGapTerminateLink(hci_msg.data)
                if msg_data.status == STATUS_SUCCESS:
                    self.ack_list.remove(msg_data.event)
                    self.central_ip = msg_data.dev_addr
                    valid_resp = True

        return valid_resp

    def ack_received(self):
        return not(len(self.ack_list))
