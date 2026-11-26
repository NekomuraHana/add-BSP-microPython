"""Persist the latest uncaught main.py exception in user-code mode only.

Called by the native pyexec exception path. Never raise a secondary exception:
filesystem/flash failures must not turn an application error into a boot loop.
"""

def log_exception(exc):
    import sys

    if isinstance(exc, (KeyboardInterrupt, SystemExit)):
        return
    try:
        with open("/error.log", "w") as log:
            sys.print_exception(exc, log)
    except Exception:
        # The root filesystem may be read-only, full, or not mounted.
        pass
