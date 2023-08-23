from Helper_file import readImage
from globals_vars import w, h, image, p_wh, s_wh, IMAGE_DIR

img_wh = image
i_w, i_h = img_wh["w"], img_wh["h"]

# App-Image-Icon
app_icon = readImage(IMAGE_DIR + "app-icon.ico")

# Blur Image i.e Loading...
blur_img = readImage(IMAGE_DIR+"bg8.jpg", (w, h), 8)

## Part-1
background_image = readImage(IMAGE_DIR+'bg11.jpg', (w, h), None)

## Part-2
# Control Frame Images
shuffle_on_img  = readImage(IMAGE_DIR+"shuff_on.png",  (i_w, i_h))
shuffle_off_img = readImage(IMAGE_DIR+"shuff_off.png", (i_w, i_h))
prev_img        = readImage(IMAGE_DIR+"pre.png",       (i_w, i_h))
play_img        = readImage(IMAGE_DIR+"play.png",      (i_w+p_wh, i_h+p_wh))
pause_img       = readImage(IMAGE_DIR+"pause.png",     (i_w+p_wh, i_h+p_wh))
next_img        = readImage(IMAGE_DIR+"next.png",      (i_w, i_h))
repeat_on_img   = readImage(IMAGE_DIR+"repeat_on.png", (i_w, i_h))
repeat_off_img  = readImage(IMAGE_DIR+"repeat_off.png",(i_w, i_h))
song_img        = readImage(IMAGE_DIR+"song.png",      (i_w+s_wh, i_h+s_wh+15)) #  (120, 150)#(i_w+s_wh, i_h+s_wh+15) #border_color='black', border_size=1

refresh_img     = readImage(IMAGE_DIR+'refresh.png', (i_w-8, i_h-8))

# Main Frame Images
search_img = readImage(IMAGE_DIR+"search.png", (i_w-8, i_h-8))

# Side Bar Images
all_song_img = readImage(IMAGE_DIR+'song.png')
playlist_img = readImage(IMAGE_DIR+'playlist.png')
new_play_img = readImage(IMAGE_DIR+'new-playlist.png')

img_dict = {
    # App-Icon
    'app-icon' : app_icon,
    
    # Loading Image
    'blur_img':blur_img,

    # Window-1
    'background_img' : background_image,

    # Main Frame 
    'search' : search_img, 'refresh':refresh_img,

    # Menu/Side Bar Frame
    'all_songs' : all_song_img,  'playlist' : playlist_img, # 'new_playlist' : {'img':new_play_img},

    # Control Frame 
    'shuff-off' : shuffle_off_img, 'shuff-on':shuffle_on_img, 'previous':prev_img, 'play':play_img, 
    'pause':pause_img, 'next':next_img, 'repeat-off': repeat_off_img, 'repeat-on':repeat_on_img, 'song-img':song_img,

}
