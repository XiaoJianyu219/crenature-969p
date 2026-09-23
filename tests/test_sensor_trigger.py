import sensor_trigger as st


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_cooldown_blocks_repeated_triggers():
    clock = FakeClock()
    cd = st.Cooldown(10, clock=clock)
    assert cd.ready()
    clock.now = 9.9
    assert not cd.ready()
    clock.now = 10.0
    assert cd.ready()
    clock.now = 15.0
    assert not cd.ready()


def test_ssh_command_keeps_user_with_space_as_one_argument():
    cmd = st.build_ssh_command("exhibit user", "192.168.0.14", "crenature")
    assert cmd[0] == "ssh"
    assert "BatchMode=yes" in cmd
    assert cmd[-2] == "exhibit user@192.168.0.14"
    assert cmd[-1] == 'schtasks /run /tn "crenature"'


def test_trigger_runs_ssh_once_within_cooldown(monkeypatch):
    calls = []

    class Result:
        returncode, stdout, stderr = 0, "SUCCESS", ""

    monkeypatch.setattr(st.subprocess, "run", lambda cmd, **kw: calls.append(cmd) or Result())
    args = st.parse_args(["--host", "10.0.0.2", "--user", "u", "--task", "t"])
    clock = FakeClock()
    trigger = st.make_trigger(args, st.Cooldown(args.cooldown, clock=clock))
    trigger()
    trigger()
    clock.now = 11
    trigger()
    assert len(calls) == 2


def test_env_defaults(monkeypatch):
    monkeypatch.setenv("CRENATURE_HOST", "10.0.0.9")
    monkeypatch.setenv("CRENATURE_USER", "someone")
    args = st.parse_args([])
    assert (args.host, args.user, args.task, args.pin, args.cooldown) == ("10.0.0.9", "someone", "crenature", 17, 10.0)
