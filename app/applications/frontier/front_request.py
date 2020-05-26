from app.applications.devices.discovery.discovery import DiscoveryHandler
from app.applications.devices.profiles.profile_uuid import CharUuid
from app.applications.frontier.signals import FrontSignals
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages


class FrontReqHandler:
    def __init__(self):
        self.disc_handler = DiscoveryHandler()
        self.req_table = {
            FrontSignals.DEV_SCAN_REQ : (
                self.handle_dev_scan_req,
                []
            ),

            FrontSignals.DEV_CONN_REQ: (
                self.handle_dev_conn_req,
                ["mac", "type", "name"]
            ),

            FrontSignals.DEV_CHANGE_STATE_REQ: (
                self.handle_dev_change_state_req,
                ["conn_handle", "value"]
            ),

            FrontSignals.DEV_CHANGE_NAME_REQ: (
                self.handle_dev_change_name_req,
                ["conn_handle", "value"]
            ),

            FrontSignals.DEV_REMOVE_REQ: (
                self.handle_dev_remove_req,
                ["conn_handle"]
            )
        }

    def handle_front_request(self, req_data):
        cmd = 'dev_req'
        data = {}
        if cmd in self.req_table.keys():
            handler, keys = self.req_table[cmd]
            if set(keys).issubset(set(data.keys())):
                handler(data)

    def handle_dev_scan_req(self, data):
        self.send_event_response(msg=Messages.SCAN_DEVICE,
                                 data={})

    def handle_dev_conn_req(self, data):
        self.send_event_response(msg=Messages.ESTABLISH_CONN,
                                 data={'mac': data['mac'],
                                       'type': data['type'],
                                       'name': data['name']})

    def handle_dev_change_state_req(self, data):
        conn_handle = data['conn_handle']
        handle = self.disc_handler.get_handle_by_uuid(conn_handle,
                                                      CharUuid.DS_STATE.uuid
                                                      )[0]
        self.send_event_response(msg=Messages.DEV_DATA_CHANGE,
                                 data={'conn_handle': conn_handle,
                                       'handle': handle,
                                       'value': data['value']})

    def handle_dev_change_name_req(self, data):
        conn_handle = data['conn_handle']
        handle = self.disc_handler.get_handle_by_uuid(conn_handle,
                                                      CharUuid.DEVICE_NAME.uuid
                                                      )[0]
        self.send_event_response(msg=Messages.DEV_DATA_CHANGE,
                                 data={'conn_handle': conn_handle,
                                       'handle': handle,
                                       'value': data['value']})

    def handle_dev_remove_req(self, data):
        self.send_event_response(msg=Messages.TERMINATE_CONN,
                                 data={'conn_handle': data['conn_handle']})

    @classmethod
    def send_event_response(cls, msg, data):
        Dispatcher.send_msg(msg, data)
