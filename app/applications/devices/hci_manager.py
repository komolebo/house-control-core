from abc import ABC, abstractmethod, abstractproperty


class HciInterceptHandler:
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def complete(self, rsp_code=None):
        pass

    @abstractmethod
    def abort(self):
        pass

    @abstractmethod
    def process_incoming_npi_msg(self, hci_msg_rx):
        pass
