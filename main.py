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

    global FONT48,FONT14,s_text14,BACK,FRONT,b_boot,b_home

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

    b_boot = Pin(0,Pin.IN)
    b_home = Pin(39,Pin.IN)


    d_logo = lv.label(scr)
    d_logo.add_style(s_text14, 0)
    d_logo.set_pos(130,100)        
    d_logo.set_text("HSOS")

    lv.screen_load(scr)

    time.sleep(2)
    
    mainscreen()
    
           


def mainscreen():      
    global FONT48,FRONT,BACK,s_text14,b_home,b_boot

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
        if b_boot.value() == 0:
            time.sleep_ms(20)
            if b_boot.value() == 0:
                mainmenu()
                while b_boot.value() == 0:
                    time.sleep_ms(10)
            
        time.sleep_ms(50)


def mainmenu():
    global FRONT, BACK, s_text14, b_boot, b_home

    # 创建新屏幕，背景色为 BACK
    scr = lv.obj()
    scr.set_style_bg_color(BACK, 0)

    # 创建菜单对象，并设置为全屏
    d_menu = lv.menu(scr)
    d_menu.set_size(lv.pct(100), lv.pct(100))   # 充满屏幕
    d_menu.center()

    # 设置菜单背景色为 BACK（可选，因为屏幕背景已经是 BACK，菜单默认透明）
    # 如果需要菜单本身也是 BACK，可取消下面一行注释
    d_menu.set_style_bg_color(BACK, 0)

    # ----- 返回按钮设置 -----
    back_btn = d_menu.get_main_header_back_button()
    # 返回按钮上的标签
    back_label = lv.label(back_btn)
    back_label.add_style(s_text14, 0)          # 应用文本样式
    back_label.set_text("返回")

    # ----- 头部标题样式（如果存在）-----
    header = d_menu.get_main_header()
    # 头部背景可设置为 BACK 或保持透明
    header.set_style_bg_color(BACK, 0)       # 可选
    if header.get_child_count() > 0:
        title_label = header.get_child(0)      # 通常第一个子对象是标题标签
        title_label.add_style(s_text14, 0)     # 应用文本样式

    # ----- 创建页面 -----
    # 设置页面
    settings_page = lv.menu_page(d_menu, "设置")
    
    header = d_menu.get_main_header()
    header.set_style_text_font(FONT14, 0)        # 设置字体
    header.set_style_text_color(FRONT, 0)  

    # 设置页面内容
    cont = lv.menu_cont(settings_page)
    label = lv.label(cont)
    label.set_text("None")
    label.add_style(s_text14, 0)               # 应用文本样式
    label.center()

    # 主页面（无标题）
    main_page = lv.menu_page(d_menu, None)

    # 主页面菜单项
    cont = lv.menu_cont(main_page)
    label = lv.label(cont)
    label.set_text("设置")
    label.add_style(s_text14, 0)               # 应用文本样式
    d_menu.set_load_page_event(cont, settings_page)

    # 设置初始显示的页面
    d_menu.set_page(main_page)

    # 加载屏幕
    lv.screen_load(scr)

    # 等待返回主屏幕的按键（b_boot）
    while True:
        if b_boot.value() == 0:
            time.sleep_ms(20)
            if b_boot.value() == 0:
                mainscreen()
                while b_boot.value() == 0:
                    time.sleep_ms(10)

main()
