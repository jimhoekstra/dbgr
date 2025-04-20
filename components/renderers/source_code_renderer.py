from pathlib import Path
from rich.syntax import Syntax
from rich.panel import Panel
from rich.console import Console, RenderResult, ConsoleOptions


class SourceCodeRenderer:
    def __init__(
        self,
        path_to_file: Path,
        line_number: int,
        max_lines: int = 20,
        border_color: str = "dark_blue",
    ) -> None:
        self.code = Path(path_to_file).read_text()
        self.line_number = line_number
        self.path_to_file = path_to_file
        self.max_lines = max_lines
        self.border_color = border_color

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        height = options.height or options.size.height
        height = min(height, self.max_lines + 2)  # account for title and border

        lines_for_code = height - 2  # account for title and border
        lines_on_top = (lines_for_code - 1) // 2
        lines_on_bottom = lines_for_code - 1 - lines_on_top

        syntax = Syntax(
            self.code,
            "python",
            line_numbers=True,
            line_range=(
                self.line_number - lines_on_top,
                self.line_number + lines_on_bottom,
            ),
            word_wrap=True,
            highlight_lines=set([self.line_number]),
            theme="monokai",
        )

        yield Panel(
            syntax,
            border_style=f"bold {self.border_color}",
            title=f"File: [underline]{self.path_to_file.name}",
            height=height,
        )
