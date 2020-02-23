from app.applications.devices.lostcomm import LostCommHandler, DeviceLostCommInfo
from app.middleware.messages import Messages
from app.middleware.threads import AppThread
from app.models.models import Sensor

# from app.models.models import Sensor
from house_control.events import send_notification_to_front, Notifications


class DevManager(AppThread):
    def __init__(self, mbox):
        super().__init__(mbox)
        LostCommHandler([device.id for device in Sensor.objects.all()])

    def on_message(self, msg, data):
        if msg is Messages.SENSOR_REMOVED_FROM_FRONT:
            pass
        elif msg is Messages.DEVICE_LOST_COMM:
            self.handle_lost_comm(data, DeviceLostCommInfo.LOST)
        elif msg is Messages.CLEAR_DEVICE_LOST_COMM:
            self.handle_lost_comm(data, DeviceLostCommInfo.ACTIVE)

    @classmethod
    def on_add_sensor(cls, data):
        device_id = data["id"]
        LostCommHandler.handle_add_device(device_id)

    @classmethod
    def on_remove_sensor(cls, data):
        device_id = data["id"]
        LostCommHandler.handle_remove_device(device_id)

    @classmethod
    def handle_lost_comm(cls, data, new_state):
        Sensor.objects.get(id=data["id"]).status = new_state
        if new_state is DeviceLostCommInfo.LOST:
            send_notification_to_front(Notifications.LOST_COMM_DEVICE, data)
        elif new_state is DeviceLostCommInfo.ACTIVE:
            send_notification_to_front(Notifications.CLEAR_LOST_COMM_DEVICE, data)
