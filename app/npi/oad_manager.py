from app.npi.npi_manager import NpiManager
from app.npi.oad_fsm import OadFsm

CONN_HANDLE = 0x0

import os
print(os.path.abspath(os.getcwd()))


if __name__ == '__main__':
    npi = NpiManager('/dev/ttyUSB0')
    oadFsm = OadFsm(CONN_HANDLE, npi)

    oadFsm.start()

    while 1:
        npi_msg = npi.process_next_msg()
        print("DUMP RX: ", npi_msg.as_output())
        oadFsm.on_event(npi_msg)
