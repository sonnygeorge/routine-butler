from typing import Union

from loguru import logger
from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.constants import (
    ABS_PROGRAM_SVG_PATH,
    ABS_REWARD_SVG_PATH,
    ICON_STRS,
    PROGRAM_SVG_SIZE,
    REWARD_SVG_SIZE,
)
from routine_butler.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.constants import SDBR_DFLT_ROW_CLS as DFLT_ROW_CLASSES
from routine_butler.constants import SDBR_V_SPACE as V_SPACE
from routine_butler.models.routine import (
    PriorityLevel,
    Routine,
    RoutineElement,
    RoutineReward,
)
from routine_butler.models.user import User
from routine_butler.ui.primitives.icon_expansion import IconExpansion
from routine_butler.ui.primitives.svg import SVG

# since TypedDicts dont's support default values
DEFAULT_REWARD = {"program": ""}
DEFAULT_ELEMENT = {"priority_level": PriorityLevel.MEDIUM, "reward": ""}


class ElementsExpansion(IconExpansion):
    def __init__(self, engine: Engine, user: User, routine: Routine):
        self.engine = engine
        self.user = user
        self.routine = routine

        # TODO: figure out how to call this when user's programs are added/deleted
        self.update_choosable_programs()

        svg_kwargs = {
            "fpath": ABS_PROGRAM_SVG_PATH,
            "size": PROGRAM_SVG_SIZE,
            "color": "black",
        }

        super().__init__("Chronology", icon=SVG, icon_kwargs=svg_kwargs)
        self.classes("justify-between items-center")

        with self:
            self.rows_frame = ui.element("div")
            self._update_rows_frame()

            # bottom buttons
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                # add routine element button
                self.add_routine_element_button = ui.button().props(
                    f"icon={ICON_STRS.add}"
                )
                self.add_routine_element_button.classes("w-3/4")
                # add reward buttom
                self.add_reward_element_button = ui.button().classes(
                    "items-center w-1/5 bg-secondary"
                )
                with self.add_reward_element_button:
                    SVG(
                        ABS_REWARD_SVG_PATH,
                        size=REWARD_SVG_SIZE,
                        color="white",
                    )

            # connect handlers
            self.add_routine_element_button.on(
                "click", self.handle_add_element
            )
            self.add_reward_element_button.on("click", self.handle_add_reward)

    @property
    def num_elements(self):
        return len(self.routine.elements)

    def _update_rows_frame(self):
        """Clear and repopulates the 'div'/frame containing `RoutineElementRow`s
        in order to accomplish internal reording"""
        # remove any rows currently in the frame
        self.rows_frame.clear()
        # instantiate new rows within the frame
        with self.rows_frame:
            for idx, element in enumerate(self.routine.elements):
                self._add_ui_row(row_lbl=idx + 1, data_obj=element)
            for idx, reward in enumerate(self.routine.rewards):
                self._add_ui_row(
                    row_lbl=self.num_elements + idx + 1, data_obj=reward
                )

    def update_choosable_programs(self):
        self.choosable_programs = self.user.get_programs(self.engine)

    def _is_reward(
        self, data_obj: Union[RoutineElement, RoutineReward]
    ) -> bool:
        """Returns True if the given data object is a reward, False otherwise"""
        # TODO: a bit hacky since isinstance() doesn't work with TypedDicts
        return "priority_level" not in data_obj.keys()

    def _row_lbl_is_reward(self, row_lbl: int) -> bool:
        """Returns True if the row for `row_lbl` is a reward row, False otherwise"""
        return row_lbl > self.num_elements

    def _elements_idx_from_row_lbl(self, row_lbl: int) -> int:
        """Returns the index of the element at the given row label"""
        return row_lbl - 1

    def _rewards_idx_from_row_lbl(self, row_lbl: int) -> int:
        """Returns the index of the reward at the given row label"""
        return row_lbl - self.num_elements - 1

    def _add_ui_row(
        self, row_lbl: int, data_obj: Union[RoutineElement, RoutineReward]
    ):
        accent_color = "secondary" if self._is_reward(data_obj) else "primary"

        with ui.row().classes(DFLT_ROW_CLASSES + " gap-x-0"):
            # row label
            lbl_frame = ui.element("div").style("width: 5%;")
            lbl_frame.classes("mx-0 self-start w-full")
            lbl_frame.classes(f"rounded bg-{accent_color} w-full drop-shadow")
            with lbl_frame:
                lbl = ui.label(f"{row_lbl}.")
                lbl.style("height: 1.125rem;")
                lbl.classes("text-white text-center text-xs text-bold")
                lbl.classes("flex items-center justify-center")
            # program select
            with ui.element("div").style("width: 32%;"):
                program_select = ui.select(
                    [p.title for p in self.choosable_programs],
                    value="",
                    label="program",
                ).props(DFLT_INPUT_PRPS)
                program_select.classes("w-full")
            # priority level select
            with ui.element("div").style("width: 27%;"):
                if self._is_reward(data_obj):
                    # if reward, add a placeholder en lieu of priority level select
                    placeholder = ui.element("q-item").props("dense")
                    placeholder.style("height: 2.5rem;")
                    cls = "items-center justify-center border-secondary"
                    cls += " rounded w-full border-dotted border-2"
                    placeholder.classes(cls)
                    with placeholder:
                        SVG(
                            ABS_REWARD_SVG_PATH,
                            size=REWARD_SVG_SIZE,
                            color="#e5e5e5",
                        )
                else:
                    # else, add priority level select
                    priority_level_select = ui.select(
                        [e.value for e in PriorityLevel],
                        value=data_obj["priority_level"],
                        label="priority",
                    ).props(DFLT_INPUT_PRPS)
                    priority_level_select.classes("w-full")
            # order movement buttons
            order_buttons_frame = ui.row().classes("gap-x-1 justify-center")
            with order_buttons_frame.style("width: 18%;"):
                up_button = ui.button().classes(f"bg-{accent_color}")
                up_button.props(f"icon={ICON_STRS.up_arrow} dense")
                down_button = ui.button().classes(f"bg-{accent_color}")
                down_button.props(f"icon={ICON_STRS.down_arrow} dense")
            # delete button
            with ui.element("div").style("width: 7%;"):
                delete_button = ui.button()
                delete_button.props(
                    f"icon={ICON_STRS.delete} color=negative dense"
                )

            # connect handlers to elements
            program_select.on(
                "update:model-value",
                lambda: self.handle_select_program(
                    row_lbl=row_lbl, new_program=program_select.value
                ),
            )
            # only connect the following handler if a priority level select truly
            # exists and is not a placeholder (as is the case for reward rows)
            if not self._is_reward(data_obj):
                priority_level_select.on(
                    "update:model-value",
                    lambda: self.handle_select_priority(
                        row_lbl=row_lbl,
                        new_priority=priority_level_select.value,
                    ),
                )
            down_button.on(
                "click", lambda: self.handle_move_row_down(row_lbl=row_lbl)
            )
            up_button.on(
                "click", lambda: self.handle_move_row_up(row_lbl=row_lbl)
            )
            delete_button.on(
                "click", lambda: self.handle_delete_row(row_label=row_lbl)
            )

    def handle_add_element(self):
        new_element = DEFAULT_ELEMENT.copy()
        self.routine.elements.append(new_element)
        self.routine.update_self_in_db(self.engine)

        if len(self.routine.rewards) == 0:
            new_row_lbl = len(self.routine.elements + self.routine.rewards)
            with self.rows_frame:
                self._add_ui_row(row_lbl=new_row_lbl, data_obj=new_element)
        else:
            self._update_rows_frame()

    def handle_add_reward(self):
        new_reward = DEFAULT_REWARD.copy()
        self.routine.rewards.append(new_reward)
        self.routine.update_self_in_db(self.engine)

        new_row_lbl = len(self.routine.elements + self.routine.rewards)
        with self.rows_frame:
            self._add_ui_row(row_lbl=new_row_lbl, data_obj=new_reward)

    def handle_move_row_up(self, row_lbl: int):
        is_first_reward = lambda row_lbl: row_lbl == self.num_elements + 1
        is_first_element = lambda row_lbl: row_lbl == 1

        if is_first_reward(row_lbl) or is_first_element(row_lbl):
            logger.info("Cannot move row further upward")
            return
        elif self._row_lbl_is_reward(row_lbl):
            # swap reward at index with reward at index - 1
            idx = self._rewards_idx_from_row_lbl(row_lbl)
            self.routine.rewards.insert(idx - 1, self.routine.rewards.pop(idx))
        else:  # (element)
            # swap element at index with element at index - 1
            idx = self._elements_idx_from_row_lbl(row_lbl)
            self.routine.elements.insert(
                idx - 1, self.routine.elements.pop(idx)
            )
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()

    def handle_move_row_down(self, row_lbl: int):
        is_last_element = lambda row_lbl: row_lbl == self.num_elements
        is_last_reward = lambda row_lbl: row_lbl == len(
            self.routine.elements + self.routine.rewards
        )

        if is_last_element(row_lbl) or is_last_reward(row_lbl):
            logger.info("Cannot move row further downward")
            return
        elif self._row_lbl_is_reward(row_lbl):
            # swap reward at index with reward at index + 1
            idx = self._rewards_idx_from_row_lbl(row_lbl)
            self.routine.rewards.insert(idx + 1, self.routine.rewards.pop(idx))
        else:  # (element)
            # swap element at index with element at index + 1
            idx = self._elements_idx_from_row_lbl(row_lbl)
            self.routine.elements.insert(
                idx + 1, self.routine.elements.pop(idx)
            )
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()

    def handle_delete_row(self, row_label: int):
        if self._row_lbl_is_reward(row_label):
            # delete reward from routine
            idx = self._rewards_idx_from_row_lbl(row_label)
            self.routine.rewards.pop(idx)
        else:  # (element)
            # delete element from routine
            idx = self._elements_idx_from_row_lbl(row_label)
            self.routine.elements.pop(idx)
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()

    def handle_select_program(self, row_lbl: int, new_program: str):
        if self._row_lbl_is_reward(row_lbl):
            # update program in reward
            idx = self._rewards_idx_from_row_lbl(row_lbl)
            self.routine.rewards[idx]["program"] = new_program
        else:  # (element)
            # update program in element at index
            idx = self._elements_idx_from_row_lbl(row_lbl)
            self.routine.elements[idx]["program"] = new_program
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()

    def handle_select_priority(self, row_lbl: int, new_priority: int):
        # NOTE: only ever called with elements (never with rewards)
        idx = self._elements_idx_from_row_lbl(row_lbl)
        self.routine.elements[idx]["priority_level"] = new_priority
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()
