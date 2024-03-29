class DummyCache:
    """This class exists so that our audio archive does not need to use a cache
    if it does not make sense to (such as in tests or our CLI).
    """

    def __init__(self):
        pass

    def add(self, _sound):
        return

    def getByName(self, _name):
        return

    def removeByName(self, _name):
        return

    def rename(self, _oldName, _newSound):
        return
