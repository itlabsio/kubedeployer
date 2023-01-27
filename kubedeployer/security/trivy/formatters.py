import abc
from collections import defaultdict

from prettytable import PrettyTable, PLAIN_COLUMNS

from kubedeployer.console.wrap import Color, colorize, indent, TAB
from kubedeployer.security.trivy.data import TrivyContent


class TrivyFormatter(abc.ABC):

    @abc.abstractmethod
    def format(self, image: str, content: TrivyContent):
        raise NotImplementedError


class TrivyConsoleStringFormatter(TrivyFormatter):

    def __init__(self, max_width: int = 50):
        self._max_width = max_width

        self._severities_colors = defaultdict(lambda: Color.NO_COLOR)
        self._severities_colors.update({
            "critical": Color.RED,
            "high": Color.YELLOW,
        })

        self._columns = ["Severity", "VulnerabilityID", "PkgName", "Title"]
        self._columns_aliases = [
            "severity", "vulnerability_id", "pkg_name", "title"
        ]
        self._columns_aligns = ["c", "c", "c", "l"]

    def _create_table(self) -> PrettyTable:
        table = PrettyTable(field_names=list(self._columns))
        table.max_width = self._max_width
        table.valign[""] = "t"
        table.sortby = "Severity"
        table.reversesort = True
        table.set_style(PLAIN_COLUMNS)
        for column, align in zip(self._columns, self._columns_aligns):
            table.align[column] = align
        return table

    def _format_image(self, image: str) -> str:
        return f"Scan image: {image}\n"

    def _format_content(self, content: TrivyContent) -> str:
        table = self._create_table()
        for r in content.results:
            for v in r.vulnerabilities:
                table.add_row([
                    colorize(
                        v.severity,
                        color=self._severities_colors[v.severity.lower()]
                    ),
                    v.vulnerability_id,
                    v.pkg_name,
                    v.title,
                ])
        return table.get_string()

    def format(self, image: str, content: TrivyContent) -> str:
        return "\n".join([
            self._format_image(image),
            indent(self._format_content(content), prefix=TAB),
        ])
