import logging
from pathlib import Path

import PyInstaller.__main__

from strings import PROJ_NAME, PROJ_FULL_NAME
from utils import caller_path


logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.INFO,
)

#
curr_dir_path = caller_path().parent


def build(target: Path, console: bool):
    PyInstaller.__main__.run([
        str(target),
        '--distpath', str(curr_dir_path / f'../dist/{PROJ_FULL_NAME}'),
        '--workpath', str(curr_dir_path / '../build'),
        '--specpath', str(curr_dir_path / '../build'),
        '--clean',
        '--onefile',
        '--console' if console else '--noconsole',
        '--optimize', '1',
    ])


build(curr_dir_path / f'{PROJ_NAME}.py', False)
build(curr_dir_path / f'stop_{PROJ_NAME}.py', True)
