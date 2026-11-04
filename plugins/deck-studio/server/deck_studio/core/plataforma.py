"""What differs between Windows and Linux, in one place: byte locks on a file, stopping a process tree, the flags of a
child process and the app's data dir. On Windows everything behaves as before the Linux port (2026-11-04)."""
import os
import signal
import subprocess
import sys
from pathlib import Path

WINDOWS = sys.platform == "win32"
if WINDOWS:
    import msvcrt

NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)  # creationflags: no console window for a child on Windows
O_BINARY = getattr(os, "O_BINARY", 0)
# a child that kill_tree may stop: on POSIX it leads a process group of its own, which kill_tree stops whole
NEW_GROUP = {} if WINDOWS else {"start_new_session": True}


def lock_byte(fd, wait=False):
    """Lock 1 byte of the file at fd's current position, for this process (the OS drops it when the process ends).
    Without wait, OSError when another process holds it; with wait, Windows tries for 10 s, POSIX waits."""
    if WINDOWS:
        msvcrt.locking(fd, msvcrt.LK_LOCK if wait else msvcrt.LK_NBLCK, 1)
    else:
        os.lockf(fd, os.F_LOCK if wait else os.F_TLOCK, 1)


def unlock_byte(fd):
    """Unlock the byte at fd's current position."""
    if WINDOWS:
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    else:
        os.lockf(fd, os.F_ULOCK, 1)


def byte_locked(fd):
    """Whether another process holds the byte at fd's current position, without ever taking it: on Windows a read
    of a locked byte fails; POSIX locks are advisory, so they are tested (F_TEST)."""
    if WINDOWS:
        try:
            os.read(fd, 1)
            return False
        except PermissionError:
            return True
    try:
        os.lockf(fd, os.F_TEST, 1)
        return False
    except OSError:
        return True


def kill_tree(pid):
    """Stop a process and every process it started. On POSIX the process must have been started with NEW_GROUP."""
    if WINDOWS:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True)
        return
    try:
        os.killpg(os.getpgid(pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def data_home():
    """The app's own data dir: %LOCALAPPDATA%\\deck-studio on Windows, $XDG_DATA_HOME/deck-studio (by default
    ~/.local/share/deck-studio) elsewhere."""
    if WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", ".")) / "deck-studio"
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "deck-studio"
