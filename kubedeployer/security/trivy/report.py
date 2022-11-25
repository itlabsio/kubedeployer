from kubedeployer.security.trivy.formatters import TrivyFormatter
from kubedeployer.security.trivy.scanner import TrivyScanner


class TrivyReport:

    def __init__(self, scanner: TrivyScanner, formatter: TrivyFormatter):
        self._scanner = scanner
        self._formatter = formatter

    def build(self, image: str):
        content = self._scanner.scan(image)
        return self._formatter.format(image, content)
