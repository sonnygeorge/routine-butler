from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.models.routine import Alarm, Routine, SoundFrequency
from routine_butler.ui.constants import ICON_STRS
from routine_butler.ui.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.ui.constants import SDBR_DFLT_ROW_CLS as DFLT_ROW_CLASSES
from routine_butler.ui.constants import SDBR_V_SPACE as V_SPACE
from routine_butler.ui.primitives.icon_expansion import IconExpansion


DEFAULT_ALARM = {  # since TypedDicts dont's support default values
    "time": "12:00",
    "volume": 0.5,
    "sound_frequency": SoundFrequency.CONSTANT,
    "enabled": True,
}
THROTTLE = 0.5


class AlarmsExpansion(IconExpansion):
    def __init__(self, engine: Engine, routine: Routine):
        self.engine = engine
        self.routine = routine
        super().__init__("Alarms", icon=ICON_STRS.alarm)

        with self:
            # alarms frame
            self.alarms_frame = ui.element("div")
            self._update_alarms_frame()

            # add alarm button
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                self.add_alarm_button = ui.button().props(
                    f"icon={ICON_STRS.add}"
                )
                self.add_alarm_button.classes("w-full")

            # connect handler
            self.add_alarm_button.on("click", self.handle_add_alarm)

    @property
    def num_alarms(self) -> int:
        return len(self.routine.alarms)

    def _update_alarms_frame(self):
        self.alarms_frame.clear()
        with self.alarms_frame:
            for idx, alarm in enumerate(self.routine.alarms):
                self._add_ui_row(row_idx=idx, alarm=alarm)

    def _add_ui_row(self, row_idx: int, alarm: Alarm):
        with ui.row().classes(DFLT_ROW_CLASSES + " gap-x-0"):
            # time input
            with ui.element("div").style("width: 23%;"):
                time_input = ui.input(value=alarm["time"])
                time_input.props(DFLT_INPUT_PRPS).classes("w-full")
                with time_input as input:
                    with input.add_slot("append"):
                        icon = ui.icon("access_time").classes("cursor-pointer")
                        icon.on("click", lambda: menu.open())
                        with ui.menu() as menu:
                            time_setter = ui.time()
                            time_setter.bind_value(time_input)
            # volume knob
            with ui.element("div").style("width: 10%;").classes("mx-1"):
                vol_knob = ui.knob(value=alarm["volume"], track_color="grey-2")
                vol_knob.props("size=lg thickness=0.3")
                with vol_knob:
                    ui.icon("volume_up").props("size=xs")
            # sound frequency select
            with ui.element("div").style("width: 32%;"):
                sound_frequency_select = ui.select(
                    [e.value for e in SoundFrequency],
                    value=alarm["sound_frequency"],
                    label="ring frequency",
                ).props(DFLT_INPUT_PRPS)
                sound_frequency_select.classes("w-full")
            # toggle switch
            with ui.element("div").style("width: 34px;").classes("mx-1"):
                switch = ui.switch().props("dense")
                switch.value = alarm["enabled"]
            # delete button
            delete_button = ui.button()
            delete_button.props(
                f"icon={ICON_STRS.delete} color=negative dense"
            )

        # connect handlers to elements
        time_setter.on(
            "update:model-value",
            lambda: self.handle_time_change(row_idx, time_input.value),
            throttle=THROTTLE,
        )
        vol_knob.on(
            "change",
            lambda: self.handle_change_volume(row_idx, vol_knob.value),
            throttle=THROTTLE,
        )
        sound_frequency_select.on(
            "update:model-value",
            lambda: self.handle_select_sound_frequency(
                row_idx, sound_frequency_select.value
            ),
        )
        switch.on(
            "click",
            lambda: self.handle_toggle_enabled(row_idx, switch.value),
        )
        delete_button.on("click", lambda: self.handle_delete_alarm(row_idx))

    def handle_add_alarm(self):
        new_alarm = DEFAULT_ALARM.copy()
        self.routine.alarms.append(new_alarm)
        self.routine.update_self_in_db(self.engine)
        with self.alarms_frame:
            self._add_ui_row(row_idx=self.num_alarms - 1, alarm=new_alarm)

    def handle_time_change(self, row_idx: int, new_time: str):
        self.routine.alarms[row_idx]["time"] = new_time
        self.routine.update_self_in_db(self.engine)

    def handle_change_volume(self, row_idx: int, new_volume: float):
        self.routine.alarms[row_idx]["volume"] = new_volume
        self.routine.update_self_in_db(self.engine)

    def handle_select_sound_frequency(
        self, row_idx: int, new_frequency: SoundFrequency
    ):
        self.routine.alarms[row_idx]["sound_frequency"] = new_frequency
        self.routine.update_self_in_db(self.engine)

    def handle_toggle_enabled(self, row_idx: int, value: bool):
        self.routine.alarms[row_idx]["enabled"] = value
        self.routine.update_self_in_db(self.engine)

    def handle_delete_alarm(self, row_idx: int):
        self.routine.alarms.pop(row_idx)
        self.routine.update_self_in_db(self.engine)
        self._update_alarms_frame()
