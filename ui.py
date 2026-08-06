# 通用 UI：字体/样式初始化、小时钟与主页时钟刷新
import time

import lvgl as lv

import state


def init_styles():
    state.FONT48 = lv.binfont_create('F:/HSUIFONT48.bin')
    state.FONT14 = lv.binfont_create('F:/HSUIFONT14.bin')

    state.FRONT = lv.color_make(100, 80, 60)
    state.BACK = lv.color_make(255, 240, 200)

    sty = lv.style_t()
    sty.init()
    sty.set_text_font(state.FONT14)
    sty.set_text_color(state.FRONT)
    sty.set_bg_color(lv.color_make(255, 255, 180))
    state.sty_text14 = sty


def os_update_clock_labels():
    if state.obj_mainclock is None:
        return
    weekdays_chinese = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    now_time = time.localtime()
    state.obj_mainclock.set_text(f"{now_time[3]:02d}:{now_time[4]:02d}:{now_time[5]:02d}")
    state.obj_mainweekday.set_text(weekdays_chinese[now_time[6]])
    state.obj_maindate.set_text(f"{now_time[1]}/{now_time[2]}")


def os_update_small_clock(obj):
    now_time = time.localtime()
    obj.set_text(f"{now_time[3]:02d}:{now_time[4]:02d}")


def os_show_small_clock(scr, x=250, y=3):
    label = lv.label(scr)
    label.add_style(state.sty_text14, 0)
    label.set_pos(x, y)
    os_update_small_clock(label)
    return label
