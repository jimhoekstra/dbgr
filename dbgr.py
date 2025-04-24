from sys import exit, settrace, gettrace
from pathlib import Path
from types import FrameType
from enum import StrEnum
from dataclasses import dataclass

from os import get_terminal_size
import inspect
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt
from rich.layout import Layout

from components.renderers.source_code_renderer import SourceCodeRenderer
from components.renderers.dict_table_renderer import DictTableRenderer
from dataframes.viewer import DataFrameViewer


class DebuggerMode(StrEnum):
    """Enum for debugger modes."""

    CONTINUE = "continue"
    STEP = "step"
    EXIT = "exit"


@dataclass
class DebuggerState:
    mode: DebuggerMode
    user_dir: Path | None = None


debugger_state = DebuggerState(DebuggerMode.CONTINUE)


@dataclass
class FrameInfo:
    """Dataclass to hold frame information."""

    path_to_file: Path
    line_number: int


def is_user_frame(frame: FrameType, user_dir: Path) -> bool:
    """Check if the frame is part of the user's code.

    Parameters
    ----------
    frame
        The frame to check.
    user_dir
        The directory of the user's code (i.e. the code that is being debugged).

    Returns
    -------
    True if the frame is part of the user's code, False otherwise.
    """
    filename = Path(frame.f_code.co_filename).resolve()

    # This assumes that any code that is in the user's directory but in a .venv subdirectory
    # is not actually the user's code and should not be debugged.
    if ".venv" in str(filename):
        return False

    if "<" in str(filename) and ">" in str(filename):
        return False

    if "dbgr.py" in str(filename):
        return False

    # Check that the file of the frame is in the user's directory
    if not filename.is_relative_to(user_dir):
        return False

    return True


def _get_frame_info(frame: FrameType) -> FrameInfo:
    """Get frame information."""
    filename = Path(frame.f_code.co_filename).resolve()
    line_number = frame.f_lineno
    return FrameInfo(filename, line_number)


def global_trace(frame, event, arg):
    if event == "call":
        return local_trace  # Set a local trace for this function call
    return None


def local_trace(frame, event, arg):
    if event == "line":
        assert debugger_state.user_dir is not None
        if is_user_frame(frame, debugger_state.user_dir):
            debug_frame(frame, "Current Frame", 15)
    return local_trace  # Keep tracing this frame


def debug_frame(
    frame: FrameType,
    title: str,
    n_source_lines: int,
    panel_color: str = "blue",
    prompt: bool = True,
) -> None:
    frame_info = _get_frame_info(frame)

    _, lines = get_terminal_size()
    height = lines - 1 if False else n_source_lines + 2

    console = Console(height=height)
    layout = Layout(name="root")
    layout.split_row(
        Layout(name="left"),
        Layout(name="right"),
    )

    syntax = SourceCodeRenderer(
        frame_info.path_to_file,
        frame_info.line_number,
        title,
        max_lines=n_source_lines,
        border_color=panel_color,
    )

    locals_table = DictTableRenderer(
        {k: v for k, v in frame.f_locals.items() if not k.startswith("__")},
        title="[bold]Local Variables",
        height=n_source_lines + 2,
        border_color=panel_color,
    )

    console.print(
        f"[yellow]{datetime.now()} dbgr: Encountered breakpoint",
    )

    layout["left"].update(syntax)
    layout["right"].update(locals_table)
    console.print(layout)

    if prompt:
        exit_command = False
        while not exit_command:
            console.print(
                "[red italic]Enter command (e: exit, s: step, c: continue, d <df_name>: display DataFrame):"
            )
            command = Prompt.ask(
                "[bold][yellow] >>>",
            )

            if command == "e":
                console.print(f"[yellow]{datetime.now()} dbgr: Exiting debugger")
                debugger_state.mode = DebuggerMode.EXIT
                exit_command = True
                raise exit(0)
            elif command == "s":
                console.print(
                    f"[yellow]{datetime.now()} dbgr: Stepping into the next line"
                )
                debugger_state.mode = DebuggerMode.STEP
                settrace(global_trace)
                exit_command = True
            elif command == "c":
                console.print(f"[yellow]{datetime.now()} dbgr: Continuing execution")
                debugger_state.mode = DebuggerMode.CONTINUE
                settrace(None)
                exit_command = True
            elif command.startswith("d"):
                df_name_to_display = command.split(" ")[1]
                df_to_display = frame.f_locals.get(df_name_to_display)
                if df_to_display is None:
                    console.print(
                        f"[yellow]{datetime.now()} dbgr: DataFrame '{df_name_to_display}' not found in local variables"
                    )
                    continue
                app = DataFrameViewer(df_to_display)
                app.run()
            elif command == "":
                pass
            else:
                console.print(f"[yellow]{datetime.now()} dbgr: Invalid command")


def dbgr():
    """Run the debugger."""
    current_trace = gettrace()
    settrace(None)

    stack = inspect.stack()
    caller_frame = stack[1]

    user_dir = Path(caller_frame.frame.f_code.co_filename).parent.resolve()
    debugger_state.user_dir = user_dir

    debug_frame(caller_frame.frame, "Current Frame", 15)
    new_trace = gettrace()
    if new_trace is None:
        settrace(current_trace)
