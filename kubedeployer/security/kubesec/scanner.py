import json
import subprocess
from json import JSONDecodeError

from pydantic import ValidationError

from kubedeployer.types import PathLike
from kubedeployer.security.kubesec.data import KubeSecurityContent
from kubedeployer.security.kubesec.errors import KubeSecurityError, KubeSecurityContentError


class KubeSecurityScanner:

    @staticmethod
    def __scan(filename: PathLike) -> str:
        cmd = f"kubesec scan --format json --exit-code 0 {str(filename)}"
        result = subprocess.run(cmd, capture_output=True, shell=True)
        if result.returncode != 0:
            raise KubeSecurityError(result.stderr.decode("utf-8"))
        return result.stdout.decode("utf-8")

    @staticmethod
    def __format(content: str) -> KubeSecurityContent:
        try:
            data = json.loads(content)
            return KubeSecurityContent.parse_obj(data)
        except (TypeError, JSONDecodeError, ValidationError) as e:
            raise KubeSecurityContentError(e)
        except Exception as e:
            raise KubeSecurityError(e)

    def scan(self, filename: PathLike) -> KubeSecurityContent:
        content = self.__scan(filename)
        return self.__format(content)
