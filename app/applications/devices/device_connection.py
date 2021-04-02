from apscheduler.schedulers.background import BackgroundScheduler

from app.applications.devices.device_data import DevDataHandler
from app.applications.devices.conn_info import DevConnDataHandler
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.middleware.timers import ScheduleItems


# Data scanning, tracking lost connections, reconnecting
class DevConnManager(DevConnDataHandler):
    scheduler = BackgroundScheduler()
    scheduler.start()
    scan_pending = False

    @classmethod
    def _add_job(cls):
        scan_period = 20  # sec
        cls.scheduler.add_job(cls.scan_schedule_cb, 'interval', seconds=scan_period, id=ScheduleItems.CONN_POLL)

    @classmethod
    def _rem_job(cls):
        if cls.scheduler.get_job(ScheduleItems.CONN_POLL):
            cls.scheduler.remove_job(ScheduleItems.CONN_POLL)

    @classmethod
    def start_scanning(cls):
        if cls.scheduler.get_job(ScheduleItems.CONN_POLL):
            print("period scanner is already enabled")
        else:
            cls._add_job()

    @classmethod
    def restart_scanning(cls):
        cls._rem_job()
        cls._add_job()

    @classmethod
    def stop_scanning(cls):
        cls._rem_job()

    @classmethod
    def scan_schedule_cb(cls):
        # check for devices in database without conn handle
        for dev in DevDataHandler.read_all_dev():
            if not cls.is_mac_active(dev.mac) and "00000000000" not in dev.mac:
                print("SCANNING for ", dict(DevDataHandler.get_dev(dev.mac, _serializable=True)))
                Dispatcher.send_msg(Messages.SCAN_DEVICE, data={})
                cls.scan_pending = True
                return

    @classmethod
    def process_scan_resp(cls, scan_list):
        cls.scan_pending = False

        # add conn handle for scanned device which is in db
        for dev in DevDataHandler.read_all_dev():
            for scan_dev in scan_list:
                print("scan dev = {}, db dev = {}".format(dev, scan_dev))
                if scan_dev.mac == dev.mac:
                    # device is available again after disconnection
                    # force conn establishment with known device
                    Dispatcher.send_msg(Messages.ESTABLISH_CONN, {"mac": dev.mac,
                                                                  "type": dev.type,
                                                                  "name": dev.name,
                                                                  "location": dev.location})

    @classmethod
    def handle_scan_on_demand(cls):
        if cls.scan_pending:
            print("Scan is already running, skipping on demand scan req")
            pass  # if periodic scan is in progress -> do not scan again
        else:  # otherwise do a scan and delay periodic
            cls.restart_scanning()
            Dispatcher.send_msg(Messages.SCAN_DEVICE, data={})
