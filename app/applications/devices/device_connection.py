from app.applications.devices.device_data import DevDataHandler
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.middleware.timers import Scheduler, ScheduleItems


class DevConnHandler:
    dev_conn_info = {}  # key -> handle
                        # value -> MAC
    @classmethod
    def add_conn_info(cls, _handle, _mac):
        if isinstance(_mac, (bytes, bytearray)):
            _mac = str(bytes(_mac).hex())
        if _handle in cls.dev_conn_info.keys():
            raise Exception("Connection handle {} is already established".format(_handle))
        cls.dev_conn_info[_handle] = _mac

    @classmethod
    def del_conn_info(cls, _conn_handle=None, _mac=None):
        if _conn_handle is not None:
            cls.dev_conn_info.pop(_conn_handle)
        elif _mac:
            cls.dev_conn_info = {hdl:mac for hdl,mac in cls.dev_conn_info.items() if mac != _mac}

    @classmethod
    def get_handle_by_mac(cls, _mac):
        for handle, mac in cls.dev_conn_info.items():
            if mac == _mac:
                return handle
        return None

    @classmethod
    def get_mac_by_handle(cls, _handle):
        return cls.dev_conn_info[_handle] if _handle in cls.dev_conn_info.keys() else None

    @classmethod
    def is_mac_active(cls, _mac):
        return cls.get_handle_by_mac(_mac) is not None


class DevConnManager(DevConnHandler):
    SCAN_PERIOD = 20  # sec
    scan_enabled = False  # by default period scanner is enabled

    @classmethod
    def scan_start_schedule(cls):
        if not cls.scan_enabled:
            Scheduler.register_job(cls.scan_req, ScheduleItems.CONN_POLL, cls.SCAN_PERIOD)
            cls.scan_enabled = True
        else:
            print("period scanner is already enabled")

    @classmethod
    def scan_disable_schedule(cls):
        if cls.scan_enabled:
            Scheduler.remove_job(ScheduleItems.CONN_POLL)
            cls.scan_enabled = False

    @classmethod
    def scan_req(cls):
        print("SCANNING")
        # check for devices in database without conn handle
        for dev in DevDataHandler.read_all_dev():
            print("SCANNING", dict(dev))
            if not cls.is_mac_active(dev['mac']) and "00000000000" not in dev["mac"]:
                Dispatcher.send_msg(Messages.SCAN_DEVICE, data={})
                return

    @classmethod
    def process_scan_resp(cls, scan_list):
        # add conn handle for scanned device which is in db
        for dev in DevDataHandler.read_all_dev():
            for scan_dev in scan_list:
                print("scan dev = {}, db dev = {}".format(dev, scan_dev))
                if scan_dev.mac == dev['mac']:
                    # device is available again after disconnection
                    # force conn establishment with known device
                    Dispatcher.send_msg(Messages.ESTABLISH_CONN, {"mac": dev['mac'],
                                                                  "type": dev['type'],
                                                                  "name": dev['name'],
                                                                  "location": dev['location']})
