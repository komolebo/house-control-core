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

    CENTRAL_RESET = create_id()
    CENTRAL_RESET_RESP = create_id()

    CENTRAL_INIT = create_id()
    CENTRAL_INIT_RESP = create_id()

    CENTRAL_ADJUST = create_id()
    CENTRAL_ADJUST_RESP = create_id()

    OAD_START = create_id()
    OAD_ABORT = create_id()
    OAD_COMPLETE = create_id()

    SCAN_DEVICE = create_id()
    SCAN_DEVICE_ABORT = create_id()
    SCAN_DEVICE_RESP = create_id()

    ESTABLISH_CONN = create_id()
    ESTABLISH_CONN_ABORT = create_id()
    ESTABLISH_CONN_RESP = create_id()

    TERMINATE_CONN = create_id()
    TERMINATE_CONN_RESP = create_id()

    DEVICE_DISCONN = create_id()

    DEV_SVC_DISCOVER = create_id()
    DEV_SVC_DISCOVER_RESP = create_id()

    DEV_CHAR_DISCOVER = create_id()
    DEV_CHAR_DISCOVER_RESP = create_id()

    DEV_VALUES_DISCOVER = create_id()
    DEV_VALUES_DISCOVER_RESP = create_id()

    ERR_DEV_MISSING_SVC = create_id()
    ERR_DEV_MISSING_CHAR = create_id()

    ERR_DEV_CONN_NOT_EXIST = create_id()

    ENABLE_DEV_INDICATION = create_id()
    ENABLE_DEV_IND_RESP = create_id()

    DEV_DATA_CHANGE = create_id()
    DEV_DATA_CHANGE_RESP = create_id()

    DEV_WRITE_CHAR_VAL = create_id()
    DEV_WRITE_CHAR_VAL_RESP = create_id()

    FRONT_ADD_DEV = create_id()
    FRONT_ADD_DEV_ACK = create_id()

    FRONT_REM_DEV = create_id()
    FRONT_REM_DEV_ACK = create_id()

    FRONT_UPD_DEV = create_id()
    FRONT_UPD_DEV_ACK = create_id()

    FRONT_READ_DEV = create_id()
    FRONT_READ_DEV_ACK = create_id()

    FRONT_READ_DEV_LIST = create_id()
    FRONT_READ_DEV_LIST_ACK = create_id()
