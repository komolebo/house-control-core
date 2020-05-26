from app.applications.frontier.front_request import FrontReqHandler
from app.applications.frontier.front_update import FrontUpdateHandler
from app.middleware.messages import Messages
from app.middleware.threads import AppThread


class FrontManager(FrontUpdateHandler, FrontReqHandler):
    pass


class FrontierApp(AppThread, FrontManager):
    def __init__(self, mbox):
        AppThread.__init__(self, mbox)
        FrontManager.__init__(self)

    def on_message(self, msg, data):
        if msg is Messages.DEV_VALUES_DISCOVER_RESP:
            pass
