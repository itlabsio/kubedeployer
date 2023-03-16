from kubedeployer.deploy import print_diff_manifests


def test_success_printing_diff_manifests(capsys, data_path):
    print_diff_manifests(data_path / "manifests/manifests.yaml")

    captured = capsys.readouterr()
    assert "+kind: Service" in captured.out
    assert "+kind: Deployment" in captured.out
    assert captured.err == ""


def test_failure_printing_diff_manifests(capsys, data_path):
    print_diff_manifests(data_path / "non-exist-manifest.yaml")

    captured = capsys.readouterr()
    assert "non-exist-manifest.yaml" in captured.out
    assert "does not exist" in captured.out
    assert captured.err == ""

