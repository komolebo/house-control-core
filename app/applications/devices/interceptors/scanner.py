import base64
import json

import struct

from app.applications.devices.interceptors.ack_handler import HciAckHandler
from app.applications.devices.interceptors.hci_handler import HciInterceptHandler
from app.applications.npi.hci_types import TxPackGapScan, Type, OpCode, Event, STATUS_SUCCESS, RxMsgGapAdvertiserScannerEvent, EventId, Constants
from app.middleware.messages import Messages


class ScanSettings:
    period = 0
    scanDuration = 500
    maxNumRecords = 40


class ScanData:
    def __init__(self, address, dev_type, rssi):
        self.type = dev_type
        self.rssi = rssi
        self.mac = str(bytes(address).hex())

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class ScanFilter:
    @staticmethod
    def decode_advert_data(adv_data):
        report_svc = None
        device_type = None

        try:
            pos = 0
            while pos < len(adv_data):
                data_len = adv_data[pos]
                data = adv_data[pos + 1 : pos + 1 + data_len]
                if data[0] == Constants.GAP_ADTYPE_FLAGS:
                    pass
                elif data[0] == Constants.GAP_ADTYPE_16BIT_MORE:
                    data = data[1:]
                    report_svc = [data[2*i:(2*i)+2] for i in range(int(len(data)/2))]
                elif data[0] == Constants.GAP_ADTYPE_LOCAL_NAME_COMPLETE:
                    device_type = data[1:].decode("utf-8").strip().lower()
                pos += data_len + 1
        except IndexError:
            pass
        return report_svc, device_type

    @staticmethod
    def scanned_device_approved(report_svc, device_type):
        if report_svc is None or device_type is None:
            return False

        for reported_service in report_svc:
            svc_uuid = int.from_bytes(reported_service, byteorder='little')
            if svc_uuid not in (Constants.OAD_RESET_SERVICE_UUID, Constants.OAD_SERVICE_UUID):
                return False

        if not str(device_type).lower().strip() == "motion":
            return False

        return True


class ScanInterceptHandler(HciInterceptHandler, HciAckHandler):
    def __init__(self, data_sender, complete_cb):
        self.data_sender = data_sender
        self.ext_complete_cb = complete_cb
        HciAckHandler.__init__(self, [
            Event.GAP_HCI_ExtentionCommandStatus, # HCI ASK
        ])
        self.scan_list = []

    def start(self):
        tx_msg = TxPackGapScan(Type.LinkCtrlCommand,
                               OpCode.GapScan_enable,
                               ScanSettings.period,
                               ScanSettings.scanDuration,
                               ScanSettings.maxNumRecords)
        self.data_sender(tx_msg.buf_str)

    @classmethod
    def parse_advert_data(cls, adv_data):
        pass

    def complete(self, msg=None, data=None):
        self.ext_complete_cb(msg, data)

    def abort(self):
        self.ext_complete_cb(self.scan_list)

    def process_advertisement(self, adv_scan_msg):
        if adv_scan_msg.status == STATUS_SUCCESS:
            data = adv_scan_msg.data

            # TODO: parse here data to select its device type
            (reported_services, device_type) = ScanFilter.decode_advert_data(data)
            # print("reported data: {0}, {1}".format(reported_services, device_type))
            if ScanFilter.scanned_device_approved(reported_services, device_type):
                scan_data = ScanData(address=adv_scan_msg.address,
                                     dev_type=device_type,
                                     rssi=adv_scan_msg.rssi)
                self.scan_list.append(scan_data)

    def process_incoming_npi_msg(self, hci_msg_rx):
        valid_resp = False

        # Assume scan request is sent, collect response
        self.handle_ack(hci_msg_rx)

        if self.ack_received():
        # if not all ACK received
            if hci_msg_rx.get_event() == Event.GAP_AdvertiserScannerEvent:
                msg_data = RxMsgGapAdvertiserScannerEvent(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    if msg_data.event_id in (EventId.GAP_EVT_ADV_REPORT, EventId.GAP_EVT_SCAN_DISABLED):
                        valid_resp = True

        # ACK received and current response is not a previous ACK
        if valid_resp and not len(self.ack_list):
            scan_report_msg_data = RxMsgGapAdvertiserScannerEvent(hci_msg_rx.data)
            if scan_report_msg_data.event_id == EventId.GAP_EVT_ADV_REPORT:
                self.process_advertisement(scan_report_msg_data)
            elif scan_report_msg_data.event_id == EventId.GAP_EVT_SCAN_DISABLED:
                # assert(len(self.scan_list) == scan_report_msg_data.number_of_reports,
                #        "{0} != {1}".format(len(self.scan_list), scan_report_msg_data.number_of_reports))
                self.complete(msg=Messages.SCAN_DEVICE_RESP,
                              data={"data": self.scan_list,
                                    "status": STATUS_SUCCESS})
