# Board-local early boot:
# - select UART REPL mode from P0.12
# - mount internal writable flash at /
module("_boot.py", base_path="$(BOARD_DIR)", opt=3)
