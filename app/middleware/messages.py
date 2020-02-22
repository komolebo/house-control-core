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
