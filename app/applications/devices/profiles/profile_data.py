from app.applications.devices.device_data import DeviceType
from app.applications.devices.profiles.profile_uuid import ServiceUuid, CharUuid


class ProfileTable:
    svc_dev_map = {
        DeviceType.motion: [
            ServiceUuid.CONFIG,
            ServiceUuid.DATA,
            ServiceUuid.TAMPER
        ],
        DeviceType.gas: [
        ]
    }

    char_dev_map = {
        DeviceType.motion: [
            CharUuid.DEVICE_NAME.uuid,
            CharUuid.DS_STATE.uuid,
            CharUuid.TS_STATE.uuid,
            CharUuid.BATTERY_LEVEL.uuid
        ]
    }