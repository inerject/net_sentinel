import sys
from pathlib import Path
from functools import lru_cache
import inspect

from strings import PROJ_NAME


#
def get_user_dir() -> Path:
    return get_user_data_path(PROJ_NAME)


#
def is_dev_mode() -> bool:
    return not getattr(sys, "frozen", False)


def is_pyinstaller_onefile() -> bool:
    if is_dev_mode():
        return False

    exe_dir = Path(sys.executable).parent
    meipass_dir = Path(getattr(sys, "_MEIPASS", ""))
    return meipass_dir.exists() and (meipass_dir != exe_dir)


@lru_cache
def get_user_data_path(proj_name: str, *, home_dir: str = 'py_app_data') -> Path:
    if is_pyinstaller_onefile():
        base_path = Path(sys.executable).parent
    elif home_dir:
        base_path = Path.home() / home_dir
    else:
        base_path = Path.home()

    user_data_path = base_path / proj_name
    user_data_path.mkdir(parents=True, exist_ok=True)
    return user_data_path


#
def caller_path() -> Path:
    """Return the absolute path to the file from which this function was called."""
    frame = inspect.stack()[1]  # caller frame
    return Path(frame.filename).resolve()
