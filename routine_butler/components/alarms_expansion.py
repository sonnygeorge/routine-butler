from nicegui import ui

from routine_butler.components import micro
from routine_butler.components.primitives import IconExpansion
from routine_butler.constants import ICON_STRS, SDBR, THROTTLE_SECONDS
from routine_butler.models.routine import Alarm, RingFrequency, Routine
from routine_butler.state import state


class AlarmsExpansion(IconExpansion):
    def __init__(self, routine: Routine):
        self.routine = routine
        super().__init__("Alarms", icon=ICON_STRS.alarm)

        with self:
            self.alarms_frame = ui.element("div")
            self._update_alarms_frame()

            with ui.row().classes(SDBR.DFLT_ROW_CLS + f" pb-{SDBR.V_SPACE}"):
                add_alarm_button = micro.add_button().classes("w-64")

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
        with ui.row().classes(SDBR.DFLT_ROW_CLS + " gap-x-0"):
            with ui.element("div").style("width: 23%;"):
                time_setter = micro.time_input(value=alarm.time)
            with ui.element("div").style("width: 10%;").classes("mx-1"):
                vol_knob = micro.volume_knob(alarm.volume)
            with ui.element("div").style("width: 32%;"):
                ring_frequency_select = micro.ring_frequency_select(
                    value=alarm.ring_frequency
                )
            with ui.element("div").style("width: 34px;").classes("mx-1"):
                switch = ui.switch(value=alarm.is_enabled).props("dense")
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
        new_alarm = Alarm()
        self.routine.alarms.append(new_alarm)
        self.routine.update_self_in_db(state.engine)
        with self.alarms_frame:
            self._add_ui_row(row_idx=self.num_alarms - 1, alarm=new_alarm)

    def hdl_time_change(self, row_idx: int, new_time: str):
        self.routine.alarms[row_idx].time = new_time
        self.routine.update_self_in_db(state.engine)

    def hdl_change_volume(self, row_idx: int, new_volume: float):
        self.routine.alarms[row_idx].volume = new_volume
        self.routine.update_self_in_db(state.engine)

    def hdl_select_ring_frequency(
        self, row_idx: int, new_frequency: RingFrequency
    ):
        self.routine.alarms[row_idx].ring_frequency = new_frequency
        self.routine.update_self_in_db(state.engine)

    def hdl_toggle_enabled(self, row_idx: int, value: bool):
        self.routine.alarms[row_idx].is_enabled = value
        self.routine.update_self_in_db(state.engine)

    def hdl_delete_alarm(self, row_idx: int):
        self.routine.alarms.pop(row_idx)
        self.routine.update_self_in_db(state.engine)
        self._update_alarms_frame()
