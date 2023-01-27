import datetime

import pytest

from kubedeployer.console.wrap import Color, colorize, indent, timestamp


@pytest.fixture
def now():
    return datetime.datetime.now()


def test_colorize_message():
    assert colorize("test", Color.RED) == "\033[0;31;40mtest\033[0m"


def test_indent_message():
    assert indent("test", "  ") == "  test"


def test_indent_multiline_message():
    assert indent("test\ntest", "  ") == "  test\n  test"


def test_add_timestamp_to_message(now):
    assert timestamp("test", lambda: now) == \
           f"{now.strftime('%d.%m.%Y %H:%M:%S')}: test"
