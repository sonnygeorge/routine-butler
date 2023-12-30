import asyncio
import datetime
from dataclasses import dataclass
from typing import List, Tuple

from loguru import logger
from nicegui import run

from routine_butler.globals import (
    DB_BACKUP_FOLDER_NAME,
    DB_PATH,
    STORAGE_BUCKET,
)
from routine_butler.utils.logging import BG_TASK_LOG_LVL


@dataclass
class ScheduledBackgroundTask:
    func: callable
    days_to_run: List[int]  # Ints representing weekdays
    hours_to_run: List[int]  # Ints representing hours
    pre_checks_that_must_be_true: Tuple[callable] = ()
    is_io_bound: bool = False
    run_on_startup: bool = False


class HourlyBackgroundTaskManager:
    def __init__(self, tasks: List[ScheduledBackgroundTask] = []):
        self._tasks = tasks
        self.last_hour_run = datetime.datetime.now().hour

    async def check_if_new_hour_and_run_tasks_if_so(self):
        """Since background tasks are handled on a per-hour basis, this method
        checks if a new hour has arrived and called the hourly_run_tasks method if so.

        This method is intended to be run on an interval <= 1 hour.
        """
        logger.log(BG_TASK_LOG_LVL, "Checking if new hour has arrived...")
        if datetime.datetime.now().hour != self.last_hour_run:
            await self.hourly_run_tasks()
            self.last_hour_run = datetime.datetime.now().hour
        else:
            logger.log(BG_TASK_LOG_LVL, "New hour has not arrived.")

    async def hourly_run_tasks(self):
        """Intended to be run once per hour. Checks if any tasks are scheduled to run
        oon the current day/hour. If so, asserts their preconditions and runs the
        task(s).
        """
        logger.log(
            BG_TASK_LOG_LVL,
            "New hour arrived, checking for scheduled tasks...",
        )
        for task in self._tasks:
            if datetime.datetime.now().weekday() in task.days_to_run:
                if datetime.datetime.now().hour in task.hours_to_run:
                    failed_checks = False
                    for check in task.pre_checks_that_must_be_true:
                        logger.log(
                            f"Found '{task.func.__name__}' to run. Asserting "
                            "preconditions are true..."
                        )
                        if asyncio.iscoroutinefunction(check):
                            was_true = await check()
                        else:
                            was_true = check()
                        if not was_true:
                            logger.log(
                                BG_TASK_LOG_LVL,
                                f"Precondition '{check.__name__}' failed for task "
                                f"'{task.func.__name__}'. Skipping task.",
                            )
                            failed_checks = True
                            break
                    if not failed_checks:
                        if asyncio.iscoroutinefunction(task.func):
                            await task.func()
                        elif task.is_io_bound:
                            await run.io_bound(task.func)
                        else:
                            await run.cpu_bound(task.func)


async def perform_db_backup():
    """Uploads a copy of the DB to the cloud storage bucket."""
    try:
        await STORAGE_BUCKET.upload(
            local_path=DB_PATH, remote_dir_path=f"{DB_BACKUP_FOLDER_NAME}/"
        )
        logger.log(BG_TASK_LOG_LVL, "DB backup complete.")
    except Exception as e:
        logger.warning(f"DB backup failed with error: {e}")


BG_TASK_MANAGER = HourlyBackgroundTaskManager(
    tasks=[
        ScheduledBackgroundTask(
            func=perform_db_backup,
            days_to_run=list(range(0, 7)),  # Every day...
            hours_to_run=[19],  # @ approximately 7pm.
            pre_checks_that_must_be_true=(STORAGE_BUCKET.validate_connection,),
            is_io_bound=True,
            run_on_startup=True,
        )
    ]
)
