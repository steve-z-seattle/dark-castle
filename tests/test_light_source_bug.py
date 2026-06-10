"""
Test case demonstrating the has_light_source() bug.

Bug: has_light_source() only checks inventory, not items in the current room.
So a lit candlestick dropped on the floor in a dark room continues burning
but ceases to provide any illumination.
"""

import sys
from pathlib import Path

# Add the backend package to the path
BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from game.engine import GameEngine


def test_lit_candlestick_in_inventory_provides_light():
    """PASSING: Lit candlestick in inventory should light up a dark room."""
    engine = GameEngine()
    engine.new_game()

    engine.process_command("take candlestick")
    engine.process_command("take matches")
    engine.process_command("light candlestick")
    engine.process_command("down")  # enter dark basement

    assert engine.world.current_room == "basement"
    assert engine.world.items["candlestick"].is_lit()
    assert "candlestick" in engine.world.inventory
    assert engine.world.has_light_source() is True
    assert engine.world.can_see() is True
    print("✅ test_lit_candlestick_in_inventory_provides_light PASSED")


def test_lit_candlestick_on_floor_should_provide_light():
    """
    FAILING (bug): Lit candlestick dropped in a dark room should still
    provide light because it is still burning on the floor.
    """
    engine = GameEngine()
    engine.new_game()

    engine.process_command("take candlestick")
    engine.process_command("take matches")
    engine.process_command("light candlestick")
    engine.process_command("down")  # enter dark basement
    engine.process_command("drop candlestick")

    assert engine.world.current_room == "basement"
    assert engine.world.items["candlestick"].is_lit() is True, (
        "candlestick should still be burning"
    )
    assert engine.world.items["candlestick"].location == "basement", (
        "candlestick should be on the floor"
    )
    assert "candlestick" not in engine.world.inventory, (
        "candlestick is no longer carried"
    )

    # BUG: has_light_source() returns False because it only checks inventory.
    # It SHOULD return True because there is a lit candlestick in the room.
    assert engine.world.has_light_source() is True, (
        "BUG: has_light_source() ignores the lit candlestick on the floor"
    )
    assert engine.world.can_see() is True, (
        "BUG: can_see() is False even though a lit candlestick is burning nearby"
    )
    print("✅ test_lit_candlestick_on_floor_should_provide_light PASSED")


def test_unlit_candlestick_on_floor_does_not_provide_light():
    """PASSING: An unlit candlestick on the floor should not provide light."""
    engine = GameEngine()
    engine.new_game()

    engine.process_command("take candlestick")
    engine.process_command("down")  # enter dark basement (unlit)
    engine.process_command("drop candlestick")

    assert engine.world.items["candlestick"].is_lit() is False
    assert engine.world.has_light_source() is False
    assert engine.world.can_see() is False
    print("✅ test_unlit_candlestick_on_floor_does_not_provide_light PASSED")


if __name__ == "__main__":
    test_lit_candlestick_in_inventory_provides_light()
    test_unlit_candlestick_on_floor_does_not_provide_light()

    print()
    try:
        test_lit_candlestick_on_floor_should_provide_light()
    except AssertionError as e:
        print(f"❌ test_lit_candlestick_on_floor_should_provide_light FAILED: {e}")
        sys.exit(1)
