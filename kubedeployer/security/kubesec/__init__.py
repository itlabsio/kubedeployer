from kubedeployer.security.kubesec.formatters import KubeSecurityConsoleStringFormatter
from kubedeployer.security.kubesec.report import KubeSecurityReport
from kubedeployer.security.kubesec.scanner import KubeSecurityScanner


def create_kube_security_report() -> KubeSecurityReport:
    return KubeSecurityReport(
        scanner=KubeSecurityScanner(),
        formatter=KubeSecurityConsoleStringFormatter()
    )
