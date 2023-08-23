from tkinter.constants import ARC, FLAT, PIESLICE, DISABLED, NORMAL, HIDDEN, END
from Helper_file import settings, update_setting, create_folder, rm_dir, rm_file
from pygame import mixer
import os, tempfile


setting = settings()
mixer.init()

SLASH = '\\' if os.name in ['nt', 'dos'] else '/'
PARENT_DIR = os.getcwd() +  SLASH
APP_PATH = os.getcwd()
CONFIG_PATH = APP_PATH + SLASH + "Config" + SLASH
IMAGE_DIR = CONFIG_PATH + 'Image' + SLASH


if not setting.get('tmp_fol_loc'):
    temp_dir = tempfile.mkdtemp() + SLASH
    tmp_ = CONFIG_PATH + "tk-font/palab.ttf".replace('/', SLASH)
    dict_ = {'tmp_fol_loc':temp_dir, 'font' : {'loading': tmp_}}
    update_setting(setting | dict_)
    setting = settings()
    print(f"Temporary Dir @:{temp_dir}")


w, h = setting['display']['x'], setting['display']['y']

root_bg_color = setting["display"]['color']
mainF_bg_c = setting["main_frame"]["bg_color"]
ctrl_bg_c = setting["ctrl-frame"]["bg" ]

image = setting["image"]
i_w, i_h = image['w'], image['h']
p_wh = image['play_song_wh'] #20

s_wh = p_wh + int(1.5*p_wh)

ctrl_frame_h_per = setting["ctrl-frame"]["height_per"]

slider_height = setting["slider"]["height"]
slider_radius = setting["slider"]["radius"]

hover_frame_set = setting["hover-frame"]
min_w, max_w = hover_frame_set["min_w"], hover_frame_set["max_w"]
frame_width = hover_frame_set["frame-width"]
sideBarFrame_color = hover_frame_set["sideBarFrame_color"]
on_click_color = hover_frame_set["on_click_color"]
btn_highligth_color = sideBarFrame_color #hover_frame_set["btn_highlight_color"]

placeholder = setting["input"]["placeholder"]
slider_dict = setting["slider"]
pre_w, pre_h = setting['display']['x'], setting['display']['y']
ctrl_bg_c = setting["ctrl-frame"]["bg" ]

entry_bg = setting['input']['bg']
entry_bg_invalid = setting['input']['bg_invalid']

song_list = setting['song_list']
lb_colors = song_list["tbl_row_color"]
song_highlight_color = song_list['highlight_color']

cur_width = min_w
expanded = False
inc_W = setting["inc_W"]

is_dwding = False

tmp_fol_loc = setting['tmp_fol_loc']
create_folder(tmp_fol_loc)

if os.path.isfile(tmp_fol_loc + "url_fn_dict.json"):
    os.remove(tmp_fol_loc + "url_fn_dict.json")

setting['dwd']="False"
local_imgs_path = tmp_fol_loc + 'local-imgs'
create_folder(local_imgs_path)

m4a_local_songs_path = tmp_fol_loc + 'local-m4a-songs'
create_folder(m4a_local_songs_path)

tmp_fold = setting["tmp_fol_loc"]
