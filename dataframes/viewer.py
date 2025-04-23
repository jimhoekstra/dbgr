from textual.app import App, ComposeResult
from textual.widgets import DataTable

import pandas as pd


class DataFrameViewer(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    DEFAULT_CSS = """
    Screen {
        align: center middle;
    }

    DataTable {
        width: auto;

        &:focus {
            background-tint: $foreground 0%;

            & > .datatable--cursor {
                background: yellow;
                color: $block-cursor-foreground;
                text-style: $block-cursor-text-style;
            }

            & > .datatable--header {
                background-tint: $foreground 0%;
            }

            & > .datatable--fixed-cursor {
                color: $block-cursor-foreground;
                background: $block-cursor-background;
            }
        }
    }
    """

    df: pd.DataFrame

    def __init__(self, df: pd.DataFrame) -> None:
        super().__init__()
        self.df = df

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        datatable = self.query_one(DataTable)

        for column in self.df.columns.values:
            datatable.add_column(column)

        for index, row in self.df.iterrows():
            datatable.add_row(*[str(value) for value in row])
