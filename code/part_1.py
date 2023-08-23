from Helper_file import get_TK_image, count_audio_ext
from network_functions import *
from part_2 import Window_2
from app_images import img_dict
from globals_vars import NORMAL, HIDDEN, DISABLED, END, setting, CONFIG_PATH, SLASH
from tk_widgets import root, background_label, my_canvas, url_entry, pb, Button, filedialog
from globals_vars import tmp_fold

import os, zipfile, sys
from threading import Thread


def animation():
    global stop
    stop=False
    my_canvas.itemconfig(rect, fill=setting['rect-box']['success'])
    my_canvas.itemconfig(label, text="Searching for audio files.....", font=(1, 25), state=NORMAL, fill=setting['label']['search'])
    pb.place(x = x1+300, y=y1+75)
    pb.start()


def start_thread():
    t1 = Thread(target=animation)
    t2 = Thread(target=on_submit)
    t1.start()
    t2.start()


def on_submit():
    url = url_entry.get()
    get_local_audio_btn.config(state=DISABLED)
    abort_btn.config(state=NORMAL)

    index_link = get_index_link(url, check_only=True)

    if index_link is None or not url.startswith('http'):
        url_entry.delete(0, END) 
        show_label()
        return

    my_canvas.itemconfig(button3_window, state=NORMAL)

    crawler(url, index_link)
    
    if links and not stop:
        call_window_2(links=links, url=url)
        return
    
    if links==[] and not stop:
        def hide_label_2():
            my_canvas.itemconfigure(label, state=HIDDEN)
            hide_label()
        
        txt = f"No audio files were found...."
        my_canvas.itemconfigure(label, text=txt, fill=setting['label']['fg'], font=(1, 20), state=NORMAL)
        get_local_audio_btn.config(state=DISABLED)
        abort_btn.config(state=DISABLED)
        root.after(5000, hide_label_2)
    
    url_entry.delete(0, END) 
    pb.stop()
    pb.place_forget()


def call_window_2(**args):
    my_canvas.itemconfig(label, state=HIDDEN)
    forget_everything()
    f.close()
    Window_2(args=args)
    
    
    
def hide_label():
    my_canvas.itemconfigure(label, state=HIDDEN)
    my_canvas.itemconfigure(rect, fill=setting['rect-box']['normal'])
    my_canvas.itemconfigure(button3_window, state="hidden")
    my_canvas.itemconfigure(button2_window, state="normal")
    get_local_audio_btn.config(state=NORMAL)


def show_label():
    my_canvas.itemconfig(label, text="Invalid URL", fill=setting['label']['error'], state=NORMAL)
    my_canvas.itemconfig(rect, fill=setting['rect-box']['error'])
    my_canvas.itemconfig(button1_window, state=DISABLED)
    my_canvas.itemconfig(button3_window, state=HIDDEN)
    my_canvas.itemconfigure(button2_window, state="hidden")
    pb.place_forget()
    root.after(3000, hide_label)


def crawler(url, index_link):
    global links, stop, f
    try:
        req = getRequest(url, max_tries=1)
        if req==-1:
            return -1
        soup = BeautifulSoup(req.content, features='html.parser')

        for href in soup.find_all('a'):
            if href.text == '..':continue
            link = nextLink(url, href, index_link)
            if href.text.endswith('/'):
                f.write(f"{link}\n")
                crawler(link, index_link)
            else:
                ext = os.path.splitext(href.text)[1]
                if ext in setting["allowed_ext"]:
                    links.append(link)
                    
            if stop: return
                
    except Exception as e:
        pass

def forget_everything():
    pb.place_forget()
    my_canvas.destroy()
    url_entry.destroy()
    background_label.place_forget()

def open_file_dialog():
    file_path = filedialog.askdirectory()
    if file_path:
        call_window_2(file_path=file_path)


def abort():
    global stop, links
    stop=True
    pb.stop()
    pb.pack_forget()
    txt = f"Found {len(links) - count_audio_ext(links)} audio files"
    my_canvas.itemconfigure(label, text=txt, fill=setting['rect-box']['found-song'], font=(1, 20), state=NORMAL)
    my_canvas.itemconfigure(button3_window, state="hidden")
    my_canvas.itemconfigure(button2_window, state="normal")
    find_audio_btn.config(state=DISABLED)

    def hide_label_2():
        my_canvas.itemconfigure(label, state=HIDDEN)
        find_audio_btn.config(state=NORMAL)
        hide_label()
    
    root.after(5000, hide_label_2) 

def btn_state(btns, state='disabled'):
    for btn in btns:
        btn.configure(state=state)

def dwd_mv_file():
    
    dir = CONFIG_PATH 
    zip_file = CONFIG_PATH+'\\ffmpeg_lib.zip'

    if os.name=='posix' and  not os.path.isfile('/usr/bin/ffmpeg'):
        print("ffmpeg File is Not installed...")
        print("Read the Readme.md file, to install it")
        root.quit()
        sys.exit()
        

    if os.path.isdir(dir+'ffmpeg_lib') or os.name != 'nt':
        print("file already downloaded.")
        return
    
    if os.path.isfile(zip_file):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(dir)
        print("\r [+]  File Unzip Successfully....")
    else:
        print("\n\nZip File Not Found...")
        print("Pls Download file from: https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-5.1.2-essentials_build.7z")
        print("Extract the 'ffmpeg.exe' file from the 'bin' folder and add it into the 'ffmpeg_lib' directory within the 'Config' folder.")
        root.quit()
        sys.exit()

def dwd_thread():
    t = Thread(target=dwd_mv_file)
    t.start()
    

def first_window():    
    my_canvas.itemconfig(button3_window, state=HIDDEN)
    my_canvas.pack(fill='both', expand=True)
    music = setting['root']
    my_canvas.itemconfig(rect, fill=setting['rect-box']['normal'])
    my_canvas.create_text(450, 100, text=music['name'], font=(music['font'], music['fs']), fill=music['fg'])
    my_canvas.create_text(50, y1+25, text="URL", font=("Roboto", 30), fill=setting['url_lbl']['fg'])
    url_entry.place(x=x1+10, y=y1+10) 
    my_canvas.itemconfigure(button3_window, state="hidden")
    dwd_thread()
    

# Rectangle
x1, y1, x2, y2 = 100, 400,  730, 450

background_image = img_dict['background_img']
background_image = get_TK_image(background_image)
background_label.config(image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1) 


# Insert background image
my_canvas.create_image(0, 0, image=background_image, anchor='nw')

# Buttons
get_local_audio_btn = Button(root, text="From Local Directory", font=("Roboto", 30))
find_audio_btn = Button(root, text="Go", font=("Arial", 16))
abort_btn = Button(root, text="Abort", font=("Arial", 16))


button1_window = my_canvas.create_window(10, 300, anchor='nw', window=get_local_audio_btn)
button2_window = my_canvas.create_window(x2 + 30, y1+5, anchor='nw', window=find_audio_btn)
button3_window = my_canvas.create_window(x2 + 30, y1+5, anchor='nw', window=abort_btn)

get_local_audio_btn.config(command=open_file_dialog)
find_audio_btn.config(command=start_thread)
abort_btn.config(command=abort)

rect = my_canvas.create_rectangle(x1, y1, x2, y2)
label = my_canvas.create_text(x1+100, y1+80,  font=("Helvetica", 30), fill=setting['label']['fg'])

links = []
stop = False
f = open(tmp_fold + "folder-paths.txt", 'w')
is_additional_file_dwd = False