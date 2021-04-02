from threading import Timer

from app.applications.devices.conn_info import DevConnDataHandler, CharData
from app.applications.devices.discovery.discovery import DiscoveryHandler
from app.applications.devices.oad.firmware import FirmwareBin
from app.applications.devices.profiles.profile_uuid import CharUuid, ServiceUuid
from app.applications.npi.hci_types import OpCode, Type, Event, RxMsgGapHciExtentionCommandStatus, \
    STATUS_SUCCESS, RxMsgAttWriteRsp, TxPackWriteCharValue, TxPackAttExchangeMtuReq, RxMsgAttExchangeMtuRsp, \
    RxMsgAttMtuUpdatedEvt, RxMsgAttHandleValueNotification, TxPackWriteNoRsp, TxPackWriteLongCharValue, \
    RxMsgAttExecuteWriteRsp, RxMsgGapTerminateLink, TxPackGapInitConnect, Constants, TxPackHciLeSetDataLenReq, \
    RxMsgGapInitConnect, RxMsgGapHciCommandCompleteEvent, TxPackGattDiscoverPrimaryServiceByUuid, \
    RxMsgAttFindByTypeValueRsp, BLE_PROCEDURE_COMPLETE, TxPackGattDiscoverAllCharsDescs, RxMsgAttFindInfoRsp, \
    TxPackGapUpdateLinkParam, RxMsgGapUpdateLinkParam
from app.middleware.timers import async_run


class GOadData:
    oad_conn_handle = None
    oad_mac = None
    start_handle = None
    end_handle = None
    chars_handles = []

    @classmethod
    def clear_all(cls):
        cls.oad_conn_handle = None
        cls.oad_mac = None
        cls.start_handle = None
        cls.end_handle = None
        cls.chars_handles.clear()


class OadEvent:
    EVT_CFG_IDENTIFY = 0
    EVT_CFG_CONTROL = 1
    EVT_GET_BLK_SZ = 2
    EVT_START_OAD = 3
    EVT_ENABLE_IMG = 4


class OadSettings:
    # handles
    # CONN_HANDLE = 0x0000
    IDENTIFY_VALUE_HANDLE = 0x000B
    IMG_ID_CFG_HANDLE = 0x000C
    CONTROL_VALUE_HANDLE = 0x0013
    # IMG_CTRL_CFG_HANDLE = 0x0014
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

    def _write_cfg(self, oad_handle, config_handle, value_bt):
        print('writing config:', config_handle)
        # Enable image identify config
        tx_msg = TxPackWriteCharValue(Type.LinkCtrlCommand,
                                      OpCode.GATT_WriteCharValue,
                                      GOadData.oad_conn_handle,
                                      config_handle,
                                      value_bt)
        self.fsm.data_sender(tx_msg.buf_str)

    def _write_no_rsp(self, oad_handle, config_handle, value_bt):
        print('writing config:', config_handle)
        # Enable image identify config
        tx_msg = TxPackWriteNoRsp(Type.LinkCtrlCommand,
                                  OpCode.GATT_WriteCharValue,
                                  GOadData.oad_conn_handle,
                                  config_handle,
                                  value_bt)
        self.fsm.data_sender(tx_msg.buf_str)


    def set_timeout_delay(self, delay):
        self.t = Timer(delay, self.timeout)

    # function to redeclare in sub-classes
    def pre_handler(self):
        pass
        # self.t.start()

    # function to redeclare in sub-classes
    def post_handler(self):
        pass

    def set_ack(self, ack_list):
        self.ack_list = ack_list

    def handle_ack(self, hci_msg_rx):
        valid_resp = False
        evt = hci_msg_rx.get_event()

        if evt in self.ack_list:
            if evt == Event.GAP_HCI_ExtentionCommandStatus:
                msg_data = RxMsgGapHciExtentionCommandStatus(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    valid_resp = True

            elif evt == Event.ATT_ExecuteWriteRsp:
                msg_data = RxMsgAttExecuteWriteRsp(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    valid_resp = True

            elif evt == Event.ATT_ExchangeMTURsp:
                msg_data = RxMsgAttExchangeMtuRsp(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    valid_resp = True

            elif evt == Event.ATT_MtuUpdatedEvt:
                msg_data = RxMsgAttMtuUpdatedEvt(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    valid_resp = True

            elif evt == Event.ATT_HandleValueNotification:
                msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    valid_resp = True

            elif evt == Event.GAP_EstablishLink:
                msg_data = RxMsgGapInitConnect(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    valid_resp = True

            elif evt == Event.GAP_TerminateLink:
                msg_data = RxMsgGapTerminateLink(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    valid_resp = True

            elif evt == Event.HCI_LE_SetDataLength:
                msg_data = RxMsgGapHciCommandCompleteEvent(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    valid_resp = True

            elif evt == Event.GAP_LinkParamUpdate:
                msg_data = RxMsgGapUpdateLinkParam(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    valid_resp = True

            elif evt == Event.ATT_WriteRsp:
                msg_data = RxMsgAttWriteRsp(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    valid_resp = True

            if valid_resp:
                self.ack_list.remove(evt)
            else:
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
        print('///////// OAD IDLE /////////////')

    def on_event(self, msg):
        pass


class StateOadLinkPrmUpd(State):
    def __init__(self, fsm):
        super().__init__(fsm)

        self.set_ack([
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.GAP_LinkParamUpdate
        ])

        print('///////// OAD UPDATE LINK  /////////////')
        tx_msg = TxPackGapUpdateLinkParam(Type.LinkCtrlCommand,
                                          OpCode.GAP_UpdateLinkParamReq,
                                          GOadData.oad_conn_handle,
                                          0x0006,
                                          0x0006,
                                          0,
                                          0x0032)
        self.fsm.data_sender(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        self.handle_ack(hci_msg_rx)

        if self.ack_received():
            self.post_handler()

    def post_handler(self):
        async_run(self.fsm.transit, params=[StateOadReset], delay=2)


class StateOadReset(State):
    RESET_DELAY = 15  # seconds

    def __init__(self, fsm):
        super().__init__(fsm)
        self.set_ack([
            Event.GAP_HCI_ExtentionCommandStatus,
            Event.ATT_ExecuteWriteRsp
        ])
        print('///////// OAD RESET /////////////')
        self.pre_handler()

    def pre_handler(self):
        reset_handle = DiscoveryHandler.get_handle_by_uuid(GOadData.oad_conn_handle,
                                                           CharUuid.OAD_RESET_UUID)[0]
        tx_msg = TxPackWriteLongCharValue(Type.LinkCtrlCommand,
                                          OpCode.GATT_WriteLongCharValue,
                                          GOadData.oad_conn_handle,
                                          reset_handle,
                                          0x0000,
                                          OadSettings.CFG_ENABLE_VALUE.to_bytes(1, byteorder='big'))
        self.fsm.data_sender(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = self.handle_ack(hci_msg_rx)

        if self.ack_received() and valid_resp:  # prevent receiving wrong package
            self.post_handler()

    def post_handler(self):
        # wait for device reset
        async_run(self.fsm.transit, delay=self.RESET_DELAY, params=[StateOadInit, StateOadInit.CONNECT])


class StateOadInit(State):
    CONNECT = 0
    SETUP = 1
    LINK_PARAM = 2

    def __init__(self, fsm, mode):
        super().__init__(fsm)
        self.mode = mode

        if mode is self.CONNECT:
            print('///////// OAD CONNECT /////////////')
            self.set_ack([
                Event.GAP_HCI_ExtentionCommandStatus,
                Event.GAP_EstablishLink
            ])
        elif mode is self.SETUP:
            print('///////// OAD SET LEN /////////////')
            self.set_ack([
                Event.HCI_LE_SetDataLength
            ])
        # elif mode is self.LINK_PARAM:
        #     self.set_ack([
        #         Event.GAP_HCI_ExtentionCommandStatus,
        #         Event.GAP_LinkParamUpdate
        #     ])

        self.pre_handler()

    def pre_handler(self):
        if self.mode == self.CONNECT:
            tx_msg = TxPackGapInitConnect(Type.LinkCtrlCommand,
                                          OpCode.GapInit_connect,
                                          Constants.PEER_ADDRTYPE_PUBLIC_OR_PUBLIC_ID,
                                          bytes.fromhex(GOadData.oad_mac),
                                          Constants.INIT_PHY_1M,
                                          timeout=0)
            self.fsm.data_sender(tx_msg.buf_str)
        elif self.mode == self.SETUP:
            tx_msg = TxPackHciLeSetDataLenReq(Type.LinkCtrlCommand,
                                              OpCode.HciLe_SetDataLength,
                                              GOadData.oad_conn_handle,
                                              0x00FB,
                                              0x0848)
            self.fsm.data_sender(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = self.handle_ack(hci_msg_rx)
        print("valid_resp: ", valid_resp)

        if self.ack_received() and valid_resp:
            # print("post3")
            self.post_handler()

    def post_handler(self):
        # print("post4")
        if self.mode == self.CONNECT:
            print('///////// OAD CONNECT POST /////////////')
            async_run(self.fsm.transit, params=[StateOadInit, self.SETUP], delay=2)
            # self.fsm.transit(StateOadInit, self.SETUP)
        elif self.mode == self.SETUP:
            async_run(self.fsm.transit, params=[StateOadDiscover, StateOadDiscover.SERVICES], delay=2)
            # self.fsm.transit(StateOadDiscover, StateOadDiscover.SERVICES)


class StateOadDiscover(State):
    SERVICES = 0
    CHARS = 1

    def __init__(self, fsm, mode):
        super().__init__(fsm)
        self.mode = mode

        self.set_ack([
            Event.GAP_HCI_ExtentionCommandStatus
        ])

        self.pre_handler()

    def pre_handler(self):
        if self.mode == self.SERVICES:
            print('///////// DISCOVER SERVICES  /////////////')
            tx_msg = TxPackGattDiscoverPrimaryServiceByUuid(Type.LinkCtrlCommand,
                                                            OpCode.GATT_DiscPrimaryServiceByUUID,
                                                            GOadData.oad_conn_handle,
                                                            ServiceUuid.OAD)
            self.fsm.data_sender(tx_msg.buf_str)
        elif self.mode == self.CHARS:
            if None in (GOadData.start_handle, GOadData.end_handle):
                raise Exception("OAD Service discovery totally failed!!")
            print('///////// DISCOVER CHARS  /////////////')
            tx_msg = TxPackGattDiscoverAllCharsDescs(Type.LinkCtrlCommand,
                                                     OpCode.GATT_DiscAllCharDescs,
                                                     GOadData.oad_conn_handle,
                                                     GOadData.start_handle,
                                                     GOadData.end_handle)
            self.fsm.data_sender(tx_msg.buf_str)

    @staticmethod
    def _parse_handle_disc(data, pdu_len, handle_format):
        uuid_len = None
        if handle_format is Constants.HANDLE_BT_UUID_TYPE_16BIT:
            uuid_len = Constants.GAP_ADTYPE_16BIT_MORE
        elif handle_format is Constants.HANDLE_UUID_TYPE_128BIT:
            uuid_len = Constants.GAP_ADTYPE_128BIT_MORE

        if uuid_len is None:
            print("Empty resp")
            return

        handles_count = pdu_len / (uuid_len + 2)
        for i in range(int(handles_count)):
            start_byte = i * (uuid_len + 2)
            handle = data[start_byte : start_byte + 2]
            start_byte += 2
            uuid = data[start_byte : start_byte + uuid_len]
            GOadData.chars_handles.append(CharData(handle, uuid, byte_format=True))
            print("Discovered: ", GOadData.chars_handles[-1].handle, GOadData.chars_handles[-1].uuid)

    def on_event(self, hci_msg_rx):
        self.handle_ack(hci_msg_rx)

        if self.mode is self.SERVICES:
            if hci_msg_rx.get_event() == Event.ATT_FindByTypeValueRsp:
                msg_data = RxMsgAttFindByTypeValueRsp(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    # interpret data
                    if msg_data.pdu_len >= 4:  # temporary hard-coding
                        GOadData.start_handle = int.from_bytes(msg_data.data[0:2], byteorder='little')
                        GOadData.end_handle = int.from_bytes(msg_data.data[2:4], byteorder='little')
                elif msg_data.status == BLE_PROCEDURE_COMPLETE:
                    if self.ack_received():
                        self.post_handler()
        if self.mode is self.CHARS:
            if hci_msg_rx.get_event() == Event.ATT_FindInfoRsp:
                msg_data = RxMsgAttFindInfoRsp(hci_msg_rx.data)
                if msg_data.status == STATUS_SUCCESS:
                    self._parse_handle_disc(msg_data.data, msg_data.pdu_len, msg_data.format)
                elif msg_data.status == BLE_PROCEDURE_COMPLETE:
                    if self.ack_received():
                        self.post_handler()


    def post_handler(self):
        if self.mode is self.SERVICES:
            self.fsm.transit(StateOadDiscover, StateOadDiscover.CHARS)
        elif self.mode is self.CHARS:
            self.fsm.transit(StateOadNotifyEnable, StateOadNotifyEnable.IMAGE_NOTIFY)


class StateOadNotifyEnable(State):
    IMAGE_NOTIFY = 0
    IMAGE_CONTROL = 1

    def __init__(self, fsm, mode):
        super().__init__(fsm)
        self.mode = mode
        self.pre_handler()

    def pre_handler(self):
        self.set_ack([
            Event.GAP_HCI_ExtentionCommandStatus,  # host ACK
            Event.ATT_WriteRsp
        ])

        if self.mode == self.IMAGE_NOTIFY:
            print('///////// NOTIFY IMAGE_NOTIFY  /////////////')
            oad_char_handle = 0x000C
            self._write_cfg(GOadData.oad_conn_handle,
                            oad_char_handle,
                            OadSettings.CFG_ENABLE_VALUE.to_bytes(2, byteorder='little'))
        elif self.mode == self.IMAGE_CONTROL:
            print('///////// NOTIFY IMAGE_CONTROL  /////////////')
            oad_char_handle = 0x0014
            self._write_cfg(GOadData.oad_conn_handle,
                            oad_char_handle,
                            OadSettings.CFG_ENABLE_VALUE.to_bytes(2, byteorder='little'))

    def on_event(self, hci_msg_rx):
        valid_resp = self.handle_ack(hci_msg_rx)

        # all notifications are enabled, transit to next state
        if valid_resp and self.ack_received():
            self.post_handler()

    def post_handler(self):
        if self.mode == self.IMAGE_NOTIFY:
            print('transit to ourselves to set control cfg')
            self.fsm.transit(StateOadNotifyEnable, self.IMAGE_CONTROL)
        if self.mode == self.IMAGE_CONTROL:
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
            Event.ATT_MtuUpdatedEvt # TODO: not sure if necessarily required
        ])
        self._exchange_mtu_size()
        super().pre_handler()  # start time

    def _exchange_mtu_size(self):
        print('///////// EXCHANGE MTU  /////////////')
        tx_msg = TxPackAttExchangeMtuReq(Type.LinkCtrlCommand,
                                         OpCode.ATT_ExchangeMTUReq,
                                         self.EXCHANGE_MTU_REQ_BYTE_LEN,
                                         GOadData.oad_conn_handle,
                                         OadSettings.SERVER_RX_MTU_SIZE)
        self.fsm.data_sender(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = self.handle_ack(hci_msg_rx)

        print("valid: ", valid_resp)
        if valid_resp and self.ack_received():
            self.post_handler()

    def post_handler(self):
        self.fsm.transit(StateOadSetCtrl, StateOadSetCtrl.GET_BLOCK_SIZE)


class StateOadSetCtrl(State):
    GET_BLOCK_SIZE = 0
    START_OAD = 1
    ENABLE_IMG = 2

    SET_CTRL_REQ_BYTE_LEN = 0x05
    IMG_CTRL_START_OAD = 3
    IMG_CTRL_ENABLE_OAD = 4


    def __init__(self, fsm, mode):
        super().__init__(fsm)
        self.mode = mode

        self.set_ack([
            Event.GAP_HCI_ExtentionCommandStatus
        ])
        self.pre_handler()

    def pre_handler(self):
        if self.mode is self.GET_BLOCK_SIZE:
            # self._set_control_value(self.ctrl_command)
            self._write_no_rsp(GOadData.oad_conn_handle, 0x0013, OadSettings.CFG_ENABLE_VALUE.to_bytes(1, byteorder='little'))
        elif self.mode is self.START_OAD:
            self._write_no_rsp(GOadData.oad_conn_handle, 0x0013, self.IMG_CTRL_START_OAD.to_bytes(1, byteorder='little'))
        elif self.mode is self.ENABLE_IMG:
            self._write_no_rsp(GOadData.oad_conn_handle, 0x0013, self.IMG_CTRL_ENABLE_OAD.to_bytes(1, byteorder='little'))
        # super().pre_handler()  # start time

    def on_event(self, hci_msg_rx):
        self.handle_ack(hci_msg_rx)

        if self.ack_received() and hci_msg_rx.get_event() == Event.ATT_HandleValueNotification:
            print('receive ATT_HandleValueNotification')
            msg_data = RxMsgAttHandleValueNotification(hci_msg_rx.data)
            # get block size from response
            if self.mode == self.GET_BLOCK_SIZE:
                mtu_size = int.from_bytes(msg_data.value[1:3], byteorder='little', signed=False)
                print('block size = ', mtu_size)
                self.fsm.firmware.set_mtu_size(mtu_size)
                # StateOadWriteBlock.block_counter = self.fsm.firmware.get_blocks_number()
                self.post_handler()
            elif self.mode == self.START_OAD or self.mode == self.ENABLE_IMG:
                self.post_handler()

    def post_handler(self):
        # after managing block size transit to meta state
        if self.mode is self.GET_BLOCK_SIZE:
            self.fsm.transit(StateOadSetMeta)
        # once metadata set, start writing OAD blocks
        elif self.mode == self.START_OAD:
            self.fsm.transit(StateOadWriteBlock)
        elif self.mode == self.ENABLE_IMG:
            self.fsm.transit(StatePostOad)
        # once new image enabled, OAD is done


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
        # super().pre_handler()  # start time

    def _set_identify(self):
        print('set meta data identify')
        meta_data = self.fsm.firmware.get_metadata_value()
        tx_msg = TxPackWriteLongCharValue(Type.LinkCtrlCommand,
                                          OpCode.GATT_WriteLongCharValue,
                                          GOadData.oad_conn_handle,
                                          OadSettings.IDENTIFY_VALUE_HANDLE,
                                          self.IMG_IDENTIFY_OFFSET,
                                          meta_data)
        self.fsm.data_sender(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = self.handle_ack(hci_msg_rx)

        if valid_resp and self.ack_received():
            self.post_handler()

    def post_handler(self):
        self.fsm.transit(StateOadSetCtrl, StateOadSetCtrl.START_OAD)


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
                                  GOadData.oad_conn_handle,
                                  OadSettings.WRITE_BLOCK_HANDLE,
                                  bytearray(block))
        self.fsm.data_sender(tx_msg.buf_str)

    def on_event(self, hci_msg_rx):
        valid_resp = self.handle_ack(hci_msg_rx)

        if valid_resp and self.ack_received():
            self.post_handler()

    def post_handler(self):
        StateOadWriteBlock.block_counter += 1
        print('blocks written: ', self.block_counter, '/', self.fsm.firmware.get_blocks_number())
        if StateOadWriteBlock.block_counter >= self.fsm.firmware.get_blocks_number():
            # switch to next state
            self.fsm.transit(StateOadSetCtrl, StateOadSetCtrl.ENABLE_IMG)
        else:
            # still have blocks to write
            self.fsm.transit(StateOadWriteBlock)


class StatePostOad(State):
    POST_DELAY_TIME_SEC = 10  # wait until image is applied

    def __init__(self, fsm):
        super().__init__(fsm)
        print("entered post OAD state")
        self.pre_handler()

    def pre_handler(self):
        self.set_ack([
            Event.GAP_TerminateLink
        ])
        # self.set_timeout_delay(self.POST_DELAY_TIME_SEC)
        # super().pre_handler()  # start time

    def on_event(self, hci_msg_rx):
        valid_resp = self.handle_ack(hci_msg_rx)

        if valid_resp and self.ack_received():
            self.post_handler()

    def post_handler(self):
        self.fsm.transit(StateOadIdle)
        self.fsm.process_complete_cb()

    def timeout(self):
        # post here an event of OAD failure
        pass

class OadFsm:
    def __init__(self, data_sender, complete_cb, conn_handle, firmware_path):
        self.state = StateOadIdle(self)
        self.firmware = FirmwareBin(firmware_path)
        # self.firmware = FirmwareBin('app/applications/devices/oad/oad.bin')
        self.data_sender = data_sender
        self.process_complete_cb = complete_cb

        GOadData.clear_all()
        GOadData.oad_conn_handle = conn_handle
        GOadData.oad_mac = DevConnDataHandler.get_mac_by_handle(conn_handle)

    def on_event(self, hci_msg):
        self.state.on_event(hci_msg)

    def transit(self, state_class, param = None):
        self.state = state_class(self) if param is None else state_class(self, param)

    def start(self):
        self.transit(StateOadLinkPrmUpd)
