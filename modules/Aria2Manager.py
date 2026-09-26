from __future__ import annotations

import atexit
import importlib.util
import shutil
import subprocess
import sys
import time
from pathlib import Path

import aria2p
from tqdm import tqdm


class Aria2Manager:
    _RPC_HOST = "http://localhost"
    _RPC_PORT = 6801
    _RPC_SECRET = "sisou-local"  # noqa: S105

    _process: subprocess.Popen | None = None
    _api: aria2p.API | None = None

    def __new__(cls):
        raise TypeError(f"{cls.__name__} is not meant to be instantiated; use its classmethods directly.")

    @classmethod
    def _daemon_alive(cls) -> bool:
        return cls._process is not None and cls._process.poll() is None

    @classmethod
    def _start_daemon(cls) -> None:
        aria2c_path = shutil.which("aria2c")

        if aria2c_path:
            cmd = [aria2c_path]
        elif importlib.util.find_spec("aria2c") is not None:
            cmd = [sys.executable, "-m", "aria2c"]
        else:
            raise RuntimeError("aria2c executable or Python module was not found.")

        cmd += [
            "--enable-rpc",
            f"--rpc-listen-port={cls._RPC_PORT}",
            f"--rpc-secret={cls._RPC_SECRET}",
            "--rpc-listen-all=false",
            "--quiet=true",
        ]

        cls._process = subprocess.Popen(  # noqa: S603
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        atexit.register(cls._stop_daemon)

        client = aria2p.Client(host=cls._RPC_HOST, port=cls._RPC_PORT, secret=cls._RPC_SECRET)
        for _ in range(50):  # up to ~5s
            try:
                client.get_version()
            except Exception:
                time.sleep(0.1)
            else:
                return
        raise RuntimeError("Timed out waiting for aria2c's RPC server to start")

    @classmethod
    def _stop_daemon(cls) -> None:
        if cls._daemon_alive():
            assert cls._process is not None  # noqa: S101
            cls._process.terminate()
            try:
                cls._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls._process.kill()
        cls._process = None

    @classmethod
    def get_api(cls) -> aria2p.API:
        """Return a ready aria2p API, starting the shared daemon on first use."""
        if not cls._daemon_alive():
            cls._start_daemon()
            cls._api = None
        if cls._api is None:
            cls._api = aria2p.API(aria2p.Client(host=cls._RPC_HOST, port=cls._RPC_PORT, secret=cls._RPC_SECRET))
        return cls._api

    @classmethod
    def download_torrent(cls, torrent_file, file) -> Path:
        out_dir = Path(f"{torrent_file}.d")
        api = Aria2Manager.get_api()
        download = api.add_torrent(
            str(torrent_file),
            options={"dir": str(out_dir), "seed-time": "0"},
        )
        download.update()

        with tqdm(
            total=download.total_length or None,
            initial=download.completed_length,
            unit="B",
            desc=Path(file).name,
            unit_scale=True,
        ) as pbar:
            try:
                while not download.is_complete:
                    time.sleep(1)
                    previous_completed = download.completed_length
                    download.update()
                    if download.has_failed:
                        raise RuntimeError(f"aria2 failed to download {file}: {download.error_message}")

                    if download.total_length and pbar.total != download.total_length:
                        pbar.total = download.total_length
                        pbar.refresh()

                    pbar.update(download.completed_length - previous_completed)
            except Exception:
                raise
            finally:
                if download is not None:
                    download.remove(force=True, files=False)
        return out_dir
