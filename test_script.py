from hello import dbgr


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
    dbgr()
    y = y * mul
    dbgr()
    return y


fun(1, 2)
