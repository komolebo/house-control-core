from app.applications.devices.discovery.discovery import DiscoveryHandler
from app.applications.devices.profiles.profile_uuid import CharUuid
from app.applications.frontier.signals import FrontSignals
from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages


class FrontReqHandler:
    def __init__(self):
        self.req_table = {
            FrontSignals.DEV_SCAN_REQ : (
                lambda data : Dispatcher.send_msg(Messages.SEARCH_DEVICES, data),
                []
            ),
            FrontSignals.DEV_CONN_REQ : (
                lambda data : Dispatcher.send_msg(Messages.ESTABLISH_CONN, data),
                []
            ),
            # FrontSignals.DEV_ADD : (
            #     lambda data : Dispatcher.send_msg(Messages.DEV_INFO_ADD, data),
            #     [] # todo
            # ),
            FrontSignals.DEV_READ : (
                lambda data : Dispatcher.send_msg(Messages.DEV_INFO_READ, data),
                [] # todo
            ),
            FrontSignals.DEV_UPD : (
                lambda data : Dispatcher.send_msg(Messages.DEV_INFO_UPD, data),
                [] # todo
            ),
            FrontSignals.DEV_REM : (
                lambda data : Dispatcher.send_msg(Messages.DEV_INFO_REM, data),
                [] # todo
            ),
            FrontSignals.DEV_READ_LIST : (
                lambda data : Dispatcher.send_msg(Messages.DEV_INFO_READ_LIST, data),
                [] # todo
            ),

            FrontSignals.UPDATE_DEV: (
                lambda data : Dispatcher.send_msg(Messages.OAD_START, data),
                []
            ),

            # FrontSignals.DEV_CONN_REQ: (
            #     lambda data: self.send_event_response(
            #         msg=Messages.ESTABLISH_CONN,
            #         data={'mac': data['mac'],
            #         'type': data['type'],
            #         'name': data['name']}),
            #     ["mac", "type", "name"]
            # ),

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

    def handle_front_request(self, msg, payload):
        if msg in self.req_table.keys():
            handler, keys = self.req_table[msg]
            if handler:
                if not len(keys):# or set(keys).issubset(set(payload.keys())):
                    # pass
                    handler(payload)

    def handle_dev_conn_req(self, data):
        self.send_event_response(msg=Messages.ESTABLISH_CONN,
                                 data={'mac': data['mac'],
                                       'type': data['type'],
                                       'name': data['name'],
                                       'version': data['version']})

    def handle_dev_change_state_req(self, data):
        conn_handle = data['conn_handle']
        handle = DiscoveryHandler.get_handle_by_uuid(conn_handle,
                                                     CharUuid.DS_STATE.uuid
                                                     )[0]
        self.send_event_response(msg=Messages.DEV_INDICATION,
                                 data={'conn_handle': conn_handle,
                                       'handle': handle,
                                       'value': data['value']})

    def handle_dev_change_name_req(self, data):
        conn_handle = data['conn_handle']
        handle = DiscoveryHandler.get_handle_by_uuid(conn_handle,
                                                     CharUuid.DEVICE_NAME.uuid
                                                     )[0]
        self.send_event_response(msg=Messages.DEV_INDICATION,
                                 data={'conn_handle': conn_handle,
                                       'handle': handle,
                                       'value': data['value']})

    def handle_dev_remove_req(self, data):
        self.send_event_response(msg=Messages.TERMINATE_CONN,
                                 data={'conn_handle': data['conn_handle']})

    @classmethod
    def send_event_response(cls, msg, data):
        Dispatcher.send_msg(msg, data)
