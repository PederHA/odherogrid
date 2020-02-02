import inspect
import json
from datetime import datetime
from pathlib import Path
from types import FrameType
import traceback

from .config import CONFIG_DIR

LOGS_DIR: Path = CONFIG_DIR / "logs" 


def handle_exception(exception: Exception) -> None:
    IGNORED = [SystemExit]
    if not any(isinstance(exception, e) for e in IGNORED):
        log_file = log_error(exception)
        print(f"ERROR: {exception}")
        print(f"Error log saved: {log_file}")    


def make_log_file(log_type: str=None) -> Path:
    """Creates a new log file and returns its path."""
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir()
    
    date_fmt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ltype = f"{log_type}_" if log_type else ""
    
    log_file = LOGS_DIR / f"odhg_{ltype}{date_fmt}.log"
    log_file.touch()
    
    return log_file


def log_error(exception: Exception) -> Path:
    """
    Logs exception. Writes traceback and contents of the 
    interpreter's stack frames to a new log file.
    """
    log_file = make_log_file("error")
    with open(log_file, "w") as f:
        exc = traceback.format_exception(
            type(exception), exception, tb=exception.__traceback__
        )
        for l in exc: # write each line of the traceback
            f.write(l)
        f.write("\n\nStack dump:\n\n")
        for frame in get_stack_frames(): # format as JSON for readability
            stack_locals = json.dumps(
                dict(frame.f_locals), indent=4, default=str
            )
            f.write(f"{stack_locals}\n")
    return log_file


def get_stack_frames() -> FrameType:
    """Generates stack frames."""
    frame = inspect.currentframe()
    while frame:
        yield frame
        frame = frame.f_back


def get_n_stack_frames(limit: int) -> FrameType:
    """Returns up to N number of stack frames.
    
    NOTE: untested.
    """
    for _ in range(limit):
        frame = next(get_stack_frames())
        if not frame:
            return StopIteration
        yield frame

