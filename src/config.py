from dataclasses import dataclass

@dataclass
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    cpu_warn: float = 85
    mem_warn: float = 85