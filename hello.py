from sys import exit, settrace, gettrace
from pathlib import Path

# from os import get_terminal_size
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
}


def is_debugger_frame(frame):
    filename = Path(frame.f_code.co_filename).resolve()
    return "test_script.py" not in str(filename)


def local_trace(frame, event, arg):
    if event == "line":
        if is_debugger_frame(frame):
            return local_trace  # Skip stepping into debugger code

        dbgr(frame)
    return local_trace


def global_trace(frame, event, arg):
    if event == "call":
        return local_trace
    return None


def dbgr(frame=None) -> None:
    if frame is None:
        frame = inspect.currentframe()
        if frame is None:
            return

        f_back = frame.f_back
        if f_back is None:
            return

    else:
        f_back = frame

    line_number = f_back.f_lineno
    path_to_file = Path(f_back.f_code.co_filename)
    prev_line = (
        path_to_file.read_text().splitlines()[line_number - 2]
        if line_number > 1
        else ""
    )

    brp = False
    if prev_line.strip().startswith("# breakpoint") or debugger_state["mode"] == "step":
        brp = True

    if brp:
        # _, lines = get_terminal_size()

        console = Console(height=12)
        layout = Layout(name="root")
        layout.split_row(
            Layout(name="left"),
            Layout(name="right"),
        )

        syntax = SourceCodeRenderer(
            path_to_file,
            line_number,
            max_lines=11,
            border_color="blue",
        )

        locals_table = DictTableRenderer(
            f_back.f_locals,
            title="[bold]Local Variables",
            height=13,
            border_color="blue",
        )

        trace_fn = gettrace()
        settrace(None)  # Temporarily disable to avoid recursion in dbgr

        console.print(
            f"[yellow]{datetime.now()} dbgr: Encountered breakpoint",
        )

        layout["left"].update(syntax)
        layout["right"].update(locals_table)
        console.print(layout)

        command = Prompt.ask(
            "[bold][yellow] >>>",
            choices=["continue", "step", "exit"],
            default="continue",
        )

        settrace(trace_fn)  # Re-enable tracing

        if command == "exit":
            console.print(f"[yellow]{datetime.now()} dbgr: Exiting debugger")
            raise exit(0)
        elif command == "step":
            console.print(f"[yellow]{datetime.now()} dbgr: Stepping into the next line")
            debugger_state["mode"] = "step"
        elif command == "continue":
            console.print(f"[yellow]{datetime.now()} dbgr: Continuing execution")
            debugger_state["mode"] = "continue"
        else:
            console.print(f"[yellow]{datetime.now()} dbgr: Invalid command")
            raise exit(0)


def run_dbgr():
    # Set the global trace function to start debugging
    settrace(global_trace)
