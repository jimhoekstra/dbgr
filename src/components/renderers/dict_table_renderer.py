from rich.table import Table
from rich.box import SIMPLE
from rich.padding import Padding
from rich.console import Console, RenderResult, ConsoleOptions, Group
from rich.text import Text


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

        padding = 4
        table_padding = 2 * 3 + 2
        width = width - (padding * 2 + table_padding)

        table = Table(
            highlight=True,
            box=SIMPLE,
            row_styles=["on grey7", ""],
            width=width,
            style="white",
        )

        key_width = width // 6
        value_width = width // 3 * 2

        table.add_column(
            "[grey50]key",
            style="cyan",
            justify="right",
            max_width=key_width,
            min_width=key_width,
        )
        table.add_column(
            "[grey50]type",
            style="magenta italic",
            max_width=key_width,
            min_width=key_width,
        )
        table.add_column(
            "[grey50]value",
            justify="left",
            max_width=value_width,
            min_width=value_width,
        )

        for k, v in self.dict_to_render.items():
            display_key = k
            if len(display_key) > (key_width - 3):
                display_key = display_key[: key_width - 3] + "..."

            display_type = v.__class__.__name__
            if len(display_type) > (key_width - 3):
                display_type = display_type[: key_width - 3] + "..."

            display_value = repr(v).replace("\n", "\\n")
            if len(display_value) > (value_width - 3):
                display_value = display_value[: value_width - 3] + "..."

            table.add_row(
                Padding(k, (0, 0)),
                Padding(v.__class__.__name__, (0, 0)),
                Padding(display_value, (0, 0)),
            )

        if len(self.dict_to_render) == 0:
            text = Text("No local variables", style="italic", justify="center")
            yield Padding(Group(table, text), (0, padding))
        else:
            yield Padding(table, (0, padding))
