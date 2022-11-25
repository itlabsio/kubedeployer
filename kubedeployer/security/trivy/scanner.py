import json
import subprocess
from json import JSONDecodeError

from pydantic import ValidationError

from kubedeployer.security.trivy.data import TrivyContent
from kubedeployer.security.trivy.errors import TrivyError, TrivyContentError


class TrivyScanner:

    @staticmethod
    def __scan(image: str) -> str:
        cmd = (
            f"trivy --quiet image "
            f"--severity HIGH,CRITICAL "
            f"--format json "
            f"--timeout 10m0s "
            f"{image}"
        )
        result = subprocess.run(cmd, capture_output=True, shell=True)
        if result.returncode != 0:
            raise TrivyError(result.stderr.decode("utf-8"))
        return result.stdout.decode("utf-8")

    @staticmethod
    def __format(content: str) -> TrivyContent:
        try:
            data = json.loads(content)
            return TrivyContent(**data)
        except (TypeError, JSONDecodeError, ValidationError) as e:
            raise TrivyContentError(e)
        except Exception as e:
            raise TrivyError(e)

    def scan(self, image: str) -> TrivyContent:
        content = self.__scan(image)
        return self.__format(content)
