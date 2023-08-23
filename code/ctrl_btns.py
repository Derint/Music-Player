from __buttons import enable_disable_ctrl_btn, remove_btn, get_frame_height, ctrl_x_cord
from tk_widgets import *
from globals_vars import *
from Helper_file import *
from threading import Thread
import os, re, subprocess
from network_functions import getRequest


def hide_btn(dict_):
    for key in dict_:
        d = dict_[key]
        if 'type' in d.keys():
            if key in ['song-name', 'song-art']:
                continue
            d['label'].place_forget()
            continue
        d['button'].place_forget()

def update_time_label(slider_val):
    ctrl_btn_dict['song_time']['label'].configure(text=convert(int(slider_val)))

       
def clear_lbl(keys):
    for key in keys:
        ctrl_btn_dict[key]['label'].config(text="")
  
def update_audio_MD(metadata):
    title = metadata['title']
    artist = metadata['artist']

    _title, _artist  = "Title : ", "Artist : "
    song_path = get_song_path()
    sp = getSplit(song_path)

    song_title = os.path.splitext(song_path.split(sp)[-1])[0]
    _title += song_title  if title in [None, ''] else title
    _artist += "Unknown Artist" if artist in [None, ''] else artist

    clear_lbl(['song-name', 'song-art'])
    ctrl_btn_dict['song-name']['label'].config(text=_title)
    ctrl_btn_dict['song-art']['label'].config(text=_artist)
    show_image(metadata['image-path'])
    

def btn_play():
    global is_paused, is_playing
    if is_paused:
        mixer.music.unpause()
        is_paused=False
        is_playing=True
        enable_disable_ctrl_btn(ctrl_frame, 'pause', 'play', ctrl_btn_dict)
        return
    
    if is_playing:  
        play_song()

def show_info():
    dwd_canvas.place_forget()
    hide_btn(ctrl_btn_dict)
    x = ctrl_x_cord(ctrl_frame, ctrl_btn_dict['play'], None) * 0.65
    y = get_frame_height(ctrl_frame, 10, True)
    ctrl_info_label.configure(text=f'Converting .M4A to .MP3')
    ctrl_info_label.place(x=x, y=y)

def convert_to_wav(m4a_file_path, song_type, metadata, format='.mp3'):
    show_info()
    mixer.music.pause()
    root.update()
    
    if song_type=='link':
        fn = os.path.splitext(m4a_file_path)[0] + format
    else:
        fn = get_m4a_file_path(m4a_file_path, song_type)
    song_time = metadata['duration']
    ffmpeg_path = FFMPEG_EXE if os.name in ['dos', 'nt'] else  '/usr/bin/ffmpeg'
    ffmpeg_command = [
        ffmpeg_path, "-i", m4a_file_path, fn
    ]

    if os.name in ['nt', 'dos']:
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    else:  
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    while True:
        line = process.stderr.readline()
        rslt = re.search(r'time=(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2}).(?P<ms>\d{2})', line)

        if rslt:
            h, m, s, ms = int(rslt['h']), int(rslt['m']), int(rslt['s']), int(rslt['ms'])
            cur_song_time = h*360+m*60+s+ms/1000
            cur_song_time = str(f"{cur_song_time/song_time*100:.2f}%").center(10)
            ctrl_info_label.configure(text=f'Converting .M4A to .MP3 ({cur_song_time})')
           
        if not line:
            break

    process.wait()

    if song_type=='link':
        rm_file(m4a_file_path)
    
    ctrl_info_label.place_forget()
    place_ctrl_btn(ctrl_frame)
    real_play_song(fn, metadata)
 

def convert_thread(song_path, song_type, metadata):
    t = Thread(target=convert_to_wav, args=(song_path, song_type, metadata))
    t.start()

def change_row_color(song_path, key=None, color='song_color'):
    if key is None:
        key = get_file_name_key(song_path)
    tree_id = url_fn_dict[key]['tree-id']
    tree.item(tree_id, tags=(color,))


def play_song():   
    song_path = get_song_path()
    fn, ext = os.path.splitext(song_path)
    sp = fn+'.mp3' if ext=='.m4a' and os.path.isfile(fn+'.mp3') else song_path

    metadata = getMetaData(sp, IMAGE_DIR + "song.png")
    update_audio_MD(metadata)
    
    if ext=='.m4a':
        key = get_file_name_key(song_path)
        song_type = url_fn_dict[key]['song-type']
        fp = get_m4a_file_path(song_path, song_type)
        cvt_cond = os.path.isfile(fp)
       
        if cvt_cond :
            sp = fp
        else:
            convert_thread(sp, song_type, metadata)
            return
    real_play_song(sp, metadata)
    root.update()

    

def real_play_song(song_path, metadata):
    global is_playing, to_val, shuffle, repeat, pos, is_slider_mvd, old_song_path
    
    if old_song_path and os.path.isfile(old_song_path):
        key = get_file_name_key(old_song_path)
        change_row_color(old_song_path, color=url_fn_dict[key]['row-color'])
    change_row_color(song_path)

    val = get_tree_values(tree)
    key = val[0].replace(' \u2714', '').strip()
    selected_item = get_file_name_key(song_path)
   
    if key != selected_item:
        d = url_fn_dict[key]
        c = lb_colors[0] if d['row-color']=='odd_row' else lb_colors[1]
        style.map("Treeview", background =[('selected', c)], foreground= [('selected', 'black')])
    else:
        style.map("Treeview", background =[('selected', song_highlight_color)], foreground= [('selected', 'black')])

    try:
        if not is_playing:
            mixer.music.unload()

        mixer.music.load(song_path)
        mixer.music.play()

        pos, is_slider_mvd, is_playing = 0, False, True
        enable_disable_ctrl_btn(ctrl_frame, 'pause', 'play', ctrl_btn_dict)
        
        to_val = metadata['duration']
        if to_val in [None, '']:
            to_val = mixer.Sound(song_path).get_length()
        old_song_path = song_path
        update_time_label(to_val)
        update_slider()

    except Exception as e:
        print("Exception Occured::", e)
        show_msg(show_msg_lbl, str(e)[:25]+'...', 5)
        print("================================")

    
def on_slider_drag(event_):
    global is_slider_mvd, to_val, slider_val, x
    mixer.music.pause()
    x = event_.x
    is_slider_mvd=True
    x = max(min(x, 10 + slider_width), 10) 
    slider_val = (x - 10) / slider_width * (to_val - from_val) + from_val
    
    mixer.music.set_pos(slider_val)
    reset_slider_canvas_cords(x)
    

def reset_slider_canvas_cords(x, up=None):
    cl_cords, inCl_cords, slider_cords, t = get_coords(x, up)
    slider_canvas.coords(complete_line, cl_cords)
    slider_canvas.coords(incomplete_line, inCl_cords)
    slider_canvas.coords(slider, slider_cords)
    slider_canvas.coords(slider_text, t)


def get_coords(x, up=None):
    global is_playing
    y = sl_y - slider_radius
    s_y = 1
    if setting['dwd']=='True' or up:
        y *= 0.7
        s_y = 0.7
    
    sl_y0, sl_y1 = (sl_y*0.868*s_y) - slider_radius, (sl_y*0.868*s_y) + slider_radius
    inCl_cords = x, y, slider_width + slider_radius, y
    cl_cords = slider_radius, y, x, y

    slider_cords = x - slider_radius, sl_y0, x + slider_radius, sl_y1
    if setting['dwd']=='True' and is_playing==False:
        slider_cords = 12 - slider_radius, sl_y0,  12 + slider_radius, sl_y1

    center_x = (slider_cords[0] + slider_cords[2])*0.5
    center_y = (slider_cords[1] + slider_cords[3])*0.35
    cords = (center_x, center_y)
    if setting['dwd']=="True":
        ctrl_btn_dict['song_time']['label'].place(y=y*1.3)
    return cl_cords, inCl_cords, slider_cords, cords


def update_slider():
    global is_playing, to_val, slider_val, is_slider_mvd, pos
    
    if is_playing:
        if is_slider_mvd==True:
            pos = slider_val
            is_slider_mvd=-1
        elif is_slider_mvd==-1:
            pos += 50/1000 #root.after
        else:
            try:
                pos = mixer.music.get_pos()/1000
            except:
                return
            
        if pos>to_val or pos<0:
            move_slider_to_value(0, to_val)
            update_time_label(0)
            enable_disable_ctrl_btn(ctrl_frame, 'play', 'pause', ctrl_btn_dict)
            btn_nxt()
            return
        move_slider_to_value(pos, to_val)

    root.update_idletasks()
    root.update()
    root.after(50, update_slider)



def move_slider_to_value(slider_val, to_val):
    global from_val, x
    x = (slider_val - from_val) / (to_val - from_val) * slider_width + 10
    slider_canvas.itemconfigure(slider_text, text=f"{convert(int(slider_val))}")
    reset_slider_canvas_cords(x)


def get_tree_values(tree, item_only=None):
    item = tree.selection()[0]
    if item_only:
        return item
    values = tree.item(item, 'values')
    return values if values else None

def song_path(link):
    rp = get_index_link(link)
    key = rm_str(link, '' if rp is None else rp)
    audio_dir = tmp_fold + calc_Chk_sum(key) 
    fn = os.path.splitext(getPlainText(key.split('/')[-1]))[0]
    return audio_dir, fn

def play_song_2(selected_item, index):
    global url_fn_dict, is_playing
    
    if url_fn_dict=={} or setting["is_updated"]:
        url_fn_dict = load_json(tmp_fold+"url_fn_dict.json")
        if shuffle:
            btn_shuff_off()

    item = url_fn_dict[selected_item]
    _song_type = item['song-type']
    path = item['path']

    if _song_type=='link':
        audio_dir, fn = song_path(path)

    if _song_type=='local' or os.path.isfile(audio_dir+ SLASH + fn+'.mp3'):
        is_playing=True
        if _song_type=='link':
            path = audio_dir + SLASH + getFilename(path)
        item['song_path'] = path
        update_song_info(item)
        btn_state(ctrl_btn_dict, NORMAL)
        btn_play()
        
    elif index and setting['dwd']=="False": 
        _w_, h = get_window_size(root)
        frame_side_bar_h = h - int(h*ctrl_frame_h_per)
      
        x = ctrl_x_cord(ctrl_frame, ctrl_btn_dict['play'], None)*0.93
        y = int(frame_side_bar_h)*1.18

        w, h_ = (i_w+p_wh)*1.4, (i_h+p_wh)*1.4
        
        dwd_canvas.config(width=w, height=h_, bd=0, bg=ctrl_bg_c)
        dwd_canvas.place(x=x, y=y)

        dr = 12 if 1080 <= _w_ <= 1200 else 16
        button_x, button_y, radius = x//dr, (h_)*0.52, 30
        image_path = IMAGE_DIR + "play.png"
        draw_progress(root, ctrl_frame, dwd_canvas, path, (button_x, button_y), radius, image_path, tree, index, selected_item)
        return
    

def get_key(key, dict_):
    for k, v in dict_.items():
        if key==v['idx']:
            return k
    return -1

def song(mode='next'):
    global shuffle, url_fn_dict, repeat
    sp = get_song_info()["song_path"]
    song_idx = url_fn_dict[get_file_name_key(sp)]['idx']
    
    if not repeat:
        cond_nxt = song_idx+1>=len(url_fn_dict)
        cond_prev = song_idx-1<0

        if cond_prev and mode!='next':
            show_msg(show_msg_lbl, "End of Song List....", 4)
            return

        if cond_nxt and mode=='next':
            show_msg(show_msg_lbl, "End of Song List....", 4)
            return
    
    idx = song_idx+1 if mode=='next' else song_idx-1
    if repeat:
        idx = song_idx
    key = get_key(idx, url_fn_dict)
    
    return key, idx

def btn_pre():
    _ = song('prev')
    if _:
        key, song_idx = _
        play_song_2(key, (song_idx, ))

def btn_nxt():
    _ = song()
    if _:
        key, song_idx = _
        play_song_2(key, (song_idx, ))

def btn_pause():
    global is_paused, is_playing
    enable_disable_ctrl_btn(ctrl_frame, 'play', 'pause', ctrl_btn_dict)
    mixer.music.pause()
    is_paused=True
    is_playing=False

def btn_shuff_on():
    global shuffle, url_fn_dict
    enable_disable_ctrl_btn(ctrl_frame, 'shuff-off', 'shuff-on', ctrl_btn_dict)
    shuffle=False
    url_fn_dict = load_json(tmp_fold+"url_fn_dict.json")
    song_dict = get_song_info()
    fn = filename_(song_dict['path'])
    song_dict['idx'] = url_fn_dict[fn]['idx']
    

def btn_shuff_off():
    global shuffle,  url_fn_dict
    enable_disable_ctrl_btn(ctrl_frame, 'shuff-on', 'shuff-off', ctrl_btn_dict)
    shuffle=True
    old_dict = url_fn_dict
    url_fn_dict = max_shuffle(old_dict, url_fn_dict)
    

def btn_repeat_on():
    global repeat
    repeat=False
    enable_disable_ctrl_btn(ctrl_frame, 'repeat-off', 'repeat-on', ctrl_btn_dict)
    
def btn_repeat_off():
    global repeat
    repeat=True
    enable_disable_ctrl_btn(ctrl_frame, 'repeat-on', 'repeat-off', ctrl_btn_dict)



def show_image(image_path):
    img = get_TK_image(readImage(image_path, (120, 150)))
    img_lbl.configure(image=img)
    img_lbl.image=img

def add_ctrl_btn(frame, ctrl_bg_c):
    by_default_off = ['pause', 'shuff-on', 'repeat-on']
    ctrl_center_y = get_frame_height(frame, 10, True)
    W, H = frame.winfo_reqwidth() // 2, frame.winfo_reqheight()//2
    for key in ctrl_btn_dict:
        d = ctrl_btn_dict[key]

        if 'type' in d.keys():
            txt = d['txt']
            label = Label(frame, bg=ctrl_bg_c, font=(15, 14))
            if key=='song_time':
                x, y = W + d['pos'], H * 0.8
                label.config(font=(18, 12), bg='lightgreen')
            elif key=='song-name':
                x, y =  W * 0.35, H * 0.1
                label.config(font=(15, 15), fg=setting['song']['title-fg'])
            elif key =='song-art':
                x, y = W * 0.35, H*0.35
                label.config(fg=setting['song']['album-fg'])
  
            label.config(text=txt)
            label.place(x=x, y=y)
            ctrl_btn_dict[key]['label'] = label
            continue 
        
        x = ctrl_x_cord(frame, d, key)
        button = Button(frame, image=d['img'], command=eval(d['cmd']), relief=FLAT, bg=ctrl_bg_c, activebackground=ctrl_bg_c, bd=0, highlightbackground=ctrl_bg_c)

        button.place(x=x, y=ctrl_center_y+30, anchor='center')
        ctrl_btn_dict[key]['button'] = button
        if key not in ['play', 'pause']:
            Tooltip(button, d['name'])

        if key in by_default_off:
            remove_btn(d['button'])
    btn_state(ctrl_btn_dict) # Initially All the buttons should be disabled..
 

def btn_state(dict_, state_=DISABLED):
    for key in dict_:
        if 'type' in dict_[key]:
            continue
        dict_[key]['button'].config(state=state_)

def threading(root, ctrl_frame, canvas, url, prog_arc, tree, index, selected_item):
    t1 = Thread(target=dwd_file, args=(root, ctrl_frame, canvas, url, prog_arc, tree, index, selected_item))
    t1.start()

def create_concentric_circle(canvas, x, y, r, start_angle, extent_angle, style=None, **options):
    x1, y1 = x - r,  y - r
    x2, y2 = x + r,  y + r
    return canvas.create_arc(x1, y1, x2, y2, start=start_angle, extent=extent_angle, style=style, **options)

def getFill(per):
    return 360 * per * -1

def draw_circles(canvas, button_x, button_y, r):
    create_concentric_circle(canvas, button_x, button_y, r, 0, 359.99999,  width=1, style=ARC)
    create_concentric_circle(canvas, button_x, button_y, r + 10, 0, 359.99999, fill=setting["dwd_prog"]['circle_bg'], width=2, style=ARC)
  
def draw_rounded_image(canvas, x, y, radius, image_path):
    canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=setting["dwd_prog"]["img_bg"])
    image = readImage(image_path)
    image = get_TK_image(image)
    stop_btn.config(command=stop_cmd, image=image)
    stop_btn.place(x=x-radius//1.4, y = y-radius//1.4)
    stop_btn.image = image

def stop_cmd():
    global stop
    stop=True

def dwd_file(root, ctrl_frame, canvas, url, prog_arc, tree, index, selected_item): 
    global stop, is_playing, url_fn_dict, x
    setting['dwd']="True"
    res = getRequest(url, 2)

    if res==-1 or res.status_code!=200:
        if res ==-1:
            txt = "Failed to Connect With Server...."
        else:
            txt = f"Response Code: {res.status_code}"
        show_msg(show_msg_lbl, txt, 4)
        print(f"!!! Something went wrong.... [{txt}]\n")
        reset_ctrl_canvas(root, ctrl_frame, canvas)
        setting['dwd']="False"
        return
    
    fn = getFilename(url)
    key = rm_str(url, get_index_link(url, check_only=True)) #So if the index link change, no need to download the audio again
    audio_loc = tmp_fold + calc_Chk_sum(key) + SLASH
    
    if not os.path.isdir(audio_loc):
        os.mkdir(audio_loc)
    
    tl, s = int(res.headers['Content-Length']), 0
    fp = audio_loc+fn

    _ = True
    try:
        if len(fn)>25:
            fn = fn[:25] + '...'
        show_msg(show_msg_lbl, f"Downloading: {getPlainText(fn)}", 5)
        with open(fp, "wb") as f:
            for chunk in res.iter_content(1024 * 10):
                canvas.itemconfigure(prog_arc, extent=getFill(s/tl))
                s+=len(chunk)
                f.write(chunk)
                if stop:
                    break
    except:
        show_msg(show_msg_lbl, "Error while Downloading the File", 6)
        print("Error while Downloading the File")
        rm_dir(audio_loc)
        _ = False

    if stop:
        show_msg(show_msg_lbl, "Downloading Stop...")
        rm_dir(audio_loc)
        stop=False
        _ = False
    
    elif _:
        # lyric_check(url, audio_loc) # 'll use later
        item = url_fn_dict[selected_item]['tree-id']
        tree.item(item, values=(get_fn(selected_item), index, fp))
        dict_ = url_fn_dict[selected_item]
        dict_['song_path'] = fp
        update_song_info(dict_)
        is_playing=True
        _ = True

    state = DISABLED if stop else NORMAL
    reset_ctrl_canvas(root, ctrl_frame, canvas, state)
    setting['dwd']="False"

    if _:
        btn_play()

    slider_canvas.itemconfigure(slider_text, state="normal")
    show_msg_lbl.place_forget()

def reset_ctrl_canvas(root, ctrl_frame, canvas, state=NORMAL):
    global is_playing
    cf_dict = get_dynamic_WH(root, 'ctrl_frame')
    canvas.place_forget()
    ctrl_frame.config(width=cf_dict['w'], height=cf_dict['h'])
    ctrl_frame.place(x=cf_dict['x'], y=cf_dict['y'])
    btn_state(ctrl_btn_dict, state)
    if not is_playing:
        enable_disable_ctrl_btn(ctrl_frame, 'play', 'pause', ctrl_btn_dict)


def draw_progress(root, ctrl_frame, canvas, url, btn_cord, radius, image_path, tree, index, selected_item):
    global x, is_playing
    slider_canvas.itemconfigure(slider_text, state="hidden")
    
    btn_state(ctrl_btn_dict)
    remove_btn(ctrl_btn_dict['play']['button'])
    button_x, button_y = btn_cord
    canvas.delete("all")
    reset_slider_canvas_cords(x, up=True)
    prog_arc = create_concentric_circle(canvas, button_x, button_y, radius+10, 90, 0, PIESLICE, fill=setting['dwd_prog']['circle_bg'])
    draw_rounded_image(canvas, button_x, button_y, radius, image_path)
    draw_circles(canvas, button_x, button_y, radius)
    threading(root, ctrl_frame, canvas, url, prog_arc, tree, index, selected_item)

def place_ctrl_btn(frame):
    global is_playing, is_paused, shuffle, repeat
    hide_btn(ctrl_btn_dict)
    ctrl_center_y = get_frame_height(frame, 10, True)
    for key in ctrl_btn_dict:
        d = ctrl_btn_dict[key]
        if 'type' in d.keys():
            if key in ['song-name', 'song-art']:
                continue
            fw, fh = frame.winfo_reqwidth() // 2 , frame.winfo_reqheight()//2
            if key=='song_time':
                x, y =fw  + d['pos'], fh * 0.8
            elif key=='song-name':
                x, y = fw * 0.35,  fh * 0.1
            elif key =='song-art':
                x, y = fw * 0.35, fh * 0.35
            d['label'].place(x=x, y=y)
            continue

        x = ctrl_x_cord(frame, d, key)
        d['button'].place(x=x, y=ctrl_center_y+30, anchor='center')

    if is_playing:
        enable_disable_ctrl_btn(ctrl_frame, 'pause', 'play', ctrl_btn_dict)

    else:
        enable_disable_ctrl_btn(ctrl_frame, 'play', 'pause', ctrl_btn_dict)

    if shuffle:
        enable_disable_ctrl_btn(ctrl_frame, 'shuff-on', 'shuff-off', ctrl_btn_dict)
    else:
        enable_disable_ctrl_btn(ctrl_frame, 'shuff-off', 'shuff-on', ctrl_btn_dict)

    if repeat:
        enable_disable_ctrl_btn(ctrl_frame, 'repeat-on', 'repeat-off', ctrl_btn_dict)
    else:
        enable_disable_ctrl_btn(ctrl_frame, 'repeat-off', 'repeat-on', ctrl_btn_dict)


def on_release(event):
    mixer.music.unpause()



# Initial Slider 
canvas_width = w*0.7
slider_width = canvas_width-50

sl_y = 75
y = sl_y - slider_radius
sl_y0, sl_y1 = (sl_y*0.868) - slider_radius, (sl_y*0.868) + slider_radius

inCl_cords = 0, y, slider_width + slider_radius, y
cl_cords = slider_radius, y, 0, y
slider_cords = 12 - slider_radius, sl_y0,  12 + slider_radius, sl_y1

center_x = (slider_cords[0] + slider_cords[2])*0.5
center_y = (slider_cords[1] + slider_cords[3])*0.35


slider_color = setting["slider"]
complete_line = slider_canvas.create_line(cl_cords, fill=slider_color['cl_color'], width=2)
incomplete_line = slider_canvas.create_line(inCl_cords, fill=slider_color['incl_color'], width=2)
slider = slider_canvas.create_oval(slider_cords, fill=slider_color['color'])
slider_text = slider_canvas.create_text(center_x, center_y, text="", fill="white")

slider_canvas.tag_bind(slider, '<B1-Motion>', lambda event : on_slider_drag(event))
slider_canvas.tag_bind(slider, '<ButtonRelease-1>', lambda event: on_release(event))


shuffle_song_dict = {}

is_paused=False
is_playing=False
repeat = False
is_slider_mvd=False
shuffle = False
stop = False
x=0
pos = 0
old_song_path = ''

url_fn_dict = {}
from_val=0
to_val = 0
