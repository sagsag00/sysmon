import attr
import threading

@attr.s(auto_attribs=True)
class Config:
    _cpu_warn: float = 85
    _mem_warn: float = 85
    _interval: int = 2
    
    @property
    def cpu_warn(self):
        with Config._lock:
            return self._cpu_warn
        
    @property.setter
    def cpu_warn(self, value):
        with Config._lock:
            self._cpu_warn = value
            
    @property
    def mem_warn(self):
        with Config._lock:
            return self._mem_warn
        
    @property.setter
    def mem_warn(self, value):
        with Config._lock:
            self._mem_warn = value
            
    @property
    def interval(self):
        with Config._lock:
            return self._interval
        
    @property.setter
    def interval(self, value):
        with Config._lock:
            self._interval = value

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                     cls._instance = cls()
        return cls._instance
    
Config._instance = None
Config._lock = threading.Lock()