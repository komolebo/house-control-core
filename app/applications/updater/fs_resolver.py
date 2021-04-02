import re

import os

from app.applications.devices.device_data import DeviceTypeInfo


class FsSensorBuildHandler:
    FS_PATH_SENSOR_BUILDS = '/opt/homenet/sensor_builds/'

    builds = {  # the keys are allowed device type to update
        DeviceTypeInfo.motion: [],
        DeviceTypeInfo.gas: []
    }

    @classmethod
    def __init__(cls):
        cls.fs_lookup_builds()

    @staticmethod
    def _verify_build_name_format(build_name):
        # accepted name format: '<type>__<major><minor><patch>'
        return re.compile('^[a-zA-Z0-9]+__[0-9]+\.[0-9]+\.[0-9]+\.bin').match(build_name) is not None

    @staticmethod
    def _parse_build_name_to_ver(build_name):
        dev_type, version = build_name.replace('.bin', '').split('__')
        return dev_type, version

    @classmethod
    def fs_lookup_builds(cls):
        # scan FS for build names
        build_list = [f.name for f in os.scandir(cls.FS_PATH_SENSOR_BUILDS) if f.is_file()]

        # verify build names
        build_list = [x for x in build_list if cls._verify_build_name_format(x)]

        # save versions based on build name
        for build_name in build_list:
            dev_type, version = cls._parse_build_name_to_ver(build_name)
            if dev_type in cls.builds.keys():
                cls.builds[dev_type].append(version)

        # sort versions to get the latest one:
        for dev_type in cls.builds.keys():
            cls.builds[dev_type].sort()

    @classmethod
    def get_latest_version(cls, dev_type):
        if dev_type in cls.builds.keys() and len(cls.builds[dev_type]):
            return cls.builds[dev_type][-1]

    @classmethod
    def get_latest_version_path(cls, dev_type):
        return cls.FS_PATH_SENSOR_BUILDS + dev_type + '__' + cls.get_latest_version(dev_type) + '.bin'
