import subprocess


def test_dry_run_with_no_vars_only_with_args(capsys, kube_config, data_path):
    result = subprocess.check_output(
        "kubedeploy "
        "--dry-run "
        f"--project-dir {data_path} "
        f"--environment stage "
        f"--manifest-folder manifests/apps/non-kustomize-app ",
        stderr=subprocess.STDOUT,
        shell=True
    )

    assert "kind: ConfigMap" in str(result)
    assert "Scanning images.." not in str(result)
    assert "Scanning manifests.." not in str(result)
    assert "Apply manifests.." not in str(result)
    assert "Waiting for applying changes.." not in str(result)
