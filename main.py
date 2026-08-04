import time
import machine 
from micropython import const 
import lcd_bus 
import fs_driver 
import lvgl as lv 

# 全局变量
FONT48 = None
FONT14 = None
sty_text14 = None
BACK = None
FRONT = None
btn_boot = None
btn_home = None
screen_state = "BOOT" # 记录当前页面状态
last_boot = 0
last_home = 0
issleep = False
need_switch = False
scr_calendar = None
scr_mainscreen = None
scr_mainmenu = None

# 保存时钟标签对象的全局引用以便局部更新
obj_mainclock = None
obj_mainweekday = None
obj_maindate = None
obj_menuclock = None
obj_calclock = None
    
def os_button_pressed(pin):
    global last_boot, need_switch, screen_state, scr_calendar
    if issleep == False:        
        now = time.ticks_ms()
        if time.ticks_diff(now, last_boot) > 200:
            last_boot = now
            need_switch = True

def os_sleep(pin):
    global last_home,issleep,display
    now = time.ticks_ms()
    if time.ticks_diff(now,last_home) > 200:   #去抖
        last_home = now
        if issleep == False:
            issleep = True
            display.set_backlight(0)
            
        else:
            issleep = False
            display.set_backlight(75)    

def os_update_clock_labels():
    global obj_mainclock
    if obj_mainclock is None:
        return
    weekdays_chinese = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    now_time = time.localtime()
    obj_mainclock.set_text(f"{now_time[3]:02d}:{now_time[4]:02d}:{now_time[5]:02d}")
    obj_mainweekday.set_text(weekdays_chinese[now_time[6]])
    obj_maindate.set_text(f"{now_time[1]}/{now_time[2]}")

def os_update_small_clock(obj):
    now_time = time.localtime()
    obj.set_text(f"{now_time[3]:02d}:{now_time[4]:02d}")

def os_show_small_clock(scr, x=250, y=3):
    global sty_text14
    label = lv.label(scr)
    label.add_style(sty_text14,0)
    label.set_pos(x,y)
    os_update_small_clock(label)
    return label

def build_mainscreen():
    global screen_state, obj_mainclock, obj_mainweekday, obj_maindate, obj_smallclock,scr_mainscreen


    
    scr_mainscreen = lv.obj()

    scr_mainscreen.set_style_bg_color(BACK, 0)

    style_mainclock = lv.style_t()
    style_mainclock.init()
    style_mainclock.set_text_font(FONT48)
    style_mainclock.set_text_color(FRONT)
    
    obj_mainclock = lv.label(scr_mainscreen)
    obj_mainclock.add_style(style_mainclock, 0)
    obj_mainclock.set_pos(40, 70)        

    obj_mainweekday = lv.label(scr_mainscreen)
    obj_mainweekday.add_style(sty_text14, 0)
    obj_mainweekday.set_pos(40, 180)

    obj_maindate = lv.label(scr_mainscreen)
    obj_maindate.add_style(sty_text14, 0)
    obj_maindate.set_pos(145, 180)

    obj_smallclock = None

    os_update_clock_labels()

def os_gotocal(pin):
    global screen_state
    screen_state = "CALENDAR"
    os_show_small_clock(scr_calendar)
    lv.screen_load(scr_calendar)


def build_mainmenu():
    global screen_state,scr_mainmenu,obj_menuclock

    
    scr_mainmenu = lv.obj()

    scr_mainmenu.set_style_bg_color(BACK, 0)

    obj_menuclock = os_show_small_clock(scr_mainmenu)



    obj_menubtn01 = lv.button(scr_mainmenu)
    obj_menubtn01.add_style(sty_text14, 0)
    obj_menubtn01.set_size(145, 70)
    obj_menubtn01.set_pos(10, 20)
    obj_menubtn01_text = lv.label(obj_menubtn01)
    obj_menubtn01_text.set_text("设置")
    obj_menubtn01_text.center()
    obj_menubtn01.add_event_cb(None, lv.EVENT.CLICKED, None)
    
    obj_menubtn02 = lv.button(scr_mainmenu)
    obj_menubtn02.add_style(sty_text14, 0)
    obj_menubtn02.set_size(145, 70)
    obj_menubtn02.set_pos(165, 20)
    obj_menubtn02_text = lv.label(obj_menubtn02)
    obj_menubtn02_text.set_text("日历")
    obj_menubtn02_text.center()
    obj_menubtn02.add_event_cb(os_gotocal, lv.EVENT.CLICKED, None)

    obj_menubtn03 = lv.button(scr_mainmenu)
    obj_menubtn03.add_style(sty_text14, 0)
    obj_menubtn03.set_size(145, 70)
    obj_menubtn03.set_pos(10, 100)
    obj_menubtn03_text = lv.label(obj_menubtn03)
    obj_menubtn03_text.set_text("none")
    obj_menubtn03_text.center()
    obj_menubtn03.add_event_cb(None, lv.EVENT.CLICKED, None)
    
    obj_menubtn04 = lv.button(scr_mainmenu)
    obj_menubtn04.add_style(sty_text14, 0)
    obj_menubtn04.set_size(145, 70)
    obj_menubtn04.set_pos(165, 100)
    obj_menubtn04_text = lv.label(obj_menubtn04)
    obj_menubtn04_text.set_text("none")
    obj_menubtn04_text.center()
    obj_menubtn04.add_event_cb(None, lv.EVENT.CLICKED, None)

    obj_menubtn05 = lv.button(scr_mainmenu)
    obj_menubtn05.add_style(sty_text14, 0)
    obj_menubtn05.set_size(145, 70)
    obj_menubtn05.set_pos(10, 180)
    obj_menubtn05_text = lv.label(obj_menubtn05)
    obj_menubtn05_text.set_text("none")
    obj_menubtn05_text.center()
    obj_menubtn05.add_event_cb(None, lv.EVENT.CLICKED, None)

    obj_menubtn06 = lv.button(scr_mainmenu)
    obj_menubtn06.add_style(sty_text14, 0)
    obj_menubtn06.set_size(145, 70)
    obj_menubtn06.set_pos(165, 180)
    obj_menubtn06_text = lv.label(obj_menubtn06)
    obj_menubtn06_text.set_text("none")
    obj_menubtn06_text.center()
    obj_menubtn06.add_event_cb(None, lv.EVENT.CLICKED, None)
   
def build_calendar(e = None):
    global screen_state,scr_calendar,obj_calclock

    
    scr_calendar = lv.obj()

    scr_calendar.set_style_bg_color(BACK, 0)

    obj_calclock = os_show_small_clock(scr_calendar)

    cal = lv.calendar(scr_calendar)
    cal.set_size(320, 220)
    cal.set_pos(0, 20)
    cal.add_style(sty_text14,0)
    now_time = time.localtime()
    cal.set_today_date(now_time[0],now_time[1],now_time[2])

def boot():
    global FONT48, FONT14, sty_text14, BACK, FRONT, btn_boot, btn_home, screen_state,issleep,display,need_switch,obj_menuclock,obj_calclock

    acc = machine.Pin(40, machine.Pin.OUT)
    acc.value(1)
    backlight = machine.Pin(8, machine.Pin.OUT)
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

    sty_text14 = lv.style_t()
    sty_text14.init()
    sty_text14.set_text_font(FONT14)
    sty_text14.set_text_color(FRONT)
    sty_text14.set_bg_color(lv.color_make(255, 255, 180))

    btn_boot = machine.Pin(0, machine.Pin.IN)
    btn_home = machine.Pin(39, machine.Pin.IN)

    # 显示开机 LOGO
    scr = lv.obj()
    scr.set_style_bg_color(BACK, 0)
    obj_logo = lv.label(scr)
    obj_logo.add_style(sty_text14, 0)
    obj_logo.set_pos(130, 100)        
    obj_logo.set_text("HSOS")
    lv.screen_load(scr)

    time.sleep(2)

    wdt = machine.WDT(timeout=10000)
    btn_boot.irq(trigger=machine.Pin.IRQ_FALLING,handler=os_button_pressed)
    btn_home.irq(trigger=machine.Pin.IRQ_FALLING,handler=os_sleep)


    # 进入主屏幕
    build_mainscreen()
    build_mainmenu()
    build_calendar()
    screen_state = "MAINSCREEN"
    lv.screen_load(scr_mainscreen)





    # 主循环：仅用于硬件物理按键检查和非阻塞轮询
    # last_btn_state = False
    while True:
        if need_switch:
            need_switch = False
            if screen_state == "MAINSCREEN":
                lv.screen_load(scr_mainmenu)
                screen_state = "MAINMENU"
                
            elif screen_state == "MAINMENU":
                lv.screen_load(scr_mainscreen)
                screen_state = "MAINSCREEN"
            elif screen_state == "CALENDAR":
                lv.screen_load(scr_mainmenu)
                screen_state = "MAINMENU"
                

        # 如果在时钟页面，实时更新时间
        if screen_state == "MAINSCREEN":
            os_update_clock_labels()
        
        if screen_state == "MAINMENU":        
            os_update_small_clock(obj_menuclock)

        if screen_state == "CALENDAR":        
            os_update_small_clock(obj_calclock)

        time.sleep_ms(50)
        wdt.feed()

boot()