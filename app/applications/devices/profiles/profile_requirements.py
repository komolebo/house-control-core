from app.applications.devices.device_data import DeviceTypeInfo
from app.applications.devices.profiles.profile_uuid import ServiceUuid, CharUuid


class ProfileTable:
    svc_dev_map = {
        DeviceTypeInfo.motion: [
            ServiceUuid.CONFIG,
            ServiceUuid.DATA,
            ServiceUuid.TAMPER,
            ServiceUuid.RESET
        ],
        DeviceTypeInfo.gas: [
        ]
    }

    char_dev_map = {
        DeviceTypeInfo.motion: [
            # CharUuid.DEVICE_NAME.uuid,
            CharUuid.CS_MODE.uuid,
            CharUuid.DS_STATE.uuid,
            CharUuid.TS_STATE.uuid,
            CharUuid.BATTERY_LEVEL.uuid,
            CharUuid.SOFTWARE_REVISION_UUID.uuid,
            # CharUuid.OAD_START_UUID
        ]
    }

    disc_char_dev_map = {
        DeviceTypeInfo.motion: [
            # CharUuid.DEVICE_NAME.uuid,
            CharUuid.CS_MODE.uuid,
            CharUuid.DS_STATE.uuid,
            CharUuid.TS_STATE.uuid,
            CharUuid.BATTERY_LEVEL.uuid,
            CharUuid.SOFTWARE_REVISION_UUID.uuid,
        ]
    }
