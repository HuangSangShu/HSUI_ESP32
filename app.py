# 系统启动与主循环
import time

import lvgl as lv
import machine

import hardware
import screens
import state
import timeedit
import ui
from timeutil import restore_saved_time


def os_button_pressed(pin):
    if not state.issleep:
        now = time.ticks_ms()
        if time.ticks_diff(now, state.last_boot) > 200:
            state.last_boot = now
            state.need_switch = True


def os_sleep(pin):
    now = time.ticks_ms()
    if time.ticks_diff(now, state.last_home) > 200:  # 去抖
        state.last_home = now
        if not state.issleep:
            state.issleep = True
            state.display.set_backlight(0)
        else:
            state.issleep = False
            state.display.set_backlight(75)


def boot():
    hardware.init_display_and_touch()
    ui.init_styles()

    state.btn_boot = machine.Pin(0, machine.Pin.IN)
    state.btn_home = machine.Pin(39, machine.Pin.IN)

    # 显示开机 LOGO
    scr = lv.obj()
    scr.set_style_bg_color(state.BACK, 0)
    obj_logo = lv.label(scr)
    obj_logo.add_style(state.sty_text14, 0)
    obj_logo.set_pos(130, 100)
    obj_logo.set_text("HSOS")
    lv.screen_load(scr)

    time.sleep(2)

    wdt = machine.WDT(timeout=10000)
    state.btn_boot.irq(trigger=machine.Pin.IRQ_FALLING, handler=os_button_pressed)
    state.btn_home.irq(trigger=machine.Pin.IRQ_FALLING, handler=os_sleep)

    # 恢复离线保存的时间（若有）
    restore_saved_time()

    # 预构建所有页面
    screens.build_mainscreen()
    screens.build_mainmenu()
    screens.build_calendar()
    screens.build_setting()
    timeedit.build_timeset()

    state.screen_state = "MAINSCREEN"
    lv.screen_load(state.scr_mainscreen)

    # 主循环：仅用于硬件物理按键检查和非阻塞轮询
    last_time_refresh = 0
    while True:
        if state.need_switch:
            state.need_switch = False
            if state.screen_state in ("MAINSCREEN", "CALENDAR", "SETTING", "SETTIME"):
                lv.screen_load(state.scr_mainmenu)
                state.screen_state = "MAINMENU"
            elif state.screen_state == "MAINMENU":
                lv.screen_load(state.scr_mainscreen)
                state.screen_state = "MAINSCREEN"

        now_ms = time.ticks_ms()
        # 如果在时钟页面，实时更新时间
        if time.ticks_diff(now_ms, last_time_refresh) > 1000:
            last_time_refresh = now_ms
            if state.screen_state == "MAINSCREEN":
                ui.os_update_clock_labels()
            elif state.screen_state == "MAINMENU" and state.obj_menuclock:
                ui.os_update_small_clock(state.obj_menuclock)
            elif state.screen_state == "CALENDAR" and state.obj_calclock:
                ui.os_update_small_clock(state.obj_calclock)
            elif state.screen_state == "SETTING" and state.obj_setclock:
                ui.os_update_small_clock(state.obj_setclock)

        time.sleep_ms(5)
        wdt.feed()
