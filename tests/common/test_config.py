"""Sample test wiring. Edit and copy alongside individual tests on the device.
All GPIO names follow the nRF port mapping; use board-specific overrides.
"""
GPIO_OUTPUT_PIN = "P0_06"
GPIO_INPUT_PIN = "P1_06"
UART_ID = 0
UART_TX_PIN = 8
UART_RX_PIN = 7
UART_BAUD = 115200
I2C_ID = 0
I2C_SCL_PIN = 26
I2C_SDA_PIN = 14
I2C_FREQ = 100000
SPI_ID = 0
SPI_SCK_PIN = 7
SPI_MOSI_PIN = 5
SPI_MISO_PIN = 8
BLE_TARGET_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"  # NUS Primary Service; adjust to your peripheral
