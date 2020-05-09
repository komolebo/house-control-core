import struct

from app.npi.firmware import FirmwareBin
from app.npi.hci import OpCode, Type, Event, RxMsgGapHciExtentionCommandStatus, \
    STATUS_SUCCESS, RxMsgAttWriteRsp, TxPackWriteCharValue, TxPackAttExchangeMtuReq, RxMsgAttExchangeMtuRsp, \
    RxMsgAttMtuUpdatedEvt, RxMsgAttHandleValueNotification, TxPackWriteNoRsp, TxPackWriteLongCharValue, \
    RxMsgAttExecuteWriteRsp

SERVER_RX_MTU_SIZE = 0x00F7
mtu_size = 0x0



class State:
    def __init__(self, fsm):
        self.error = 0
        self.fsm = fsm

    def handle_error(self):
        print('error happened')
        self.error = 1
        # TODO: define func later
        assert "error happened"

    def handle_notifications_on_setup(self, hci_msg_rx):
        if hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.data, 3)

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
    CFG_ENABLE_VALUE = 0x0001
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
        print('enable identify notification')
        # Enable image identify config
        tx_msg = TxPackWriteCharValue(Type.LinkCtrlCommand,
                                      OpCode.GATT_WriteCharValue,
                                      self.NOTIFY_REQ_BYTE_LEN,
                                      self.conn_handle,
                                      self.IMG_ID_CFG_HANDLE,
                                      self.CFG_ENABLE_VALUE)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def _enable_control_notify(self):
        print('enable control notification')
        # enable control notification config
        tx_msg = TxPackWriteCharValue(Type.LinkCtrlCommand,
                                      OpCode.GATT_WriteCharValue,
                                      self.NOTIFY_REQ_BYTE_LEN,
                                      self.conn_handle,
                                      self.IMG_CTRL_CFG_HANDLE,
                                      self.CFG_ENABLE_VALUE)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        print('receive event in StateOadNotifyEnable')
        valid_resp = False
        # host stack ACK received:
        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            print('receive GAP_HCI_ExtentionCommandStatus')
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)

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
            print('receive ATT_WriteRsp')
            msg_data = RxMsgAttWriteRsp(hci_msg_rx.data)

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
            print('transit from STATE_ENABLE to STATE_MTU')
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
            # Event.ATT_MtuUpdatedEvt # TODO: not sure if necessarily required
        ]

        self._exchange_mtu_size()

    def _exchange_mtu_size(self):
        print('exchange mtu size')
        tx_msg = TxPackAttExchangeMtuReq(Type.LinkCtrlCommand,
                                         OpCode.ATT_ExchangeMTUReq,
                                         self.EXCHANGE_MTU_REQ_BYTE_LEN,
                                         self.fsm.conn_handle,
                                         SERVER_RX_MTU_SIZE)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False

        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            print('receive GAP_HCI_ExtentionCommandStatus')
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)

            if msg_data.status == STATUS_SUCCESS:
                self.mtu_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_ExchangeMTURsp:
            print('receive ATT_ExchangeMTURsp')
            msg_data = RxMsgAttExchangeMtuRsp(hci_msg_rx.data)

            if msg_data.status == STATUS_SUCCESS:
                self.mtu_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_MtuUpdatedEvt:
            print('receive ATT_MtuUpdatedEvt')
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
    OAD_EXT_CTRL_ENABLED_IMG = 0x04

    SET_CTRL_REQ_BYTE_LEN = 0x05
    CONTROL_VALUE_HANDLE = 0x0013

    def __init__(self, fsm, param):
        super().__init__(fsm)
        self.control_ack_getlist = [
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_HandleValueNotification
        ]
        self.ctrl_command = param
        if self.ctrl_command == self.OAD_EXT_CTRL_GET_BLK_SZ:
            self.exp_value_len_resp = 3
        elif self.ctrl_command == self.OAD_EXT_CTRL_START_OAD:
            self.exp_value_len_resp = 6

        self._set_control_value(self.ctrl_command)

    def _set_control_value(self, value):
        print('setting control value:', hex(value))
        value_arr = bytearray([value])
        tx_msg = TxPackWriteNoRsp(Type.LinkCtrlCommand,
                                  OpCode.GATT_WriteNoRsp,
                                  self.SET_CTRL_REQ_BYTE_LEN,
                                  self.fsm.conn_handle,
                                  self.CONTROL_VALUE_HANDLE,
                                  value_arr)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False
        global mtu_size

        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            print('receive GAP_HCI_ExtentionCommandStatus')
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)

            if msg_data.status == STATUS_SUCCESS:
                self.control_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            print('receive ATT_HandleValueNotification')
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.data, self.exp_value_len_resp)

            if msg_data.status == STATUS_SUCCESS:
                if self.ctrl_command == self.OAD_EXT_CTRL_GET_BLK_SZ:
                    mtu_size = int.from_bytes(msg_data.value[1:3], byteorder='little', signed=False)
                    print('block size = ', mtu_size)
                    self.fsm.firmware.set_mtu_size(mtu_size)
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
            # once new image enabled, OAD is done
                self.fsm.transit(StateOadIdle)


class StateOadSetMeta(State):
    SET_META_REQ_BYTE_LEN = 0x1C
    IDENTIFY_VALUE_HANDLE = 0x000B
    IMG_IDENTIFY_OFFSET = 0x0000

    def __init__(self, fsm):
        super().__init__(fsm)
        self.meta_ack_getlist = [
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_ExecuteWriteRsp,
            Event.ATT_HandleValueNotification
        ]
        self._set_identify()

    def _set_identify(self):
        print('set meta data identify')
        meta_data = self.fsm.firmware.get_metadata_value()
        tx_msg = TxPackWriteLongCharValue(Type.LinkCtrlCommand,
                                          OpCode.GATT_WriteLongCharValue,
                                          self.SET_META_REQ_BYTE_LEN,
                                          self.fsm.conn_handle,
                                          self.IDENTIFY_VALUE_HANDLE,
                                          self.IMG_IDENTIFY_OFFSET,
                                          meta_data)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False

        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            print('receive GAP_HCI_ExtentionCommandStatus in SET_META')
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)

            if msg_data.status == STATUS_SUCCESS:
                self.meta_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_ExecuteWriteRsp:
            print('receive ATT_ExecuteWriteRsp in SET_META')
            msg_data = RxMsgAttExecuteWriteRsp(hci_msg_rx.data)

            if msg_data.status == STATUS_SUCCESS:
                self.meta_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            print('receive ATT_HandleValueNotification in SET_META')
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.data, 1)

            if msg_data.status == STATUS_SUCCESS:
                self.meta_ack_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        if valid_resp and not len(self.meta_ack_getlist):
            self.fsm.transit(StateOadSetControl, StateOadSetControl.OAD_EXT_CTRL_START_OAD)


class StateOadWriteBlock(State):
    BLOCK_NUM_FIELD_BYTE_LEN = 0x04
    WRITE_BLOCK_HANDLE = 0x000F # TODO: dynamic


    def __init__(self, fsm):
        super().__init__(fsm)
        self.blocks_written = 0
        self.ack_write_getlist = [
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_HandleValueNotification
        ]
        self.write_block()

    def write_block(self):
        tx_msg = TxPackWriteNoRsp(Type.LinkCtrlCommand,
                                  OpCode.GATT_WriteNoRsp,
                                  self.BLOCK_NUM_FIELD_BYTE_LEN + mtu_size,
                                  self.fsm.conn_handle,
                                  self.WRITE_BLOCK_HANDLE,
                                  bytearray(self.fsm.firmware.get_next_block()))
        self.fsm.npi.send_binary_data(tx_msg.buf_str)
        self.blocks_written += 1

    def retry_write_bloc(self):
        # TODO: to define later
        pass


    def on_event(self, hci_msg_rx):
        valid_resp = False
        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)

            if msg_data.status == STATUS_SUCCESS:
                self.ack_write_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        elif hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.data, 0x06)

            if msg_data.status == STATUS_SUCCESS:
                self.ack_write_getlist.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()

        if valid_resp and not len(self.ack_write_getlist):
            if not self.fsm.firmware.is_read_complete():
                self.write_block()
            # switch to next state
            else:
                self.fsm.transit(StateOadSetControl, StateOadSetControl.OAD_EXT_CTRL_ENABLED_IMG)


class OadFsm:
    conn_handle = 0xFFFF

    def __init__(self, conn_handle, npi_manager):
        self.state = StateOadIdle(self)
        self.conn_handle = conn_handle
        self.npi = npi_manager
        self.firmware = FirmwareBin('app/npi/oad.bin')

    def on_event(self, hci_msg):
        self.state.on_event(hci_msg)

    def transit(self, state_class, param = None):
        if param is None:
            self.state = state_class(self)
        else:
            self.state = state_class(self, param)

    def start(self):
        self.transit(StateOadNotifyEnable)
