from hello import run_dbgr


def fun(z: int, mul: int) -> int:
    """This is a function that adds 1 to the input value z and returns it.

    Parameters
    ----------
    z
        The input value to be incremented.
    mul


    Returns
    -------
    int
        The incremented value.
    """
    y: int = z + 1
    z = 0
    # breakpoint
    y = y * mul
    y = y * mul
    y = y * mul
    # breakpoint
    return y


def main():
    run_dbgr()
    result_a = fun(1, 2)
    result_b = fun(10, 20)
    print(result_a)
    print(result_b)


if __name__ == "__main__":
    main()
