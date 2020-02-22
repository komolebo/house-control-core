class AbstractNamedEnumsInClass:
    @classmethod
    def get_name_by_enum_id(cls, enum_id):
        public_attr_names = [msg for msg in dir(cls) if not msg.startswith("__")]
        messages_names = [attr for attr in public_attr_names if not callable(getattr(cls, attr))]
        return next(filter(lambda msg_name: getattr(cls, msg_name) == enum_id, messages_names), None)
