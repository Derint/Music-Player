
from bind_funcs import *
from tk_widgets import *
from Helper_file import *
from globals_vars import tmp_fold
from network_functions import *
import os
import concurrent.futures
from threading import Thread


def add_side_bar_btn():
    for i in menu_bar_dict.keys():
        d = menu_bar_dict[i]
        button = Button(frame, image=d['img'], bg=sideBarFrame_color, relief='flat', activebackground=on_click_color, highlightbackground=sideBarFrame_color)
        button.place(x=d['img-x'], y=d['img-y'])
        button.bind("<Enter>", lambda event: on_enter_sb(hover_frame, event, btn_highligth_color))
        button.bind("<Leave>", lambda event: on_leave_sb(hover_frame, event, sideBarFrame_color))
        button.config(command= eval(d['cmd']))
        menu_bar_dict[i]['btn'] = button


def start_thread():
    global links
    show_msg(show_msg_lbl, "Searching for New Songs", keep_it=True)
    with open(tmp_fold + 'folder-paths.txt') as f:
        con = f.read().split('\n')
    if con[0] == '':
        con[0] = url

    with concurrent.futures.ThreadPoolExecutor(3) as executor:
        futures = []
        for link in con:
            future = executor.submit(crawler, link, index_link)
            futures.append(future)
        concurrent.futures.wait(futures)

    for future in concurrent.futures.as_completed(futures):
        try:
            links.extend(future.result())
        except Exception as e:
            pass
    
    show_msg_lbl.place_forget()
    links = list(set(links))
    audio_files = get_files(links)
    on_refresh(audio_files)

def thread_start():
    t = Thread(target=start_thread)
    t.start()


def get_files(links, folder_path=''):
    if folder_path:
        audio_links = get_local_files(folder_path)
    else:
        audio_links = get_audio_links(links)
    return audio_links



def song_list_dict(songs):
    global index_link
    url_fn_dict = {}
    song_type = 'link' if index_link else 'local'
    songs = sorted(songs)
    for i, song in enumerate(songs):
        if song.endswith('.lrc'):
            continue
        fn = get_file_name_key(song)
        if fn not in url_fn_dict.keys():
            url_fn_dict[fn] = {'idx':i, 'song-type':song_type, 'path':song}
    return url_fn_dict


def is_dwd(path, fn):
    global url_fn_dict
    str_ = ""
    if url_fn_dict[fn]['song-type']=='link':
        key = rm_str(path, index_link)
        fol = calc_Chk_sum(key)
        if key.endswith('.m4a'):
            key = key.replace('.m4a', '.mp3')
        audio_file =  tmp_fold + fol + SLASH + getPlainText(key.split('/')[-1])
        str_ = "  ✔" if os.path.isfile(audio_file) else ""
    return str_


def clean_tree():
    for item in tree.get_children():
        tree.detach(item)

def get_song_id(song):
    global url_fn_dict
    key = get_file_name_key(song)
    _id_ = url_fn_dict[key].get('tree-id', None)
    return _id_ if _id_ else '' 

def get_song_ids(songs):
    return [get_song_id(song) for song in songs]


def list_songs(songs):
    global is_p2_initial, url_fn_dict, is_search
    clean_tree()

    songs_ids = get_song_ids(songs)
    songs = [url_fn_dict[key]['path'] for key in url_fn_dict]
    songs = sorted(songs)
    idx = 0
    for i, audio_file in enumerate(songs):
        fn = get_file_name_key(audio_file)
        str_ = is_dwd(real_song_path(audio_file), fn)
        r_c = 'odd_row' if idx%2!=0 else 'even_row'
        _song_id = get_song_id(audio_file)

        if is_search:
            if not (_song_id in songs_ids):
                tree.detach(_song_id)
                continue
        
        if 'tree-id' in url_fn_dict[fn]:
            item = url_fn_dict[fn]['tree-id']
            tree.item(item, tags=(item, r_c)) 
            tree.move(item, '', 'end')
        else:
            item = tree.insert('', 'end', values=(get_fn(fn, str_), i, audio_file), tags=(r_c,))
            url_fn_dict[fn]['tree-id'] = item

        url_fn_dict[fn]['row-color'] = r_c
        idx +=1
 
    if is_p2_initial:
        blur_label.place_forget()
        root.resizable(True, True)
        is_p2_initial=False

    if is_search:
        is_search = False

    if len(tree.get_children()) > 16:
        w, h = get_window_size(root)
        frame_side_bar_h = h - int(h*ctrl_frame_h_per)
        scrollbar.place(x =(w - frame_width)*0.982, y=50, height=frame_side_bar_h*0.88)

   
def clear_entry():
    entry.delete(0, END)
    search_btn.config(state=NORMAL)
    entry.configure(bg=setting['input']['bg'])


def update_dict(info_dict, audio_files):
    global index_link
    song_type = 'link' if index_link else 'local'
    updated_list = []
    for file in audio_files:
        key = filename_(file)
        if not info_dict.get(key, False):
            updated_list.append(file)
    
    if not updated_list:
        return info_dict
 
    dict_ = {}
    idx = len(info_dict)
    for path in updated_list:
        key = filename_(path)
        dict_[key] = {"idx":idx, "song-type":song_type, "path":path}
        idx+=1
    return info_dict | dict_


def crawler(url, index_link):
    req = getRequest(url, max_tries=1)
    links = []
    if req==-1:
        return
    soup = BeautifulSoup(req.content, features='html.parser')
    for href in soup.find_all('a'):
        try:
            if href.text == '..':continue
            link = nextLink(url, href, index_link)
            ext = os.path.splitext(href.text)[1]
            if ext in settings()["allowed_ext"]:
                links.append(link)      
        except:
            pass
    return links 
    
def search():
    global url_fn_dict, file_path, is_search
    query = entry.get()
    if query in [placeholder, '']:
        return

    query = query.strip().lower()
    audio_names = search_algo(query, url_fn_dict)

    if not audio_names:
        search_btn.config(state=DISABLED)
        entry.configure(bg=entry_bg_invalid, font=(18, 18))
        entry.delete(0, END)
        entry.insert(0, " !!! No SONG Found...")
        root.after(3000, clear_entry)
        return

    is_search=True
    audio_links = audio_names # for local songs...
    if not file_path:
        audio_links= get_files(audio_names, file_path)
    list_songs(audio_links)


def second_window():
    global canvas_width, slider_width
    frame.place(x=0, y=5)
    ctrl_frame.pack_propagate(False)
    tree.place(x=5, y=50)
    img_lbl.place(x=10, y=20)


def Window_2(**additional):
    global index_link, url, links, url_fn_dict, file_path
    
    txt_in_img(blur_label, blur_image, "Loading....") 
    root.update()
    
    additional = additional['args']
    if 'file_path' in additional:
        file_path = additional.get('file_path').replace('/', SLASH)
    else: 
        links = additional['links']
        url = additional['url']
        index_link = get_index_link(links[0], True)
    
    entry.config(fg='grey')
    other_dict['search']['button'] = search_btn.config(command= search)
    other_dict['refresh']['button'] = refresh_btn.config(command= lambda : refresh(file_path))
    
    resize_window_frames()
    second_window()
    add_side_bar_btn()

    files = get_local_files(file_path) if file_path else links
    url_fn_dict = song_list_dict(files)
    audio_links = get_files(links, file_path)
    list_songs(audio_links)

    write_2_json(url_fn_dict)
    bind_all_btns()


def all_songs():
    global url_fn_dict, filepath, links
    audio_links = get_files(links, file_path)
    list_songs(audio_links)
    

def on_refresh(audio_files):
    global url_fn_dict, file_path, links
    upd_dict = update_dict(url_fn_dict, audio_files)
    
    if len(upd_dict)==len(url_fn_dict):
        show_msg(show_msg_lbl, "All Songs Up-to-Date", 5)
        return
    
    n = len(upd_dict) - len(url_fn_dict) 
    
    url_fn_dict = url_fn_dict | upd_dict
    n_ = dict.fromkeys(url_fn_dict, {})
    for idx, key in enumerate(sorted(url_fn_dict)):
        n_[key] = url_fn_dict[key]
        n_[key]['idx'] = idx
    url_fn_dict = n_

    show_msg(show_msg_lbl, f"Song List Updated... (added {n} songs)", 5)
    setting["is_updated"]=True
    links = [url_fn_dict[key]['path'] for key in url_fn_dict]
    audio_links= get_files(links, file_path)
    list_songs(audio_links)
    write_2_json(url_fn_dict)



def refresh(fold_path):
    global links
    if links:
        thread_start()
        return 
    audio_files = get_files([], fold_path)
    on_refresh(audio_files)
    

file_path = ''  
setting["is_updated"]=False
is_p2_initial = True
url_fn_dict = {}
index_link = ''
links = []
url = ''
is_search=False

def playlist():
    print("Playlist button clicked...")
    messagebox.showinfo("Upcoming Update", "This Button will be functional in the upcoming Update")


def new_playlist():
    print("new playlist button click")
    messagebox.showinfo("Upcoming Update", "This Button will be functional in the upcoming Update")

