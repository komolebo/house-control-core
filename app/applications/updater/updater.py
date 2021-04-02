from abc import ABC

from app.applications.devices.device_data import DeviceTypeInfo
from app.applications.devices.conn_info import DevConnDataHandler
from app.applications.updater.fs_resolver import FsSensorBuildHandler
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.middleware.threads import AppThread


class SensorVersionData:
    def __init__(self, dev_type, version):
        self.dev_type = dev_type
        self.version = version
        self.major, self.minor, self.patch = self.version.split('.')

    def is_older_than(self, version):
        if version:
            major, minor, patch = version.split('.')
            return int(major) > int(self.major) or int(minor) > int(self.minor) or int(patch) > int(self.patch)
        else:
            # assume an invalid version provided, thus the current is the latest
            return False


class TrackInfoHandler:
    # keys -> mac, values -> (type, version)
    version_track_table = { }

    def add_dev(self, mac, dev_type, version):
        self.version_track_table[mac] = SensorVersionData(dev_type, version)

    def rem_dev(self, mac):
        self.version_track_table.pop(mac)


class UpdateManager(TrackInfoHandler):
    pass


class UpdateApp(AppThread, UpdateManager):
    def __init__(self, mbox):
        AppThread.__init__(self, mbox)
        FsSensorBuildHandler.__init__()

    def on_message(self, msg, data):
        if msg is Messages.UPDATE_VERSION_DISCOVERED:
            self.add_dev(data['mac'], data['type'], data['version'])
            # check device for an update
            added_dev = self.version_track_table[data['mac']]
            latest_version = FsSensorBuildHandler.get_latest_version(data['type'])
            if added_dev.is_older_than(latest_version):
                # notify application that update is possible
                file_path = FsSensorBuildHandler.get_latest_version_path(data['type'])
                Dispatcher.send_msg(Messages.UPDATE_AVAILABLE, data={'mac': data['mac'],
                                                                     'version': latest_version,
                                                                     'type': data['type'],
                                                                     'file_path': file_path})

        elif msg in (Messages.TERMINATE_CONN, Messages.DEVICE_DISCONN):
            mac = DevConnDataHandler.get_mac_by_handle(data["conn_handle"])
            self.rem_dev(mac)
