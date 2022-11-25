from kubedeployer.security.trivy.formatters import TrivyConsoleStringFormatter
from kubedeployer.security.trivy.report import TrivyReport
from kubedeployer.security.trivy.scanner import TrivyScanner


def create_trivy_report() -> TrivyReport:
    return TrivyReport(
        scanner=TrivyScanner(),
        formatter=TrivyConsoleStringFormatter(),
    )
