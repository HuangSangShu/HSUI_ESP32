import time
import machine 
from machine import Pin 
from micropython import const 
import lcd_bus 
import fs_driver 
import lvgl as lv 


def main():
    acc = Pin(40, Pin.OUT)
    acc.value(1)
    backlight = Pin(8, Pin.OUT)
    backlight.value(1)
    
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
    import st7789  
    import lvgl as lv  

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

    import i2c  
    import task_handler  
    import ft6x36  

    display.init()

    i2c_bus = i2c.I2C.Bus(host=0, scl=_SCL, sda=_SDA, freq=_TP_FREQ, use_locks=False)
    touch_dev = i2c.I2C.Device(bus=i2c_bus, dev_id=ft6x36.I2C_ADDR, reg_bits=ft6x36.BITS)

    indev = ft6x36.FT6x36(touch_dev)

    
    display.set_rotation(lv.DISPLAY_ROTATION._270)
  
    display.set_backlight(75)
    
    #联机调试时注释以下一行，单机运行请保留该行
    th = task_handler.TaskHandler()      

    fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(fs_drv, 'F')

    global FONT48,FONT14,s_text14,BACK,FRONT

    FONT48 = lv.binfont_create('F:/HSUIFONT48.bin')
    FONT14 = lv.binfont_create('F:/HSUIFONT14.bin')

    FRONT = lv.color_make(100,80,60)
    BACK = lv.color_make(255,240,200)

    s_text14 = lv.style_t()
    s_text14.init()
    s_text14.set_text_font(FONT14)
    s_text14.set_text_color(FRONT)

    SCR = lv.screen_active()
    scr = lv.obj()
    scr.set_style_bg_color(BACK, 0)


    d_logo = lv.label(scr)
    d_logo.add_style(s_text14, 0)
    d_logo.set_pos(130,100)        
    d_logo.set_text("HSOS")

    lv.screen_load(scr)

    time.sleep(2)
    
    mainscreen()
    
           


def mainscreen():      
    global FONT48,FRONT,BACK,s_text14

    scr = lv.obj()
    scr.set_style_bg_color(BACK, 0)

    s_main_clock = lv.style_t()
    s_main_clock.init()
    s_main_clock.set_text_font(FONT48)
    s_main_clock.set_text_color(FRONT)
    
    
    d_main_clock = lv.label(scr)
    d_main_clock.add_style(s_main_clock, 0)
    d_main_clock.set_pos(40,70)        
    d_main_clock.set_text("00:00:00")

    d_weekday = lv.label(scr)
    d_weekday.add_style(s_text14,0)
    d_weekday.set_pos(40,180)
    weekdays_chinese = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]    

    d_date = lv.label(scr)
    d_date.add_style(s_text14,0)
    d_date.set_pos(145,180)

    lv.screen_load(scr)

    while True:
        now_time = time.localtime()
        d_main_clock.set_text(f"{now_time[3]:02d}:{now_time[4]:02d}:{now_time[5]:02d}")
        d_weekday.set_text(weekdays_chinese[now_time[6]])
        d_date.set_text(f"{now_time[1]}/{now_time[2]}")
        for i in range(10):
            if Pin(39,Pin.IN,Pin.PULL_UP) == 0:
                time.sleep_ms(20)
                if Pin(39,Pin.IN,Pin.PULL_UP) == 0:
                    mainmenu()
                    while Pin(39,Pin.IN,Pin.PULL_UP) == 0:
                        time.sleep_ms(10)
            else:
                time.sleep(0.1)


def mainmenu():
    global FRONT,BACK,s_text14

    scr = lv.obj()
    scr.set_style_bg_color(BACK, 0)

    d_menu = lv.menu_create(scr)
    d_menu.center()
    
    d_back_btn = lv.menu_get_main_header_back_button(d_menu)
    d_back_button_label = lv.label_create(d_back_btn)
    d_back_button_label.add_style(s_text14,0)
    d_back_button_label.set_text("Back")

    d_setting = lv.menu_page_create(d_menu,"设置")
    cont = lv.menu_cont_create(d_setting)
    label = lv.label_create(cont)
    label.set_text("none")

    d_menu_main_page = lv.menu_page_create(d_menu, None)

    cont = lv.menu_cont_create(d_menu_main_page)
    label = lv.label_create(cont)
    label.set_text("Item 1 (Click me!)")
    lv.menu_set_load_page_event(d_menu, cont, d_setting)
    
    header = lv.menu_get_main_header(d_menu)
    title_label = lv.obj_get_child(header, 0)
    title_label.add_style(s_text14, 0)

    while True:
        if Pin(0,Pin.IN,Pin.PULL_UP) == 0:
            time.sleep_ms(20)
            if Pin(0,Pin.IN,Pin.PULL_UP) == 0:
                mainscreen()
                while Pin(0,Pin.IN,Pin.PULL_UP) == 0:
                    time.sleep_ms(10)


main()
