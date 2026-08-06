# 全局共享状态
# 所有模块通过 `import state` 读写这些变量，避免跨模块传参

FONT48 = None
FONT14 = None
sty_text14 = None
BACK = None
FRONT = None
btn_boot = None
btn_home = None
display = None
task_handler = None
fs_drv = None

# 记录当前页面状态
screen_state = "BOOT"
last_boot = 0
last_home = 0
issleep = False
need_switch = False

scr_calendar = None
scr_mainscreen = None
scr_mainmenu = None
scr_setting = None
scr_timeset = None

# 保存时钟标签对象的全局引用，便于局部更新
obj_mainclock = None
obj_mainweekday = None
obj_maindate = None
obj_smallclock = None
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
