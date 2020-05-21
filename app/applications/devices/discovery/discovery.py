from app.applications.devices.profiles.profile_data import ProfileTable


class DiscoveryManager:
    @staticmethod
    def diagnose_device_uuid(dev_type):
        services = ProfileTable.info[dev_type]