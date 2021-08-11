""" AutoDict class definition file"""


class AutoDict(dict):
    """Utility class for creating a Dict that also
    on a key error gets the object from the API
    """

    def __init__(self, BaseClass, *args, **kwargs):  # pylint: disable=invalid-name
        self.Base = BaseClass  # pylint: disable=invalid-name
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        if key not in self.keys():
            self[key] = self.Base.find(key)
        return super().__getitem__(key)
