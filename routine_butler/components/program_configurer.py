from functools import partial
from typing import Any, Dict, Optional, Type

from nicegui import ui
from pydantic import BaseModel, ValidationError

from routine_butler.components import micro
from routine_butler.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.models.program import Program
from routine_butler.state import state
from routine_butler.utils import ProgramPlugin

# TODO: needs a way to delete programs
# TODO: fix taken name validation failure when editing self


def passes_pydantic_validation(
    model_type: Type[BaseModel], key: str, value: Any
) -> bool:
    """Returns True if value passes pydantic validation for model_type"""
    print(key, value, model_type)
    try:
        model_type(**{key: value})
        return True
    except ValidationError:
        return False


INVALID_MSG = "Does not pass pydantic validation!"
TAKEN_NAME_MSG = "Name already in use!"


def plugin_factory(  # TODO: move to utils and have RoutineAdministrator use it
    plugin_name: Optional[str], kwargs: Optional[Dict[str, Any]]
) -> Optional[ProgramPlugin]:
    """Retrieves a plugin type from state.plugins and instantiates it with kwargs"""
    if plugin_name is None:
        return None
    elif kwargs is None:
        return state.plugins[plugin_name]()
    else:
        return state.plugins[plugin_name](**kwargs)


class ProgramConfigurer(ui.card):
    def __init__(self, program: Program):
        self.program = program
        self.plugin = plugin_factory(program.plugin, program.plugin_config)
        self.plugin_config_inputs: Dict[str, ui.input] = {}

        super().__init__()

        with self:
            self.title_input = ui.input(
                value=program.title,
                validation={
                    TAKEN_NAME_MSG: lambda v: v not in state.program_titles
                },
            ).props(DFLT_INPUT_PRPS)
            with ui.row():
                self.plugin_select = micro.plugin_select(value=program.plugin)
                choose_plugin_button = ui.button("choose")
            self.plugin_config_frame = ui.element("div")
            # save_button is a class attribute so parent context can listen to it
            self.save_button = micro.save_button()

        self._update_plugin_config_frame()

        choose_plugin_button.on("click", self.hdl_choose_plugin)
        self.save_button.on("click", self.hdl_save)

    def _update_plugin_config_frame(self):
        if self.plugin_select.value is None:
            return
        self.plugin_config_frame.clear()
        plugin = state.plugins[self.plugin_select.value](
            **self.program.plugin_config
        )
        for key, value in plugin.dict().items():
            is_pydantic_valid = partial(
                passes_pydantic_validation, plugin.__class__, key
            )  # partial seems to be necessary here, lambdas don't quite work
            with self.plugin_config_frame:
                with ui.row():
                    ui.label(key)
                    self.plugin_config_inputs[key] = ui.input(
                        value=value,
                        validation={f"{INVALID_MSG}": is_pydantic_valid},
                    )

    def _update_plugin_with_current_input_values(self):
        kwargs = {
            k: elem.value for k, elem in self.plugin_config_inputs.items()
        }
        self.plugin = plugin_factory(self.program.plugin, kwargs)

    def hdl_plugin_config_change(self, key, value):
        self.program.plugin_config[key] = value

    def hdl_choose_plugin(self):
        if not self.plugin_select.value == self.program.plugin:
            self.program.plugin = self.plugin_select.value
            self.program.plugin_config = {}
            self._update_plugin_config_frame()

    def _update_program_with_widget_values(self):
        self.program.title = self.title_input.value
        self.program.plugin = self.plugin_select.value
        self._update_plugin_with_current_input_values()
        self.program.plugin_config = self.plugin.dict()

    def hdl_save(self):
        self._update_program_with_widget_values()
        if not self.program.uid:
            self.program.add_self_to_db(state.engine)
            state.user.add_program(state.engine, self.program)
        else:
            self.program.update_self_in_db(state.engine)
        state.update_programs()
        ui.notify("Program saved!")
