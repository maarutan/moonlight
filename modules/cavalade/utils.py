import os
import time
import signal
import ctypes

from pathlib import Path
from loguru import logger
from utils.constants import Const


def set_death_signal():
    """Ensure cava dies with the parent process."""
    libc = ctypes.CDLL("libc.so.6")
    PR_SET_PDEATHSIG = 1
    libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM)  # pyright: ignore[reportFunctionMemberAccess]]


class AttributeDict(dict):
    def __getattr__(self, attr):
        return self.get(attr, 3)

    def __setattr__(self, attr, value):
        self[attr] = value


def kill_all_cava_pids(grace_period: float = 1.0):
    """
    Read PIDs from Const.CAVA_PIDS (one per line), dedupe, send SIGTERM,
    wait brief grace_period, then SIGKILL remaining. Finally remove the file.
    """
    p = Path(Const.CAVA_PIDS)
    if not p.exists():
        return

    try:
        raw = p.read_text(encoding="utf-8")
    except Exception:
        logger.exception("Failed to read cava pid file")
        return

    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    seen = set()
    pids = []
    for ln in lines:
        try:
            pid = int(ln)
            if pid > 0 and pid not in seen:
                seen.add(pid)
                pids.append(pid)
        except Exception:
            continue

    if not pids:
        try:
            p.unlink()
        except Exception:
            logger.exception("Failed to delete empty cava pid file")
        return

    # 1) send SIGTERM
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            logger.debug(f"Sent SIGTERM to cava pid {pid}")
        except ProcessLookupError:
            logger.debug(f"cava pid {pid} not found")
        except PermissionError:
            logger.warning(f"No permission to signal pid {pid}")
        except Exception:
            logger.exception(f"Failed to send SIGTERM to cava pid {pid}")

    # 2) wait briefly for processes to exit
    deadline = time.time() + grace_period
    alive = list(pids)
    while time.time() < deadline and alive:
        remaining = []
        for pid in alive:
            try:
                os.kill(pid, 0)  # check existence
                remaining.append(pid)
            except ProcessLookupError:
                continue
            except PermissionError:
                remaining.append(pid)
            except Exception:
                remaining.append(pid)
        if not remaining:
            break
        time.sleep(0.1)
        alive = remaining

    # 3) force kill remaining
    for pid in alive:
        try:
            os.kill(pid, signal.SIGKILL)
            logger.debug(f"Sent SIGKILL to cava pid {pid}")
        except ProcessLookupError:
            logger.debug(f"cava pid {pid} already exited before SIGKILL")
        except PermissionError:
            logger.warning(f"No permission to SIGKILL pid {pid}")
        except Exception:
            logger.exception(f"Failed to send SIGKILL to cava pid {pid}")

    # 4) remove pid file
    try:
        p.unlink()
    except FileNotFoundError:
        pass
    except Exception:
        logger.exception("Failed to delete cava pid file")
