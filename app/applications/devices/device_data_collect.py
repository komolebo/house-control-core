from app.applications.devices.conn_info import CharValueData, DevConnDataHandler
from app.applications.devices.device_data import DeviceTypeInfo, MotionData, DevDataHandler
from app.applications.devices.discovery.discovery import DiscoveryHandler
from app.applications.devices.profiles.profile_uuid import CharUuid
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages


class DeviceIndicationHandler:
    def __new__(cls, send_response):  # singleton class
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeviceIndicationHandler, cls).__new__(cls)
            cls.send_response = send_response
            cls.device_info = {}
        return cls.instance

    def add_device(self, conn_handle, dev_type, name):
        if conn_handle in self.device_info.keys():
            print('Device already added!')
        if dev_type == DeviceTypeInfo.motion:
            self.device_info[conn_handle] = MotionData(name)

    def process_indication(self, conn_handle, handle, value):
        if conn_handle not in self.device_info.keys():
            self.send_response(msg=Messages.ERR_DEV_CONN_NOT_EXIST,
                               data={"conn_handle": conn_handle})
            return False

        data_uuid = DiscoveryHandler.get_uuid_by_handle(conn_handle, handle)
        mac = DevConnDataHandler.get_mac_by_handle(conn_handle)

        # print("+++++++++++++++++++++++++++ uuid:", data_uuid)
        data_changed = True
        if data_uuid == CharUuid.CS_MODE.uuid:
            DevDataHandler.upd_dev_state(mac, value)

        elif data_uuid == CharUuid.DS_STATE.uuid:
            DevDataHandler.upd_dev_status(mac, value)

        elif data_uuid == CharUuid.BATTERY_LEVEL.uuid:
            DevDataHandler.upd_dev_battery(mac, value)

        elif data_uuid == CharUuid.TS_STATE.uuid:
            DevDataHandler.upd_dev_tamper(mac, value)

        elif data_uuid == CharUuid.DEVICE_NAME:
            # TODO: handle device name
            pass

        elif data_uuid == CharUuid.SOFTWARE_REVISION_UUID.uuid:
            version = value.decode("ascii")
            print("Discovered SOFTWARE REVISION UUID:", value, version)
            dev_type = DevDataHandler.get_dev(mac).type
            Dispatcher.send_msg(Messages.UPDATE_VERSION_DISCOVERED, {'mac': mac, 'version': version, 'type': dev_type})
            pass
        else:
            data_changed = False

        return data_changed


    def process_val_disc_resp(self, conn_handle, char_value_data):
        if conn_handle not in self.device_info.keys():
            self.send_response(msg=Messages.ERR_DEV_CONN_NOT_EXIST,
                               data={"conn_handle": conn_handle})
            return
        for char_val_item in char_value_data:
            if isinstance(char_val_item, CharValueData):
                self.process_indication(conn_handle, char_val_item.handle, char_val_item.value)
        device = self.device_info[conn_handle]
        # if isinstance(device, MotionData):
        #     self.frontNotifier.handle_dev_add_new(conn_handle, device.dev_type, device.state, device.batt_level,
        #                                           device.tamper_state, device.detect_state)