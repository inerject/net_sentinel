import logging
import os
import asyncio
import subprocess
import time
import winsound

from dotenv import dotenv_values

import log
import config
from pid_file import PidFile
from strings import PROJ_FULL_NAME


logger = logging.getLogger()

stop_event = asyncio.Event()
ssh_proc = None


#
async def runner(settings):
    await asyncio.gather(
        main(settings),
        check_stop_event(),
    )


async def main(settings):
    while not stop_event.is_set():
        await ssh_dynamic_forwarding(
            settings['DEST'],
            settings['DEST_USERNAME'],
            settings['IDENTITY_FILE'],
            settings['LOCAL_PORT'],
        )
        await asyncio.sleep(1)


async def check_stop_event():
    while not stop_event.is_set():
        await asyncio.sleep(0.1)
        if config.STOP_FILE_PATH.exists():
            stop_event.set()

    if ssh_proc:
        ssh_proc.terminate()


#
async def ssh_dynamic_forwarding(
    dest, dest_username, identity_file,
    local_port, *, local_host='localhost',
):
    logger.info('Start ssh forwarding')
    args = [
        '-N',
        '-o', 'ServerAliveCountMax=3',
        '-o', 'ServerAliveInterval=5',
        '-o', 'ExitOnForwardFailure=yes',
        '-i', f'{identity_file}',
        '-D', f'{local_host}:{local_port}', f'{dest_username}@{dest}',
    ]

    global ssh_proc
    ssh_proc = await asyncio.create_subprocess_exec(
        'ssh', *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW,
        env={**os.environ, "LANG": "C", "LC_ALL": "C"},
    )
    try:
        await asyncio.gather(
            catch_output(ssh_proc.stdout, logging.INFO),
            catch_output(ssh_proc.stderr, logging.DEBUG),
        )
    finally:
        if ssh_proc.returncode is None:
            ssh_proc.terminate()
            try:
                await asyncio.wait_for(ssh_proc.wait(), timeout=3)
            except asyncio.TimeoutError:
                ssh_proc.kill()
                await ssh_proc.wait()

    logger.info('ssh forwarding finished')


async def catch_output(stream, default_level=logging.INFO):
    while True:
        data = await stream.readline()
        if not data:
            return

        line = data.decode(errors='replace').rstrip().lower()

        if any(word in line for word in ("error", "failed", "fatal")):
            logger.error(line)
        elif any(word in line for word in ("warn", "deprecated")):
            logger.warning(line)
        else:
            logger.log(default_level, line)


#
def wait_old_process_finished():
    if config.STOP_FILE_PATH.exists():
        for _ in range(50):  # ~5 s
            if not config.STOP_FILE_PATH.exists():
                break
            time.sleep(0.1)


#
if __name__ == '__main__':
    log.init()

    #
    pid_file = PidFile(config.PID_FILE_PATH)
    pid_file.send_kill_if_alive(config.STOP_FILE_PATH)
    wait_old_process_finished()

    #
    logger.info(f"{PROJ_FULL_NAME} started")
    pid_file.write()

    #
    try:
        if not config.ENV_FILE_PATH.exists():
            raise FileNotFoundError(
                f'.env file not found at "{config.ENV_FILE_PATH}"')

        settings = dotenv_values(config.ENV_FILE_PATH)
        missing = [k for k in config.REQUIRED_KEYS if k not in settings]
        if missing:
            raise RuntimeError(f"Missing required environment keys: {missing}")

    except Exception as e:
        logger.critical(f"Configuration error: {e}")
        pid_file.remove()
        config.STOP_FILE_PATH.unlink(missing_ok=True)
        winsound.MessageBeep(winsound.MB_ICONHAND)
        raise

    #
    kb_listener = None
    if __debug__:
        from pynput import keyboard

        kb_listener = keyboard.GlobalHotKeys({
            config.DEBUG_INTERRUPT_GLOBAL_HOTKEY: stop_event.set,
        }).start()

    try:
        asyncio.run(runner(settings))
    except KeyboardInterrupt:
        logger.info('Interrupted!')
    finally:
        if kb_listener:
            kb_listener.stop()
        pid_file.remove()
        config.STOP_FILE_PATH.unlink(missing_ok=True)

        logger.info(f"{PROJ_FULL_NAME} finished")
        winsound.MessageBeep(winsound.MB_OK)

    # curl --socks5 127.0.0.1:1080 ifconfig.me
