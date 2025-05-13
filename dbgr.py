from sys import exit, settrace, gettrace
import sys
from pathlib import Path
from types import FrameType
from enum import StrEnum
from dataclasses import dataclass
import runpy
import threading

from os import get_terminal_size
import inspect
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt
from rich.layout import Layout
from rich import print as rich_print

from components.renderers.source_code_renderer import SourceCodeRenderer
from components.renderers.dict_table_renderer import DictTableRenderer


class DebuggerMode(StrEnum):
    """Enum for debugger modes."""

    CONTINUE = "continue"
    STEP = "step"
    EXIT = "exit"


@dataclass
class FrameInfo:
    """Dataclass to hold frame information."""

    path_to_file: Path
    line_number: int


# Global debugger state
debugger_state = {
    "mode": "continue",  # can be "step" or "continue"
    "user_dir": None,
    "full_screen": False,
}


def is_user_frame(frame: FrameType) -> bool:
    """Check if the frame is part of the user's code.

    Parameters
    ----------
    frame
        The frame to check.

    Returns
    -------
    True if the frame is part of the user's code, False otherwise.
    """
    filename = Path(frame.f_code.co_filename).resolve()

    if "<" in str(filename) and ">" in str(filename):
        return False

    # This assumes that any code that is in the user's directory but in a .venv subdirectory
    # is not actually the user's code and should not be debugged.
    if ".venv" in str(filename):
        return False

    assert debugger_state["user_dir"] is not None, "User directory not set"
    # Check that the file of the frame is in the user's directory
    if not filename.is_relative_to(debugger_state["user_dir"]):
        return False

    return True


class Debugger:
    user_dir: Path
    mode: DebuggerMode
    full_screen: bool
    n_source_lines: int

    def __init__(self, user_dir: Path) -> None:
        self.user_dir = user_dir
        self.mode = DebuggerMode.CONTINUE
        self.full_screen = False
        self.n_source_lines = 20

    def local_trace(self, frame: FrameType, event, arg):
        if not is_user_frame(frame):
            return self.local_trace  # Skip stepping into debugger code

        if event == "line":
            self.dbgr_trace(frame)
        elif event == "call":
            rich_print(
                f"[yellow]{datetime.now()} dbgr: Function call {frame.f_code.co_name}"
            )
        elif event == "return":
            rich_print(
                f"[yellow]{datetime.now()} dbgr: Function {frame.f_code.co_name} returned"
            )
        else:
            pass

        # Continue tracing
        return self.local_trace

    def global_trace(self, frame, event, arg):
        if event == "call":
            if not is_user_frame(frame):
                # rich_print(
                #     f"[yellow]{datetime.now()} dbgr: Not stepping into function {frame.f_code.co_name}"
                # )
                return None
            else:
                rich_print(
                    f"[yellow]{datetime.now()} dbgr: Stepping into function {frame.f_code.co_name}"
                )
                self.dbgr_trace(frame)
                return self.local_trace
    
        return None

    def is_user_code(self, frame: FrameType) -> bool:
        filename = Path(frame.f_code.co_filename).resolve()
        return filename.is_relative_to(self.user_dir)

    def filtered_trace(self, frame, event, arg):
        if is_user_frame(frame):
            return self.global_trace(frame, event, arg)
        return None

    @staticmethod
    def _get_frame_info(frame: FrameType) -> FrameInfo:
        """Get frame information."""
        filename = Path(frame.f_code.co_filename).resolve()
        line_number = frame.f_lineno
        return FrameInfo(filename, line_number)

    def dbgr_trace(self, frame: FrameType) -> None:
        trace_fn = gettrace()
        settrace(None)  # Temporarily disable to avoid recursion in dbgr

        frame_info = self._get_frame_info(frame)

        prev_line = (
            frame_info.path_to_file.read_text().splitlines()[frame_info.line_number - 2]
            if frame_info.line_number > 1
            else ""
        )

        if (
            prev_line.strip().startswith("# breakpoint")
            or self.mode == DebuggerMode.STEP
        ):
            self.debug_frame(frame)

        settrace(trace_fn)  # Re-enable the original trace function

    def debug_frame(self, frame: FrameType) -> None:
        frame_info = self._get_frame_info(frame)

        _, lines = get_terminal_size()
        height = lines - 1 if debugger_state["full_screen"] else self.n_source_lines + 2

        console = Console(height=height)
        layout = Layout(name="root")
        layout.split_row(
            Layout(name="left"),
            Layout(name="right"),
        )

        syntax = SourceCodeRenderer(
            frame_info.path_to_file,
            frame_info.line_number,
            max_lines=self.n_source_lines,
            border_color="blue",
        )

        locals_table = DictTableRenderer(
            frame.f_locals,
            title="[bold]Local Variables",
            height=self.n_source_lines + 2,
            border_color="blue",
        )

        console.print(
            f"[yellow]{datetime.now()} dbgr: Encountered breakpoint",
        )

        layout["left"].update(syntax)
        layout["right"].update(locals_table)
        console.print(layout)

        command = Prompt.ask(
            "[bold][yellow] >>>",
            choices=["c", "s", "e"],
            default="s" if debugger_state["mode"] == "step" else "c",
        )

        if command == "e":
            console.print(f"[yellow]{datetime.now()} dbgr: Exiting debugger")
            self.mode = DebuggerMode.EXIT
            raise exit(0)
        elif command == "s":
            console.print(f"[yellow]{datetime.now()} dbgr: Stepping into the next line")
            debugger_state["mode"] = "step"
            self.mode = DebuggerMode.STEP
        elif command == "c":
            console.print(f"[yellow]{datetime.now()} dbgr: Continuing execution")
            debugger_state["mode"] = "continue"
            self.mode = DebuggerMode.CONTINUE
        else:
            console.print(f"[yellow]{datetime.now()} dbgr: Invalid command")
            raise exit(0)


def run_dbgr():
    stack = inspect.stack()
    caller_frame = stack[1]
    caller_file = caller_frame.filename
    debugger_state["user_dir"] = Path(caller_file).parent

    dbgr = Debugger(debugger_state["user_dir"])

    # Set the global trace function to start debugging
    settrace(dbgr.global_trace)


def dummy_trace(frame: FrameType, event, arg):
    pass


def main():
    if len(sys.argv) < 2:
        print("Usage: python dbgr.py <script_to_debug.py>")
        exit(1)

    script_path = Path(sys.argv[1]).resolve()
    if not script_path.exists():
        print(f"Script {script_path} does not exist.")
        exit(1)

    # Set the user directory to the script's directory
    debugger_state["user_dir"] = script_path.parent
    dbgr = Debugger(debugger_state["user_dir"])

    settrace(dbgr.filtered_trace)
    threading.settrace(dummy_trace)

    # Run the script with the debugger
    runpy.run_path(str(script_path), run_name="__main__")


if __name__ == "__main__":
    main()
