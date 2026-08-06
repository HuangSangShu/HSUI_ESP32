# 各页面（主屏 / 主菜单 / 设置 / 日历）的构建与跳转
import time

import lvgl as lv

import state
import timeedit
import ui


def goto_calendar(e=None):
    state.screen_state = "CALENDAR"
    lv.screen_load(state.scr_calendar)


def goto_setting(e=None):
    state.screen_state = "SETTING"
    lv.screen_load(state.scr_setting)


def build_mainscreen():
    state.scr_mainscreen = lv.obj()
    state.scr_mainscreen.set_style_bg_color(state.BACK, 0)

    style_mainclock = lv.style_t()
    style_mainclock.init()
    style_mainclock.set_text_font(state.FONT48)
    style_mainclock.set_text_color(state.FRONT)

    state.obj_mainclock = lv.label(state.scr_mainscreen)
    state.obj_mainclock.add_style(style_mainclock, 0)
    state.obj_mainclock.set_pos(40, 70)

    state.obj_mainweekday = lv.label(state.scr_mainscreen)
    state.obj_mainweekday.add_style(state.sty_text14, 0)
    state.obj_mainweekday.set_pos(40, 180)

    state.obj_maindate = lv.label(state.scr_mainscreen)
    state.obj_maindate.add_style(state.sty_text14, 0)
    state.obj_maindate.set_pos(145, 180)

    state.obj_smallclock = None

    ui.os_update_clock_labels()


def build_mainmenu():
    state.scr_mainmenu = lv.obj()
    state.scr_mainmenu.set_style_bg_color(state.BACK, 0)

    state.obj_menuclock = ui.os_show_small_clock(state.scr_mainmenu)

    obj_menubtn01 = lv.button(state.scr_mainmenu)
    obj_menubtn01.add_style(state.sty_text14, 0)
    obj_menubtn01.set_size(145, 70)
    obj_menubtn01.set_pos(10, 20)
    obj_menubtn01_text = lv.label(obj_menubtn01)
    obj_menubtn01_text.set_text("设置")
    obj_menubtn01_text.center()
    obj_menubtn01.add_event_cb(goto_setting, lv.EVENT.CLICKED, None)

    obj_menubtn02 = lv.button(state.scr_mainmenu)
    obj_menubtn02.add_style(state.sty_text14, 0)
    obj_menubtn02.set_size(145, 70)
    obj_menubtn02.set_pos(165, 20)
    obj_menubtn02_text = lv.label(obj_menubtn02)
    obj_menubtn02_text.set_text("日历")
    obj_menubtn02_text.center()
    obj_menubtn02.add_event_cb(goto_calendar, lv.EVENT.CLICKED, None)

    obj_menubtn03 = lv.button(state.scr_mainmenu)
    obj_menubtn03.add_style(state.sty_text14, 0)
    obj_menubtn03.set_size(145, 70)
    obj_menubtn03.set_pos(10, 100)
    obj_menubtn03_text = lv.label(obj_menubtn03)
    obj_menubtn03_text.set_text("none")
    obj_menubtn03_text.center()
    obj_menubtn03.add_event_cb(None, lv.EVENT.CLICKED, None)

    obj_menubtn04 = lv.button(state.scr_mainmenu)
    obj_menubtn04.add_style(state.sty_text14, 0)
    obj_menubtn04.set_size(145, 70)
    obj_menubtn04.set_pos(165, 100)
    obj_menubtn04_text = lv.label(obj_menubtn04)
    obj_menubtn04_text.set_text("none")
    obj_menubtn04_text.center()
    obj_menubtn04.add_event_cb(None, lv.EVENT.CLICKED, None)

    obj_menubtn05 = lv.button(state.scr_mainmenu)
    obj_menubtn05.add_style(state.sty_text14, 0)
    obj_menubtn05.set_size(145, 70)
    obj_menubtn05.set_pos(10, 180)
    obj_menubtn05_text = lv.label(obj_menubtn05)
    obj_menubtn05_text.set_text("none")
    obj_menubtn05_text.center()
    obj_menubtn05.add_event_cb(None, lv.EVENT.CLICKED, None)

    obj_menubtn06 = lv.button(state.scr_mainmenu)
    obj_menubtn06.add_style(state.sty_text14, 0)
    obj_menubtn06.set_size(145, 70)
    obj_menubtn06.set_pos(165, 180)
    obj_menubtn06_text = lv.label(obj_menubtn06)
    obj_menubtn06_text.set_text("none")
    obj_menubtn06_text.center()
    obj_menubtn06.add_event_cb(None, lv.EVENT.CLICKED, None)


def build_setting():
    state.scr_setting = lv.obj()
    state.scr_setting.set_style_bg_color(state.BACK, 0)
    state.obj_setclock = ui.os_show_small_clock(state.scr_setting)

    obj_menubtn01 = lv.button(state.scr_setting)
    obj_menubtn01.add_style(state.sty_text14, 0)
    obj_menubtn01.set_size(145, 70)
    obj_menubtn01.set_pos(10, 20)
    obj_menubtn01_text = lv.label(obj_menubtn01)
    obj_menubtn01_text.set_text("日期与时间")
    obj_menubtn01_text.center()
    obj_menubtn01.add_event_cb(timeedit.open_timeset, lv.EVENT.CLICKED, None)

    obj_menubtn02 = lv.button(state.scr_setting)
    obj_menubtn02.add_style(state.sty_text14, 0)
    obj_menubtn02.set_size(145, 70)
    obj_menubtn02.set_pos(165, 20)
    obj_menubtn02_text = lv.label(obj_menubtn02)
    obj_menubtn02_text.set_text("显示")
    obj_menubtn02_text.center()
    obj_menubtn02.add_event_cb(None, lv.EVENT.CLICKED, None)

    obj_menubtn03 = lv.button(state.scr_setting)
    obj_menubtn03.add_style(state.sty_text14, 0)
    obj_menubtn03.set_size(145, 70)
    obj_menubtn03.set_pos(10, 100)
    obj_menubtn03_text = lv.label(obj_menubtn03)
    obj_menubtn03_text.set_text("电源")
    obj_menubtn03_text.center()
    obj_menubtn03.add_event_cb(None, lv.EVENT.CLICKED, None)

    obj_menubtn04 = lv.button(state.scr_setting)
    obj_menubtn04.add_style(state.sty_text14, 0)
    obj_menubtn04.set_size(145, 70)
    obj_menubtn04.set_pos(165, 100)
    obj_menubtn04_text = lv.label(obj_menubtn04)
    obj_menubtn04_text.set_text("关于")
    obj_menubtn04_text.center()
    obj_menubtn04.add_event_cb(None, lv.EVENT.CLICKED, None)


def build_calendar(e=None):
    state.scr_calendar = lv.obj()
    state.scr_calendar.set_style_bg_color(state.BACK, 0)

    state.obj_calclock = ui.os_show_small_clock(state.scr_calendar)

    cal = lv.calendar(state.scr_calendar)
    cal.set_size(320, 220)
    cal.set_pos(0, 20)
    cal.add_style(state.sty_text14, 0)
    now_time = time.localtime()
    cal.set_today_date(now_time[0], now_time[1], now_time[2])
    cal.set_shown_year(now_time[0])
    cal.set_shown_month(now_time[1])
