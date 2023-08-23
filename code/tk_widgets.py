from tkinter import *
from globals_vars import root_bg_color, w, h, sideBarFrame_color, ctrl_bg_c, mainF_bg_c, entry_bg, setting, frame_width, song_highlight_color
from tkinter import ttk
from tkinter import filedialog, messagebox
from app_images import img_dict
from Helper_file import get_TK_image


# Root Window Configuration
root = Tk()
root.title("Derint: Groove Zone")
root.tk.call('wm', 'iconphoto', root._w, get_TK_image(img_dict['app-icon']))
root.geometry(f"{w}x{h}")
root.configure(bg=root_bg_color)
root.minsize(w, h)
root.resizable(False, False)


ctrl_btn_dict = {
    'shuff-on'  : {'name': 'Shuffle On',    'cmd': "btn_shuff_on",   'pos':250},
    'shuff-off' : {'name': 'Shuffle Off',   'cmd': "btn_shuff_off",  'pos':250},
    'previous'  : {'name': 'Previous Song', 'cmd': "btn_pre",        'pos':100},
    'play'      : {'name': 'Play',          'cmd': "btn_play",       'pos': 0 },
    'pause'     : {'name': 'Pause',         'cmd': "btn_pause",      'pos': 0 },
    'next'      : {'name': 'Next Song',     'cmd': "btn_nxt",        'pos':100},
    'repeat-on' : {'name': 'Repeat On',     'cmd': "btn_repeat_on",  'pos':200},
    'repeat-off': {'name': 'Repeat Off',    'cmd': "btn_repeat_off", 'pos':200},
    'song_time' : {'type': 'lbl',           'txt': '0m:0s',          'pos':400},
    'song-name' : {'type': 'lbl',           'txt': 'Title : '                 },
    'song-art'  : {'type': 'lbl',           'txt': 'Artist : '                }    
}

menu_bar_dict = {
    'all_songs' : {'pre':0, 'txt': 'All Songs', 'cmd' : "all_songs",
        'txt-x':0 , 'txt-y': 25, 'img-x': 5, 'img-y':25 },

    'playlist' : {'pre':0, 'txt': 'Playlist', 'cmd': "playlist",
        'txt-x':0 , 'txt-y': 90, 'img-x': 5, 'img-y': 100}
}

other_dict = {'search': {}, 'refresh':{}}

for key in img_dict:
    if key in ctrl_btn_dict:
        ctrl_btn_dict[key]['img'] = get_TK_image(img_dict[key])

    elif key in menu_bar_dict:
        menu_bar_dict[key]['img'] = get_TK_image(img_dict[key])

    elif key in ['search', 'refresh']:
        other_dict[key]['img'] = get_TK_image(img_dict[key])
    else:
        pass


# Widgets Functions
def destroy_error_label(error_label):
    error_label.place_forget()

def show_msg(error_label, text, sec=3, keep_it=False):
    ms = sec*1000
    error_label.config(text=text, bg=setting['error_label']['bg'], fg=setting['error_label']['fg'])
    error_label.place(x=(w-frame_width)*0.1, y=10)
    if not keep_it:
        root.after(ms, destroy_error_label, error_label)

class Tooltip:
    def __init__(self, widget, text, bg="#ffffe0", fg="black", font=None):
        self.widget = widget
        self.text = text
        self.bg = bg  
        self.fg = fg 
        self.font = font 

        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = Label(
            self.tooltip_window, text=self.text, background=self.bg,
            foreground=self.fg, relief="solid", borderwidth=1, font=self.font,
        )
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


# Widgets Initialization
blur_image = img_dict['blur_img']
bg_image = get_TK_image(blur_image)
blur_label = Label(root, image=bg_image)


## Part-1
background_label = Label(root)

my_canvas = Canvas(root, width=w, height=h)
url_entry = Entry(root, width=50, font=("Arial", 16))
url_entry.insert(0, 'http://localhost:8000/Music/tmp/')
pb = ttk.Progressbar(root, orient='horizontal', style="red.Horizontal.TProgressbar", mode='indeterminate',length=200)


## Part-2
frame = Frame(root, bg=sideBarFrame_color, highlightbackground=sideBarFrame_color)
hover_frame = Frame(frame, bg=sideBarFrame_color, bd=0, highlightbackground=sideBarFrame_color)

# Main Frame
main_frame = Frame(root, bg=mainF_bg_c, borderwidth=0, relief='solid')
ctrl_frame = Frame(root, bg=ctrl_bg_c, highlightthickness=0)

entry = Entry(main_frame, bg=entry_bg, width=25, font=(5, 15), highlightbackground=entry_bg)

search_btn = Button(main_frame, image=other_dict['search']['img'], relief=FLAT, bg=mainF_bg_c, activebackground=mainF_bg_c, bd=0, highlightbackground=mainF_bg_c)
refresh_btn = Button(main_frame, image=other_dict['refresh']['img'], relief=FLAT, bg=mainF_bg_c, activebackground=mainF_bg_c, bd=0, highlightbackground=mainF_bg_c)
Tooltip(refresh_btn, "Refresh Button")

slider_canvas = Canvas(ctrl_frame,  bg=ctrl_bg_c, highlightthickness=0)

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background=mainF_bg_c, fieldbackground=mainF_bg_c, foreground="purple", borderwidth=0, rowheight=35)
style.map("Treeview", background =[('selected', song_highlight_color)])

tree = ttk.Treeview(main_frame, columns=("Data", ), show='', style="Treeview")
style.configure("Treeview", rowheight=35)
tree.column("#0", stretch=YES)

scrollbar = Scrollbar(main_frame, orient='vertical', command=tree.yview, width=12, troughcolor='blue')
tree.configure(yscrollcommand=scrollbar.set)

dwd_canvas = Canvas(root, bg=ctrl_bg_c, highlightthickness=0, highlightbackground=ctrl_bg_c)

img1 = get_TK_image(img_dict['song-img']) 
img_lbl = Label(ctrl_frame, image=img1, bg=ctrl_bg_c, highlightbackground=ctrl_bg_c)

show_msg_lbl = Label(main_frame, font=(18, 15, 'bold'))
ctrl_info_label = Label(ctrl_frame, font=(20, 15, 'bold'), bg='purple', fg='white')


stop_btn = Button(dwd_canvas, bg=setting['dwd_prog']['img_bg'], highlightbackground=setting['dwd_prog']['img_bg'], relief='flat', activebackground=setting['dwd_prog']['img_bg'], bd=0)
Tooltip(stop_btn, "Press to Stop Downloading Audio", fg='red')

