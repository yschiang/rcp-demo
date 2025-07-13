from typing import List
from .die import Die

class WaferMap:
    def __init__(self, dies: List[Die]):
        self.dies = dies

    def get_available_dies(self) -> List[Die]:
        return [die for die in self.dies if die.available]
