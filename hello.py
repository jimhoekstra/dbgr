from sys import exit, settrace, gettrace
from pathlib import Path
from types import FrameType

from os import get_terminal_size
import inspect
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt
from rich.layout import Layout

from components.renderers.source_code_renderer import SourceCodeRenderer
from components.renderers.dict_table_renderer import DictTableRenderer


# Global debugger state
debugger_state = {
    "mode": "continue",  # can be "step" or "continue"
    "user_dir": None,
    "full_screen": False,
}


def is_user_frame(frame: FrameType) -> bool:
    filename = Path(frame.f_code.co_filename).resolve()
    if ".venv" in str(filename):
        return False

    assert debugger_state["user_dir"] is not None, "User directory not set"
    if not filename.is_relative_to(debugger_state["user_dir"]):
        return False

    return True


def local_trace(frame: FrameType, event, arg):
    if not is_user_frame(frame):
        return local_trace  # Skip stepping into debugger code

    if event == "line":
        dbgr(frame)
    elif event == "call":
        print(f"dbgr: Function call {frame.f_code.co_name}")
    else:
        print(f"dbgr: Event {event} in {frame.f_code.co_name}")
    return local_trace


def global_trace(frame, event, arg):
    if not is_user_frame(frame):
        return global_trace  # Skip stepping into debugger code

    if event == "call":
        dbgr(frame)
        return local_trace
    return None


def dbgr(frame: FrameType) -> None:
    trace_fn = gettrace()
    settrace(None)  # Temporarily disable to avoid recursion in dbgr

    source_lines = 20

    line_number = frame.f_lineno
    path_to_file = Path(frame.f_code.co_filename)

    prev_line = (
        path_to_file.read_text().splitlines()[line_number - 2]
        if line_number > 1
        else ""
    )

    brp = False
    if prev_line.strip().startswith("# breakpoint") or debugger_state["mode"] == "step":
        brp = True

    if brp:
        _, lines = get_terminal_size()
        height = lines - 1 if debugger_state["full_screen"] else source_lines + 2

        console = Console(height=height)
        layout = Layout(name="root")
        layout.split_row(
            Layout(name="left"),
            Layout(name="right"),
        )

        syntax = SourceCodeRenderer(
            path_to_file,
            line_number,
            max_lines=source_lines,
            border_color="blue",
        )

        locals_table = DictTableRenderer(
            frame.f_locals,
            title="[bold]Local Variables",
            height=source_lines + 2,
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
            raise exit(0)
        elif command == "s":
            console.print(f"[yellow]{datetime.now()} dbgr: Stepping into the next line")
            debugger_state["mode"] = "step"
        elif command == "c":
            console.print(f"[yellow]{datetime.now()} dbgr: Continuing execution")
            debugger_state["mode"] = "continue"
        else:
            console.print(f"[yellow]{datetime.now()} dbgr: Invalid command")
            raise exit(0)

    settrace(trace_fn)  # Re-enable tracing


def run_dbgr():
    stack = inspect.stack()
    caller_frame = stack[1]
    caller_file = caller_frame.filename
    debugger_state["user_dir"] = Path(caller_file).parent

    # Set the global trace function to start debugging
    settrace(global_trace)
