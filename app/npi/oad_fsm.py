from threading import Timer
from app.npi.firmware import FirmwareBin
from app.npi.hci import OpCode, Type, Event, RxMsgGapHciExtentionCommandStatus, \
    STATUS_SUCCESS, RxMsgAttWriteRsp, TxPackWriteCharValue, TxPackAttExchangeMtuReq, RxMsgAttExchangeMtuRsp, \
    RxMsgAttMtuUpdatedEvt, RxMsgAttHandleValueNotification, TxPackWriteNoRsp, TxPackWriteLongCharValue, \
    RxMsgAttExecuteWriteRsp, RxMsgGapTerminateLink


class OadEvent:
    EVT_CFG_IDENTIFY = 0
    EVT_CFG_CONTROL = 1
    EVT_GET_BLK_SZ = 2
    EVT_START_OAD = 3
    EVT_ENABLE_IMG = 4


class OadSettings:
    # handles
    CONN_HANDLE = 0x0000
    IDENTIFY_VALUE_HANDLE = 0x000B
    IMG_ID_CFG_HANDLE = 0x000C
    CONTROL_VALUE_HANDLE = 0x0013
    IMG_CTRL_CFG_HANDLE = 0x0014
    WRITE_BLOCK_HANDLE = 0x000F

    # commands
    OAD_EXT_CTRL_GET_BLK_SZ = 0x01
    OAD_EXT_CTRL_START_OAD = 0x03
    OAD_EXT_CTRL_ENABLED_IMG = 0x04

    # values
    CFG_ENABLE_VALUE = 0x0001

    SERVER_RX_MTU_SIZE = 0x00F7
    mtu_size = 0x0


# Base state handles timeout case
class State:
    MAX_RETRIES = 3
    RETRY_TIME_SEC = 3

    def __init__(self, fsm):
        self.fsm = fsm
        self.retry_counter = 0
        self.ack_list = None
        self.t = Timer(self.RETRY_TIME_SEC, self.timeout)

    def set_timeout_delay(self, delay):
        self.t = Timer(delay, self.timeout)

    # function to redeclare in sub-classes
    def pre_handler(self):
        self.t.start()

    # function to redeclare in sub-classes
    def post_handler(self):
        pass

    def set_ack(self, ack_list):
        self.ack_list = ack_list

    def handle_ack(self, msg_data):
        valid_resp = False
        # check wanted ACK type
        if len(self.ack_list):
            # process image identify host stack ACK status
            if msg_data.status == STATUS_SUCCESS:
                self.ack_list.remove(msg_data.event)
                valid_resp = True
            else:
                self.handle_error()
        else:
            # unexpected package receive, TODO: check with multiple connections
            self.handle_error()

        if not len(self.ack_list):
            self.t.cancel()

        return valid_resp

    def ack_received(self):
        return not len(self.ack_list)

    def retry(self):
        if self.retry_counter < self.MAX_RETRIES:
            print('timeout expired, retries:', self.retry_counter)
            self.pre_handler()
            self.retry_counter += 1

    def timeout(self):
        print('timeout expired: retry started')
        self.retry()

    def handle_error(self):
        print('error happened')
        self.retry()


class StateOadIdle(State):
    def __init__(self, fsm):
        super().__init__(fsm)
        print('previous OAD process is ended')

    def on_event(self, msg):
        print("Unexpected event received while OAD in IDLE")


class StateOadNotifyEnable(State):
    # constants
    NOTIFY_REQ_BYTE_LEN = 0x06

    def __init__(self, fsm, notify_item):
        super().__init__(fsm)
        self.notify_item = notify_item
        self.pre_handler()

    def pre_handler(self):
        self.set_ack([
            Event.GAP_HCI_ExtentionCommandStatus,  # host ACK
            Event.ATT_WriteRsp
        ])

        if self.notify_item == OadEvent.EVT_CFG_IDENTIFY:
            self._enable_notification(OadSettings.IMG_ID_CFG_HANDLE)
        elif self.notify_item == OadEvent.EVT_CFG_CONTROL:
            self._enable_notification(OadSettings.IMG_CTRL_CFG_HANDLE)
        super().pre_handler()  # start time

    def _enable_notification(self, config_handle):
        print('enable notification:', config_handle)
        # Enable image identify config
        tx_msg = TxPackWriteCharValue(Type.LinkCtrlCommand,
                                      OpCode.GATT_WriteCharValue,
                                      self.NOTIFY_REQ_BYTE_LEN,
                                      OadSettings.CONN_HANDLE,
                                      config_handle,
                                      OadSettings.CFG_ENABLE_VALUE)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        print('receive event in StateOadNotifyEnable')
        valid_resp = False
        # host stack ACK received:
        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            print('receive GAP_HCI_ExtentionCommandStatus')
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)
            valid_resp = self.handle_ack(msg_data)

        # target device's ACK received:
        elif hci_msg_rx.get_event() == Event.ATT_WriteRsp:
            print('receive ATT_WriteRsp')
            msg_data = RxMsgAttWriteRsp(hci_msg_rx.data)
            valid_resp = self.handle_ack(msg_data)

        # all notifications are enabled, transit to next state
        if valid_resp and self.ack_received():
            self.post_handler()

    def post_handler(self):
        if self.notify_item == OadEvent.EVT_CFG_IDENTIFY:
            print('transit to ourselves to set control cfg')
            self.fsm.transit(StateOadNotifyEnable, OadEvent.EVT_CFG_CONTROL)
        if self.notify_item == OadEvent.EVT_CFG_CONTROL:
            print('transit from STATE_ENABLE to STATE_MTU')
            self.fsm.transit(StateOadExchangeMtu)


class StateOadExchangeMtu(State):
    EXCHANGE_MTU_REQ_BYTE_LEN = 0x04

    def __init__(self, fsm):
        super().__init__(fsm)
        self.pre_handler()

    def pre_handler(self):
        self.set_ack([
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_ExchangeMTURsp,
            # Event.ATT_MtuUpdatedEvt # TODO: not sure if necessarily required
        ])
        self._exchange_mtu_size()
        super().pre_handler()  # start time

    def _exchange_mtu_size(self):
        print('exchange mtu size')
        tx_msg = TxPackAttExchangeMtuReq(Type.LinkCtrlCommand,
                                         OpCode.ATT_ExchangeMTUReq,
                                         self.EXCHANGE_MTU_REQ_BYTE_LEN,
                                         OadSettings.CONN_HANDLE,
                                         OadSettings.SERVER_RX_MTU_SIZE)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False

        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            print('receive GAP_HCI_ExtentionCommandStatus')
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)
            valid_resp = self.handle_ack(msg_data)

        elif hci_msg_rx.get_event() == Event.ATT_ExchangeMTURsp:
            print('receive ATT_ExchangeMTURsp')
            msg_data = RxMsgAttExchangeMtuRsp(hci_msg_rx.data)
            valid_resp = self.handle_ack(msg_data)

        elif hci_msg_rx.get_event() == Event.ATT_MtuUpdatedEvt:
            print('receive ATT_MtuUpdatedEvt')
            msg_data = RxMsgAttMtuUpdatedEvt(hci_msg_rx.msg_data)
            valid_resp = self.handle_ack(msg_data)

        if valid_resp:
            # all ACKs received
            if self.ack_received():
                self.post_handler()

    def post_handler(self):
        self.fsm.transit(StateOadSetControl, OadSettings.OAD_EXT_CTRL_GET_BLK_SZ)


class StateOadSetControl(State):
    SET_CTRL_REQ_BYTE_LEN = 0x05


    def __init__(self, fsm, param):
        super().__init__(fsm)
        self.pre_handler()

        self.ctrl_command = param
        if self.ctrl_command == OadSettings.OAD_EXT_CTRL_GET_BLK_SZ:
            self.exp_value_len_resp = 3
        elif self.ctrl_command == OadSettings.OAD_EXT_CTRL_START_OAD:
            self.exp_value_len_resp = 6
        elif self.ctrl_command == OadSettings.OAD_EXT_CTRL_ENABLED_IMG:
            self.exp_value_len_resp = 2

        self._set_control_value(self.ctrl_command)

    def pre_handler(self):
        self.set_ack([
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_HandleValueNotification
        ])
        super().pre_handler()  # start time

    def _set_control_value(self, value):
        print('setting control value:', hex(value))
        value_arr = bytearray([value])
        tx_msg = TxPackWriteNoRsp(Type.LinkCtrlCommand,
                                  OpCode.GATT_WriteNoRsp,
                                  self.SET_CTRL_REQ_BYTE_LEN,
                                  OadSettings.CONN_HANDLE,
                                  OadSettings.CONTROL_VALUE_HANDLE,
                                  value_arr)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False

        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            print('receive GAP_HCI_ExtentionCommandStatus')
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)
            valid_resp = self.handle_ack(msg_data)

        elif hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            print('receive ATT_HandleValueNotification')
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.data, self.exp_value_len_resp)
            valid_resp = self.handle_ack(msg_data)
            # get block size from response
            if self.ctrl_command == OadSettings.OAD_EXT_CTRL_GET_BLK_SZ:
                OadSettings.mtu_size = int.from_bytes(msg_data.value[1:3], byteorder='little', signed=False)
                print('block size = ', OadSettings.mtu_size)
                self.fsm.firmware.set_mtu_size(OadSettings.mtu_size)
                # StateOadWriteBlock.block_counter = self.fsm.firmware.get_blocks_number()

        # control cmd done, switch to next state
        if valid_resp and self.ack_received():
            self.post_handler()

    def post_handler(self):
        # after managing block size transit to meta state
        if self.ctrl_command == OadSettings.OAD_EXT_CTRL_GET_BLK_SZ:
            self.fsm.transit(StateOadSetMeta)
        # once metadata set, start writing OAD blocks
        elif self.ctrl_command == OadSettings.OAD_EXT_CTRL_START_OAD:
            self.fsm.transit(StateOadWriteBlock)
        # once new image enabled, OAD is done
        elif self.ctrl_command == OadSettings.OAD_EXT_CTRL_ENABLED_IMG:
            self.fsm.transit(StatePostOad)


class StateOadSetMeta(State):
    SET_META_REQ_BYTE_LEN = 0x1C
    IMG_IDENTIFY_OFFSET = 0x0000

    def __init__(self, fsm):
        super().__init__(fsm)
        self.pre_handler()

    def pre_handler(self):
        self.set_ack([
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_ExecuteWriteRsp,
            Event.ATT_HandleValueNotification
        ])
        self._set_identify()
        super().pre_handler()  # start time

    def _set_identify(self):
        print('set meta data identify')
        meta_data = self.fsm.firmware.get_metadata_value()
        tx_msg = TxPackWriteLongCharValue(Type.LinkCtrlCommand,
                                          OpCode.GATT_WriteLongCharValue,
                                          self.SET_META_REQ_BYTE_LEN,
                                          OadSettings.CONN_HANDLE,
                                          OadSettings.IDENTIFY_VALUE_HANDLE,
                                          self.IMG_IDENTIFY_OFFSET,
                                          meta_data)
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False

        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            print('receive GAP_HCI_ExtentionCommandStatus in SET_META')
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)
            valid_resp = self.handle_ack(msg_data)

        elif hci_msg_rx.get_event() == Event.ATT_ExecuteWriteRsp:
            print('receive ATT_ExecuteWriteRsp in SET_META')
            msg_data = RxMsgAttExecuteWriteRsp(hci_msg_rx.data)
            valid_resp = self.handle_ack(msg_data)

        elif hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            print('receive ATT_HandleValueNotification in SET_META')
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.data, 1)
            valid_resp = self.handle_ack(msg_data)

        if valid_resp and self.ack_received():
            self.post_handler()

    def post_handler(self):
        self.fsm.transit(StateOadSetControl, OadSettings.OAD_EXT_CTRL_START_OAD)


class StateOadWriteBlock(State):
    HANDLE_FIELDS_BYTE_LEN = 0x04
    block_counter = 0

    def __init__(self, fsm):
        super().__init__(fsm)
        self.pre_handler()

    def pre_handler(self):
        self.set_ack([
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_HandleValueNotification
        ])
        self.write_block()
        super().pre_handler()  # start time

    def write_block(self):
        print('writing block')
        block = self.fsm.firmware.get_block(StateOadWriteBlock.block_counter)
        tx_msg = TxPackWriteNoRsp(Type.LinkCtrlCommand,
                                  OpCode.GATT_WriteNoRsp,
                                  self.HANDLE_FIELDS_BYTE_LEN + len(block),
                                  OadSettings.CONN_HANDLE,
                                  OadSettings.WRITE_BLOCK_HANDLE,
                                  bytearray(block))
        self.fsm.npi.send_binary_data(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = False
        if hci_msg_rx.get_event() == Event.GAP_HCI_ExtentionCommandStatus:
            msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)
            valid_resp = self.handle_ack(msg_data)

        elif hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.data, 0x06)
            valid_resp = self.handle_ack(msg_data)

        if valid_resp and self.ack_received():
            self.post_handler()

    def post_handler(self):
        StateOadWriteBlock.block_counter += 1
        print('blocks written: ', self.block_counter, '/', self.fsm.firmware.get_blocks_number())
        if StateOadWriteBlock.block_counter >= self.fsm.firmware.get_blocks_number():
            # switch to next state
            self.fsm.transit(StateOadSetControl, OadSettings.OAD_EXT_CTRL_ENABLED_IMG)
        else:
            # still have blocks to write
            self.fsm.transit(StateOadWriteBlock)


class StatePostOad(State):
    POST_DELAY_TIME_SEC = 40  # wait until image is applied

    def __init__(self, fsm):
        super().__init__(fsm)
        print("entered post OAD state")
        self.pre_handler()

    def pre_handler(self):
        self.set_ack([
            Event.GAP_TerminateLink
        ])
        self.set_timeout_delay(self.POST_DELAY_TIME_SEC)
        super().pre_handler()  # start time

    def on_event(self, hci_msg_rx):
        print('received post event')
        if hci_msg_rx.get_event() == Event.GAP_TerminateLink:
            msg_data = RxMsgGapTerminateLink(hci_msg_rx.data)
            if self.handle_ack(msg_data):
                self.post_handler()

    def post_handler(self):
        self.fsm.transit(StateOadIdle)

    def timeout(self):
        # post here an event of OAD failure
        pass


class OadFsm:
    def __init__(self, npi_manager):
        self.state = StateOadIdle(self)
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
        self.transit(StateOadNotifyEnable, OadEvent.EVT_CFG_IDENTIFY)
