from __buttons import get_frame_height, ctrl_x_cord
from ctrl_btns import add_ctrl_btn, play_song_2, place_ctrl_btn, get_tree_values
from globals_vars import *
from tk_widgets import *
from Helper_file import get_window_size, rm_dir, get_local_files, rm_file


def on_enter_sb(frame, event, btn_highligth_color):
    x, y, width, height = event.widget.winfo_x(), event.widget.winfo_y(), event.widget.winfo_width(), event.widget.winfo_height()
    frame.place(x=x - 5, y=y - 5, width=width + 10, height=height + 10)
    event.widget.config(bg=btn_highligth_color)

def on_leave_sb(frame, event, sideBarFrame_color):
    frame.place_forget()
    event.widget.config(bg=sideBarFrame_color)


def on_focus_in(_, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, END)
        entry.config(fg=setting['input']['f-in-fg'])

def on_focus_out(_, entry, placeholder):
    if entry.get() == '':
        entry.insert(0, placeholder)
        entry.config(fg=setting['input']['f-out-fg'])


def on_double_click(_):
    selected_item, idx, path = get_tree_values(tree)
    selected_item = selected_item.replace("  \u2714", "").lstrip()
    play_song_2(selected_item, idx)
   

def expand(e):
    global cur_width, expanded
    cur_width += 10 
    rep = root.after(5, expand, e) 
    frame.config(width=cur_width)
    if cur_width >= max_w:
        expanded = True
        root.after_cancel(rep)
        fill()

def contract(e):
    global cur_width, expanded
    cur_width -= 10
    rep = root.after(5, contract, e) 
    frame.config(width=cur_width) 
    if cur_width <= min_w:
        expanded = False 
        root.after_cancel(rep)
        fill()

def fill():
    for i in menu_bar_dict.keys():
        d = menu_bar_dict[i]
        btn = d['btn']

        img = '' if expanded else d['img']
        text = d['txt'] if expanded else ''
        width = 15 if expanded else d['pre']
        anchor = 'nw' if expanded else 'c'
        btn.config(text=text, image=img, font=(0, 21), width=width, bg=sideBarFrame_color, anchor=anchor)

        x = d['txt-x'] if expanded else d['img-x']
        y = d['txt-y'] if expanded else d['img-y']+inc_W
        btn.place(x=x, y=y)

    w, h = get_window_size(root)
    main_frame_w = w - frame_width
    w_ = w - frame.winfo_width()-inc_W if expanded else main_frame_w
    x_ = frame.winfo_width()+15 if expanded else frame_width+5
    frame_side_bar_h = h - int(h*ctrl_frame_h_per)

    if expanded:
        entry.place_forget()
        search_btn.place_forget()
        scrollbar.place_forget()
    else:
        frame.config(width=frame_width)
        adjust_search_entry_btn(entry, search_btn, main_frame_w)
        if len(tree.get_children())>15:
            scrollbar.place(x = w_*0.982, y=50, height=frame_side_bar_h*0.90)
    tree.place(width=w_-20)
    main_frame.config(width=w_)
    main_frame.place(x=x_, y=5)


def adjust_search_entry_btn(entry, search_btn, main_frame_w):
    entry.delete(0, END)
    entry.insert(0, placeholder)
    entry.config(fg=setting['input']['f-out-fg'])

    entry_x = main_frame_w*0.9
    search_x = entry_x*1.02

    entry.place(x=entry_x, y=10, anchor='ne', height=25)
    search_btn.place(x=search_x, y=23, anchor='center')

def resize_window_frames():
    global is_initial
    w, h = get_window_size(root)

    frame_side_bar_h = h - int(h*ctrl_frame_h_per)
    ctrl_h = h - frame_side_bar_h
    main_frame_w = w-frame_width
    w_ = w - frame.winfo_width()-inc_W if expanded else main_frame_w

    frame.config(width=frame_width, height=frame_side_bar_h+5)
    hover_frame.place_forget()
    frame.grid_propagate(False)

    
    main_frame.config(width=main_frame_w, height=frame_side_bar_h+5)
    main_frame.place(x=frame_width+5, y=5)

    ctrl_frame.config(width=w, height=ctrl_h)
    ctrl_frame.pack_propagate(False)

    canvas_width = ctrl_frame.winfo_reqwidth()*0.7
    canvas_height = get_frame_height(ctrl_frame, 20) + 40
    slider_canvas.config(width=canvas_width, height=canvas_height)
    
    
    sc_x = ctrl_x_cord(ctrl_frame, slider_dict, None) + 50
    sc_y = ctrl_frame.winfo_reqheight() -170

    adjust_search_entry_btn(entry, search_btn, main_frame_w)

    tree.place(width=w_*0.976, height=frame_side_bar_h*0.9231)
    
    ctrl_frame.place(x=0, y=int(frame_side_bar_h + inc_W + inc_W/2))
    slider_canvas.place(x=sc_x, y=sc_y)
   
    scrollbar.place(x =w_*0.982, y=50, height=frame_side_bar_h*0.88)

    x = main_frame_w * 0.95
    refresh_btn.place(x=x, y=10)
    
    if is_initial:
        add_ctrl_btn(ctrl_frame, ctrl_bg_c=ctrl_bg_c)
        on_leave_sbar(None)
        is_initial=False
    else:
        place_ctrl_btn(ctrl_frame)

    if len(tree.get_children())<16:
        scrollbar.place_forget()
    
    
def on_resize(event):
    global pre_h, pre_w
    w, h = get_window_size(root)
    if pre_h == h and pre_w == w:
        return
    
    if setting['dwd']=='True':
        show_msg_lbl.place_forget()
        show_msg(show_msg_lbl, "Download in Progress, Cannot resize the window.")
        root.geometry(f"{pre_w}x{pre_h}")
        return
    pre_w, pre_h = w, h
    resize_window_frames()

def shrink_sb():
    if len(tree.get_children()) > 16:
        scrollbar.config(width=6)
        w, _ = get_window_size(root)
        scrollbar.place(x =(w-frame_width)*0.985)
  
def on_leave_sbar(event):
    root.after(2000, shrink_sb)

def on_enter_sbar(event):
    if len(tree.get_children())>16:
        w, _ = get_window_size(root)
        scrollbar.config(width=12)
        scrollbar.place(x =(w-frame_width)*0.982)

def on_release(event):
    mixer.music.unpause()

def on_closing():
    mixer.music.stop()
    mixer.music.unload()
    mixer.quit()

    rm_dir(setting['tmp_fol_loc'] + 'local-m4a-songs')
    if get_local_files(setting['tmp_fol_loc']):
        response = messagebox.askyesno("Warning", "Do you want to DELETE the downloaded songs??",)
        
        rm_file(setting['tmp_fol_loc'] + "song-info.json")
      
        if response:
            rm_dir(tmp_fol_loc)
            setting.pop('tmp_fol_loc')
            setting.pop('font')
            update_setting(setting)

    root.destroy()


def bind_all_btns( ):
    root.bind("<Configure>", on_resize)

    # Bind the FocusIn and FocusOut events
    entry.bind("<FocusIn>", lambda e: on_focus_in(e, entry, placeholder))
    entry.bind("<FocusOut>", lambda e: on_focus_out(e, entry, placeholder))

    scrollbar.bind("<ButtonRelease-1>", lambda e: on_leave_sbar(e))
    scrollbar.bind("<Enter>", lambda e: on_enter_sbar(e))

    # Bind to the frame, if entered or left
    frame.bind('<Enter>', lambda e: expand(e))
    frame.bind('<Leave>', lambda e: contract(e))

    tree.bind("<Double-1>", on_double_click)
    
    custom_font = ('Cascadia Code Light', 15)
    tree.tag_configure('odd_row', background=lb_colors[0], foreground= 'black', font=custom_font)
    tree.tag_configure('even_row', background=lb_colors[1], foreground= 'black',font=custom_font) 
    tree.tag_configure('song_color', background=song_highlight_color, foreground= 'black', font=custom_font) 

    # Bind the closing event of the main window
    root.protocol("WM_DELETE_WINDOW", on_closing)

is_initial = True
