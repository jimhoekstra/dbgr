from dbgr import dbgr
import pandas as pd


def get_pandas_df():
    """This function creates a pandas DataFrame with some sample data.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing sample data.
    """
    data = {
        "Name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"],
        "Age": [25, 30, 35, 40, 45, 50],
        "City": [
            "New York",
            "Los Angeles",
            "Chicago",
            "Houston",
            "Phoenix",
            "Philadelphia",
        ],
        "Salary": [70000, 80000, 90000, 100000, 110000, 120000],
        "Department": ["HR", "IT", "Finance", "Marketing", "Sales", "Operations"],
        "Experience": [5, 7, 10, 12, 15, 20],
    }
    df = pd.DataFrame(data)
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
    dbgr()
    z = 0
    for i in range(3):
        y = y * mul

    return y


def main():
    dbgr()
    result_a = fun(1, 2)
    result_b = fun(10, 20)
    df = get_pandas_df()
    long_string = "hello, world! " * 20

    print(result_a)
    print(result_b)
    print(df)
    print(long_string)

    dbgr()


if __name__ == "__main__":
    main()
