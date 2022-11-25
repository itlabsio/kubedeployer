from kubedeployer import console


def test_write_single_line_message(capsys):
    console.write("example of ")
    console.write("single line message")

    captured = capsys.readouterr()
    assert captured.out == "example of single line message"


def test_write_multiline_message(capsys):
    console.writeln("example of")
    console.writeln("multiline message")

    captured = capsys.readouterr()
    assert captured.out == (
        "example of\n"
        "multiline message\n"
    )
