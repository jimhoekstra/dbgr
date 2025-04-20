from sys import exit
from pathlib import Path
from os import get_terminal_size
import inspect

from rich.console import Console
from rich.prompt import Prompt
from rich.layout import Layout

from components.renderers.source_code_renderer import SourceCodeRenderer
from components.renderers.dict_table_renderer import DictTableRenderer


def dbgr(frame = None) -> None:
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

    _, lines = get_terminal_size()

    console = Console(height=lines - 1)
    layout = Layout(name="root")
    layout.split_row(
        Layout(name="left"),
        Layout(name="right"),
    )

    syntax = SourceCodeRenderer(
        Path(f_back.f_code.co_filename),
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

    console.print(
        "[italic red]Encountered breakpoint in",
        f_back.f_code.co_filename,
        "at line",
        line_number,
    )

    layout["left"].update(syntax)
    layout["right"].update(locals_table)
    console.print(layout)

    command = Prompt.ask(
        "[bold][yellow] >>>", choices=["continue", "step", "exit"], default="continue"
    )

    if command == "exit":
        console.print("[italic red]Exiting debugger")
        raise exit(0)
    elif command == "step":
        raise NotImplementedError("Step command not implemented yet")
    else:
        console.print("[italic red]Continuing execution")
