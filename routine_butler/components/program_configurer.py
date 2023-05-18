from functools import partial
from typing import Any, Dict, Optional, Type

from nicegui import ui
from pydantic import BaseModel, ValidationError

from routine_butler.components import micro
from routine_butler.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.models.program import Program
from routine_butler.state import state
from routine_butler.utils import ProgramPlugin

# TODO: fix taken name validation failure when editing self


INVALID_MSG = "Does not pass pydantic validation!"
TAKEN_NAME_MSG = "Name already in use!"


def passes_pydantic_validation(
    model_type: Type[BaseModel], key: str, value: Any
) -> bool:
    """Returns True if value passes pydantic validation for model_type"""
    try:
        model_type(**{key: value})
        return True
    except ValidationError:
        return False


def plugin_factory(  # TODO: move to utils and have RoutineAdministrator use it?
    plugin_name: Optional[str], plugin_dict: Optional[Dict[str, Any]]
) -> Optional[ProgramPlugin]:
    """Retrieves a plugin type from state.plugin_types and instantiates it with kwargs"""
    if plugin_name is None:
        return None
    elif plugin_dict is None:
        return state.plugin_types[plugin_name]()
    else:
        return state.plugin_types[plugin_name](**plugin_dict)


class ProgramConfigurer(ui.card):
    def __init__(self, program: Program):
        self.program = program
        self.plugin = plugin_factory(program.plugin_type, program.plugin_dict)

        super().__init__()

        with self:
            self.title_input = ui.input(
                value=program.title,
                validation={
                    TAKEN_NAME_MSG: lambda v: v not in state.program_titles
                },
            ).props(DFLT_INPUT_PRPS)
            with ui.row():
                self.plugin_select = micro.plugin_type_select(
                    value=program.plugin_type
                )
                choose_plugin_button = ui.button("choose")

            self.plugin_frame = ui.element("div")
            self.plugin_input_elements: Dict[str, ui.input] = {}

            # save_button is a class attribute so parent context can listen to it
            self.save_button = micro.save_button()

        self._update_plugin_frame_with_plugin_values()

        choose_plugin_button.on("click", self.hdl_choose_plugin)
        self.save_button.on("click", self.hdl_save)

    def _update_plugin_frame_with_plugin_values(self):
        if self.plugin_select.value is None:
            return
        self.plugin_frame.clear()
        plugin = state.plugin_types[self.plugin_select.value](
            **self.program.plugin_dict
        )
        for key, value in plugin.dict().items():
            is_pydantic_valid = partial(
                passes_pydantic_validation, plugin.__class__, key
            )  # partial seems to be necessary here, lambdas don't quite work
            with self.plugin_frame:
                with ui.row():
                    ui.label(key)
                    self.plugin_input_elements[key] = ui.input(
                        value=value,
                        validation={f"{INVALID_MSG}": is_pydantic_valid},
                    )

    def _update_plugin_with_plugin_frame_values(self):
        kwargs = {
            k: elem.value for k, elem in self.plugin_input_elements.items()
        }
        self.plugin = plugin_factory(self.program.plugin_type, kwargs)

    def hdl_choose_plugin(self):
        if not self.plugin_select.value == self.program.plugin_type:
            self.program.plugin_type = self.plugin_select.value
            self.program.plugin_dict = {}
            self._update_plugin_frame_with_plugin_values()

    def _update_program_with_widget_values(self):
        self.program.title = self.title_input.value
        self.program.plugin_type = self.plugin_select.value
        self._update_plugin_with_plugin_frame_values()
        self.program.plugin_dict = self.plugin.dict()

    def hdl_save(self):
        self._update_program_with_widget_values()
        if not self.program.uid:
            self.program.add_self_to_db(state.engine)
            state.user.add_program(state.engine, self.program)
        else:
            self.program.update_self_in_db(state.engine)
        state.update_programs()
        ui.notify("Program saved!")
