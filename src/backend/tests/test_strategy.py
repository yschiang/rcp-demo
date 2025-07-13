import pytest
from backend.app.core.models.die import Die
from backend.app.core.models.wafer_map import WaferMap
from backend.app.core.models.rule import FixedPointRule
from backend.app.core.models.strategy import GenericStrategy

@pytest.fixture
def wafer_map():
    dies = [Die(x, y) for x in range(5) for y in range(5)]
    return WaferMap(dies)

def test_fixed_point_rule_applies_correctly(wafer_map):
    rule = FixedPointRule(points=[(1, 1), (2, 2)])
    result = rule.apply(wafer_map)
    assert len(result) == 2
    coords = [(die.x, die.y) for die in result]
    assert (1, 1) in coords
    assert (2, 2) in coords

def test_strategy_applies_all_rules(wafer_map):
    rule1 = FixedPointRule(points=[(0, 0)])
    rule2 = FixedPointRule(points=[(4, 4)])
    strategy = GenericStrategy(name="test", rules=[rule1, rule2])
    result = strategy.apply(wafer_map)
    coords = [(die.x, die.y) for die in result]
    assert (0, 0) in coords
    assert (4, 4) in coords
