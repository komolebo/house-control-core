from app.applications.devices.conn_info import DeviceConnData
from app.applications.devices.profiles.profile_requirements import ProfileTable
from app.applications.devices.profiles.profile_uuid import CharUuid
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages


# class that reports handle IDs to access any type of device data
class DiscoveryHandler:
    def __new__(cls):  # singleton class
        if not hasattr(cls, 'instance'):
            cls.instance = super(DiscoveryHandler, cls).__new__(cls)
            cls.handle_info = {}
        return cls.instance

    def add_conn(self, conn_handle, dev_type):
        print("add_conn")
        if conn_handle in self.handle_info.keys():
            print("Handle already exist!")
        # Overwrite data
        self.handle_info[conn_handle] = DeviceConnData(dev_type,
                                                       services=None,
                                                       chars=None)

    def add_services(self, conn_handle, svc_list):
        if conn_handle in self.handle_info.keys():
            self.handle_info[conn_handle].services = svc_list

    def add_chars(self, conn_handle, char_list):
        if conn_handle in self.handle_info.keys():
            self.handle_info[conn_handle].chars = char_list

    def check_device_services(self, conn_handle):
        dev_type = self.handle_info[conn_handle].dev_type
        svc_list = self.handle_info[conn_handle].services
        return self.diagnose_device_svc(dev_type, svc_list)

    def check_device_chars(self, conn_handle):
        dev_type = self.handle_info[conn_handle].dev_type
        char_list = [i.uuid for i in  self.handle_info[conn_handle].chars]
        return self.diagnose_device_char(dev_type, char_list)

    def get_handle_by_uuid(self, conn_handle, uuid):
        if conn_handle in self.handle_info.keys():
            return [i.handle for i in self.handle_info[conn_handle].chars if i.uuid == uuid]
        return None

    def get_ccc_handle_by_uuid(self, conn_handle, uuid):
        if conn_handle in self.handle_info.keys():
            uuid_handles = self.get_handle_by_uuid(conn_handle, uuid)
            if len(uuid_handles):
                uuid_handle = uuid_handles[0]
                all_svc_handles = self.get_handle_by_uuid(conn_handle, CharUuid.GATT_CCC_UUID)
                return uuid_handle + 1 if uuid_handle + 1 in all_svc_handles else None
        return None

    def get_uuid_by_handle(self, conn_handle, handle):
        if conn_handle in self.handle_info.keys():
            for char in self.handle_info[conn_handle].chars:
                if char.handle == handle:
                    return char.uuid
        return None

    @classmethod
    def diagnose_device_svc(cls, dev_type, svc_list):
        required_services = ProfileTable.svc_dev_map[dev_type]
        for req_svc in required_services:
            if req_svc not in svc_list:
                return False
        return True

    @classmethod
    def diagnose_device_char(cls, dev_type, char_list):
        required_chars = ProfileTable.char_dev_map[dev_type]
        for req_char in required_chars:
            if req_char not in char_list:
                return False
        return True


# ProfileTable.info[DeviceType.gas]
class DiscoveryManager:
    def __init__(self):
        self.disc_handler = DiscoveryHandler()

    def handle_new_conn(self, conn_handle, dev_type):
        self.disc_handler.add_conn(conn_handle, dev_type)

        # device connected, start discovery
        Dispatcher.send_msg(Messages.DEV_MTU_CFG, {"conn_handle": conn_handle})

    def handle_mtu_cfg(self, conn_handle):
        # device connected, start discovery
        Dispatcher.send_msg(Messages.DEV_SVC_DISCOVER, {"conn_handle": conn_handle})

    def handle_svc_report(self, conn_handle, svc_list):
        self.disc_handler.add_services(conn_handle, svc_list)

        # Services received, discover chars if services are ok
        if not self.disc_handler.check_device_services(conn_handle):
            Dispatcher.send_msg(Messages.ERR_DEV_MISSING_SVC, {"conn_handle": conn_handle})
        else:
            Dispatcher.send_msg(msg_id=Messages.DEV_CHAR_DISCOVER,
                                data={"conn_handle": conn_handle})

    def handle_char_report(self, conn_handle, char_list):
        self.disc_handler.add_chars(conn_handle, char_list)

        if not self.disc_handler.check_device_chars(conn_handle):
            Dispatcher.send_msg(Messages.ERR_DEV_MISSING_CHAR, {"conn_handle": conn_handle})
        else:
            # everything's fine enable indications/notifications
            Dispatcher.send_msg(Messages.ENABLE_DEV_INDICATION, {"conn_handle": conn_handle})

    def handle_ccc_enabled(self, conn_handle):
        dev_type = self.disc_handler.handle_info[conn_handle].dev_type
        required_char_uuid_list = ProfileTable.char_dev_map[dev_type]
        handles = [self.disc_handler.get_handle_by_uuid(conn_handle, uuid)[0] for uuid in required_char_uuid_list]
        Dispatcher.send_msg(Messages.DEV_VALUES_DISCOVER, {"conn_handle": conn_handle})
