import pytest

from kubedeployer.utils.convert import str_to_bool


@pytest.mark.parametrize(
    "values, expected",
    (
            (("y", "yes", "t", "true", "True", "on", "1", 1), True),

            (("n", "no", "f", "false", "False", "off", "0", 0), False),
    )
)
def test_str_to_bool(values, expected):
    for v in values:
        assert str_to_bool(v) is expected


@pytest.mark.parametrize("value", ([1], {"True"},))
def test_raises_str_to_bool_on_get_invalid_value_type(value):
    with pytest.raises(TypeError):
        str_to_bool(value)


@pytest.mark.parametrize("value", ("test", "1000", -1,))
def test_raises_str_to_bool_on_invalid_value(value):
    with pytest.raises(ValueError):
        str_to_bool(value)
