from nicegui import ui

from routine_butler.components import micro
from routine_butler.configs import ICON_STRS, THROTTLE_SECONDS
from routine_butler.models import Alarm, RingFrequency, Routine
from routine_butler.state import state


class AlarmsConfigurer(micro.ExpandableCard):
    def __init__(self, routine: Routine):
        self.routine = routine
        super().__init__("Alarms", icon=ICON_STRS.alarm, width="850px")

        with self:
            self.alarms_frame = ui.column()
            self.alarms_frame.classes("items-center justify-center pt-4")
            self._update_ui()

    @property
    def num_alarms(self) -> int:
        return len(self.routine.alarms)

    def _update_ui(self):
        self.alarms_frame.clear()
        with self.alarms_frame:
            for idx, alarm in enumerate(self.routine.alarms):
                self._add_ui_row(row_idx=idx, alarm=alarm)

            add_alarm_button = micro.add_button()
            add_alarm_button.classes("w-40 mb-4")
            add_alarm_button.on("click", self.hdl_add_alarm)

    def _add_ui_row(self, row_idx: int, alarm: Alarm):
        row = ui.row().classes("items-center w-full px-4 gap-x-2")
        with row.classes("justify-between").style("width: 725px;"):
            time_setter = micro.time_input(value=alarm.time_str).classes(
                "w-40"
            )
            vol_knob = micro.volume_knob(value=alarm.volume)
            ring_frequency_select = micro.ring_frequency_select(
                value=alarm.ring_frequency, ring_frequencies=RingFrequency
            ).classes("w-40")
            switch = ui.switch(value=alarm.is_enabled).props("dense")
            delete_alarm_button = micro.delete_button().props("dense")

        ui.separator().classes("bg-gray-100 w-full")

        time_setter.on(
            "update:model-value",
            lambda: self.hdl_time_change(row_idx, time_setter.value),
            throttle=THROTTLE_SECONDS,
        )
        vol_knob.on(
            "change",
            lambda: self.hdl_colume_change(row_idx, vol_knob.value),
            throttle=THROTTLE_SECONDS,
        )
        ring_frequency_select.on(
            "update:model-value",
            lambda: self.hdl_select_ring_frequency(
                row_idx, ring_frequency_select.value
            ),
        )
        switch.on(
            "click", lambda: self.hdl_toggle_is_enabled(row_idx, switch.value)
        )
        delete_alarm_button.on("click", lambda: self.hdl_delete_alarm(row_idx))

    def hdl_add_alarm(self):
        new_alarm = Alarm()
        self.routine.alarms.append(new_alarm)
        self.routine.update_self_in_db(state.engine)
        state.update_next_alarm_and_next_routine()
        self._update_ui()

    def hdl_time_change(self, row_idx: int, new_time: str):
        self.routine.alarms[row_idx].time_str = new_time
        self.routine.update_self_in_db(state.engine)
        state.update_next_alarm_and_next_routine()

    def hdl_colume_change(self, row_idx: int, new_volume: float):
        self.routine.alarms[row_idx].volume = new_volume
        self.routine.update_self_in_db(state.engine)

    def hdl_select_ring_frequency(
        self, row_idx: int, new_frequency: RingFrequency
    ):
        self.routine.alarms[row_idx].ring_frequency = new_frequency
        self.routine.update_self_in_db(state.engine)

    def hdl_toggle_is_enabled(self, row_idx: int, value: bool):
        self.routine.alarms[row_idx].is_enabled = value
        self.routine.update_self_in_db(state.engine)
        state.update_next_alarm_and_next_routine()

    def hdl_delete_alarm(self, row_idx: int):
        self.routine.alarms.pop(row_idx)
        self.routine.update_self_in_db(state.engine)
        state.update_next_alarm_and_next_routine()
        self._update_ui()
