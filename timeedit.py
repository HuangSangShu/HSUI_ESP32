# 时间设置页面：构建与所有修改/保存逻辑
import machine
import sys
import time

import lvgl as lv

import state
from timeutil import compute_weekday, days_in_month


def open_timeset(e=None):
    now_time = time.localtime()
    state.time_edit_vals = [
        now_time[0], now_time[1], now_time[2],
        now_time[3], now_time[4], now_time[5],
    ]
    state.time_edit_sel = 0
    for i in range(6):
        time_refresh_value(i)
    time_refresh_highlight()
    state.screen_state = "SETTIME"
    lv.screen_load(state.scr_timeset)


def build_timeset():
    state.scr_timeset = lv.obj()
    state.scr_timeset.set_style_bg_color(state.BACK, 0)

    d_title = lv.label(state.scr_timeset)
    d_title.add_style(state.sty_text14, 0)
    d_title.set_pos(132, 6)
    d_title.set_text("设置时间")

    state.time_field_buttons = []
    state.time_field_value_labels = []
    for i in range(6):
        col = i % 3
        row = i // 3
        b = lv.button(state.scr_timeset)
        b.set_size(95, 48)
        b.set_pos(10 + col * 105, 32 + row * 57)
        b.add_style(state.sty_text14, 0)
        b.add_event_cb(_field_cb(i), lv.EVENT.CLICKED, None)
        lab = lv.label(b)
        state.time_field_buttons.append(b)
        state.time_field_value_labels.append(lab)
        time_refresh_value(i)

    d_minus = lv.button(state.scr_timeset)
    d_minus.set_size(60, 48)
    d_minus.set_pos(10, 175)
    d_minus.add_style(state.sty_text14, 0)
    d_minus_lab = lv.label(d_minus)
    d_minus_lab.set_text("-")
    d_minus_lab.center()
    d_minus.add_event_cb(_adjust_cb(-1), lv.EVENT.CLICKED, None)

    d_plus = lv.button(state.scr_timeset)
    d_plus.set_size(60, 48)
    d_plus.set_pos(75, 175)
    d_plus.add_style(state.sty_text14, 0)
    d_plus_lab = lv.label(d_plus)
    d_plus_lab.set_text("+")
    d_plus_lab.center()
    d_plus.add_event_cb(_adjust_cb(1), lv.EVENT.CLICKED, None)

    d_save = lv.button(state.scr_timeset)
    d_save.set_size(75, 48)
    d_save.set_pos(150, 175)
    d_save.add_style(state.sty_text14, 0)
    d_save_lab = lv.label(d_save)
    d_save_lab.set_text("保存")
    d_save_lab.center()
    d_save.add_event_cb(time_save_cb, lv.EVENT.CLICKED, None)

    d_back = lv.button(state.scr_timeset)
    d_back.set_size(75, 48)
    d_back.set_pos(235, 175)
    d_back.add_style(state.sty_text14, 0)
    d_back_lab = lv.label(d_back)
    d_back_lab.set_text("返回")
    d_back_lab.center()
    d_back.add_event_cb(time_back_cb, lv.EVENT.CLICKED, None)

    time_refresh_highlight()


def time_refresh_value(i):
    v = state.time_edit_vals[i]
    if i == 0:
        value_text = "%d" % v
    else:
        value_text = "%02d" % v
    state.time_field_value_labels[i].set_text("%s %s" % (state.TIME_FIELD_NAMES[i], value_text))
    state.time_field_value_labels[i].center()


def time_refresh_highlight():
    if state.time_field_buttons is None:
        return
    sel_bg = lv.color_make(255, 205, 120)
    normal_bg = lv.color_make(255, 255, 180)
    for i in range(len(state.time_field_buttons)):
        if i == state.time_edit_sel:
            state.time_field_buttons[i].set_style_bg_color(sel_bg, 0)
        else:
            state.time_field_buttons[i].set_style_bg_color(normal_bg, 0)


def _sett_error(err):
    sys.print_exception(err)
    try:
        state.screen_state = "MAINMENU"
        lv.screen_load(state.scr_mainmenu)
    except Exception:
        pass


def _field_cb(idx):
    def cb(e, *args):
        try:
            state.time_edit_sel = idx
            time_refresh_highlight()
        except Exception as err:
            _sett_error(err)
    return cb


def _adjust_cb(delta):
    def cb(e, *args):
        try:
            i = state.time_edit_sel
            v = state.time_edit_vals[i] + delta
            if v < state.TIME_FIELD_MIN[i]:
                v = state.TIME_FIELD_MAX[i]
            elif v > state.TIME_FIELD_MAX[i]:
                v = state.TIME_FIELD_MIN[i]
            state.time_edit_vals[i] = v
            time_refresh_value(i)
        except Exception as err:
            _sett_error(err)
    return cb


def time_save_cb(e, *args):
    y, m, d, hh, mm, ss = state.time_edit_vals
    if d > days_in_month(y, m):
        d = days_in_month(y, m)
    try:
        wd = compute_weekday(y, m, d, hh, mm, ss)
        machine.RTC().datetime((y, m, d, wd, hh, mm, ss, 0))
        with open(state.TIME_SAVE_FILE, 'w') as f:
            f.write("%d,%d,%d,%d,%d,%d" % (y, m, d, hh, mm, ss))
    except Exception as err:
        sys.print_exception(err)
    state.screen_state = "MAINMENU"
    lv.screen_load(state.scr_mainmenu)


def time_back_cb(e, *args):
    try:
        state.screen_state = "MAINMENU"
        lv.screen_load(state.scr_mainmenu)
    except Exception as err:
        sys.print_exception(err)
