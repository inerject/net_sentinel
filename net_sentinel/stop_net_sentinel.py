if __name__ == "__main__":
    import logging
    import sys

    from pid_file import PidFile
    from config import PID_FILE_PATH, STOP_FILE_PATH

    #
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.INFO,
    )

    pid_file = PidFile(PID_FILE_PATH, verbose=True)
    code = 0 if pid_file.send_kill_if_alive(STOP_FILE_PATH) else 1

    input("Press Enter to exit...")
    sys.exit(code)
