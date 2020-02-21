from app.middleware.threads import AppThread
from house_control.events import EventHandler, Events


class SensorHandler(AppThread):
    def __init__(self, mbox):
        super().__init__(mbox)
        EventHandler.subscribe(Events.SENSOR_ADD_REQUEST, self.on_add_sensor)
        EventHandler.subscribe(Events.SENSOR_REMOVE_REQUEST, self.on_remove_sensor)


    def on_message(self, msg, data):
        pass

    def on_add_sensor(self, data):
        pass

    def on_remove_sensor(self, data):
        pass
