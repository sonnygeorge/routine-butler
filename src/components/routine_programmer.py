from typing import List

import remi
from loguru import logger

from components.primitives.button import Button
from components.primitives.centered_label import CenteredLabel
from components.primitives.configurer import Configurer
from components.trash_button import TrashButton
from database import database
from models import PriorityLevel, Program, Routine, RoutineProgram, User

BUTTON_BOX_WIDTH = "15%"
FORMATTABLE_ORDER_LABEL = "Program #{order_index}:"


class InvalidDisplacementAmountError(Exception):
    """
    Raised when a RoutineProgram.order_index is attempted to be displaced by
    an invalid amount
    """

    pass


def check_order_indexes_are_valid_chronology(order_indexes: List[int]) -> bool:
    check = order_indexes == list(range(0, len(order_indexes)))
    if not check:
        logger.debug(
            f"Order index chronology chronology needs a reset: {order_indexes}"
        )
    return check


def reset_program_order(routine: Routine) -> None:
    """
    Resets the order_index of all routine_programs in a routine to a consecutive
    chronology

    E.G. if the routine's routine_program's order_index attributes are [0, 2, 4],
    they would become [0, 1, 2] respectively.

    Args:
        routine (Routine): The routine to reset the order_index's of.
    """
    # sort the routine's routine_programs by their order_index
    routine.routine_programs.sort(key=lambda rp: rp.order_index)
    # reset the order_index attributes of all routine_programs
    for idx, routine_program in enumerate(routine.routine_programs):
        routine_program.order_index = idx


def move_routine_program_in_order(
    routine: Routine, routine_program_to_move: RoutineProgram, displace_by: int
) -> None:
    """
    Moves a routine_program within a routine's routine_program chronology,
    displacing its order_index by the given amount.

    Args:
        routine (Routine): The routine to move the routine_program within.
        program_to_move (RoutineProgram): The routine_program to move.
        displace_by (int): The amount to displace the routine_program by.
    """
    # quick check to see if the order idxs are already a valid chronology
    order_idxs = [rp.order_index for rp in routine.routine_programs]
    assert check_order_indexes_are_valid_chronology(order_idxs)
    # sort the routine's routine_programs by their order_index
    routine.routine_programs.sort(key=lambda rp: rp.order_index)
    # get the index of the routine_program to move
    idx = routine.routine_programs.index(routine_program_to_move)
    # get the index of the routine_program to displace it by
    displaced_idx = idx + displace_by

    if displaced_idx < 0 or displaced_idx >= len(routine.routine_programs):
        raise InvalidDisplacementAmountError(
            f"Unable to displace routine_program with order_index: "
            f"{routine_program_to_move.order_index} by {displace_by} as it "
            f"would result in an invalid new index: {displaced_idx}"
        )

    # remove the routine_program from the list
    routine.routine_programs.pop(idx)
    # insert the routine_program into the list at the displaced index
    routine.routine_programs.insert(displaced_idx, routine_program_to_move)
    # update the order_index of all routine_programs accordingly
    for i, routine_program in enumerate(routine.routine_programs):
        routine_program.order_index = i


class ProgramSetter(remi.gui.HBox):
    """A component to offer controls to set an individual program's settings."""

    trashed: bool = False
    pending_order_displacement: int = 0

    def __init__(self, routine_program: RoutineProgram, user: User):
        Configurer.__init__(self)

        self.routine_program = routine_program
        self.user = user

        # self.program
        if self.routine_program.program_id is None:
            new_program = Program()
            self.user.programs.append(new_program)
            new_program.routine_programs.append(self.routine_program)
            self.program = new_program
        else:
            self.program = database.get(
                Program, self.routine_program.program_id
            )

        # order buttons
        self.order_buttons = remi.gui.HBox(
            height="100%", width=BUTTON_BOX_WIDTH
        )
        self.append(self.order_buttons, "order_buttons")

        # order up button
        self.order_up_button = Button("▲")
        self.order_up_button.onclick.connect(self.on_order_up)
        self.order_buttons.append(self.order_up_button, "order_up_button")

        # order down button
        self.order_down_button = Button("▼")
        self.order_down_button.onclick.connect(self.on_order_down)
        self.order_buttons.append(self.order_down_button, "order_down_button")

        # order label
        self.order_label = CenteredLabel(
            FORMATTABLE_ORDER_LABEL.format(
                order_index=self.routine_program.order_index + 1
            )
        )
        self.append(self.order_label, "order_label")

        # program title label
        self.program_title_label = remi.gui.TextInput(single_line=True)
        self.program_title_label.css_width = "25%"
        self.program_title_label.set_value(self.program.title)
        self.program_title_label.onchange.connect(self.on_program_title_change)
        self.append(self.program_title_label, "program_title_label")

        # program chooser dropdown
        self.program_chooser = remi.gui.DropDown()
        self.program_chooser.css_width = "25%"
        self.program_chooser.append(remi.gui.DropDownItem("drink .5l water"))
        self.program_chooser.append(remi.gui.DropDownItem("20 pushups"))
        self.append(self.program_chooser, "program_chooser")

        # priority dropdown
        self.priority_dropdown = remi.gui.DropDown()
        self.priority_dropdown.css_width = "10%"
        for level in PriorityLevel:
            self.priority_dropdown.append(
                remi.gui.DropDownItem(level.value), level.value
            )
        self.priority_dropdown.select_by_key(
            self.routine_program.priority_level
        )
        self.priority_dropdown.onchange.connect(self.on_priority_change)
        self.append(self.priority_dropdown, "priority_dropdown")

        # trash button
        self.trash_button = TrashButton()
        self.trash_button.onclick.connect(self.on_trash)
        self.append(self.trash_button, "trash_button")

    def on_order_up(self, _):
        self.pending_order_displacement -= 1

    def on_order_down(self, _):
        self.pending_order_displacement += 1

    def on_program_title_change(self, _, new_value):
        self.program.title = new_value
        self.program.title = new_value

    def on_priority_change(self, _, new_value):
        self.routine_program.priority_level = PriorityLevel(new_value)

    def on_trash(self, _):
        self.trashed = True


class RoutineProgrammer(remi.gui.VBox):
    """A component to offer controls to set the routine's programs."""

    def __init__(self, routine: Routine, user: User):
        remi.gui.VBox.__init__(self, width="100%")
        self.routine = routine
        self.user = user

        # program_setters vbox
        self.program_setters_vbox = remi.gui.VBox(width="100%")
        for routine_program in routine.routine_programs:
            program_setter = ProgramSetter(routine_program, self.user)
            self.program_setters_vbox.append(program_setter)

        self.append(self.program_setters_vbox, "program_setters_vbox")

        # add program button
        self.add_program_button = Button("Add Program")
        self.add_program_button.onclick.connect(self.on_add_program)
        self.append(self.add_program_button, "add_program_button")

    def idle(self):
        """runs every update_interval seconds"""
        self.remove_any_trashed_program_setters()
        self.update_order_indexes()
        self.update_vbox_order()

    def on_add_program(self, widget):
        """
        1. Adds a new routine_program to the routine with an order_index of one
        greater than the routines current max order_index
        2. Adds a new program_setter to the program_setters_vbox
        """
        if len(self.routine.routine_programs) == 0:
            new_order_index = 0
        else:
            order_indexs = [
                p.order_index for p in self.routine.routine_programs
            ]
            new_order_index = max(order_indexs) + 1
        self.routine.routine_programs.append(
            RoutineProgram(order_index=new_order_index)
        )
        self.program_setters_vbox.append(
            ProgramSetter(self.routine.routine_programs[-1], self.user)
        )

    def remove_any_trashed_program_setters(self):
        """update the vbox of program_setters"""
        program_setters = list(self.program_setters_vbox.children.values())
        for program_setter in program_setters:
            if program_setter.trasheds:
                self.program_setters_vbox.remove_child(program_setter)
                self.routine.routine_programs.remove(
                    program_setter.routine_program
                )
                reset_program_order(self.routine)

    def update_order_indexes(self):
        """
        Updates the order_index of all routine_programs of the routine_program
        setters in the vbox
        """
        for program_setter in self.program_setters_vbox.children.values():
            if program_setter.pending_order_displacement != 0:
                try:
                    move_routine_program_in_order(
                        self.routine,
                        program_setter.routine_program,
                        program_setter.pending_order_displacement,
                    )
                except InvalidDisplacementAmountError as e:
                    logger.info(e)
                program_setter.pending_order_displacement = 0

    def update_vbox_order(self):
        """update the vbox of program_setters"""
        if not self.vbox_properly_ordered():
            logger.debug("reording program_setters_vbox...")
            # sort the program_setters by their routine_program's order_index
            program_setters = [
                ps for ps in self.program_setters_vbox.children.values()
            ]
            program_setters.sort(key=lambda ps: ps.routine_program.order_index)
            # remove all program_setters from the vbox
            for program_setter in program_setters:
                self.program_setters_vbox.remove_child(program_setter)
            # add all program_setters back to the vbox in the correct order
            for program_setter in program_setters:
                program_setter.order_label.set_text(
                    FORMATTABLE_ORDER_LABEL.format(
                        order_index=program_setter.routine_program.order_index
                        + 1
                    )
                )
                self.program_setters_vbox.append(program_setter)

    def vbox_properly_ordered(self) -> bool:
        """returns True if the program_setters_vbox is properly ordered"""
        program_setters = [
            ps for ps in self.program_setters_vbox.children.values()
        ]
        if len(program_setters) == 0:
            return True  # no order to check
        order_indexes = [
            ps.routine_program.order_index for ps in program_setters
        ]
        return check_order_indexes_are_valid_chronology(order_indexes)
