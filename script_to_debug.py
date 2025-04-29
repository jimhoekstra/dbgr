import polars as pl
from dbgr import run_dbgr


def get_pl_df() -> pl.DataFrame:
    """This function creates a polars DataFrame with some sample data.

    Returns
    -------
    pl.DataFrame
        A DataFrame containing sample data.
    """
    data = {
        "City": ["New York", "Los Angeles", "Chicago"],
        "Temperature": [85, 90, 78],
        "Humidity": [70, 65, 80],
        "Wind Speed": [10, 12, 8],
    }
    df = pl.DataFrame(data)
    return df


def fun(z: int, mul: int) -> int:
    """This is a function that adds 1 to the input value z and returns it.

    Parameters
    ----------
    z
        The input value to be incremented.
    mul
        The multiplier to be applied to the incremented value.

    Returns
    -------
    int
        The incremented value.
    """
    y: int = z + 1
    z = 0
    for i in range(3):
        y = y * mul
    return y


def main():
    result_a = fun(1, 2)
    result_b = fun(10, 20)
    # breakpoint
    df = get_pl_df()
    # breakpoint
    print(df)

    print(result_a)
    print(result_b)


if __name__ == "__main__":
    run_dbgr()
    main()
