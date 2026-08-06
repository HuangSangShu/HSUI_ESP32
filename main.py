import time
import sys
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
scr_setting = None
scr_timeset = None

# 保存时钟标签对象的全局引用以便局部更新
obj_mainclock = None
obj_mainweekday = None
obj_maindate = None
obj_menuclock = None
obj_calclock = None
obj_setclock = None

# 离线修改时间相关
TIME_SAVE_FILE = '/time.dat'
TIME_FIELD_NAMES = ["年", "月", "日", "时", "分", "秒"]
TIME_FIELD_MIN = [2000, 1, 1, 0, 0, 0]
TIME_FIELD_MAX = [2099, 12, 31, 23, 59, 59]
time_edit_vals = [0, 0, 0, 0, 0, 0]
time_edit_sel = 0
time_field_buttons = None
time_field_value_labels = None
    
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
    lv.screen_load(scr_calendar)

def os_gotoset(pin):
    global screen_state
    screen_state = "SETTING"
    lv.screen_load(scr_setting)

def os_gototime(pin):
    global screen_state, time_edit_vals, time_edit_sel
    now_time = time.localtime()
    time_edit_vals = [now_time[0], now_time[1], now_time[2], now_time[3], now_time[4], now_time[5]]
    time_edit_sel = 0
    for i in range(6):
        time_refresh_value(i)
    time_refresh_highlight()
    screen_state = "SETTIME"
    lv.screen_load(scr_timeset)

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
    obj_menubtn01.add_event_cb(os_gotoset, lv.EVENT.CLICKED, None)
    
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

def build_setting():

    global screen_state,scr_setting,obj_setclock

    
    scr_setting = lv.obj()
    scr_setting.set_style_bg_color(BACK, 0)
    obj_setclock = os_show_small_clock(scr_setting)



    obj_menubtn01 = lv.button(scr_setting)
    obj_menubtn01.add_style(sty_text14, 0)
    obj_menubtn01.set_size(145, 70)
    obj_menubtn01.set_pos(10, 20)
    obj_menubtn01_text = lv.label(obj_menubtn01)
    obj_menubtn01_text.set_text("日期与时间")
    obj_menubtn01_text.center()
    obj_menubtn01.add_event_cb(os_gototime, lv.EVENT.CLICKED, None)
    
    obj_menubtn02 = lv.button(scr_setting)
    obj_menubtn02.add_style(sty_text14, 0)
    obj_menubtn02.set_size(145, 70)
    obj_menubtn02.set_pos(165, 20)
    obj_menubtn02_text = lv.label(obj_menubtn02)
    obj_menubtn02_text.set_text("显示")
    obj_menubtn02_text.center()
    obj_menubtn02.add_event_cb(None, lv.EVENT.CLICKED, None)

    obj_menubtn03 = lv.button(scr_setting)
    obj_menubtn03.add_style(sty_text14, 0)
    obj_menubtn03.set_size(145, 70)
    obj_menubtn03.set_pos(10, 100)
    obj_menubtn03_text = lv.label(obj_menubtn03)
    obj_menubtn03_text.set_text("电源")
    obj_menubtn03_text.center()
    obj_menubtn03.add_event_cb(None, lv.EVENT.CLICKED, None)
    
    obj_menubtn04 = lv.button(scr_setting)
    obj_menubtn04.add_style(sty_text14, 0)
    obj_menubtn04.set_size(145, 70)
    obj_menubtn04.set_pos(165, 100)
    obj_menubtn04_text = lv.label(obj_menubtn04)
    obj_menubtn04_text.set_text("关于")
    obj_menubtn04_text.center()
    obj_menubtn04.add_event_cb(None, lv.EVENT.CLICKED, None)

    '''obj_menubtn05 = lv.button(scr_setting)
    obj_menubtn05.add_style(sty_text14, 0)
    obj_menubtn05.set_size(145, 70)
    obj_menubtn05.set_pos(10, 180)
    obj_menubtn05_text = lv.label(obj_menubtn05)
    obj_menubtn05_text.set_text("none")
    obj_menubtn05_text.center()
    obj_menubtn05.add_event_cb(None, lv.EVENT.CLICKED, None)

    obj_menubtn06 = lv.button(scr_setting)
    obj_menubtn06.add_style(sty_text14, 0)
    obj_menubtn06.set_size(145, 70)
    obj_menubtn06.set_pos(165, 180)
    obj_menubtn06_text = lv.label(obj_menubtn06)
    obj_menubtn06_text.set_text("none")
    obj_menubtn06_text.center()
    obj_menubtn06.add_event_cb(None, lv.EVENT.CLICKED, None)'''
 
def build_timeset():
    global time_field_buttons, time_field_value_labels, scr_timeset

    scr_timeset = lv.obj()
    scr_timeset.set_style_bg_color(BACK, 0)

    d_title = lv.label(scr_timeset)
    d_title.add_style(sty_text14, 0)
    d_title.set_pos(132, 6)
    d_title.set_text("设置时间")

    time_field_buttons = []
    time_field_value_labels = []
    for i in range(6):
        col = i % 3
        row = i // 3
        b = lv.button(scr_timeset)
        b.set_size(95, 48)
        b.set_pos(10 + col * 105, 32 + row * 57)
        b.add_style(sty_text14, 0)
        b.add_event_cb(_field_cb(i), lv.EVENT.CLICKED, None)
        lab = lv.label(b)
        time_field_buttons.append(b)
        time_field_value_labels.append(lab)
        time_refresh_value(i)

    d_minus = lv.button(scr_timeset)
    d_minus.set_size(60, 48)
    d_minus.set_pos(10, 175)
    d_minus.add_style(sty_text14, 0)
    d_minus_lab = lv.label(d_minus)
    d_minus_lab.set_text("-")
    d_minus_lab.center()
    d_minus.add_event_cb(_adjust_cb(-1), lv.EVENT.CLICKED, None)

    d_plus = lv.button(scr_timeset)
    d_plus.set_size(60, 48)
    d_plus.set_pos(75, 175)
    d_plus.add_style(sty_text14, 0)
    d_plus_lab = lv.label(d_plus)
    d_plus_lab.set_text("+")
    d_plus_lab.center()
    d_plus.add_event_cb(_adjust_cb(1), lv.EVENT.CLICKED, None)

    d_save = lv.button(scr_timeset)
    d_save.set_size(75, 48)
    d_save.set_pos(150, 175)
    d_save.add_style(sty_text14, 0)
    d_save_lab = lv.label(d_save)
    d_save_lab.set_text("保存")
    d_save_lab.center()
    d_save.add_event_cb(time_save_cb, lv.EVENT.CLICKED, None)

    d_back = lv.button(scr_timeset)
    d_back.set_size(75, 48)
    d_back.set_pos(235, 175)
    d_back.add_style(sty_text14, 0)
    d_back_lab = lv.label(d_back)
    d_back_lab.set_text("返回")
    d_back_lab.center()
    d_back.add_event_cb(time_back_cb, lv.EVENT.CLICKED, None)

    time_refresh_highlight()

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

def days_in_month(y, m):
    if m == 2:
        if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0:
            return 29
        return 28
    if m in (4, 6, 9, 11):
        return 30
    return 31


def compute_weekday(y, m, d, hh, mm, ss):
    ts = time.mktime((y, m, d, hh, mm, ss, 0, 0))
    return time.localtime(ts)[6]


def restore_saved_time():
    try:
        with open(TIME_SAVE_FILE, 'r') as f:
            data = f.read().strip()
        parts = [int(x) for x in data.split(',')]
        if len(parts) != 6:
            return
        y, m, d, hh, mm, ss = parts
        if not (2000 <= y <= 2099 and 1 <= m <= 12 and 1 <= d <= 31):
            return
        if not (0 <= hh <= 23 and 0 <= mm <= 59 and 0 <= ss <= 59):
            return
        if d > days_in_month(y, m):
            d = days_in_month(y, m)
        wd = compute_weekday(y, m, d, hh, mm, ss)
        machine.RTC().datetime((y, m, d, wd, hh, mm, ss, 0))
    except Exception:
        pass


def time_refresh_value(i):
    global time_field_value_labels, time_edit_vals
    v = time_edit_vals[i]
    if i == 0:
        value_text = "%d" % v
    else:
        value_text = "%02d" % v
    time_field_value_labels[i].set_text("%s %s" % (TIME_FIELD_NAMES[i], value_text))
    time_field_value_labels[i].center()


def time_refresh_highlight():
    global time_field_buttons, time_edit_sel
    if time_field_buttons is None:
        return
    sel_bg = lv.color_make(255, 205, 120)
    normal_bg = lv.color_make(255, 255, 180)
    for i in range(len(time_field_buttons)):
        if i == time_edit_sel:
            time_field_buttons[i].set_style_bg_color(sel_bg, 0)
        else:
            time_field_buttons[i].set_style_bg_color(normal_bg, 0)


def _sett_error(err):
    global screen_state
    sys.print_exception(err)
    try:
        screen_state = "MAINMENU"
        lv.screen_load(scr_mainmenu)
    except Exception:
        pass


def _field_cb(idx):
    def cb(e, *args):
        try:
            global time_edit_sel
            time_edit_sel = idx
            time_refresh_highlight()
        except Exception as err:
            _sett_error(err)
    return cb


def _adjust_cb(delta):
    def cb(e, *args):
        try:
            global time_edit_vals
            i = time_edit_sel
            v = time_edit_vals[i] + delta
            if v < TIME_FIELD_MIN[i]:
                v = TIME_FIELD_MAX[i]
            elif v > TIME_FIELD_MAX[i]:
                v = TIME_FIELD_MIN[i]
            time_edit_vals[i] = v
            time_refresh_value(i)
        except Exception as err:
            _sett_error(err)
    return cb


def time_save_cb(e, *args):
    global time_edit_vals, screen_state
    y, m, d, hh, mm, ss = time_edit_vals
    if d > days_in_month(y, m):
        d = days_in_month(y, m)
    try:
        wd = compute_weekday(y, m, d, hh, mm, ss)
        machine.RTC().datetime((y, m, d, wd, hh, mm, ss, 0))
        with open(TIME_SAVE_FILE, 'w') as f:
            f.write("%d,%d,%d,%d,%d,%d" % (y, m, d, hh, mm, ss))
    except Exception as err:
        sys.print_exception(err)
    screen_state = "MAINMENU"
    lv.screen_load(scr_mainmenu)


def time_back_cb(e, *args):
    global screen_state
    try:
        screen_state = "MAINMENU"
        lv.screen_load(scr_mainmenu)
    except Exception as err:
        sys.print_exception(err)

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
    _BUFFER_SIZE = const(75000)

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

    # 恢复离线保存的时间（若有）
    restore_saved_time()

    # 进入主屏幕
    build_mainscreen()
    build_mainmenu()
    build_calendar()
    build_setting()
    build_timeset()
    screen_state = "MAINSCREEN"
    lv.screen_load(scr_mainscreen)





    # 主循环：仅用于硬件物理按键检查和非阻塞轮询
    last_time_refresh = 0
    while True:

        if need_switch:
            need_switch = False
            if screen_state in ("MAINSCREEN","CALENDAR","SETTING","SETTIME"):
                lv.screen_load(scr_mainmenu)
                screen_state = "MAINMENU"
                
            elif screen_state == "MAINMENU":
                lv.screen_load(scr_mainscreen)
                screen_state = "MAINSCREEN"


        
                
        now_ms = time.ticks_ms()
        # 如果在时钟页面，实时更新时间
        if time.ticks_diff(now_ms, last_time_refresh) > 1000:
            last_time_refresh = now_ms
            if screen_state == "MAINSCREEN":
                os_update_clock_labels()
            elif screen_state == "MAINMENU" and obj_menuclock:
                os_update_small_clock(obj_menuclock)
            elif screen_state == "CALENDAR" and obj_calclock:
                os_update_small_clock(obj_calclock)
            elif screen_state == "SETTING" and obj_setclock:
                os_update_small_clock(obj_setclock)

        time.sleep_ms(5)
        wdt.feed()

boot()
