/*
 * MicroPython board definition for the Akizuki AE-HY0020-DIP kit.
 *
 * HY0020 uses an nRF52832 (512 KiB Flash / 64 KiB RAM).  The Akizuki kit
 * ships with an Adafruit nRF52 bootloader and exposes UART on P0.06/P0.08.
 */

#define MICROPY_HW_BOARD_NAME        "Akizuki AE-HY0020-DIP"
#define MICROPY_HW_MCU_NAME          "NRF52832"

// Keep the initial BSP close to the upstream PCA10040/FEATHER52 feature set.
#define MICROPY_PY_MACHINE_UART      (1)
#define MICROPY_PY_MACHINE_HW_PWM    (1)
#define MICROPY_PY_MACHINE_RTCOUNTER (1)
#define MICROPY_PY_MACHINE_I2C       (1)
#define MICROPY_PY_MACHINE_SPI       (1)
#define MICROPY_PY_MACHINE_ADC       (1)
#define MICROPY_PY_MACHINE_TEMP      (1)

#define MICROPY_HW_ENABLE_RNG        (1)

// nRF52832 has no native USB peripheral.  The console uses UART0.
#define MICROPY_HW_ENABLE_USBDEV     (0)
#define MICROPY_HW_UART_REPL_SELECT_PIN (12)
#define MICROPY_HW_ENABLE_UART_REPL  (1)
#define MICROPY_HW_UART_REPL         (0)
#define MICROPY_HW_UART_REPL_BAUD    (115200)

// nRF52832 provides one UARTE/UART hardware instance.
#define MICROPY_HW_UART_COUNT        (1)

// Akizuki/Adafruit bootloader wiring.
// MicroPython calls this board-default mapping UART1 internally, while the
// Python-facing peripheral is machine.UART(0).
#define MICROPY_HW_UART1_TX          (6)
#define MICROPY_HW_UART1_RX          (8)
#define MICROPY_HW_UART1_HWFC        (0)

// Build-time SPI defaults (all brought out on the Akizuki carrier).
// Applications can select another supported pin mapping explicitly.
#define MICROPY_HW_SPI0_NAME         "SPI0"
#define MICROPY_HW_SPI0_SCK          (2)
#define MICROPY_HW_SPI0_MOSI         (3)
#define MICROPY_HW_SPI0_MISO         (4)

// There is no on-board user LED on the AE-HY0020-DIP carrier.
#define MICROPY_HW_LED_COUNT         (0)

// The initial build does not reserve a VfsROM partition.  Frozen _boot.py is
// sufficient and leaves more flash for the application and writable LFS.
#define MICROPY_VFS_ROM              (0)

#define MICROPY_HW_PWM0_NAME         "PWM0"
#define MICROPY_HW_PWM1_NAME         "PWM1"
#define MICROPY_HW_PWM2_NAME         "PWM2"
