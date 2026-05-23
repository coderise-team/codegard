"""
Isolated code execution in a fresh Docker container.

Each call to run_in_sandbox spins up a new container, injects the solution
via put_archive, executes it with exec_create/exec_start, reads output, then
removes the container. Containers are never reused between submissions.
"""

import io
import logging
import socket as _socket
import struct
import tarfile
import time
from dataclasses import dataclass

import docker
import docker.errors

logger = logging.getLogger(__name__)

_PYTHON_IMAGE = "python:3.13-slim"
_MEM_LIMIT = "128m"
_CPU_QUOTA = 25_000
_CPU_PERIOD = 100_000
_TIMEOUT_BUFFER_SEC = 2.0
_FRAME_HEADER_SIZE = 8


@dataclass
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    oom_killed: bool
    execution_time_ms: int


_docker_client: docker.DockerClient | None = None


def _get_docker_client() -> docker.DockerClient:
    global _docker_client
    if _docker_client is None:
        _docker_client = docker.from_env()
    return _docker_client


def _make_tar(filename: str, content: bytes) -> io.BytesIO:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        info = tarfile.TarInfo(name=filename)
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))
    buf.seek(0)
    return buf


def _read_exec_output(
    raw_sock: _socket.socket, timeout_sec: float
) -> tuple[bytes, bytes, bool]:
    """
    Read Docker multiplexed exec output (stdout + stderr).
    Returns (stdout_bytes, stderr_bytes, timed_out).

    Docker frame format: [stream_type(1)][padding(3)][payload_size(4)][payload]
    stream_type: 1 = stdout, 2 = stderr
    """
    raw_sock.settimeout(timeout_sec)
    stdout: list[bytes] = []
    stderr: list[bytes] = []

    try:
        while True:
            header = b""
            while len(header) < _FRAME_HEADER_SIZE:
                chunk = raw_sock.recv(_FRAME_HEADER_SIZE - len(header))
                if not chunk:
                    return b"".join(stdout), b"".join(stderr), False
                header += chunk

            stream_type = header[0]
            payload_size = struct.unpack(">I", header[4:8])[0]

            payload = b""
            while len(payload) < payload_size:
                chunk = raw_sock.recv(payload_size - len(payload))
                if not chunk:
                    break
                payload += chunk

            if stream_type == 1:
                stdout.append(payload)
            elif stream_type == 2:
                stderr.append(payload)

    except _socket.timeout:
        return b"".join(stdout), b"".join(stderr), True


def run_in_sandbox(
    code: str,
    stdin: str,
    time_limit_ms: int,
    language: str = "python",
) -> SandboxResult:
    """
    Execute user code in an isolated Docker container.
    Always spins up a fresh container and removes it after execution.
    """
    if language != "python":
        raise NotImplementedError(f"Language {language!r} is not supported")

    client = _get_docker_client()
    timeout_sec = time_limit_ms / 1000
    container = None

    try:
        container = client.containers.run(
            image=_PYTHON_IMAGE,
            command=["sleep", "30"],
            mem_limit=_MEM_LIMIT,
            cpu_quota=_CPU_QUOTA,
            cpu_period=_CPU_PERIOD,
            network_disabled=True,
            read_only=True,
            tmpfs={"/tmp": "size=64m"},
            pids_limit=20,
            user="nobody",
            stdin_open=True,
            detach=True,
            remove=False,
        )

        container.put_archive("/tmp", _make_tar("solution.py", code.encode()))

        exec_id = client.api.exec_create(
            container.id,
            ["python", "/tmp/solution.py"],
            stdin=True,
            stdout=True,
            stderr=True,
        )["Id"]

        sock = client.api.exec_start(exec_id, socket=True)
        raw = sock._sock

        start_ms = int(time.monotonic() * 1000)

        if stdin:
            raw.sendall(stdin.encode())
        try:
            raw.shutdown(_socket.SHUT_WR)
        except OSError:
            pass

        stdout_bytes, stderr_bytes, timed_out = _read_exec_output(
            raw, timeout_sec + _TIMEOUT_BUFFER_SEC
        )
        elapsed_ms = int(time.monotonic() * 1000) - start_ms

        try:
            raw.close()
        except OSError:
            pass

        if timed_out:
            try:
                container.kill()
            except docker.errors.APIError:
                pass
            return SandboxResult(
                stdout="",
                stderr="",
                exit_code=-1,
                timed_out=True,
                oom_killed=False,
                execution_time_ms=elapsed_ms,
            )

        exec_info = client.api.exec_inspect(exec_id)
        exit_code = exec_info.get("ExitCode")
        if exit_code is None:
            exit_code = -1

        container.reload()
        oom_killed = container.attrs["State"].get("OOMKilled", False)

        return SandboxResult(
            stdout=stdout_bytes.decode(errors="replace"),
            stderr=stderr_bytes.decode(errors="replace"),
            exit_code=exit_code,
            timed_out=False,
            oom_killed=oom_killed,
            execution_time_ms=elapsed_ms,
        )

    finally:
        if container is not None:
            try:
                container.remove(force=True)
            except docker.errors.APIError as e:
                logger.warning("Failed to remove container %s: %s", container.id, e)
