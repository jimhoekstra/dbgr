from dbgr import run_dbgr


# breakpoint
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


# breakpoint
def main():
    result_a = fun(1, 2)
    result_b = fun(10, 20)
    print(result_a)
    # breakpoint
    print(result_b)


if __name__ == "__main__":
    run_dbgr()
    main()
