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


setup_fs()
del setup_fs
