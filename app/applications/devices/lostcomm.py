from time import time

from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.middleware.timers import TimerHandler

DEFAULT_LOSTCOMM_TIME = 5  # seconds
POOLING_TIME = 1  # second


class DeviceLostCommInfo:
    LOST = 0
    ACTIVE = 1

    def __init__(self, _id, _time=time()):
        self._id = _id
        self.state = self.ACTIVE
        self.last_response_time = _time

    def set_state(self, state):
        self.state = state


class LostCommHandler:
    lost_comm_table = {}

    @classmethod
    def __init__(cls, device_id_list):
        curr_time = time()
        for _id in device_id_list:
            cls.lost_comm_table[_id] = DeviceLostCommInfo(_id, curr_time)

        cls.timer_handler = TimerHandler(cls.monitor_table, POOLING_TIME)

    @classmethod
    def monitor_table(cls):
        print("Monitoring lost comm")
        curr_time = time()
        for device_id in cls.lost_comm_table.keys():
            lost_comm_item = cls.lost_comm_table[device_id]

            # skip already lost devices
            if lost_comm_item.state is DeviceLostCommInfo.LOST:
                return

            if curr_time - lost_comm_item.last_response_time > DEFAULT_LOSTCOMM_TIME:
                lost_comm_item.set_state(DeviceLostCommInfo.LOST)
                Dispatcher.send_msg(Messages.DEVICE_LOST_COMM, {"id": device_id})

    @classmethod
    def process_device_response(cls, device_id):
        cls.lost_comm_table[device_id] = time()

        old_state = cls.lost_comm_table[device_id].state
        if old_state is DeviceLostCommInfo.LOST:
            Dispatcher.send_msg(Messages.CLEAR_DEVICE_LOST_COMM, {"id": device_id})

    @classmethod
    def handle_remove_device(cls, device_id):
        cls.lost_comm_table.pop(device_id)

    @classmethod
    def handle_add_device(cls, device_id):
        curr_time = time()
        cls.lost_comm_table[device_id] = DeviceLostCommInfo(device_id, curr_time)
