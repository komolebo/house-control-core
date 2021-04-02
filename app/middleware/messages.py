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

    SEARCH_DEVICES = create_id()
    SEARCH_DEVICES_RESP = create_id()

    SCAN_DEVICE = create_id()
    SCAN_DEVICE_ABORT = create_id()
    SCAN_DEVICE_RESP = create_id()

    ESTABLISH_CONN = create_id()
    ESTABLISH_CONN_ABORT = create_id()
    ESTABLISH_CONN_RESP = create_id()

    TERMINATE_CONN = create_id()
    TERMINATE_CONN_RESP = create_id()

    DEVICE_DISCONN = create_id()

    DEV_MTU_CFG = create_id()
    DEV_MTU_CFG_RESP = create_id()

    DEV_LINK_PARAM_CFG = create_id()
    DEV_LINK_PARAM_CFG_RESP = create_id()

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

    DEV_INDICATION = create_id()
    DEV_DATA_CHANGE_RESP = create_id()

    DEV_WRITE_CHAR_VAL = create_id()
    DEV_WRITE_CHAR_VAL_RESP = create_id()

    FRONT_MSG = create_id()

    DEV_INFO_ADD = create_id()
    DEV_INFO_ADD_ACK = create_id()

    DEV_INFO_REM = create_id()
    DEV_INFO_REM_ACK = create_id()

    DEV_INFO_UPD = create_id()
    DEV_INFO_UPD_ACK = create_id()

    DEV_INFO_READ = create_id()
    DEV_INFO_READ_ACK = create_id()

    DEV_INFO_READ_LIST = create_id()
    DEV_INFO_READ_LIST_ACK = create_id()

# update
    UPDATE_VERSION_DISCOVERED = create_id()
    UPDATE_AVAILABLE = create_id()