from typing import Union


def str_to_bool(value: Union[str, int]) -> bool:
    if not isinstance(value, (str, int)):
        raise TypeError(f"Invalid type {type(value)} (expected str or int)")

    if isinstance(value, str):
        value = value.lower()

    if value in ("y", "yes", "t", "true", "on", "1", 1):
        return True

    if value in ("n", "no", "f", "false", "off", "0", 0):
        return False

    raise ValueError(f"Invalid truth value {value}")
