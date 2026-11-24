# Frozen HY0020 boot support and read-only board metadata.
# Both DFU and standalone firmware expose the same board information API.
module("_boot.py", base_path="$(BOARD_DIR)", opt=3)
module("board_info.py", base_path="$(BOARD_DIR)", opt=3)
module("_hy0020_variant.py", base_path="$(BOARD_DIR)/variant_dfu", opt=3)
