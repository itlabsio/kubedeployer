from typing import List

from pydantic import Field

from kubedeployer.types import BaseModel


class TrivyContent(BaseModel):
    results: List["TrivyResult"] = Field(
        alias="Results", default_factory=list
    )

    class Config:
        allow_population_by_field_name = True


class TrivyResult(BaseModel):
    vulnerabilities: List["TrivyVulnerability"] = Field(
        alias="Vulnerabilities", default_factory=list
    )


class TrivyVulnerability(BaseModel):
    severity: str = Field(alias="Severity")
    vulnerability_id: str = Field(alias="VulnerabilityID")
    pkg_name: str = Field(alias="PkgName")
    title: str = Field(alias="Title")


TrivyContent.update_forward_refs()
TrivyResult.update_forward_refs()
