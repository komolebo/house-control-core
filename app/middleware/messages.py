from app.middleware.abstracts import AbstractNamedEnumsInClass

enum_counter = 0

def create_id():
    global enum_counter
    current_number = enum_counter
    enum_counter += 1
    return current_number


class Messages(AbstractNamedEnumsInClass):
    TEST_MSG = create_id()
    TEST_MSG2 = create_id()
    SENSOR_REMOVED_FROM_FRONT = create_id()
    DEVICE_LOST_COMM = create_id()
    CLEAR_DEVICE_LOST_COMM = create_id()

    NPI_SERIAL_PORT_LISTEN = create_id()
    NPI_RX_MSG = create_id()

    OAD_START = create_id()
    OAD_ABORT = create_id()

