from kubedeployer.types import PathLike
from kubedeployer.security.kubesec.formatters import KubeSecurityFormatter
from kubedeployer.security.kubesec.scanner import KubeSecurityScanner


class KubeSecurityReport:

    def __init__(self,
                 scanner: KubeSecurityScanner,
                 formatter: KubeSecurityFormatter):
        self._scanner = scanner
        self._formatter = formatter

    def build(self, filename: PathLike):
        content = self._scanner.scan(filename)
        return self._formatter.format(content)
