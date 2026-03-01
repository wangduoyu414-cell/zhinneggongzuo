from hello_graph import run


def test_run_with_name() -> None:
    assert run("Codex") == "Hello, Codex!"


def test_run_with_blank_name() -> None:
    assert run("") == "Hello, world!"
