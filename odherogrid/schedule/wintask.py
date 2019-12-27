"""
(NYI) Provides an interface to create, manage and delete ODHG
tasks using Windows task scheduler. More platforms to follow.

https://docs.microsoft.com/en-us/windows/win32/taskschd/schtasks
https://click.palletsprojects.com/en/7.x/commands/#nested-handling-and-contexts ?
"""

import subprocess
from enum import Enum

import click

from ..config import CONF


class Schedule(Enum):
    MINUTE = 0
    HOURLY = 1
    DAILY = 2
    WEEKLY = 3
    MONTHLY = 4
    ONCE = 5
    ONLOGON = 6
    ONIDLE = 7
    ONEVENT = 8


def schedule_task(schedule: Schedule, *args) -> None:
    args = ["/SC"]
    if not CONF.exists():
        raise ValueError("A config is required to create a task! Run odhg --setup to create a config.")
    
    args.append(schedule.name)

    # NOTE: vvvv remove? vvvv
    if schedule == Schedule.MINUTE:
        args.extend()
    elif schedule == Schedule.ONLOGON:
        args.extend(("/SC", "ONLOGON"))
    ###################################


@click.option("--schedule, --sc", default=Schedule.ONLOGON)
@click.option("--modifier, --mo", default=Schedule.ONLOGON)
def main(**options):
    pass