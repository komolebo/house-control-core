import struct

STATUS_SUCCESS = 0


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
    HCI_LEReadRemoteUsedFeatures = 0x2016
    GATT_DiscPrimaryServiceByUUID = 0xFD86
    ATT_FindByTypeValueReq = 0x06
    GAP_UpdateLinkParamReq = 0xFE11
    ATT_DiscAllCharDescs = 0xFD84
    GATT_WriteCharValue = 0xFD92
    ATT_ExchangeMTUReq = 0xFD02
    GATT_WriteNoRsp = 0xFDB6
    GATT_WriteLongCharValue = 0xFD96


class Event:
    # receive codes
    GAP_HCI_ExtentionCommandStatus = 0x067F
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