import attr

@attr.s(auto_attribs=True)
class Config:
    cpu_warn: float = 85
    mem_warn: float = 85
    interval: int = 2

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance