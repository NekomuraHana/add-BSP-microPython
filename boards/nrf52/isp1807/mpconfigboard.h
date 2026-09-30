/*
 * MicroPython board definition for the Switch Science ISP1807 Breakout
 * (SSCI-064545 / SSCI-061001 family).
 *
 * The board uses an Insight SiP ISP1807-LR (nRF52840) module and exposes
 * native USB directly from the module.
 */

#define MICROPY_HW_BOARD_NAME        "SSCI ISP1807 Breakout"
#define MICROPY_HW_MCU_NAME          "NRF52840"

// Enable native emitters.
#define MICROPY_EMIT_THUMB           (1)
#define MICROPY_EMIT_INLINE_THUMB    (1)

// Optional modules.
#define MICROPY_PY_ERRNO             (1)
#define MICROPY_PY_HASHLIB           (1)

// Peripherals.
#define MICROPY_PY_MACHINE_UART      (1)
#define MICROPY_PY_MACHINE_HW_PWM    (1)
#define MICROPY_PY_MACHINE_RTCOUNTER (1)
#define MICROPY_PY_MACHINE_I2C       (1)
#define MICROPY_PY_MACHINE_ADC       (1)
#define MICROPY_PY_MACHINE_TEMP      (1)

#define MICROPY_HW_ENABLE_RNG        (1)

// Console policy:
// - REPL is exposed over the board's native USB CDC interface.
// - Hardware UART remains available through machine.UART, but is not a REPL.
#define MICROPY_HW_ENABLE_USBDEV     (1)
#define MICROPY_HW_USB_CDC           (1)
#define MICROPY_HW_ENABLE_UART_REPL  (0)

// Keep the application CDC identity distinct from the pre-installed
// Switch Science / Adafruit-compatible bootloader. This makes it obvious
// whether the running device is the MicroPython application or the bootloader.
#define MICROPY_HW_USB_VID                 (0xf055)
#define MICROPY_HW_USB_PID                 (0x9802)
#define MICROPY_HW_USB_MANUFACTURER_STRING "MicroPython"
#define MICROPY_HW_USB_PRODUCT_FS_STRING   "ISP1807 MicroPython REPL"
#define MICROPY_HW_USB_CDC_INTERFACE_STRING "MicroPython REPL"

// On-board green user LED: P0.06, active-low.
#define MICROPY_HW_HAS_LED           (1)
#define MICROPY_HW_LED_COUNT         (1)
#define MICROPY_HW_LED_PULLUP        (1)
#define MICROPY_HW_LED1              (6)
#define HELP_TEXT_BOARD_LED          "1"

// UART mapping follows the Switch Science ISP1807 Breakout board definition.
// RX=P0.25, TX=P0.11. Hardware flow control is not wired on the board.
#define MICROPY_HW_UART1_RX          (25)
#define MICROPY_HW_UART1_TX          (11)
#define MICROPY_HW_UART1_HWFC        (0)

// SPI0 mapping follows the Switch Science ISP1807 Breakout board definition.
// SCK=P0.14, MOSI=P0.10, MISO=P0.12.
#define MICROPY_HW_SPI0_NAME         "SPI0"
#define MICROPY_HW_SPI0_SCK          (14)
#define MICROPY_HW_SPI0_MOSI         (10)
#define MICROPY_HW_SPI0_MISO         (12)

#define MICROPY_HW_PWM0_NAME         "PWM0"
#define MICROPY_HW_PWM1_NAME         "PWM1"
#define MICROPY_HW_PWM2_NAME         "PWM2"
