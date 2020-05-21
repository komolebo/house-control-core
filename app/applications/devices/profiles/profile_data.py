from app.applications.devices.device_manager import DeviceType
from app.applications.devices.profiles.profile_uuid import ServiceUuid


class ProfileTable:
    info = {
        DeviceType.motion: [
            ServiceUuid.CONFIG,
            ServiceUuid.DATA,
            ServiceUuid.TAMPER
        ],
        DeviceType.gas: [

        ]
    }