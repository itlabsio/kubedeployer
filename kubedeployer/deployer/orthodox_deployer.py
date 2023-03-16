import glob
import os
import re
import tempfile
from pathlib import Path
from typing import List, Tuple

import yaml

from kubedeployer import k8s, console
from kubedeployer.deployer.abstract_deployer import AbstractDeployer
from kubedeployer.gitlab_ci.environment_variables import settings
from kubedeployer.k8s.models import K8sObject


def is_yaml_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    return os.path.isfile(file_path) and (file_extension in ('.yaml', '.yml'))


def get_yaml_files(manifests_folder_path: Path, recursive=False) -> List[str]:
    yaml_files = []
    if manifests_folder_path is not None:
        if recursive:
            yaml_files = [
                f
                for f in glob.iglob(os.path.join(manifests_folder_path, '**/*'), recursive=True)
                if is_yaml_file(f)
            ]
        else:
            yaml_files = [f for f in glob.iglob(os.path.join(manifests_folder_path, '*')) if is_yaml_file(f)]
    return yaml_files


def subst_env_vars(variables, text):
    def repl(matchobj):
        variable = matchobj.group(1)
        if variable in variables:
            return os.getenv(variable)
        return matchobj.group(0)

    # TODO: need fix regexp, when $$aaaa (with two dollar signs) won't be replaced, dut $aaaa$bbbb will
    return re.sub(r'\${?([a-zA-Z_][a-zA-Z0-9_]*)}?', repl, text)


def prepare_manifest_files(files: List[str]):
    prepared_files = []
    dest_path = tempfile.mkdtemp()
    variables = list(os.environ.keys())
    for file_path in files:
        file_name = os.path.basename(file_path)

        with open(file_path, 'r', encoding='utf-8') as in_manifest:
            # TODO: it will be a problem when filenames in files have same names
            # for example: stage/ing/obj.yml and stage/svc/obj.yml, in result will be only one file
            new_file_path = os.path.join(dest_path, file_name)
            with open(new_file_path, 'a', encoding='utf-8') as out_manifest:
                for line in in_manifest:
                    prepared_line = subst_env_vars(variables, line)
                    out_manifest.write(prepared_line)
                prepared_files.append(new_file_path)
    return prepared_files


def add_annotations(file_paths: List[str], dest_path: Path) -> List[str]:
    annotations = k8s.get_annotations()
    prepared_files = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_name = os.path.basename(file_path)
            new_file_path = os.path.join(dest_path, file_name)
            manifest = yaml.safe_load_all(file)
            with open(new_file_path, 'a', encoding='utf-8') as out_manifest:
                k8s_dict_list = []
                for k8s_object_dict in manifest:
                    k8s_object = K8sObject(object_as_dict=k8s_object_dict)
                    k8s_object.add_annotations(annotations=annotations)
                    k8s_dict_list.append(k8s_object.object_as_dict)
                k8s_object_yaml = yaml.safe_dump_all(k8s_dict_list)
                out_manifest.write(k8s_object_yaml)
                prepared_files.append(new_file_path)
    return prepared_files


def concat_files(filename: Path, read_files: List[str]):
    with open(filename, "wb") as outfile:
        for f in read_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())
            outfile.write('\n---\n'.encode('utf-8'))


class OrthodoxDeployer(AbstractDeployer):
    @staticmethod
    def deploy(tmp_path: Path, manifests_path: Path) -> Tuple[str, Path]:
        environment = settings.environment.value

        console.stage("Searching yaml files...")
        yaml_files = get_yaml_files(manifests_path, False)

        if environment is not None:
            yaml_files.extend(get_yaml_files(manifests_path / environment, True))

        console.info("Found yaml files:", console.TAB)
        console.info("\n".join(filename for filename in yaml_files), console.TAB * 2)

        console.stage("Processing found yaml files...")
        prepared_files = prepare_manifest_files(yaml_files)
        add_annotations(prepared_files, tmp_path)
        manifests_filename = tmp_path / "manifests.yaml"
        concat_files(manifests_filename, prepared_files)
        manifest_content = manifests_filename.read_text()
        return manifest_content, manifests_filename
