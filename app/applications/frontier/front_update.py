from app.applications.frontier.signals import FrontSignals
from house_control.events import send_notification_to_front

class FrontUpdateHandler:
    @classmethod
    def notify_front(cls, notification, data):
        send_notification_to_front(notification, data)

    def handle_dev_notify_battery(self, conn_handle, value):
        self.notify_front(FrontSignals.DEV_NOTIFY_BATTERY_DATA,
                          {'conn_handle': conn_handle,
                           'value': value})

    def handle_dev_notify_tamper(self, conn_handle, value):
        self.notify_front(FrontSignals.DEV_NOTIFY_TAMPER_DATA,
                          {'conn_handle': conn_handle,
                           'value': value})

    def handle_dev_notify_status(self, conn_handle, value):
        self.notify_front(FrontSignals.DEV_NOTIFY_STATUS_DATA,
                          {'conn_handle': conn_handle,
                           'value': value})

    def handle_dev_add_new(self, conn_handle, device_type, state, battery, tamper, status, location='Kitchen',
                           device_name='motion'):
        self.notify_front(FrontSignals.DEV_ADD_SENSOR,
                          {'conn_handle': conn_handle,
                           'device_type': device_type,
                           'state': state,
                           'battery': battery,
                           'tamper': tamper,
                           'status': status,
                           'location': location,
                           'device_name': device_name})