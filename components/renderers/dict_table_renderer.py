from rich.table import Table
from rich.box import SIMPLE
from rich.padding import Padding
from rich.panel import Panel
from rich.console import Console, RenderResult, ConsoleOptions


class DictTableRenderer:
    def __init__(self, dict_to_render: dict, title: str, height: int, border_color: str) -> None:
        self.dict_to_render = dict_to_render
        self.title = title
        self.height = height
        self.border_color = border_color

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width

        table = Table(
            highlight=True, box=SIMPLE, row_styles=["on grey11", ""], width=width
        )

        table.add_column("[grey50]key", style="cyan", justify="right")
        table.add_column("[grey50]value", justify="left")
        table.add_column("[grey50]type", style="magenta italic")

        for k, v in self.dict_to_render.items():
            table.add_row(
                Padding(k, (0, 0)),
                Padding(repr(v), (0, 0)),
                Padding(v.__class__.__name__, (0, 0)),
            )

        yield Panel(
            Padding(table, (0, 4)),
            border_style=f"bold {self.border_color}",
            title=self.title,
            height=self.height,
        )
