import logging
import os
from pathlib import Path

import psutil


logger = logging.getLogger(__name__)


class PidFile:
    def __init__(self, file: Path | str, *, verbose: bool = False):
        self.path = Path(file)
        self.verbose = verbose

    def write(self) -> None:
        p = psutil.Process(os.getpid())
        ctime = int(p.create_time())
        self.path.write_text(f"{p.pid} {ctime}")
        if self.verbose:
            logger.info(f"Wrote PID file with pid={p.pid} ctime={ctime}")

    def is_alive(self) -> int | None:
        try:
            pid_str, ctime_str = self.path.read_text().split()
            pid, ctime = int(pid_str), int(ctime_str)
        except (FileNotFoundError, ValueError):
            return None

        try:
            p = psutil.Process(pid)
            if int(p.create_time()) == ctime:
                return pid
            return None

        except psutil.NoSuchProcess:
            return None

    def send_kill_if_alive(self, stop_file_path: Path | str) -> bool:
        pid = self.is_alive()
        if pid is None:
            if self.verbose:
                logger.debug(
                    f'Process from "{self.path}" not alive, removing PID file')
            self.remove()
            return False

        stop_file_path = Path(stop_file_path)
        stop_file_path.touch(exist_ok=True)
        if self.verbose:
            logger.info(
                f'Sent stop signal to pid={pid} '
                f'(stop-file created: "{stop_file_path}")'
            )
        return True

    def remove(self) -> None:
        try:
            self.path.unlink()
            if self.verbose:
                logger.info(f'Removed PID file "{self.path}"')
        except FileNotFoundError:
            if self.verbose:
                logger.debug(f'PID file "{self.path}" already removed')
