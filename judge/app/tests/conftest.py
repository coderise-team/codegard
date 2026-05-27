import struct
from unittest.mock import MagicMock

from app.core.sandbox import SandboxResult


def make_sandbox_result(**overrides) -> SandboxResult:
    defaults = {
        "stdout": "",
        "stderr": "",
        "exit_code": 0,
        "timed_out": False,
        "oom_killed": False,
        "execution_time_ms": 50,
    }
    return SandboxResult(**{**defaults, **overrides})


def build_docker_frames(stdout: bytes = b"", stderr: bytes = b"") -> bytes:
    """Build a Docker multiplexed stream payload for use in recv() mocks."""
    frames = b""
    if stdout:
        frames += struct.pack(">BBBBI", 1, 0, 0, 0, len(stdout)) + stdout
    if stderr:
        frames += struct.pack(">BBBBI", 2, 0, 0, 0, len(stderr)) + stderr
    return frames


def make_recv_fn(data: bytes):
    """Return a recv() side_effect that streams `data` in chunks then returns EOF."""
    pos = [0]

    def recv(n: int) -> bytes:
        if pos[0] >= len(data):
            return b""
        chunk = data[pos[0] : pos[0] + n]
        pos[0] += len(chunk)
        return chunk

    return recv


def make_mock_docker_client(
    stdout: bytes = b"",
    stderr: bytes = b"",
    exit_code: int = 0,
    oom_killed: bool = False,
) -> MagicMock:
    """Build a fully mocked Docker client for sandbox unit tests."""
    client = MagicMock()

    container = MagicMock()
    container.id = "test-container-id"
    container.attrs = {"State": {"OOMKilled": oom_killed}}
    client.containers.run.return_value = container

    client.api.exec_create.return_value = {"Id": "test-exec-id"}
    client.api.exec_inspect.return_value = {"ExitCode": exit_code}

    frames = build_docker_frames(stdout, stderr)
    raw_sock = MagicMock()
    raw_sock.recv.side_effect = make_recv_fn(frames)

    sock_wrapper = MagicMock()
    sock_wrapper._sock = raw_sock
    client.api.exec_start.return_value = sock_wrapper

    return client
