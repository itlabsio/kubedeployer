import argparse

from kubedeployer import deploy
from kubedeployer.deployer.abstract_deployer import AbstractDeployer
from kubedeployer.deployer.kustomize_deployer import KustomizeDeployer
from kubedeployer.deployer.orthodox_deployer import OrthodoxDeployer
from kubedeployer.deployer.smart_deployer import SmartDeployer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--deployer",
        choices=['orthodox', 'kustomize', 'smart'],
        default='smart',
        help="deploy by available choices: orthodox, kustomize or smart, default is orthodox"
    )
    args = parser.parse_args()
    deployer_type = args.deployer
    deployer_classes = {
        'orthodox': OrthodoxDeployer,
        'kustomize': KustomizeDeployer,
        'smart': SmartDeployer
    }
    deployer: AbstractDeployer = deployer_classes[deployer_type]
    deploy.run(deployer=deployer)
