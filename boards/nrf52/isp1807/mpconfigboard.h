/*
 * Initial MicroPython board definition for the Insight SiP ISP1807-LR.
 *
 * The ISP1807-LR is an nRF52840 module. It exposes 46 GPIOs; P0.00 and P0.01
 * are not brought out by the module.
 *
 * UART/SPI pins below are BSP defaults only. They are not fixed by the module
 * hardware and may be changed for a carrier board.
 */

#define MICROPY_HW_BOARD_NAME        "ISP1807-LR"
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

// Native USB is available on D+/D-/VBUS when the carrier exposes it.
#define MICROPY_HW_ENABLE_USBDEV     (1)
#define MICROPY_HW_USB_CDC           (1)

// The module itself has no user LED.
#define MICROPY_HW_HAS_LED           (0)
#define MICROPY_HW_LED_COUNT         (0)

// Default UART mapping for the generic module BSP.
// RX=P0.08, TX=P0.06. Hardware flow control is disabled.
#define MICROPY_HW_UART1_RX          (8)
#define MICROPY_HW_UART1_TX          (6)
#define MICROPY_HW_UART1_HWFC        (0)

// Default SPI0 mapping for the generic module BSP.
// SCK=P1.15, MOSI=P1.13, MISO=P1.14.
#define MICROPY_HW_SPI0_NAME         "SPI0"
#define MICROPY_HW_SPI0_SCK          (47)
#define MICROPY_HW_SPI0_MOSI         (45)
#define MICROPY_HW_SPI0_MISO         (46)

#define MICROPY_HW_PWM0_NAME         "PWM0"
#define MICROPY_HW_PWM1_NAME         "PWM1"
#define MICROPY_HW_PWM2_NAME         "PWM2"
