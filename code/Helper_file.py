import os, json, hashlib, requests
from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageDraw, ImageFont
from tinytag import TinyTag
import random, copy, shutil
from network_functions import get_index_link


SLASH = '\\' if os.name in ['nt', 'dos'] else '/'
APP_PATH = os.getcwd() 
CONFIG_PATH = APP_PATH + SLASH + "Config" + SLASH
FFMPEG_EXE = CONFIG_PATH + "ffmpeg_lib\\ffmpeg.exe"
SETTINGS_PATH = CONFIG_PATH +  "setting.json"


def settings(SETTINGS_PATH=SETTINGS_PATH):
    with open(SETTINGS_PATH) as f:
        setting = json.load(f)
    return setting

def update_setting(dict_):
    write_2_json(dict_, SETTINGS_PATH)

def update_song_info(dict_):
    fn = settings()["tmp_fol_loc"] + "song-info.json"
    with open(fn, "w") as f:
        json.dump(dict_, f)

def get_song_info():
    fn = settings()["tmp_fol_loc"] + "song-info.json"
    with open(fn) as f:
        con = json.load(f)
    return con

def load_json(path):
    with open(path, "r") as f:
        dict_ = json.load(f)
    return dict_

def rm_dir(path):
    shutil.rmtree(path)

def rm_file(path):
    if os.path.isfile(path):
        os.remove(path)
        return

def write_2_json(dict_, path=None):
    if path is None:
        path=settings()["tmp_fol_loc"]+"url_fn_dict.json"
    with open(path, "w") as f:
        json.dump(dict_, f)


def create_folder(path):
    if not os.path.isdir(path):
        os.mkdir(path)
        print("Folder Created...@", path)


def search_algo(query, url_fn_dict):
    audio_names = []
    for fn in url_fn_dict:
        l=0
        qsplit = query.split()
        for q in qsplit:
            try:
                if len(qsplit)>1:
                    float(q)
            except:
                pass
            if [_ for _ in fn.lower().split() if q in _]:
                l+=1
            if len(qsplit)>1 and l>1:
                audio_names.append(url_fn_dict[fn]['path'])
            elif len(qsplit)==1 and l>0:
                audio_names.append(url_fn_dict[fn]['path'])
    return list(set(audio_names))

def get_m4a_file_path(song_path, _type):
    if _type=='link':
        fn, _ = os.path.splitext(song_path) 
    else:
        filename = os.path.splitext(os.path.basename(song_path))[0]
        fn = settings()['tmp_fol_loc'] + 'local-m4a-songs' + SLASH + filename 
    return fn + '.mp3'


def get_song_path():
    fn = settings()["tmp_fol_loc"] + "song-info.json"
    if os.path.isfile(fn):
        with open(fn) as f:
            dict_ = json.load(f)
        return dict_['song_path']
    return 

def get_window_size(root):
    return root.winfo_width(), root.winfo_height()

def calc_Chk_sum(text, algorithm='md5'):
    text_bytes = text.encode('utf-8')
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text_bytes)
    return hash_obj.hexdigest()

def filename_(path):
    return os.path.splitext(getFilename(path))[0]

def getSplit(url):
    if '%2F' in url:
        return '%2F'
    elif '\\' in url:
        return '\\'
    return '/'

def convert(seconds):
    hour = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    h, m, s= '', '0m:', '0s'
    if hour: h = f'{hour}h:'
    if minutes: m = f"0{minutes}m:" if minutes<9 else f"{minutes}m:"
    if seconds: s = f"0{seconds}s" if seconds<9 else f"{seconds}s"
    return h+m+s

def getPlainText(text):
    for i in switch_elts.keys():
        if i in text:
            text = text.replace(i, switch_elts[i])
    return text

def getFilename(url, remove_ascii=True):
    sp = getSplit(url)
    fn = url.split(sp)[-1]
    return getPlainText(fn) if remove_ascii else fn

def lyric_check(url, fold_path):
    url = os.path.splitext(url)[0]+'.lrc'
    res = requests.get(url, stream=True)
    fn = getFilename(url)
    if res.ok:
        with open(fold_path+fn, "wb") as f:
            f.write(res.content)

def count_audio_ext(links, ext='.lrc'):
    filter_ = filter(lambda x: os.path.splitext(x)[1] == ext, links)
    return len(list(filter_))
  
def txt_in_img(blur_label, image, text):
    blur_label.place(x=0, y=0, anchor='nw')
    draw = ImageDraw.Draw(image)
    font_path = settings()['font']['loading'].replace('\\', SLASH)
    font = ImageFont.truetype(font_path, 40) 

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_position = ((image.width - text_bbox[2]) // 2, (image.height - text_bbox[3]) // 2)
    draw.text(text_position, text, fill="white", font=font)
  
    updated_tk_image = get_TK_image(image)
    blur_label.configure(image=updated_tk_image)
    blur_label.image = updated_tk_image
    blur_label.tkraise()
    

def get_fn(fn, str_="  ✔"):
    return f'  {fn}{str_}'

def real_song_path(song_path):
    fn, ext = os.path.splitext(song_path)
    sp = fn+'.mp3' if ext=='.m4a' and os.path.isfile(fn+'.mp3') else song_path
    return sp

def readImage(path, size=(40,40), alpha=None, **border):
    image = Image.open(path)
    image = image.resize(size, Image.LANCZOS)
    if alpha:
        image = image.filter(ImageFilter.GaussianBlur(alpha))

    if border:
        _border_ = {'border_size':3, 'border_color':'black'}
        border = _border_ | border
        image = ImageOps.expand(image, border=border['border_size'], fill=border['border_color'])

    return image

def get_TK_image(image):
    return ImageTk.PhotoImage(image)

def get_Fname(file_path):
    sp = getSplit(file_path)
    fn = os.path.splitext(file_path.split(sp)[-1])[0]
    return getPlainText(fn)


def get_file_name_key(audio_file):
    index_link = get_index_link(audio_file, check_only=True)
    if index_link:
        fn =  file_name_link(audio_file, index_link)
    else:
        fn = get_Fname(audio_file)
    return fn.lstrip()

def rm_str(string, rm_str):
    return string.replace(rm_str, '')

def file_name_link(link, index_link):
    tmpDir = rm_str(link, index_link) 
    return get_Fname(tmpDir)

def get_audio_links(links):
    return list(filter(lambda x: os.path.splitext(x)[1] != '.lrc', links))

def get_local_files(path):
    fp_list = []
    for i, _, files in os.walk(path):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in settings()["allowed_ext"] and ext!='.lrc':
                fp_list.append(i+SLASH+file)
    return fp_list
   
def getMetaData(audio_path, default_img):
    tmp_fp = settings()["tmp_fol_loc"]

    tag = TinyTag.get(audio_path, image=True)
    keys = ['album', 'title', 'artist', 'albumartist', 'duration', 'genre']
    meta_data_dict = dict.fromkeys(keys, "Unknown")
    for key in keys:
        meta_data_dict[key] =  eval(f"tag.{key}")
    image_data = tag.get_image()
    is_local = audio_path.split(getSplit(audio_path))[-3] != tmp_fp.split(getSplit(tmp_fp))[-2]

    fn = os.path.splitext(os.path.basename(audio_path))[0]
  
    if is_local:
        audio_dir = tmp_fp + 'local-imgs'
    else:
        audio_dir = os.path.dirname(audio_path)
    audio_dir += SLASH
    
    if image_data:
        tmp_fp = audio_dir + fn +'.jpg'
        if not os.path.isfile(tmp_fp):
            with open(tmp_fp, "wb") as f:
                f.write(image_data)
        try:
            Image.open(tmp_fp)
        except:
            os.remove(tmp_fp)
            tmp_fp = default_img
    else:
        tmp_fp = default_img # default image

    meta_data_dict['image-path'] = tmp_fp
    return meta_data_dict


def check_shuffle(pre_dict, post_dict):
    for key in pre_dict:
        idx1, idx2 = pre_dict[key]['idx'], post_dict[key]['idx']
        if idx1==idx2:
            return False
    return True

def max_shuffle(info_dict, info_dict2):   
    i = 0
    while True:
        if check_shuffle(info_dict, info_dict2):
            break
        info_dict2 = shuffle_songs(info_dict2)
        i+=1
    return info_dict2

def shuffle_songs(info_dict):  
    tmp_dict = copy.deepcopy(info_dict)
    keys = list(tmp_dict.keys())
    random.shuffle(keys)
    shuffled_data = {}
    for idx, key in enumerate(keys):
        tmp_dict[key]['idx'] = idx
        shuffled_data[key] = tmp_dict[key]
    return shuffled_data

def get_dynamic_WH(root, key, return_all=False):
    setting = settings()
    ctrl_frame_h_per = setting["ctrl-frame"]["height_per"]
    frame_width = setting["hover-frame"]["frame-width"]
    inc_W = setting["inc_W"]

    w, h = get_window_size(root)
    frame_side_bar_h = h - int(h * ctrl_frame_h_per)
    ctrl_h = h - frame_side_bar_h
    main_frame_w = w - frame_width
    lb_w = int ( (main_frame_w-inc_W*2) * 0.0889 )

    dict_ = {
        'win-dim'   : {'w':w, 'h':h},
        'frame'     : {'w':frame_width, 'h':frame_side_bar_h},
        'main_frame': {'w':main_frame_w, 'h':frame_side_bar_h, 'x':frame_width+5, 'y':5},
        'scrollbar' : {'x':main_frame_w-30, 'y':90, 'h':530},
        'ctrl_frame': {'w':w, 'h':ctrl_h, 'x':0, 'y':int(frame_side_bar_h + inc_W + inc_W/2)},
        'listbox'   : {'w':lb_w, 'h':22}
    }

    if return_all:
        return dict_
    
    if key not in dict_:
        print(f" !!  key: {key} not found in dict..... ")
    return dict_.get(key, {})


def screen_size(root, mode='unlock'):
    if mode=='lock':
        W_, H_ = get_window_size(root)
        root.maxsize(W_, H_)
        return

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.maxsize(screen_width, screen_height)

with open(CONFIG_PATH + "ASCII-Encoding.json") as f:
    switch_elts = json.load(f)
