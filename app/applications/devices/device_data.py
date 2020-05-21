class DeviceType:
    motion = "motion"
    gas = "gas"


class DeviceConnData:
    def __init__(self, dev_type, services, chars):
        self.dev_type = dev_type
        self.services = services
        self.chars = chars