import pytest
from pydantic import ValidationError

from kubedeployer.security.trivy.data import TrivyContent, TrivyResult, \
    TrivyVulnerability


def test_parse_trivy_content():
    data = {
        "Results": [{
            "Vulnerabilities": [{
                "Severity": "test",
                "VulnerabilityID": "test",
                "PkgName": "test",
                "Title": "test",
            }]
        }]
    }
    content = TrivyContent(**data)
    assert content == TrivyContent(
        results=[TrivyResult(
            vulnerabilities=[
                TrivyVulnerability(
                    severity="test",
                    vulnerability_id="test",
                    pkg_name="test",
                    title="test",
                )
            ]
        )]
    )


def test_parse_trivy_content_with_empty_results():
    data = {}
    content = TrivyContent(**data)
    assert content.results == []


def test_parse_trivy_content_with_empty_vulnerabilities():
    data = {"Results": [{}]}
    content = TrivyContent(**data)
    [record] = content.results  # type: TrivyResult
    assert record.vulnerabilities == []


def test_raises_parse_trivy_content_with_incorrect_data():
    data = {
        "Results": [{
            "Vulnerabilities": [{
            }]
        }]
    }
    with pytest.raises(ValidationError):
        TrivyContent(**data)
