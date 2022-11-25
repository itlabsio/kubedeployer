import abc
from collections import defaultdict
from typing import List

from prettytable import PrettyTable, PLAIN_COLUMNS

from kubedeployer.console.wrap import colorize, Color, indent, TAB
from kubedeployer.security.kubesec.data import KubeSecurityContent, ScoringRecord, \
    ScoringLevel, KubeObject


class KubeSecurityFormatter(abc.ABC):

    @abc.abstractmethod
    def format(self, content: KubeSecurityContent):
        raise NotImplementedError


class KubeSecurityConsoleStringFormatter(KubeSecurityFormatter):

    def __init__(self, max_width: int = 50):
        self._max_width = max_width

        self._scoring_level_colors = defaultdict(lambda: Color.NO_COLOR)
        self._scoring_level_colors.update({
            "critical": Color.RED,
            "passed": Color.GREEN,
            "advise": Color.YELLOW,
        })

        self._columns = ["id", "selector", "reason"]
        self._columns_aligns = ["r", "r", "l"]

    def __create_table(self) -> PrettyTable:
        table = PrettyTable(field_names=[c.capitalize() for c in self._columns])
        table.max_width = self._max_width
        table.valign[""] = "t"
        table.set_style(PLAIN_COLUMNS)
        for column, align in zip(self._columns, self._columns_aligns):
            table.align[column.capitalize()] = align
        return table

    def __format_kube_object(self, kube_object: KubeObject) -> str:
        scoring = "\n".join([
            indent(self.__format_scoring(level, records), prefix=TAB)
            for level, records in kube_object.scoring.items()
        ])

        return f"Scan {kube_object.object}\n{scoring}"

    def __format_scoring(
            self, level: ScoringLevel, records: List[ScoringRecord]
    ) -> str:
        return "\n".join([
            self.__format_scoring_level(level),
            self.__format_scoring_records(records),
        ])

    def __format_scoring_level(self, scoring_level: str) -> str:
        return colorize(
            scoring_level.upper(),
            color=self._scoring_level_colors[scoring_level],
        )

    def __format_scoring_records(self, records: List[ScoringRecord]) -> str:
        table = self.__create_table()
        for r in records:
            table.add_row([getattr(r, c) for c in self._columns])
        return table.get_string()

    def format(self, content: KubeSecurityContent) -> str:
        res = "\n".join([
            self.__format_kube_object(kube_object)
            for kube_object in list(content)
        ])
        return res
