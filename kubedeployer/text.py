import os
import re


def envsubst(text: str) -> str:
    """
    Set value by environment variable name

    Variable names are must match the format:
        - $VARIABLE;
        - ${VARIABLE}.

    Example:

        $ export VARIABLE=test

        >>> envsubst("Example of replacing: $VARIABLE")
        Example of replacing: test
    """

    def replace(match: re.Match):
        variable = match.group("variable")
        return os.getenv(variable) if variable in os.environ else match.group()

    # Expression (?<!\$) allow to exclude next variant:
    #   $$VARIABLE
    regexp = r"(?<!\$)\${?(?P<variable>([a-zA-Z_]\w*))}?"
    return re.sub(regexp, replace, text)
