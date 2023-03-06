import os

import pytest
from unittest import mock

from kubedeployer.text import envsubst


@pytest.fixture(autouse=True)
def environments():
    variables = {
        "HOST_NAME": "host.local",
        "NAMESPACE": "default",
        "SERVICE_NAME": "example",

        "VARIABLE": "test",
        "IGNORED_VARIABLE": "ignore",
        "DIGIT_VARIABLE": "123"
    }
    with mock.patch.dict(os.environ, variables, clear=True):
        yield


def test_envsubst_replace_variable():
    text = "$VARIABLE"
    assert envsubst(text) == "test"


def test_envsubst_replace_variable_with_curly_braces():
    text = "${VARIABLE}"
    assert envsubst(text) == "test"


def test_envsubst_replace_multiply_variables():
    text = "$VARIABLE$VARIABLE"
    assert envsubst(text) == "testtest"


def test_envsubst_replace_variables_in_multiline():
    text = """
    Line 1: $VARIABLE
    Line 2: ${VARIABLE}
    """
    expected = """
    Line 1: test
    Line 2: test
    """
    assert envsubst(text) == expected


def test_envsubst_replace_variables_in_multiline_with_quotes():
    text = """
    Line 1: "$VARIABLE"
    Line 2: "${VARIABLE}"
    Line 3: $VARIABLE
    Line 4: ${VARIABLE}
    Line 5: "${DIGIT_VARIABLE}"
    Line 6: ${DIGIT_VARIABLE}
    """
    expected = """
    Line 1: "test"
    Line 2: "test"
    Line 3: test
    Line 4: test
    Line 5: "123"
    Line 6: 123
    """
    assert envsubst(text) == expected


def test_envsubst_ignore_unknown_variables():
    text = "$UNKNOWN_VARIABLE"
    assert envsubst(text) == "$UNKNOWN_VARIABLE"


def test_envsubst_ignore_variables_with_unknown_forms():
    text = "$$IGNORED_VARIABLE"
    assert envsubst(text) == "$$IGNORED_VARIABLE"


def test_envsubst_replace_variables_in_file(data_path):
    with open(data_path / "manifests/env-manifest.yaml", "r") as f:
        retrieved = envsubst(f.read())

        assert "name: host.local-example" in retrieved
        assert "namespace: default" in retrieved
        assert "- host: host.local" in retrieved
        assert "- path: /example" in retrieved
        assert "name: example" in retrieved
