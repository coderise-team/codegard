import socket as _socket

import docker.errors
import pytest

from app.core.sandbox import run_in_sandbox

from .conftest import make_mock_docker_client


def _patch(monkeypatch, client):
    monkeypatch.setattr("app.core.sandbox._get_docker_client", lambda: client)


class TestRunInSandbox:
    def test_successful_execution_returns_stdout(self, monkeypatch):
        client = make_mock_docker_client(stdout=b"42\n")
        _patch(monkeypatch, client)

        result = run_in_sandbox("print(42)", "", 1000)

        assert result.stdout == "42\n"
        assert result.exit_code == 0
        assert not result.timed_out
        assert not result.oom_killed

    def test_stderr_captured_separately(self, monkeypatch):
        client = make_mock_docker_client(
            stderr=b"ZeroDivisionError: division by zero\n", exit_code=1
        )
        _patch(monkeypatch, client)

        result = run_in_sandbox("1/0", "", 1000)

        assert result.exit_code == 1
        assert "ZeroDivisionError" in result.stderr

    def test_container_removed_on_success(self, monkeypatch):
        client = make_mock_docker_client(stdout=b"ok\n")
        _patch(monkeypatch, client)

        run_in_sandbox("print('ok')", "", 1000)

        client.containers.run.return_value.remove.assert_called_once_with(force=True)

    def test_timeout_sets_timed_out_flag(self, monkeypatch):
        client = make_mock_docker_client()
        client.api.exec_start.return_value._sock.recv.side_effect = _socket.timeout
        _patch(monkeypatch, client)

        result = run_in_sandbox("while True: pass", "", 100)

        assert result.timed_out
        assert result.exit_code == -1

    def test_timeout_kills_container(self, monkeypatch):
        client = make_mock_docker_client()
        client.api.exec_start.return_value._sock.recv.side_effect = _socket.timeout
        _patch(monkeypatch, client)

        run_in_sandbox("while True: pass", "", 100)

        client.containers.run.return_value.kill.assert_called_once()

    def test_container_removed_after_timeout(self, monkeypatch):
        client = make_mock_docker_client()
        client.api.exec_start.return_value._sock.recv.side_effect = _socket.timeout
        _patch(monkeypatch, client)

        run_in_sandbox("while True: pass", "", 100)

        client.containers.run.return_value.remove.assert_called_once_with(force=True)

    def test_kill_api_error_swallowed_on_timeout(self, monkeypatch):
        client = make_mock_docker_client()
        client.api.exec_start.return_value._sock.recv.side_effect = _socket.timeout
        client.containers.run.return_value.kill.side_effect = docker.errors.APIError(
            "container already stopped"
        )
        _patch(monkeypatch, client)

        result = run_in_sandbox("pass", "", 100)

        assert result.timed_out  # Did not raise

    def test_oom_killed_detected(self, monkeypatch):
        client = make_mock_docker_client(exit_code=137, oom_killed=True)
        _patch(monkeypatch, client)

        result = run_in_sandbox("x = b'A' * (200 * 2**20)", "", 5000)

        assert result.oom_killed
        assert not result.timed_out

    def test_resource_limits_applied(self, monkeypatch):
        client = make_mock_docker_client()
        _patch(monkeypatch, client)

        run_in_sandbox("pass", "", 1000)

        kwargs = client.containers.run.call_args.kwargs
        assert kwargs["mem_limit"] == "128m"
        assert kwargs["cpu_quota"] == 25_000
        assert kwargs["cpu_period"] == 100_000
        assert kwargs["network_disabled"] is True
        assert kwargs["read_only"] is True
        assert kwargs["pids_limit"] == 20

    def test_stdin_sent_to_container(self, monkeypatch):
        client = make_mock_docker_client()
        _patch(monkeypatch, client)

        run_in_sandbox("x = input()", "hello", 1000)

        raw_sock = client.api.exec_start.return_value._sock
        raw_sock.sendall.assert_called_once_with(b"hello")

    def test_empty_stdin_not_sent(self, monkeypatch):
        client = make_mock_docker_client()
        _patch(monkeypatch, client)

        run_in_sandbox("pass", "", 1000)

        raw_sock = client.api.exec_start.return_value._sock
        raw_sock.sendall.assert_not_called()

    def test_unsupported_language_raises(self, monkeypatch):
        client = make_mock_docker_client()
        _patch(monkeypatch, client)

        with pytest.raises(NotImplementedError):
            run_in_sandbox("print(1)", "", 1000, language="cpp")

    def test_remove_api_error_is_logged_not_raised(self, monkeypatch):
        client = make_mock_docker_client()
        client.containers.run.return_value.remove.side_effect = docker.errors.APIError(
            "remove failed"
        )
        _patch(monkeypatch, client)

        run_in_sandbox("pass", "", 1000)  # Must not raise
