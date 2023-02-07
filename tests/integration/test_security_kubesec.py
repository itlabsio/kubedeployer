from pathlib import Path

import pytest

from kubedeployer.security.kubesec.data import KubeSecurityContent, KubeObject, ScoringRecord
from kubedeployer.security.kubesec.errors import KubeSecurityError
from kubedeployer.security.kubesec.formatters import KubeSecurityConsoleStringFormatter
from kubedeployer.security.kubesec.scanner import KubeSecurityScanner


def test_scan_file_with_manifests(data_path):
    scanner = KubeSecurityScanner()

    content = scanner.scan(data_path / "manifests/manifests.yaml")

    assert len(content) == 5


def test_raises_scanning_unsupported_file():
    filename = Path(__file__)
    scanner = KubeSecurityScanner()

    with pytest.raises(KubeSecurityError):
        scanner.scan(filename)


def test_format_content_to_console_string():
    content = KubeSecurityContent.parse_obj([
        KubeObject(
            object="test",
            scoring={
                "advise": [ScoringRecord(id="1", selector="none", reason="")],
                "passed": [ScoringRecord(id="2", selector="none", reason="")],
                "critical": [ScoringRecord(id="3", selector="none", reason="")],
            }
        )
    ])
    formatter = KubeSecurityConsoleStringFormatter()

    retrieved = formatter.format(content)

    assert retrieved == (
        "Scan test\n"
        "    \033[0;93;40mADVISE\033[0m\n"
        "    Id        Selector        Reason        \n"
        "     1            none                      \n"
        "    \033[0;32;40mPASSED\033[0m\n"
        "    Id        Selector        Reason        \n"
        "     2            none                      \n"
        "    \033[0;31;40mCRITICAL\033[0m\n"
        "    Id        Selector        Reason        \n"
        "     3            none                      "
    )
