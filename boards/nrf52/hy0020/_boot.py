def setup_console():
    import os
    from machine import Pin

    # P0.12 is the initial development-mode selector:
    #   LOW  -> keep UART0 attached to the REPL at 115200 bps
    #   HIGH -> detach/deinit the REPL UART so machine.UART(0) is available
    #           to boot.py/main.py with user-selected TX/RX pins.
    mode = Pin(12, Pin.IN, Pin.PULL_UP)
    if mode.value():
        uart = os.dupterm(None)
        if uart is not None:
            try:
                uart.deinit()
            except:
                pass


def setup_fs():
    import gc
    import vfs
    import sys
    import nrf
    import os

    fs_type = getattr(vfs, "VfsLfs2", getattr(vfs, "VfsLfs1", getattr(vfs, "VfsFat", None)))

    try:
        bdev = nrf.Flash()
    except:
        return

    try:
        vfs.mount(bdev, "/")
    except:
        if fs_type is None:
            return
        try:
            fs_type.mkfs(bdev)
            vfs.mount(bdev, "/")
        except:
            return

    os.chdir("/")
    sys.path.append("/")
    sys.path.append("/lib")
    gc.collect()


setup_console()
setup_fs()
del setup_console
del setup_fs
