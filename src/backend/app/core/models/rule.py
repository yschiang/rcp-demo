from abc import ABC, abstractmethod
from .wafer_map import WaferMap
from .die import Die
from typing import List

class Rule(ABC):
    @abstractmethod
    def apply(self, wafer_map: WaferMap) -> List[Die]:
        pass

class FixedPointRule(Rule):
    def __init__(self, points: List[tuple]):
        self.points = points

    def apply(self, wafer_map: WaferMap) -> List[Die]:
        return [die for die in wafer_map.dies if (die.x, die.y) in self.points]
