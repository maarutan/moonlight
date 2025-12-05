import ctypes
import signal


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
