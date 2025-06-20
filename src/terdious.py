from pathlib import Path
from sys import settrace, gettrace, exit
from types import FrameType
from datetime import datetime
import inspect
from dataclasses import dataclass

from rich import print as rich_print
from rich.console import Console
from rich.prompt import Prompt
from rich.layout import Layout
from rich.panel import Panel

from components.renderers.source_code_renderer import SourceCodeRenderer
from components.renderers.dict_table_renderer import DictTableRenderer


@dataclass
class Breakpoint:
    file_path: Path
    line_number: int


class DebuggerState:
    user_dir: None | Path
    breakpoints: list[Breakpoint]
    disabled_breakpoints: list[Breakpoint]
    print_fn_calls: bool

    def __init__(self) -> None:
        self.user_dir = None
        self.breakpoints = []
        self.disabled_breakpoints = []
        self.print_fn_calls = True

    def set_user_dir(self, user_dir: Path) -> None:
        self.user_dir = user_dir

    def add_breakpoint(self, file_path: Path, line_number: int) -> None:
        breakpoint = Breakpoint(file_path, line_number)
        if breakpoint in self.breakpoints:
            return
        self.breakpoints.append(Breakpoint(file_path, line_number))

    def disable_breakpoint(self, file_path: Path, line_number: int) -> None:
        breakpoint = Breakpoint(file_path, line_number)
        if breakpoint in self.breakpoints:
            self.disabled_breakpoints.append(breakpoint)

    def is_breakpoint(self, frame: FrameType) -> bool:
        breakpoint = Breakpoint(
            file_path=Path(frame.f_code.co_filename), line_number=frame.f_lineno
        )
        if breakpoint in self.disabled_breakpoints:
            return False
        if breakpoint in self.breakpoints:
            return True

        return False


debugger_state = DebuggerState()


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
    if ".venv" in str(filename) or "terdious.py" in str(filename):
        return False

    assert debugger_state.user_dir is not None, "User directory not set"
    # Check that the file of the frame is in the user's directory
    if not filename.is_relative_to(debugger_state.user_dir):
        return False

    return True


def terdious_print(text_to_print: str) -> None:
    rich_print(f"[yellow]{datetime.now()} terdious: {text_to_print}")


def local_trace(frame: FrameType, event, arg):
    if not is_user_frame(frame):
        return None

    if event == "return" and debugger_state.print_fn_calls:
        terdious_print(
            f"Function [bold green]{frame.f_code.co_name}[/bold green] returned in "
            f"{frame.f_code.co_filename}:{frame.f_lineno}"
        )
    elif event == "line":
        if debugger_state.is_breakpoint(frame):
            debug_frame(frame)
            return local_trace

    return local_trace


def global_trace(frame: FrameType, event, arg):
    if not is_user_frame(frame):
        return None

    if event == "call":
        if debugger_state.print_fn_calls:
            terdious_print(
                f"Stepping into function [bold green]{frame.f_code.co_name}[/bold green] in "
                f"{frame.f_code.co_filename}:{frame.f_lineno}"
            )
        return local_trace

    return None


def breakpoint():
    stack = inspect.stack()
    caller_frame = stack[1]
    debug_frame(caller_frame.frame)


def debug_frame(frame: FrameType) -> None:
    trace = gettrace()
    settrace(None)

    console = Console(height=22)

    layout = Layout(name="root")
    layout.split_row(
        Layout(name="left"),
        Layout(name="right"),
    )

    syntax = SourceCodeRenderer(
        Path(frame.f_code.co_filename),
        frame.f_lineno,
        max_lines=20,
        border_color="blue",
    )

    locals_table = DictTableRenderer(
        frame.f_locals,
        title="[bold]Local Variables",
        height=20 + 2,
        border_color="blue",
    )

    layout["left"].update(syntax)
    layout["right"].update(locals_table)
    console.print(layout)

    continue_debugging = True
    while continue_debugging:
        response = Prompt.ask()
        if response == "q" or response == "quit":
            terdious_print("[bold red]Exiting debugger.[/bold red]")
            continue_debugging = False
            exit(0)
        elif response.startswith("p "):
            var_name = response[2:].strip()
            if var_name in frame.f_locals:
                value = frame.f_locals[var_name]
                rich_print(Panel(value))
            else:
                terdious_print(f"[bold red]Variable '{var_name}' not found.[/bold red]")
        elif response == "c" or response == "continue":
            terdious_print("[bold green]Continuing execution...[/bold green]")
            continue_debugging = False

    settrace(trace)


def set_print_fn_calls(print_fn_calls: bool) -> None:
    debugger_state.print_fn_calls = print_fn_calls


def enable_debugger():
    stack = inspect.stack()
    debugger_state.set_user_dir(Path(stack[-1].filename).parent)
    settrace(global_trace)
    terdious_print("[bold red]Debugger is running![/bold red]")
