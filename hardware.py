# 屏幕与触摸硬件初始化
from micropython import const

import fs_driver
import lcd_bus
import lvgl as lv
import machine

import state

_WIDTH = const(240)
_HEIGHT = const(320)
_BL = const(8)
_RST = const(7)
_DC = const(15)

_MOSI = const(17)
_MISO = const(16)
_SCK = const(18)
_HOST = const(1)
_BUFFER_SIZE = const(75000)

_LCD_CS = const(6)
_LCD_FREQ = const(80000000)

_SCL = const(9)
_SDA = const(11)
_TP_FREQ = const(400000)


def init_display_and_touch():
    acc = machine.Pin(40, machine.Pin.OUT)
    acc.value(1)
    backlight = machine.Pin(8, machine.Pin.OUT)
    backlight.value(1)

    spi_bus = machine.SPI.Bus(
        host=_HOST,
        mosi=_MOSI,
        miso=_MISO,
        sck=_SCK,
    )

    display_bus = lcd_bus.SPIBus(
        spi_bus=spi_bus,
        freq=_LCD_FREQ,
        dc=_DC,
        cs=_LCD_CS,
    )
    fb1 = display_bus.allocate_framebuffer(_BUFFER_SIZE, lcd_bus.MEMORY_INTERNAL | lcd_bus.MEMORY_DMA)
    fb2 = display_bus.allocate_framebuffer(_BUFFER_SIZE, lcd_bus.MEMORY_INTERNAL | lcd_bus.MEMORY_DMA)

    import st7789
    display = st7789.ST7789(
        data_bus=display_bus,
        frame_buffer1=fb1,
        frame_buffer2=fb2,
        display_width=_WIDTH,
        display_height=_HEIGHT,
        backlight_pin=_BL,
        reset_pin=_RST,
        reset_state=0,
        color_space=lv.COLOR_FORMAT.RGB565,
        color_byte_order=st7789.BYTE_ORDER_BGR,
        rgb565_byte_swap=True,
    )

    import ft6x36
    import i2c
    import task_handler

    display.init()

    i2c_bus = i2c.I2C.Bus(host=0, scl=_SCL, sda=_SDA, freq=_TP_FREQ, use_locks=False)
    touch_dev = i2c.I2C.Device(bus=i2c_bus, dev_id=ft6x36.I2C_ADDR, reg_bits=ft6x36.BITS)
    indev = ft6x36.FT6x36(touch_dev)

    display.set_rotation(lv.DISPLAY_ROTATION._270)
    display.set_backlight(75)

    # 保持引用，防止被垃圾回收
    state.task_handler = task_handler.TaskHandler()
    state.fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(state.fs_drv, 'F')

    state.display = display
    return display
