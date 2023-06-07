import argparse
from typing import Type

from kubedeployer import deploy
from kubedeployer.deployer.abstract_deployer import AbstractDeployer
from kubedeployer.deployer.kustomize_deployer import KustomizeDeployer
from kubedeployer.deployer.orthodox_deployer import OrthodoxDeployer
from kubedeployer.deployer.smart_deployer import SmartDeployer

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--deployer",
    choices=['orthodox', 'kustomize', 'smart'],
    default='smart',
    help="deploy by available choices: orthodox, kustomize or smart, default is orthodox",
)
parser.add_argument(
    "--dry-run",
    type=bool,
    action=argparse.BooleanOptionalAction,
    help="show only manifests if dry-run is set",
)
parser.add_argument(
    "--env-file",
    type=str,
    nargs="+",
    action="extend",
    help="read in a file of environment variables",
)

args = parser.parse_args()
deployer_type = args.deployer
deployer_classes = {
    'orthodox': OrthodoxDeployer,
    'kustomize': KustomizeDeployer,
    'smart': SmartDeployer
}
deployer: Type[AbstractDeployer] = deployer_classes[deployer_type]
deploy.run(deployer=deployer, dry_run=args.dry_run, env_files=args.env_file)
