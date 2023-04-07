import pytest

from routine_butler.elements.routines_sidebar import (
    RoutinesSidebar,  # TODO
    RoutineConfigurer,  # TODO
    RoutineItemsExpansion,
    RoutineItemRow,  # TODO
    AlarmsExpansion,  # TODO
    AlarmRow,  # TODO
)
from routine_butler.database.repository import Repository
from routine_butler.database.models import User, Routine, RoutineItem


@pytest.fixture(scope="function")
def empty_routine_items_expansion(repository: Repository):
    routine = Routine()
    user = User(routines=[routine])
    ri_exp = RoutineItemsExpansion(
        user=user, routine=routine, repository=repository
    )
    yield ri_exp
    del ri_exp


class TestRoutineItemsExpansion:
    def test_add_routine_item(
        self, empty_routine_items_expansion: RoutineItemsExpansion
    ):
        ri_exp = empty_routine_items_expansion
        ri_exp.add_routine_item()
        assert len(ri_exp.routine.routine_items) == 1
        assert ri_exp.routine.routine_items[0].order_index == 0
        assert ri_exp.routine.routine_items[0].is_reward is False
        ri_exp.add_routine_item()
        assert len(ri_exp.routine.routine_items) == 2
        assert ri_exp.routine.routine_items[1].order_index == 1
        assert ri_exp.routine.routine_items[1].is_reward is False

    def test_add_reward_item(
        self, empty_routine_items_expansion: RoutineItemsExpansion
    ):
        ri_exp = empty_routine_items_expansion
        ri_exp.add_reward_item()
        assert len(ri_exp.routine.routine_items) == 1
        assert ri_exp.routine.routine_items[0].order_index == 0
        assert ri_exp.routine.routine_items[0].is_reward is True
        ri_exp.add_reward_item()
        assert len(ri_exp.routine.routine_items) == 2
        assert ri_exp.routine.routine_items[1].order_index == 1
        assert ri_exp.routine.routine_items[1].is_reward is True

    # *
    def test_move_routine_item_upward(
        self, empty_routine_items_expansion: RoutineItemsExpansion
    ):
        ri_exp = empty_routine_items_expansion
        ri_exp.add_routine_item()
        ri_exp.add_routine_item()
        r_idx_0 = ri_exp.routine.routine_items[0]
        r_idx_1 = ri_exp.routine.routine_items[1]
        ri_exp.move_routine_item(r_idx_1, up=True)
        assert ri_exp.routine.routine_items[0] == r_idx_1
        assert ri_exp.routine.routine_items[1] == r_idx_0

    # *
    def test_move_routine_item_downard(
        self, empty_routine_items_expansion: RoutineItemsExpansion
    ):
        ri_exp = empty_routine_items_expansion
        ri_exp.add_routine_item()
        ri_exp.add_routine_item()
        r_idx_0 = ri_exp.routine.routine_items[0]
        r_idx_1 = ri_exp.routine.routine_items[1]
        ri_exp.move_routine_item(r_idx_0, down=True)
        assert ri_exp.routine.routine_items[0] == r_idx_1
        assert ri_exp.routine.routine_items[1] == r_idx_0

    def test_delete_routine_item(
        self, empty_routine_items_expansion: RoutineItemsExpansion
    ):
        pass

    # TODO: * these fail because I am not passing a RoutineItemRow... However,
    # I think I can rewrite the moving function to not need to take a RoutineItemRow

    # TODO: non-basic situations like:
    # - moving an item up when it's already at the top
    # - moving an item down when it's already at the bottom
    # - trying to move a non-reward item below a reward item
    # - trying to move a reward item above a non-reward item
    # - adding a routine item when there are already reward items
    # - moving reward items
