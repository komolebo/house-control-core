from app.applications.devices.device_data import DeviceTypeInfo
from app.applications.devices.profiles.profile_uuid import ServiceUuid, CharUuid


class ProfileTable:
    svc_dev_map = {
        DeviceTypeInfo.motion: [
            ServiceUuid.CONFIG,
            ServiceUuid.DATA,
            ServiceUuid.TAMPER
        ],
        DeviceTypeInfo.gas: [
        ]
    }

    char_dev_map = {
        DeviceTypeInfo.motion: [
            CharUuid.DEVICE_NAME.uuid,
            CharUuid.DS_STATE.uuid,
            CharUuid.TS_STATE.uuid,
            CharUuid.BATTERY_LEVEL.uuid
        ]
    }
