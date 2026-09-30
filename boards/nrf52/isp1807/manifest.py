# Use a board-local _boot.py so the internal filesystem is mounted at /.
module("_boot.py", base_path="$(BOARD_DIR)", opt=3)

# Keep the same default frozen package set as the upstream nRF manifest.
include("$(MPY_DIR)/extmod/asyncio")
