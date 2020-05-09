from app.npi.hci import EventCode, OpCode, Type, Event, RxMsgGapHciExtentionCommandStatus, \
    STATUS_SUCCESS, RxMsgAttWriteRsp, TxPackWriteCharValue, TxPackAttExchangeMtuReq, RxMsgAttExchangeMtuRsp, \
    RxMsgAttMtuUpdatedEvt, RxMsgAttHandleValueNotification, TxPackWriteNoRsp, TxPackWriteLongCharValue, \
    RxMsgAttExecuteWriteRsp
from app.npi.npi_manager import NpiManager


SERVER_RX_MTU_SIZE = 0x00F7
block_size = 0x0


class FirmwareBin:
    def __init__(self, bin_path):
        self.bin_path = bin_path
        with open(self.bin_path, "rb") as f:
            self.binary_data = list(f.read())
            self.firmware_len = len(list(self.binary_data))
            self.curr_block = 0

    def set_mtu_size(self, mtu_size):
        self.mtu_size = mtu_size
        self.blocks_num = self.firmware_len / mtu_size + (self.firmware_len % mtu_size)

    def get_blocks_number(self):
        return self.blocks_num

    def get_next_block(self):
        if self.curr_block < self.blocks_num:
            return self.binary_data[self.curr_block * self.mtu_size : (self.curr_block + 1) * self.mtu_size]
        return None

class State:
    def __init__(self, fsm):
        self.error = 0
        self.fsm = fsm

    def handle_error(self):
        self.error = 1
        # TODO: define func later
        assert "error happened"

    def handle_notifications_on_setup(self, hci_msg_rx):
        if hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.msg_data, 3)

            if msg_data.status == STATUS_SUCCESS and msg_data.conn_handle == self.fsm.conn_handle:
                # TODO: handle here receive MTU size
                pass


class StateOadIdle(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def on_event(self, msg):
        print("Oad should be started on host's demand")
        exit(-1)


class StateOadNotifyEnable(State):
    # constants
    NOTIFY_REQ_BYTE_LEN = 0x06
    IMG_ID_CFG_HANDLE = 0x000C
    IMG_CTRL_CFG_HANDLE = 0x0014
    CFG_ENABLE_VALUE = 0x0100
    REQUIRED_ACK_NUM = 2

    def __init__(self, fsm):
        super().__init__(fsm)
        self.conn_handle = self.fsm.conn_handle

        # set needed ACKs to successfully complete notification
        self.identify_ack_getlist = [
            Event.GAP_HCI_ExtentionCommandStatus, # host ACK
            Event.ATT_WriteRsp # peripheral ACK
        ]
        self.control_ack_getlist = [
            Event.GAP_HCI_ExtentionCommandStatus,  # host ACK
            Event.ATT_WriteRsp  # peripheral ACK
        ]

        self._enable_identify_notify()

    def _enable_identify_notify(self):
        # Enable image identify config
        tx_msg = TxPackWriteCharValue(Type.LinkCtrlCommand,
                                      OpCode.GATT_WriteCharValue,
                                      self.NOTIFY_REQ_BYTE_LEN,
                                      self.conn_handle,
                                      self.IMG_ID_CFG_HANDLE,
                                      self.CFG_ENABLE_VALUE)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def _enable_control_notify(self):
        # enable control notification config
        tx_msg = TxPackWriteCharValue(Type.LinkCtrlCommand,
                                      OpCode.GATT_WriteCharValue,
                                      self.NOTIFY_REQ_BYTE_LEN,
                                      self.conn_handle,
                                      self.IMG_CTRL_CFG_HANDLE,
                                      self.CFG_ENABLE_VALUE)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False
        # host stack ACK received:
        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.msg_data)

            # check wanted ACK type
            if len(self.identify_ack_getlist):
                # process image identify host stack ACK status
                if msg_data.status == STATUS_SUCCESS:
                    self.identify_ack_getlist.remove(msg_data.event)
                    valid_resp = True
                else:
                    self.handle_error()
            elif len(self.control_ack_getlist):
                # process image control host stack ACK status
                if msg_data.status == STATUS_SUCCESS:
                    self.control_ack_getlist.remove(msg_data.event)
                    valid_resp = True
                else:
                    self.handle_error()
            else:
                # unexpected package receive, TODO: check with multiple connections
                self.handle_error()

        # target device's ACK received:
        elif hci_msg_rx.get_event() == Event.ATT_WriteRsp:
            msg_data = RxMsgAttWriteRsp(hci_msg_rx.msg_data)

            # check wanted ACK type
            if len(self.identify_ack_getlist):
                # process image identify host stack ACK status
                if msg_data.status == STATUS_SUCCESS and msg_data.conn_handle == self.fsm.conn_handle:
                    self.identify_ack_getlist.remove(msg_data.event)
                    valid_resp = True
                else:
                    self.handle_error()
            elif len(self.control_ack_getlist):
                # process image control host stack ACK status
                if msg_data.status == STATUS_SUCCESS and msg_data.conn_handle == self.fsm.conn_handle:
                    self.control_ack_getlist.remove(msg_data.event)
                    valid_resp = True

        # all notifications are enabled, transit to next state
        if not len(self.identify_ack_getlist) and not len(self.control_ack_getlist):
            self.fsm.transit(StateOadExchangeMtu)
        # identify notification cfg just ACK'ed
        elif not len(self.identify_ack_getlist) and len(self.control_ack_getlist) == self.REQUIRED_ACK_NUM:
            # if good resp received:
            if valid_resp:
                self._enable_control_notify()


class StateOadExchangeMtu(State):
    EXCHANGE_MTU_REQ_BYTE_LEN = 0x04

    def __init__(self, fsm):
        super().__init__(fsm)

        self.mtu_ack_getlist = [
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_ExchangeMTURsp,
            Event.ATT_MtuUpdatedEvt # TODO: not sure if necessarily required
        ]

        self._exchange_mtu_size()

    def _exchange_mtu_size(self):
        tx_msg = TxPackAttExchangeMtuReq(Type.LinkCtrlCommand,
                                         OpCode.ATT_ExchangeMTUReq,
                                         self.EXCHANGE_MTU_REQ_BYTE_LEN,
                                         self.fsm.conn_handle,
                                         SERVER_RX_MTU_SIZE)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False

        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.msg_data)

            if msg_data.status == STATUS_SUCCESS:
                self.mtu_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_ExchangeMTURsp:
            msg_data = RxMsgAttExchangeMtuRsp(hci_msg_rx.msg_data)

            if msg_data.status == STATUS_SUCCESS:
                self.mtu_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_MtuUpdatedEvt:
            msg_data = RxMsgAttMtuUpdatedEvt(hci_msg_rx.msg_data)

            if msg_data.status == STATUS_SUCCESS:
                self.mtu_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        # handle setup notifications response
        # self.handle_notifications_on_setup(hci_msg_rx)

        if valid_resp:
            # all ACKs received
            if not len(self.mtu_ack_getlist):
                self.fsm.transit(StateOadSetControl, StateOadSetControl.OAD_EXT_CTRL_GET_BLK_SZ)


class StateOadSetControl(State):
    OAD_EXT_CTRL_GET_BLK_SZ = 0x01
    OAD_EXT_CTRL_START_OAD = 0x03
    SET_CTRL_REQ_BYTE_LEN = 0x05
    CONTROL_VALUE_HANDLE = 0x0013

    def __init__(self, fsm, param):
        super().__init__(fsm)
        self.control_ack_getlist = [
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_HandleValueNotification
        ]
        self.ctrl_command = param
        self._set_control_value(self.ctrl_command)

    def _set_control_value(self, value):
        tx_msg = TxPackWriteNoRsp(Type.LinkCtrlCommand,
                                  OpCode.GATT_WriteNoRsp,
                                  self.SET_CTRL_REQ_BYTE_LEN,
                                  self.fsm.conn_handle,
                                  self.CONTROL_VALUE_HANDLE,
                                  value)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False
        global block_size

        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.msg_data)

            if msg_data.status == STATUS_SUCCESS:
                self.control_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.msg_data, 3)

            if msg_data.status == STATUS_SUCCESS:
                block_size = msg_data.value[1:3]  # TODO: handle magic number
                self.control_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        # control cmd done, switch to next state
        if valid_resp and not len(self.control_ack_getlist):
            # after managing block size transit to meta state
            if self.ctrl_command == self.OAD_EXT_CTRL_GET_BLK_SZ:
                self.fsm.transit(StateOadSetMeta)
            # once metadata set, start writing OAD blocks
            elif self.ctrl_command == self.OAD_EXT_CTRL_START_OAD:
                self.fsm.transit(StateOadWriteBlock)


class StateOadSetMeta(State):
    SET_META_REQ_BYTE_LEN = 0x1C
    IDENTIFY_VALUE_HANDLE = 0x000B

    def __init__(self, fsm):
        super().__init__(fsm)
        self.meta_ack_getlist = [
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_ExecuteWriteRsp,
            Event.ATT_HandleValueNotification
        ]
        self._set_identify()

    def _set_identify(self):
        tx_msg = TxPackWriteLongCharValue(Type.LinkCtrlCommand,
                                          OpCode.GATT_WriteLongCharValue,
                                          self.SET_META_REQ_BYTE_LEN,
                                          self.fsm.conn_handle,
                                          self.IDENTIFY_VALUE_HANDLE,
                                          0x0000,
                                          0)  # TODO: fill value
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False

        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.msg_data)

            if msg_data.status == STATUS_SUCCESS:
                self.meta_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_ExecuteWriteRsp:
            msg_data = RxMsgAttExecuteWriteRsp(hci_msg_rx.msg_data)

            if msg_data.status == STATUS_SUCCESS:
                self.meta_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.msg_data, 1)

            if msg_data.status == STATUS_SUCCESS:
                self.meta_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        if valid_resp and not len(self.meta_ack_getlist):
            self.fsm.transit(StateOadSetControl, StateOadSetControl.OAD_EXT_CTRL_START_OAD)


class StateOadWriteBlock(State):
    def __init__(self, fsm):
        super().__init__(fsm)
        self.blocks_written = 0

    def on_event(self, msg):
        pass


class OadFsm:
    conn_handle = 0xFFFF

    def __init__(self, conn_handle, npi_manager):
        self.state = StateOadIdle(self)
        self.conn_handle = conn_handle
        self.npi = npi_manager
        self.firmware = FirmwareBin('oad.bin')

    def on_event(self, hci_msg):
        self.state.on_event(hci_msg)

    def transit(self, state_class, param = None):
        if param is None:
            self.state = state_class(self)
        else:
            self.state = state_class(self, param)

    def start(self):
        self.transit(StateOadNotifyEnable)
