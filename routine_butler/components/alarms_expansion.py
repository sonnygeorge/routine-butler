from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.components import micro
from routine_butler.components.primitives.icon_expansion import IconExpansion
from routine_butler.constants import ICON_STRS
from routine_butler.constants import SDBR_DFLT_ROW_CLS as DFLT_ROW_CLASSES
from routine_butler.constants import SDBR_V_SPACE as V_SPACE
from routine_butler.constants import THROTTLE_SECONDS
from routine_butler.models.routine import Alarm, RingFrequency, Routine

DEFAULT_ALARM = {  # since TypedDicts dont's support default values
    "time": "12:00",
    "volume": 0.5,
    "ring_frequency": RingFrequency.CONSTANT,
    "is_enabled": True,
}


class AlarmsExpansion(IconExpansion):
    def __init__(self, engine: Engine, routine: Routine):
        self.engine = engine
        self.routine = routine
        super().__init__("Alarms", icon=ICON_STRS.alarm)

        with self:
            self.alarms_frame = ui.element("div")
            self._update_alarms_frame()

            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                add_alarm_button = micro.add_button().classes("w-full")

            add_alarm_button.on("click", self.hdl_add_alarm)

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
            with ui.element("div").style("width: 23%;"):
                time_setter = micro.time_input(value=alarm["time"])
            with ui.element("div").style("width: 10%;").classes("mx-1"):
                vol_knob = micro.volume_knob(alarm["volume"])
            with ui.element("div").style("width: 32%;"):
                ring_frequency_select = micro.ring_frequency_select(
                    value=alarm["ring_frequency"]
                )
            with ui.element("div").style("width: 34px;").classes("mx-1"):
                switch = ui.switch(value=alarm["is_enabled"]).props("dense")
            delete_alarm_button = micro.delete_button().props("dense")

        time_setter.on(
            "update:model-value",
            lambda: self.hdl_time_change(row_idx, time_setter.value),
            throttle=THROTTLE_SECONDS,
        )
        vol_knob.on(
            "change",
            lambda: self.hdl_change_volume(row_idx, vol_knob.value),
            throttle=THROTTLE_SECONDS,
        )
        ring_frequency_select.on(
            "update:model-value",
            lambda: self.hdl_select_ring_frequency(
                row_idx, ring_frequency_select.value
            ),
        )
        switch.on(
            "click", lambda: self.hdl_toggle_enabled(row_idx, switch.value)
        )
        delete_alarm_button.on("click", lambda: self.hdl_delete_alarm(row_idx))

    def hdl_add_alarm(self):
        new_alarm = DEFAULT_ALARM.copy()
        self.routine.alarms.append(new_alarm)
        self.routine.update_self_in_db(self.engine)
        with self.alarms_frame:
            self._add_ui_row(row_idx=self.num_alarms - 1, alarm=new_alarm)

    def hdl_time_change(self, row_idx: int, new_time: str):
        self.routine.alarms[row_idx]["time"] = new_time
        self.routine.update_self_in_db(self.engine)

    def hdl_change_volume(self, row_idx: int, new_volume: float):
        self.routine.alarms[row_idx]["volume"] = new_volume
        self.routine.update_self_in_db(self.engine)

    def hdl_select_ring_frequency(
        self, row_idx: int, new_frequency: RingFrequency
    ):
        self.routine.alarms[row_idx]["ring_frequency"] = new_frequency
        self.routine.update_self_in_db(self.engine)

    def hdl_toggle_enabled(self, row_idx: int, value: bool):
        self.routine.alarms[row_idx]["is_enabled"] = value
        self.routine.update_self_in_db(self.engine)

    def hdl_delete_alarm(self, row_idx: int):
        self.routine.alarms.pop(row_idx)
        self.routine.update_self_in_db(self.engine)
        self._update_alarms_frame()
