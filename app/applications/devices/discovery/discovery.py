from app.applications.devices.device_data import DeviceConnData
from app.applications.devices.profiles.profile_data import ProfileTable
from app.applications.devices.profiles.profile_uuid import CharUuid
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages


# class that reports handle IDs to access any type of device data
class DiscoveryHandler:
    def __init__(self):
        self.handle_info = {}

    def add_conn(self, conn_handle, dev_type):
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
        # Chars received, check if sensor has necessary services
        dev_type = self.handle_info[conn_handle].dev_type
        svc_list = self.handle_info[conn_handle].services
        return self.diagnose_device_svc(dev_type, svc_list)

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

    @classmethod
    def diagnose_device_svc(cls, dev_type, svc_list):
        required_services = ProfileTable.svc_type_map[dev_type]
        for req_svc in required_services:
            if req_svc not in svc_list:
                return False
        return True


# ProfileTable.info[DeviceType.gas]
class DiscoveryManager(DiscoveryHandler):
    def __init__(self):
        super().__init__()

    def handle_new_conn(self, conn_handle, dev_type):
        self.add_conn(conn_handle, dev_type)

        # device connected, start discovery
        Dispatcher.send_msg(Messages.DEV_SVC_DISCOVER, {"conn_handle": conn_handle})

    def handle_svc_report(self, conn_handle, svc_list):
        self.add_services(conn_handle, svc_list)

        # Services received, discover chars
        Dispatcher.send_msg(msg_id=Messages.DEV_CHAR_DISCOVER,
                            data={"conn_handle": conn_handle})

    def handle_char_report(self, conn_handle, char_list):
        self.add_chars(conn_handle, char_list)

        if not self.check_device_services(conn_handle):
            Dispatcher.send_msg(Messages.ERR_DEV_MISSING_SVC, {"conn_handle": conn_handle})
        else:
            # everything's fine enable indications/notifications
            Dispatcher.send_msg(Messages.ENABLE_DEV_IND, {"conn_handle": conn_handle})

    def handle_ccc_enabled(self, conn_handle):
        pass
