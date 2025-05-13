import polars as pl
from subscript_to_debug import test_sub_script
import terdious


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
    terdious.set_breakpoint()
    y: int = z + 1
    z = 0
    for i in range(3):
        y = y * mul

    test_sub_script()
    return y


def main():
    result_a = fun(1, 2)
    result_b = fun(10, 20)
    df = get_pl_df()


if __name__ == "__main__":
    main()
