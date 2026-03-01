import time
import machine
from machine import Pin
from micropython import const

import lcd_bus

def main():
    acc = Pin(40, Pin.OUT)
    acc.value(1)
    backlight = Pin(8, Pin.OUT)
    backlight.value(1)
    # display settings
    _WIDTH = const(240)
    _HEIGHT = const(320)
    _BL = const(8)
    _RST = const(7)
    _DC = const(15)

    _MOSI = const(17)
    _MISO = const(16)
    _SCK = const(18)
    _HOST = const(1)
    _BUFFER_SIZE = const(30720)

    _LCD_CS = const(6)
    _LCD_FREQ = const(80000000)

    _SCL = const(9)
    _SDA = const(11)
    _TP_FREQ = const(400000)
    spi_bus = machine.SPI.Bus(
        host=_HOST,
        mosi=_MOSI,
        miso=_MISO,
        sck=_SCK
    )

    display_bus = lcd_bus.SPIBus(
        spi_bus=spi_bus,
        freq=_LCD_FREQ,
        dc=_DC,
        cs=_LCD_CS,
    )
    fb1 = display_bus.allocate_framebuffer(_BUFFER_SIZE, lcd_bus.MEMORY_INTERNAL | lcd_bus.MEMORY_DMA)
    fb2 = display_bus.allocate_framebuffer(_BUFFER_SIZE, lcd_bus.MEMORY_INTERNAL | lcd_bus.MEMORY_DMA)
    import st7789  # NOQA
    import lvgl as lv  # NOQA

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

    import i2c  # NOQA
    import task_handler  # NOQA
    import ft6x36  # NOQA

    display.init()

    i2c_bus = i2c.I2C.Bus(host=0, scl=_SCL, sda=_SDA, freq=_TP_FREQ, use_locks=False)
    touch_dev = i2c.I2C.Device(bus=i2c_bus, dev_id=ft6x36.I2C_ADDR, reg_bits=ft6x36.BITS)

    indev = ft6x36.FT6x36(touch_dev)

    # you want to rotate the display after the calibration has been done in order
    # to keep the corners oriented properly.
    display.set_rotation(lv.DISPLAY_ROTATION._270)
  
    display.set_backlight(100)
    
    th = task_handler.TaskHandler()

    #以上代码感谢Cookie_987提供的支持 | THANKS TO Cookie_987 FOR THE ABOVE CODE
    

    scrn = lv.screen_active()
    scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

    
    #改就光改下面的好吧，上面全是初始化
    
    
    time_label = lv.label(scrn)
    time_label.set_pos(0,0)
    time_label.set_text("loading")

    calendar = lv.calendar(scrn)    
    calendar.set_size(300, 200)
    calendar.set_pos(10, 20)
    calendar.set_today_date(2026,3,1)
    calendar.set_month_shown(2026,3)
          
    while True:
        now_time = time.localtime()
        time_label.set_text(f"{now_time[3]:02d}:{now_time[4]:02d}:{now_time[5]:02d}")
        time.sleep(1)

if __name__ == '__main__':
    main()
    

