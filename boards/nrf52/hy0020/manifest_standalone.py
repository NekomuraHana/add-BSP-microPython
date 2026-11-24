# HY0020 bootloader-free firmware: freeze matching build variant metadata.
module("_boot.py", base_path="$(BOARD_DIR)", opt=3)
module("board_info.py", base_path="$(BOARD_DIR)", opt=3)
module("_hy0020_variant.py", base_path="$(BOARD_DIR)/variant_standalone", opt=3)
