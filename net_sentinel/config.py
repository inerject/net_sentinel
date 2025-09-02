from utils import get_user_dir
from strings import PROJ_NAME


DEBUG_INTERRUPT_GLOBAL_HOTKEY = '<ctrl>+<alt>+<shift>+6'

ENV_FILE_PATH = get_user_dir() / '.env'
REQUIRED_KEYS = ('DEST', 'DEST_USERNAME', 'IDENTITY_FILE', 'LOCAL_PORT')

PID_FILE_NAME = f'{PROJ_NAME}.pid'
PID_FILE_PATH = get_user_dir() / PID_FILE_NAME

STOP_FILE_PATH = get_user_dir() / 'STOP_SIG'
