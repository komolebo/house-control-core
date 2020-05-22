from app.applications.devices.device_data import DeviceType
from app.applications.devices.profiles.profile_uuid import ServiceUuid


class ProfileTable:
    svc_type_map = {
        DeviceType.motion: [
            ServiceUuid.CONFIG,
            ServiceUuid.DATA,
            ServiceUuid.TAMPER
        ],
        DeviceType.gas: [

        ]
    }