from app.applications.devices.device_data import DeviceConnData
from app.applications.devices.profiles.profile_data import ProfileTable
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages


class DiscoveryHandler:
    @staticmethod
    def diagnose_device_uuid(dev_type, svc_list):
        required_services = ProfileTable.svc_type_map[dev_type]
        for req_svc in required_services:
            if req_svc not in svc_list:
                return False
        return True


# ProfileTable.info[DeviceType.gas]
class DiscoveryManager:
    def __init__(self):
        self.handle_info = {}

    def handle_new_conn(self, conn_handle, dev_type):
        if conn_handle in self.handle_info.keys():
            print("Handle already exist!")
        # Overwrite data
        self.handle_info[conn_handle] = DeviceConnData(dev_type,
                                                       services=None,
                                                       chars=None)
        # device connected, start discovery
        Dispatcher.send_msg(Messages.DEV_SVC_DISCOVER, {"conn_handle": conn_handle})

    def handle_svc_report(self, conn_handle, svc_list):
        if conn_handle in self.handle_info.keys():
            self.handle_info[conn_handle].services = svc_list

        # Services received, discover chars
        Dispatcher.send_msg(msg_id=Messages.DEV_CHAR_DISCOVER,
                            data={"conn_handle": conn_handle})

    def handle_char_report(self, conn_handle, char_list):
        if conn_handle in self.handle_info.keys():
            self.handle_info[conn_handle].chars = char_list

        # Chars received, check if sensor has necessary services
        dev_type = self.handle_info[conn_handle].dev_type
        svc_list = self.handle_info[conn_handle].services
        svc_ok = DiscoveryHandler.diagnose_device_uuid(dev_type, svc_list)
        if not svc_ok:
            Dispatcher.send_msg(Messages.ERR_DEV_MISSING_SVC, {"conn_handle": conn_handle})
