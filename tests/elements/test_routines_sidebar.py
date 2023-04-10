from copy import deepcopy

import pytest
from sqlmodel import Session

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


def empty_routine_items_expansion(
    repository: Repository,
) -> RoutineItemsExpansion:
    routine = Routine()
    ri_exp = RoutineItemsExpansion(routine=routine, repository=repository)
    return ri_exp


ADD_ITEMS_CASES = [
    # same number of routine and reward items
    {"n_routine": 2, "n_rwrd": 2, "alternate": False, "rwrd_1st": False},
    {"n_routine": 3, "n_rwrd": 3, "alternate": True, "rwrd_1st": False},
    {"n_routine": 2, "n_rwrd": 2, "alternate": False, "rwrd_1st": True},
    {"n_routine": 3, "n_rwrd": 3, "alternate": True, "rwrd_1st": True},
    # more routine items than reward items
    {"n_routine": 3, "n_rwrd": 2, "alternate": False, "rwrd_1st": False},
    {"n_routine": 4, "n_rwrd": 3, "alternate": True, "rwrd_1st": False},
    {"n_routine": 3, "n_rwrd": 2, "alternate": False, "rwrd_1st": True},
    {"n_routine": 4, "n_rwrd": 3, "alternate": True, "rwrd_1st": True},
    # more reward items than routine items
    {"n_routine": 2, "n_rwrd": 3, "alternate": False, "rwrd_1st": False},
    {"n_routine": 3, "n_rwrd": 4, "alternate": True, "rwrd_1st": False},
    {"n_routine": 2, "n_rwrd": 3, "alternate": False, "rwrd_1st": True},
    {"n_routine": 3, "n_rwrd": 4, "alternate": True, "rwrd_1st": True},
]


class TestRoutineItemsExpansion:
    def _add_items(
        self,
        ri_exp: RoutineItemsExpansion,
        session: Session,
        n_routine: int,
        n_rwrd: int,
        alternate: bool = False,
        rwrd_1st: bool = False,
    ):
        """Adds `n_routine` routine items and `n_reward` reward items to a
        routine, alternating between the two if `alternate` is True, and
        adding reward items first if `reward_first` is True"""
        if alternate:
            while n_rwrd > 0 and n_routine > 0:
                if rwrd_1st:
                    if n_rwrd > 0:
                        ri_exp.add_reward_item(session=session)
                        n_rwrd -= 1
                    if n_routine > 0:
                        ri_exp.add_routine_item(session=session)
                        n_routine -= 1
                else:
                    if n_routine > 0:
                        ri_exp.add_routine_item(session=session)
                        n_routine -= 1
                    if n_rwrd > 0:
                        ri_exp.add_reward_item(session=session)
                        n_rwrd -= 1
        else:
            if rwrd_1st:
                for _ in range(n_rwrd):
                    ri_exp.add_reward_item(session=session)
                for _ in range(n_routine):
                    ri_exp.add_routine_item(session=session)
            elif not rwrd_1st:
                for _ in range(n_routine):
                    ri_exp.add_routine_item(session=session)
                for _ in range(n_rwrd):
                    ri_exp.add_reward_item(session=session)

    def _valid_order_indexes(self, routine: Routine) -> bool:
        """Returns true if the `order_index`s of a routine's `routine_items`
        match their position in the routine's list"""
        order_idxs = [ritem.order_index for ritem in routine.routine_items]
        return sorted(order_idxs) == list(range(len(order_idxs)))

    def _routine_items_first(self, routine: Routine) -> bool:
        """Returns true if all `routine_items` in a routine come before any
        reward items"""
        items = sorted(routine.routine_items, key=lambda x: x.order_index)
        for i, routine_item in enumerate(items):
            if routine_item.is_reward:
                first_reward_i = i
                break
        else:
            return True  # if no reward items, then order is valid by default
        should_be_rewards = items[first_reward_i:]
        return all([x.is_reward for x in should_be_rewards])

    @pytest.mark.parametrize("item_variety", ["routine", "reward"])
    def test_basic_add_item(
        self, item_variety, repository: Repository, session: Session
    ):
        ri_exp = empty_routine_items_expansion(repository)
        for i in range(10):
            if item_variety == "routine":
                ri_exp.add_routine_item(session=session)
                # check that the new item is not a reward
                assert ri_exp.routine.routine_items[i].is_reward is False
            elif item_variety == "reward":
                ri_exp.add_reward_item(session=session)
                # check that the new item is a reward
                assert ri_exp.routine.routine_items[i].is_reward is True
            # check routine now has one more item
            assert len(ri_exp.routine.routine_items) == i + 1
            # check an item was committed to the database and id is as expected
            assert session.query(RoutineItem).count() == i + 1
            assert ri_exp.routine.routine_items[i].id == i + 1
        # check that all order indexes pass validity test
        assert self._valid_order_indexes(ri_exp.routine)

    @pytest.mark.parametrize("add_items_case", ADD_ITEMS_CASES)
    def test_various_add_items_cases(
        self, add_items_case: dict, repository: Repository, session: Session
    ):
        ri_exp = empty_routine_items_expansion(repository)
        self._add_items(ri_exp, session, **add_items_case)
        if not self._valid_order_indexes(ri_exp.routine):
            print("Invalid order indexes")
        assert self._valid_order_indexes(ri_exp.routine)
        assert self._routine_items_first(ri_exp.routine)

    @pytest.mark.parametrize("item_variety", ["routine", "reward"])
    def test_valid_movements(
        self, item_variety: str, repository: Repository, session: Session
    ):
        ri_exp = empty_routine_items_expansion(repository)
        # add two items
        if item_variety == "routine":
            ri_exp.add_routine_item(session=session)
            ri_exp.add_routine_item(session=session)
        elif item_variety == "reward":
            ri_exp.add_reward_item(session=session)
            ri_exp.add_reward_item(session=session)
        # keep track of items
        original_item_0 = ri_exp.routine.routine_items[0]
        original_item_1 = ri_exp.routine.routine_items[1]
        # move original item 0 down
        ri_exp.move_item(original_item_0, down=True)
        # check that both the list position and order_index swapped correctly
        assert ri_exp.routine.routine_items[0] == original_item_1
        assert ri_exp.routine.routine_items[1] == original_item_0
        self._valid_order_indexes(ri_exp.routine)
        # move original item 0 back up and check again
        ri_exp.move_item(original_item_0, up=True)
        assert ri_exp.routine.routine_items[0] == original_item_0
        assert ri_exp.routine.routine_items[1] == original_item_1
        self._valid_order_indexes(ri_exp.routine)

    @pytest.mark.parametrize("n_routine, n_rwrd", [(1, 1), (3, 4), (12, 5)])
    def test_invalid_movements(
        self,
        n_routine: int,
        n_rwrd: int,
        repository: Repository,
        session: Session,
    ):
        def _attempt_move_and_assert_no_change(
            item_to_move: RoutineItem,
            ri_exp: RoutineItemsExpansion,
            up: bool = False,
            down: bool = False,
        ):
            order_index_before = item_to_move.order_index
            ri_exp.move_item(item_to_move, up=up, down=down)
            assert item_to_move.order_index == order_index_before
            assert len(ri_exp.routine.routine_items) == n_routine + n_rwrd
            assert self._valid_order_indexes(ri_exp.routine)
            assert self._routine_items_first(ri_exp.routine)

        ri_exp = empty_routine_items_expansion(repository)
        self._add_items(
            ri_exp, session=session, n_routine=n_routine, n_rwrd=n_rwrd
        )
        last_routine_i, first_rwrd_i = n_routine - 1, n_routine

        # 1. moving an item up when it's already at the top
        item_to_move = ri_exp.routine.routine_items[0]
        _attempt_move_and_assert_no_change(item_to_move, ri_exp, up=True)
        # 2. moving an item down when it's already at the bottom
        item_to_move = ri_exp.routine.routine_items[-1]
        _attempt_move_and_assert_no_change(item_to_move, ri_exp, down=True)
        # 3. moving a non-reward item below a reward item
        item_to_move = ri_exp.routine.routine_items[last_routine_i]
        _attempt_move_and_assert_no_change(item_to_move, ri_exp, down=True)
        # 4. moving a reward item above a non-reward item
        item_to_move = ri_exp.routine.routine_items[first_rwrd_i]
        _attempt_move_and_assert_no_change(item_to_move, ri_exp, up=True)

    def test_delete_item(self, repository: Repository, session: Session):
        ri_exp = empty_routine_items_expansion(repository)
        self._add_items(ri_exp, n_routine=5, n_rwrd=5, session=session)
        for i, idx_to_delete in enumerate([0, 3, 7]):
            item_to_delete = ri_exp.routine.routine_items[idx_to_delete]
            ri_exp.delete_item(item_to_delete, session)
            assert len(ri_exp.routine.routine_items) == 9 - i
            assert self._valid_order_indexes(ri_exp.routine)
            assert self._routine_items_first(ri_exp.routine)
            # assert item_to_delete is no longer in the database
            assert session.query(RoutineItem).count() == 9 - i
            assert session.get(RoutineItem, item_to_delete.id) is None
            # assert query of routine doesn't contain item_to_delete in items
            ris_in_db = session.get(Routine, ri_exp.routine.id).routine_items
            assert item_to_delete not in ris_in_db
