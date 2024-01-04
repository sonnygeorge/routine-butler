import asyncio
import datetime
from dataclasses import dataclass
from typing import List, Tuple
from functools import partial

from loguru import logger
from nicegui import run

from routine_butler.globals import (
    DB_BACKUP_FOLDER_NAME,
    DB_PATH,
    STORAGE_BUCKET,
)
from routine_butler.utils.logging import BG_TASK_LOG_LVL


log_this = partial(logger.log, BG_TASK_LOG_LVL)


@dataclass
class ScheduledBackgroundTask:
    func: callable
    days_to_run: List[int]  # Ints representing weekdays
    hours_to_run: List[int]  # Ints representing hours
    pre_checks_that_must_be_true: Tuple[callable] = ()
    is_io_bound: bool = False
    is_pending: bool = False

    def should_be_run(self) -> bool:
        """Returns True if the current day/hour matches the days/hours this task is
        scheduled to run on.
        """
        print(1)
        if self.is_pending:
            return True
        else:
            print(
                print(datetime.datetime.now().weekday()),
                "in",
                self.days_to_run,
            )
            print(datetime.datetime.now().hour, "in", self.hours_to_run)
            return (
                datetime.datetime.now().weekday() in self.days_to_run
                and datetime.datetime.now().hour in self.hours_to_run
            )


class HourlyBackgroundTaskManager:
    def __init__(self, tasks: List[ScheduledBackgroundTask] = []):
        self._tasks = tasks
        self.last_hour_run = datetime.datetime.now().hour

    async def check_if_new_hour_and_run_tasks_if_so(self):
        """Since background tasks are handled on a per-hour basis, this method
        checks if a new hour has arrived and called the hourly_run_tasks method if so.

        This method is intended to be run on an interval <= 1 hour.
        """
        log_this("Checking if new hour has arrived...")
        if True:  # FIXME: datetime.datetime.now().hour != self.last_hour_run:
            await self.hourly_run_tasks()
            self.last_hour_run = datetime.datetime.now().hour
        else:
            log_this("New hour has not arrived.")

    async def hourly_run_tasks(self):
        """Intended to be run once per hour. Checks if any tasks are scheduled to run
        on the current day/hour. If so, asserts their preconditions and runs the
        task(s).
        """
        log_this("New hour arrived, checking for tasks to run...")
        task_was_found_to_run = False
        for task in self._tasks:
            print(0)
            if not task.should_be_run():
                continue
            print(2)
            task_was_found_to_run = True
            failed_checks = False
            task_name = task.func.__name__
            print(3)
            log_this(f"Found '{task_name}'. Asserting preconditions...")
            for check in task.pre_checks_that_must_be_true:
                if asyncio.iscoroutinefunction(check):
                    was_true = await check()
                else:
                    was_true = check()
                if not was_true:
                    log_this(
                        f"Precondition '{check.__name__}' failed for task "
                        f"'{task_name}'. Skipping task.",
                    )
                    failed_checks = True
                    break
            if not failed_checks:
                if asyncio.iscoroutinefunction(task.func):
                    was_success = await task.func()
                elif task.is_io_bound:
                    was_success = await run.io_bound(task.func)
                else:
                    was_success = await run.cpu_bound(task.func)
                if was_success:
                    log_this(f"Task '{task_name}' completed successfully.")
                    task.is_pending = False
                else:
                    log_this(f"Task '{task_name}' failed. Marked pending.")
                    task.is_pending = True
        if not task_was_found_to_run:
            log_this("No tasks were found to be run at this time.")


async def perform_db_backup() -> bool:
    """Uploads a copy of the DB to the cloud storage bucket."""
    try:
        await STORAGE_BUCKET.upload(
            local_path=DB_PATH,
            remote_dir_path=f"{DB_BACKUP_FOLDER_NAME}/",
        )
        return True
    except Exception as e:
        logger.warning(f"'perform_db_backup' failed with error: {e}")
        return False


BG_TASK_MANAGER = HourlyBackgroundTaskManager(
    tasks=[
        ScheduledBackgroundTask(
            func=perform_db_backup,
            days_to_run=list(range(0, 7)),  # Every day...
            hours_to_run=[18],  # @ approximately 6pm.
            pre_checks_that_must_be_true=(STORAGE_BUCKET.validate_connection,),
            is_io_bound=True,
        )
    ]
)
