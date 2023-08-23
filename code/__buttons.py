def remove_btn(button):
    button.place_forget()

def enable_btn(frame, button, _dict_, key=None):
    x = ctrl_x_cord(frame, _dict_, key)
    y = get_frame_height(frame, 10, True)
    button.place(x=x, y=y+30, anchor='center')

def enable_disable_ctrl_btn(frame, enable, disable, dict_):
    dis_btn = dict_[disable]['button']
    remove_btn(dis_btn)

    en_btn_dict = dict_[enable]
    en_btn = en_btn_dict['button']
    enable_btn(frame, en_btn, en_btn_dict, enable)

def ctrl_x_cord(frame, _dict_, key):
    ctrl_center_x = frame.winfo_reqwidth() // 2 
    pos = _dict_['pos']
    if key in ['next', 'repeat-off', 'repeat-on']:
        pos *= -1
    return ctrl_center_x - pos

def get_frame_height(frame, n=0, positive=None):
    if positive:
        n *= -1
    return frame.winfo_reqheight() // 2 - n

