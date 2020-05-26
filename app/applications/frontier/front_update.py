from app.applications.frontier.signals import FrontSignals
from house_control.events import send_notification_to_front


class FrontUpdateHandler:
    def __init__(self):
        # self.disc_handler = DiscoveryHandler()
        pass

    @classmethod
    def notify_front(cls, notification, data):
        send_notification_to_front(notification, data)

    # def handle_dev_values_discover(self, conn_handle, char_value_data):
    #     for char_val_item in char_value_data:
    #         if isinstance(char_val_item, CharValueData):
    #             self.disc_handler.process_data_change(conn_handle, char_val_item.handle, char_val_item.value)
    #
    # def handle_dev_data_update(self, conn_handle, handle, value):
    #     uuid = self.disc_handler.get_uuid_by_handle(conn_handle, handle)
    #     if uuid == CharUuid.DS_STATE.uuid:
    #         self.handle_dev_notify_status(conn_handle, value)
    #     elif uuid == CharUuid.BATTERY_LEVEL.uuid:
    #         self.handle_dev_notify_battery(conn_handle, value)
    #     elif uuid == CharUuid.TS_STATE.uuid:
    #         self.handle_dev_notify_tamper(conn_handle, value)

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