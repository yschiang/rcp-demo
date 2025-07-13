from backend.app.core.models.die import Die
from backend.app.core.models.wafer_map import WaferMap

def build_dummy_wafer():
    dies = [Die(x, y) for x in range(5) for y in range(5)]
    return WaferMap(dies)
