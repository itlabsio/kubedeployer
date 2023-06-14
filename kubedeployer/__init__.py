import argparse
import os
from typing import Type

from kubedeployer import deploy
from kubedeployer.deployer.abstract_deployer import AbstractDeployer
from kubedeployer.deployer.kustomize_deployer import KustomizeDeployer
from kubedeployer.deployer.orthodox_deployer import OrthodoxDeployer
from kubedeployer.deployer.smart_deployer import SmartDeployer

__all__ = ['run_kubedeployer']

from kubedeployer.gitlab_ci import specification


def run_kubedeployer():
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

    parser.add_argument(
        "--project-dir",
        type=str,
        help="full path to folder with project",
    )

    parser.add_argument(
        "--environment",
        type=str,
        help="environment for builder",
    )

    parser.add_argument(
        "--manifest-folder",
        type=str,
        help="path to folder with manifest, path is relative to current working directory",
    )

    args = parser.parse_args()
    deployer_type = args.deployer
    dry_run = args.dry_run
    if args.manifest_folder:
        os.environ[specification.MANIFEST_FOLDER_ENV_VAR] = args.manifest_folder
    if args.project_dir:
        os.environ[specification.CI_PROJECT_DIR_ENV_VAR] = args.project_dir
    if args.environment:
        os.environ[specification.ENVIRONMENT_ENV_VAR] = args.environment
    if dry_run:
        os.environ[specification.CI_PROJECT_ID_ENV_VAR] = '0'
    deployer_classes = {
        'orthodox': OrthodoxDeployer,
        'kustomize': KustomizeDeployer,
        'smart': SmartDeployer
    }
    deployer: Type[AbstractDeployer] = deployer_classes[deployer_type]
    deploy.run(deployer=deployer, dry_run=dry_run, env_files=args.env_file)
