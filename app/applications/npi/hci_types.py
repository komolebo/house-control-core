import struct

STATUS_SUCCESS = 0


class Constants:
    GAP_ADTYPE_FLAGS = 0x01
    GAP_ADTYPE_16BIT_MORE = 0x02
    GAP_ADTYPE_LOCAL_NAME_COMPLETE = 0x09
    OAD_SERVICE_UUID = 0xFFC0
    OAD_RESET_SERVICE_UUID = 0xFFD0


class Type:
    LinkCtrlCommand = 0x01
    HciPolicyCommand = 0x02
    HostControllerAndBaseband = 0x03
    HciEvent = 0x04


class EventCode:
    HCI_LE_ExtEvent = 0x00FF
    HCI_LE_GenericReportEvent = 0x003E


class OpCode:
    # transmit codes
    GapScan_enable = 0xFE51
    HCI_LEReadRemoteUsedFeatures = 0x2016
    GATT_DiscPrimaryServiceByUUID = 0xFD86
    ATT_FindByTypeValueReq = 0x06
    GAP_UpdateLinkParamReq = 0xFE11
    ATT_DiscAllCharDescs = 0xFD84
    GATT_WriteCharValue = 0xFD92
    ATT_ExchangeMTUReq = 0xFD02
    GATT_WriteNoRsp = 0xFDB6
    GATT_WriteLongCharValue = 0xFD96


class EventId:
    GAP_EVT_SCAN_ENABLED = 0x00010000
    GAP_EVT_SCAN_DISABLED = 0x00020000
    GAP_EVT_ADV_REPORT = 0x00400000


class Event:
    # receive codes
    GAP_HCI_ExtentionCommandStatus = 0x067F
    GAP_AdvertiserScannerEvent = 0x0613
    ATT_ErrorRsp = 0x0501
    ATT_FindByTypeValueRsp = 0x0507
    ATT_FindInfoRsp = 0x0505
    GAP_LinkParamUpdate = 0x0607
    ATT_WriteRsp = 0x0513
    ATT_ExchangeMTURsp = 0x0503
    ATT_MtuUpdatedEvt = 0x057F
    ATT_HandleValueNotification = 0x051B
    ATT_ExecuteWriteRsp = 0x0519
    GAP_TerminateLink = 0x0606


# ------------------------------------------------------------------------
# Abstract Tx structure class
class TxPackBase:
    def __init__(self):
        self.buf_str = None

    def as_binary(self):
        print("Dump TX: ", self.buf_str)
        return self.buf_str



class HciPackageRx:
    HCI_RX_EVENT_BYTE_LEN = 0x02

    def __init__(self, type, code, len, data):
        self.type = type
        self.code = code
        self.len = len
        self.data = data

    def get_event(self):
        if self.data:
            event = self.data[0:self.HCI_RX_EVENT_BYTE_LEN]
            return int.from_bytes(event, byteorder='little', signed=False)
        return None

    def as_output(self):
        str = ""
        str += hex(self.type)
        str += ' '
        str += hex(self.code)
        str += ' '
        str += hex(self.len)
        str += ' '
        for ch in self.data:
            str += hex(ch)
            str += ' '
        return str

    def is_valid(self):
        if not self.len:
            return False
        return True


# ------------------------------------------------------------------------
# Gap scan
class TxPackGapScan(TxPackBase):
    pattern = '<BHBHHH'
    DATA_LEN = 6

    def __init__(self, type, op_code, period, duration, max_num_records):
        super().__init__()
        data_length = self.DATA_LEN
        self.buf_str = struct.pack(self.pattern,
                                   type,
                                   op_code,
                                   data_length,
                                   period,
                                   duration,
                                   max_num_records)


class RxMsgGapAdvertiserScannerEvent:
    SCAN_ENABLED_MSG_LEN = 0x07
    SCAN_DISABLED_MSG_LEN = 0x09

    def __init__(self, data_bytes):
        if len(data_bytes) == self.SCAN_ENABLED_MSG_LEN:
            pattern = '<HBI'
            fields = struct.unpack(pattern, data_bytes)
            (self.event,
             self.status,
             self.event_id) = fields
        elif len(data_bytes) == self.SCAN_DISABLED_MSG_LEN:
            pattern = '<HBIBB'
            fields = struct.unpack(pattern, data_bytes)
            (self.event,
             self.status,
             self.event_id,
             self.end_reason,
             self.number_of_reports) = fields
        else:
            # TODO: remove magic number
            data_len = len(data_bytes) - self.SCAN_ENABLED_MSG_LEN - 24
            pattern = '<HBIBB6sBBBBBB6sHH{0}s'.format(data_len)
            fields = struct.unpack(pattern, data_bytes)
            (self.event,
             self.status,
             self.event_id,
             self.adv_rpt_event_type,
             self.address_type,
             self.address,
             self.primary_phy,
             self.secondary_phy,
             self.adv_sid,
             self.tx_power,
             self.rssi,
             self.direct_addr_type,
             self.direct_addr,
             self.periodic_adv_int,
             self.data_length,
             self.data) = fields


# ------------------------------------------------------------------------
# Write char value handlers
class TxPackWriteCharValue(TxPackBase):
    pattern = '<BHBHHH'

    def __init__(self, type, op_code, len, conn_handle, handle, value):
        super().__init__()
        self.buf_str = struct.pack(self.pattern,
                                   type,
                                   op_code,
                                   len,
                                   conn_handle,
                                   handle,
                                   value)


class RxMsgAttWriteRsp:
    pattern = '<HBHB'

    def __init__(self, data_bytes):
        fields = struct.unpack(self.pattern, data_bytes)
        (self.event,
         self.status,
         self.conn_handle,
         self.pdu_len) = fields


# ------------------------------------------------------------------------
# Write no response
class TxPackWriteNoRsp(TxPackBase):
    HANDLES_BYTE_LEN = 0x04

    def __init__(self, type, op_code, data_length, conn_handle, handle, value):
        pattern = '<BHBHH{0}s'.format(data_length - self.HANDLES_BYTE_LEN)
        super().__init__()
        self.buf_str = struct.pack(pattern,
                                   type,
                                   op_code,
                                   data_length,
                                   conn_handle,
                                   handle,
                                   value)


# ------------------------------------------------------------------------
# Write long char values
class TxPackWriteLongCharValue(TxPackBase):
    def __init__(self, type, op_code, data_length, conn_handle, handle, offset, value):
        super().__init__()
        pattern = '<BHBHHH{0}s'.format(len(value))
        self.buf_str = struct.pack(pattern,
                                   type,
                                   op_code,
                                   data_length,
                                   conn_handle,
                                   handle,
                                   offset,
                                   value)


class RxMsgAttExecuteWriteRsp:
    pattern = '<HBHB'

    def __init__(self, data_bytes):
        fields = struct.unpack(self.pattern, data_bytes)
        (self.event,
         self.status,
         self.conn_handle,
         self.pdu_len) = fields

# ------------------------------------------------------------------------
# MTU exchange handlers
class TxPackAttExchangeMtuReq(TxPackBase):
    pattern = '<BHBHH'

    def __init__(self, type, op_code, data_length, conn_handle, client_rx_mtu):
        super().__init__()
        self.buf_str = struct.pack(self.pattern,
                                   type,
                                   op_code,
                                   data_length,
                                   conn_handle,
                                   client_rx_mtu)


class RxMsgAttExchangeMtuRsp:
    pattern = '<HBHBH'

    def __init__(self, data_bytes):
        fields = struct.unpack(self.pattern, data_bytes)
        (self.event,
         self.status,
         self.conn_handle,
         self.pdu_len,
         self.server_rx_mtu) = fields


class RxMsgAttMtuUpdatedEvt:
    pattern = '@HBHBH'

    def __init__(self, data_bytes):
        fields = struct.unpack(self.pattern, data_bytes)
        (self.event,
         self.status,
         self.conn_handle,
         self.pdu_len,
         self.mtu) = fields


# ------------------------------------------------------------------------
# Handle value notification responses
class RxMsgAttHandleValueNotification:
    def __init__(self, data_bytes, exp_val_len):
        pattern = '<HBHBH{0}s'.format(exp_val_len)
        fields = struct.unpack(pattern, data_bytes)
        (self.event,
         self.status,
         self.conn_handle,
         self.pdu_len,
         self.handle,
         self.value) = fields


# ------------------------------------------------------------------------
# Rest HCI handlers
class RxMsgGapHciExtentionCommandStatus:
    pattern = '<HBHB'

    def __init__(self, data_bytes):
        fields = struct.unpack(self.pattern, data_bytes)
        (self.event,
         self.status,
         self.op_code,
         self.data_length) = fields

class RxMsgGapTerminateLink:
    pattern = '<HBHB'
    def __init__(self, data_bytes):
        fields = struct.unpack(self.pattern, data_bytes)
        (self.event,
         self.status,
         self.conn_handle,
         self.reason) = fields