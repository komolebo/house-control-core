import struct

STATUS_SUCCESS = 0


class Constants:
    CHIP_RESET = 0x00

    GAP_ADTYPE_FLAGS = 0x01
    GAP_ADTYPE_16BIT_MORE = 0x02
    GAP_ADTYPE_LOCAL_NAME_COMPLETE = 0x09

    OAD_SERVICE_UUID = 0xFFC0
    OAD_RESET_SERVICE_UUID = 0xFFD0

    PEER_ADDRTYPE_PUBLIC_OR_PUBLIC_ID = 0x00
    INIT_PHY_1M = 0x01
    INIT_PHYPARAM_CONN_INT_MIN = 0x02
    INIT_PHYPARAM_CONN_INT_MAX = 0x03
    INIT_PHYPARAM_CONN_LATENCY = 0x04
    INIT_PHYPARAM_SUP_TIMEOUT = 0x05

    PROFILE_ROLE_CENTRAL = 0x08
    ADDRMODE_PUBLIC = 0x00

    REMOTE_USER_TERMINATED = 0x13


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
    HCIExt_ResetSystemCmd = 0xFC1D
    GapInit_getPhyParam = 0xFE61
    GapScan_enable = 0xFE51
    Gap_DeviceInit = 0xFE00
    GapInit_connect = 0xFE62
    HCI_LEReadRemoteUsedFeatures = 0x2016
    GATT_DiscPrimaryServiceByUUID = 0xFD86
    ATT_FindByTypeValueReq = 0x06
    GAP_UpdateLinkParamReq = 0xFE11
    ATT_DiscAllCharDescs = 0xFD84
    GATT_WriteCharValue = 0xFD92
    ATT_ExchangeMTUReq = 0xFD02
    GATT_WriteNoRsp = 0xFDB6
    GATT_WriteLongCharValue = 0xFD96
    GAP_TerminateLinkRequest = 0xFE0A


class EventId:
    GAP_EVT_SCAN_ENABLED = 0x00010000
    GAP_EVT_SCAN_DISABLED = 0x00020000
    GAP_EVT_ADV_REPORT = 0x00400000


class Event:
    # receive codes
    GAP_HCI_ExtentionCommandStatus = 0x067F
    GAP_DeviceInitDone = 0x0600
    HCIExt_ResetSystemCmdDone = 0x041D
    GAP_AdvertiserScannerEvent = 0x0613
    GAP_EstablishLink = 0x0605
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
# Device reset
class TxPackHciExtResetSystemCmd(TxPackBase):
    pattern = '<BHBB'

    def __init__(self, type, op_code, reset_type):
        super().__init__()
        data_length = 1
        self.buf_str = struct.pack(self.pattern,
                                   type,
                                   op_code,
                                   data_length,
                                   reset_type)


class RxMsgGapHciExtResetSystemCmdDone:
    pattern = '<HBH'

    def __init__(self, data_bytes):
        fields = struct.unpack(self.pattern, data_bytes)
        (self.event,
         self.status,
         self.cmd_op_code) = fields

# ------------------------------------------------------------------------
# Device init
class TxPackGapDeviceInit(TxPackBase):
    pattern = '<BHBBB6s'
    DATA_LEN = 0x08

    def __init__(self, type, op_code, profile_role, addr_mode, random_addr):
        super().__init__()
        data_length = self.DATA_LEN
        self.buf_str = struct.pack(self.pattern,
                                   type,
                                   op_code,
                                   data_length,
                                   profile_role,
                                   addr_mode,
                                   random_addr)


class RxMsgGapDeviceInitDone:
    pattern = '<HB6sHB16s16s'

    def __init__(self, data_bytes):
        fields = struct.unpack(self.pattern, data_bytes)
        (self.event,
         self.status,
         self.dev_addr,
         self.data_pkt_len,
         self.num_data_pkt,
         self.irk,
         self.csrk) = fields


# ------------------------------------------------------------------------
# Device setup
class TxPackGapInitGetPhyParam(TxPackBase):
    pattern = '<BHBBB'
    DATA_LEN = 0x02

    def __init__(self, type, op_code, phy, param_id):
        super().__init__()
        data_length = self.DATA_LEN
        self.buf_str = struct.pack(self.pattern,
                                   type,
                                   op_code,
                                   data_length,
                                   phy,
                                   param_id)


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
# Init connect
class TxPackGapInitConnect(TxPackBase):
    pattern = '<BHBB6sBH'
    DATA_LEN = 0x0A

    def __init__(self, type, op_code, peer_addr_type, peer_addr, initiating_phy, timeout):
        super().__init__()
        data_length = self.DATA_LEN
        self.buf_str = struct.pack(self.pattern,
                                   type,
                                   op_code,
                                   data_length,
                                   peer_addr_type,
                                   peer_addr,
                                   initiating_phy,
                                   timeout)


class RxMsgGapInitConnect:
    pattern = '<HBB6sHBHHHB'

    def __init__(self, data_bytes):
        fields = struct.unpack(self.pattern, data_bytes)
        (self.event,
         self.status,
         self.dev_addr_type,
         self.dev_addr,
         self.conn_handle,
         self.conn_role,
         self.conn_interval,
         self.conn_latency,
         self.timeout,
         self.clock_accuracy) = fields


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
# Terminate connection
class TxPackGapTerminateLink(TxPackBase):
    pattern = '<BHBHB'

    def __init__(self, type, op_code, conn_handle, disc_reason):
        super().__init__()
        data_length = 3
        self.buf_str = struct.pack(self.pattern,
                                   type,
                                   op_code,
                                   data_length,
                                   conn_handle,
                                   disc_reason)

class RxMsgGapTerminateLink:
    pattern = '<HBHB'
    def __init__(self, data_bytes):
        fields = struct.unpack(self.pattern, data_bytes)
        (self.event,
         self.status,
         self.conn_handle,
         self.reason) = fields


# ------------------------------------------------------------------------
# Rest HCI handlers
class RxMsgGapHciExtentionCommandStatus:
    short_pattern = '<HBHB'
    long_pattern = '<HBHBBH'

    def __init__(self, data_bytes):
        if len(data_bytes) == struct.calcsize(self.short_pattern):
            (self.event,
             self.status,
             self.op_code,
             self.data_length) = struct.unpack(self.short_pattern, data_bytes)
        elif len(data_bytes) == struct.calcsize(self.long_pattern):
            (self.event,
             self.status,
             self.op_code,
             self.data_length,
             self.param_id,
             self.param_data) = struct.unpack(self.long_pattern, data_bytes)
