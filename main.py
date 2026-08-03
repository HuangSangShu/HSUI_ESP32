import time
import sys
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
last_time = 0
last_time2 = 0
issleep = False

# 离线修改时间相关
TIME_SAVE_FILE = '/time.dat'
TIME_FIELD_NAMES = ["年", "月", "日", "时", "分", "秒"]
TIME_FIELD_MIN = [2000, 1, 1, 0, 0, 0]
TIME_FIELD_MAX = [2099, 12, 31, 23, 59, 59]
time_edit_vals = [0, 0, 0, 0, 0, 0]
time_edit_sel = 0
time_field_buttons = None
time_field_value_labels = None



'''def check_button(select):
    global b_boot, b_home
    if select == 0:
        return not b_boot.value() # 假设低电平按下
    elif select == 1:
        return not b_home.value()
    else:
        return False'''
    
def button_pressed(pin):
    global last_time
    if issleep == False:
        now = time.ticks_ms()
        if time.ticks_diff(now,last_time) > 200:   #去抖
            last_time = now
            if current_screen_state == "MAINSCREEN":
                load_mainmenu()
            elif current_screen_state == "MAINMENU":
                load_mainscreen()
            elif current_screen_state == "CALENDAR":
                load_mainmenu()
            elif current_screen_state == "SETTIME":
                load_mainmenu()


def ossleep(pin):
    global display,last_time2,issleep
    now = time.ticks_ms()
    if time.ticks_diff(now,last_time2) > 200:   #去抖
        last_time2 = now
        if issleep == False:
            issleep = True
            display.set_backlight(0)
            
        else:
            issleep = False
            display.set_backlight(75)    
            


def boot():
    global FONT48, FONT14, s_text14, BACK, FRONT, b_boot, b_home, current_screen_state,display

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

    wdt = machine.WDT(timeout=10000)
    b_boot.irq(trigger=Pin.IRQ_FALLING,handler=button_pressed)
    b_home.irq(trigger=Pin.IRQ_FALLING,handler=ossleep)


    # 恢复离线保存的时间（若有）
    restore_saved_time()

    # 进入主屏幕
    load_mainscreen()





    # 主循环：仅用于硬件物理按键检查和非阻塞轮询
    # last_btn_state = False
    while True:
        '''btn_pressed = check_button(0)
        
        # 检测按键边沿（按下瞬间）
        if btn_pressed and not last_btn_state:
            if current_screen_state == "MAINSCREEN":
                load_mainmenu()
            elif current_screen_state == "MAINMENU":
                load_mainscreen()
            elif current_screen_state == "CALENDAR":
                load_mainmenu()
        
        last_btn_state = btn_pressed'''
        
        # 如果在时钟页面，实时更新时间
        if current_screen_state == "MAINSCREEN":
            update_clock_labels()

        time.sleep_ms(50)
        wdt.feed()





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
    sys.print_exception(err)
    try:
        load_mainmenu()
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
    global time_edit_vals
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
    load_mainmenu()


def time_back_cb(e, *args):
    try:
        load_mainmenu()
    except Exception as err:
        sys.print_exception(err)


def load_time_setting():
    try:
        _load_time_setting_impl()
    except Exception as err:
        sys.print_exception(err)
        try:
            load_mainmenu()
        except Exception:
            pass


def _load_time_setting_impl():
    global current_screen_state
    global time_edit_vals, time_edit_sel, time_field_buttons, time_field_value_labels
    current_screen_state = "SETTIME"

    now_time = time.localtime()
    time_edit_vals = [now_time[0], now_time[1], now_time[2], now_time[3], now_time[4], now_time[5]]
    time_edit_sel = 0

    scr = lv.obj()
    scr.set_style_bg_color(BACK, 0)

    d_title = lv.label(scr)
    d_title.add_style(s_text14, 0)
    d_title.set_pos(132, 6)
    d_title.set_text("设置时间")

    time_field_buttons = []
    time_field_value_labels = []
    for i in range(6):
        col = i % 3
        row = i // 3
        b = lv.button(scr)
        b.set_size(95, 48)
        b.set_pos(10 + col * 105, 32 + row * 57)
        b.add_style(s_text14, 0)
        b.add_event_cb(_field_cb(i), lv.EVENT.CLICKED, None)
        lab = lv.label(b)
        time_field_buttons.append(b)
        time_field_value_labels.append(lab)
        time_refresh_value(i)

    d_minus = lv.button(scr)
    d_minus.set_size(60, 48)
    d_minus.set_pos(10, 175)
    d_minus.add_style(s_text14, 0)
    d_minus_lab = lv.label(d_minus)
    d_minus_lab.set_text("-")
    d_minus_lab.center()
    d_minus.add_event_cb(_adjust_cb(-1), lv.EVENT.CLICKED, None)

    d_plus = lv.button(scr)
    d_plus.set_size(60, 48)
    d_plus.set_pos(75, 175)
    d_plus.add_style(s_text14, 0)
    d_plus_lab = lv.label(d_plus)
    d_plus_lab.set_text("+")
    d_plus_lab.center()
    d_plus.add_event_cb(_adjust_cb(1), lv.EVENT.CLICKED, None)

    d_save = lv.button(scr)
    d_save.set_size(75, 48)
    d_save.set_pos(150, 175)
    d_save.add_style(s_text14, 0)
    d_save_lab = lv.label(d_save)
    d_save_lab.set_text("保存")
    d_save_lab.center()
    d_save.add_event_cb(time_save_cb, lv.EVENT.CLICKED, None)

    d_back = lv.button(scr)
    d_back.set_size(75, 48)
    d_back.set_pos(235, 175)
    d_back.add_style(s_text14, 0)
    d_back_lab = lv.label(d_back)
    d_back_lab.set_text("返回")
    d_back_lab.center()
    d_back.add_event_cb(time_back_cb, lv.EVENT.CLICKED, None)

    time_refresh_highlight()
    lv.screen_load(scr)




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
    d_2button_text.set_text("修改时间")
    d_2button_text.center()
    d_2button.add_event_cb(open_time_setting_cb, lv.EVENT.CLICKED, None)

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




def open_time_setting_cb(e, *args):
    load_time_setting()


def open_calendar_cb(e, *args):
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
