from functools import partial
from typing import Any, Dict, Optional, Type

from nicegui import ui
from pydantic import BaseModel, ValidationError

from routine_butler.components import micro
from routine_butler.constants import SDBR
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
        self.classes("flex items-center justify-center")
        self.style("width: 853px")

        with self:
            with ui.row().classes("items-center justify-start"):
                micro.program_svg(size=20, color="lightgray").classes("mx-1")
                self.title_input = (
                    ui.input(
                        value=program.title,
                        label="title",
                        validation={
                            TAKEN_NAME_MSG: lambda v: v
                            not in state.program_titles
                        },
                    )
                    .props(SDBR.DFLT_INPUT_PRPS)
                    .classes("w-64")
                )
                ui.separator().props("vertical").classes("mx-3")
                self.plugin_select = micro.plugin_type_select(
                    value=program.plugin_type
                ).classes("w-64")
                choose_plugin_button = ui.button("choose").classes("w-40")

            ui.separator()

            self.temp_filler = ui.label("choose a type...")
            self.temp_filler.classes("text-gray-300 italic")

            self.plugin_grid = ui.grid(columns=2).classes("mt-3 mb-6")
            self.plugin_grid.classes("items-center justify-center w-3/5")
            self.plugin_grid.set_visibility(False)
            self.plugin_input_elements: Dict[str, ui.input] = {}

            ui.separator()

            # save_button is a class attribute so parent context can listen to it
            self.save_button = micro.save_button().classes("w-40")

        self._update_plugin_grid_with_plugin_values()

        choose_plugin_button.on("click", self.hdl_choose_plugin)
        self.save_button.on("click", self.hdl_save)

    def _update_plugin_grid_with_plugin_values(self):
        if self.plugin_select.value is None:
            return
        self.plugin_grid.clear()
        self.temp_filler.set_visibility(False)
        self.plugin_grid.set_visibility(True)
        plugin = state.plugin_types[self.plugin_select.value](
            **self.program.plugin_dict
        )
        for key, value in plugin.dict().items():
            is_pydantic_valid = partial(
                passes_pydantic_validation, plugin.__class__, key
            )  # partial seems to be necessary here, lambdas don't quite work
            with self.plugin_grid:
                ui.markdown(f"`{key}`")
                self.plugin_input_elements[key] = ui.input(
                    value=value,
                    validation={f"{INVALID_MSG}": is_pydantic_valid},
                )

    def _update_plugin_with_plugin_grid_values(self):
        kwargs = {
            k: elem.value for k, elem in self.plugin_input_elements.items()
        }
        self.plugin = plugin_factory(self.program.plugin_type, kwargs)

    def hdl_choose_plugin(self):
        if not self.plugin_select.value == self.program.plugin_type:
            self.program.plugin_type = self.plugin_select.value
            self.program.plugin_dict = {}
            self._update_plugin_grid_with_plugin_values()

    def _update_program_with_widget_values(self):
        self.program.title = self.title_input.value
        self.program.plugin_type = self.plugin_select.value
        self._update_plugin_with_plugin_grid_values()
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
