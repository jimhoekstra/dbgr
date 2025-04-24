from rich.table import Table
from rich.box import SIMPLE
from rich.padding import Padding
from rich.console import Console, RenderResult, ConsoleOptions, Group
from rich.text import Text

import pandas as pd


class DictTableRenderer:
    def __init__(
        self, dict_to_render: dict, title: str, height: int, border_color: str
    ) -> None:
        self.dict_to_render = dict_to_render
        self.title = title
        self.height = height
        self.border_color = border_color

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width

        table = Table(
            highlight=True,
            box=SIMPLE,
            row_styles=["on grey11", ""],
            width=width - 10,
            style="white",
        )

        table.add_column("[bright_black]Key", style="cyan", justify="right")
        table.add_column("[bright_black]Value", justify="left")
        table.add_column("[bright_black]Type", style="magenta italic")

        for k, v in self.dict_to_render.items():
            value = repr(v)
            if isinstance(v, pd.DataFrame):
                value = f"[bold]DataFrame[{len(v)} rows, {len(v.columns)} columns]"
            if len(value) > 50:
                value = value[:30] + "..."

            table.add_row(
                Padding(k, (0, 0)),
                Padding(value, (0, 0)),
                Padding(v.__class__.__name__, (0, 0)),
            )

        if len(self.dict_to_render) == 0:
            text = Text("No local variables", style="italic", justify="center")
            yield Padding(Group(table, text), (0, 4))
        else:
            yield Padding(table, (0, 4))
