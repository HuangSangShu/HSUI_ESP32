import time
import machine 
from machine import Pin 
from micropython import const 
import lcd_bus 
import fs_driver 
import lvgl as lv 

# 全局变量
FONT48 = None
FONT14 = None
s_text14 = None
BACK = None
FRONT = None
b_boot = None
b_home = None
current_screen_state = "BOOT" # 记录当前页面状态

def check_button(select):
    global b_boot, b_home
    if select == 0:
        return not b_boot.value() # 假设低电平按下
    elif select == 1:
        return not b_home.value()
    else:
        return False
    
def boot():
    global FONT48, FONT14, s_text14, BACK, FRONT, b_boot, b_home, current_screen_state

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
    
    th = task_handler.TaskHandler()      

    fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(fs_drv, 'F')

    # 字体与颜色设置
    FONT48 = lv.binfont_create('F:/HSUIFONT48.bin')
    FONT14 = lv.binfont_create('F:/HSUIFONT14.bin')

    FRONT = lv.color_make(100, 80, 60)
    BACK = lv.color_make(255, 240, 200)

    s_text14 = lv.style_t()
    s_text14.init()
    s_text14.set_text_font(FONT14)
    s_text14.set_text_color(FRONT)
    s_text14.set_bg_color(lv.color_make(255, 255, 180))

    b_boot = Pin(0, Pin.IN)
    b_home = Pin(39, Pin.IN)

    # 显示开机 LOGO
    scr = lv.obj()
    scr.set_style_bg_color(BACK, 0)
    d_logo = lv.label(scr)
    d_logo.add_style(s_text14, 0)
    d_logo.set_pos(130, 100)        
    d_logo.set_text("HSOS")
    lv.screen_load(scr)

    time.sleep(2)
    
    # 进入主屏幕
    load_mainscreen()

    # 主循环：仅用于硬件物理按键检查和非阻塞轮询
    last_btn_state = False
    while True:
        btn_pressed = check_button(0)
        
        # 检测按键边沿（按下瞬间）
        if btn_pressed and not last_btn_state:
            if current_screen_state == "MAINSCREEN":
                load_mainmenu()
            elif current_screen_state == "MAINMENU":
                load_mainscreen()
            elif current_screen_state == "CALENDAR":
                load_mainmenu()
        
        last_btn_state = btn_pressed
        
        # 如果在时钟页面，实时更新时间
        if current_screen_state == "MAINSCREEN":
            update_clock_labels()

        time.sleep_ms(50)

# 保存时钟标签对象的全局引用以便局部更新
d_main_clock = None
d_weekday = None
d_date = None

def load_mainscreen():
    global current_screen_state, d_main_clock, d_weekday, d_date
    current_screen_state = "MAINSCREEN"

    scr = lv.obj()
    scr.set_style_bg_color(BACK, 0)

    s_main_clock = lv.style_t()
    s_main_clock.init()
    s_main_clock.set_text_font(FONT48)
    s_main_clock.set_text_color(FRONT)
    
    d_main_clock = lv.label(scr)
    d_main_clock.add_style(s_main_clock, 0)
    d_main_clock.set_pos(40, 70)        

    d_weekday = lv.label(scr)
    d_weekday.add_style(s_text14, 0)
    d_weekday.set_pos(40, 180)

    d_date = lv.label(scr)
    d_date.add_style(s_text14, 0)
    d_date.set_pos(145, 180)

    update_clock_labels()
    lv.screen_load(scr)

def update_clock_labels():
    if d_main_clock is None:
        return
    weekdays_chinese = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    now_time = time.localtime()
    d_main_clock.set_text(f"{now_time[3]:02d}:{now_time[4]:02d}:{now_time[5]:02d}")
    d_weekday.set_text(weekdays_chinese[now_time[6]])
    d_date.set_text(f"{now_time[1]}/{now_time[2]}")

def load_mainmenu():
    global current_screen_state
    current_screen_state = "MAINMENU"

    scr = lv.obj()
    scr.set_style_bg_color(BACK, 0)

    # 左下按钮（设置/日历）
    d_setting_button = lv.button(scr)
    d_setting_button.add_style(s_text14, 0)
    d_setting_button.set_size(145, 70)
    d_setting_button.set_pos(10, 160)
    d_setting_button_text = lv.label(d_setting_button)
    d_setting_button_text.set_text("设置")
    d_setting_button_text.center()
    d_setting_button.add_event_cb(open_calendar_cb, lv.EVENT.CLICKED, None)

    # 右下按钮
    d_2button = lv.button(scr)
    d_2button.add_style(s_text14, 0)
    d_2button.set_size(145, 70)
    d_2button.set_pos(165, 160)
    d_2button_text = lv.label(d_2button)
    d_2button_text.set_text("none")
    d_2button_text.center()

    # 左上按钮
    d_3button = lv.button(scr)
    d_3button.add_style(s_text14, 0)
    d_3button.set_size(145, 140)
    d_3button.set_pos(10, 10)
    d_3button_text = lv.label(d_3button)
    d_3button_text.set_text("none")
    d_3button_text.center()

    # 右上按钮
    d_4button = lv.button(scr)
    d_4button.add_style(s_text14, 0)
    d_4button.set_size(145, 140)
    d_4button.set_pos(165, 10)
    d_4button_text = lv.label(d_4button)
    d_4button_text.set_text("none")
    d_4button_text.center()

    lv.screen_load(scr)

def open_calendar_cb(e):
    global current_screen_state
    current_screen_state = "CALENDAR"

    scr = lv.obj()
    scr.set_style_bg_color(BACK, 0)

    cal = lv.calendar(scr)
    cal.set_size(320, 240)
    cal.set_pos(0, 0)
    cal.add_style(s_text14,0)

    lv.screen_load(scr)

boot()