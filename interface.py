#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 13:08:10 2022

@author: math
"""

import tkinter as tk
import os
from PIL import ImageTk,Image  
import pandas as pd
from functools import partial #allows to ad arguments to button function
from random import randint
import textwrap
import webbrowser
import subprocess
import shutil
import threading
import platform


if platform.system() == 'Linux':
    path_main = '/mnt/Дми́трий'
    #sudo mkdir /mnt/<USER>/Дми́трий
    #edit /etc/fstab -> //dmitri.local/films /mnt/<USER>/Дми́трий cifs username=math,password=no,noauto,user 0 0
    #python3 -m pip install --upgrade pip
    # sudo apt install python3-tk
    #python3 -m pip install --upgrade pillow
    #pip3 install pandas
    if os.path.isfile(os.path.join(path_main, 'library.db')) == False:
        mount = subprocess.run(('mount', path_main))
        # gio mount smb://server/share
        
# path_main = '/run/user/1000/gvfs/smb-share:server=dmitri.local,share=films'
path_db = os.path.join(path_main, 'library.db')
db = pd.read_csv(path_db, sep=';').sort_values(by="title")


buttonFont = 'Courier 10'
meta_txt_break = 40
meta_txt_size = 10
meta_txt_type = 'bold'
meta_txt_font= 'Courier'
meta_title_size = 20
meta_title_break = 32

def initiate_search(mode):
    global search_menu_it
    search_menu_it = 0
    
    if mode == 'random':
        
        rand_num = randint(0,len(db)-1)
        display_movie(db.iloc[rand_num:rand_num+1])
    
    if mode == 'search':
        entry = ent_search.get().split(' ')
        entry = [x for x in entry if x] #removes empty fields created by multiple spaces
        db_s = db
        for keyword in entry:
            db_s = db_s[db_s.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1).values]
        if len(db_s) > 0:
            display_movie(db_s)
        else:
            for widgets in frm_result.winfo_children():
                widgets.destroy()
            lbl_nores = tk.Label(master=frm_result, text="\n No result found.")
            lbl_nores.pack()
  
    if mode == 'last_entry':
        db_le = db.sort_values(by="date_imported", ascending=False)
        display_movie(db_le)

def display_movie(db_movies, index=-1):
    
    for widgets in frm_result.winfo_children():
        widgets.destroy()
    
    search_frame = tk.Frame(frm_result, width=250, height=422)
    search_frame.pack(side='left', padx=10, pady=10)
    search_frame.propagate(0)
    
    poster_frame = tk.Frame(frm_result, width=285, height=422)
    poster_frame.pack(side='left', padx=10, pady=10)
    poster_frame.propagate(0)
    
    meta_frame = tk.Frame(frm_result, width=505, height=422)
    meta_frame.pack(side='right', padx=10, pady=10)
    meta_frame.propagate(0)

    def more_search():
        global search_menu_it
        search_menu_it +=12
        for widgets in search_frame.winfo_children():
            widgets.destroy()
        set_others_menu()

    def set_others_menu():
        srch_frm_title = tk.Label(master=search_frame, text='Results (' + str(len(db_movies)) + '):', font=(meta_txt_font, meta_txt_size, meta_txt_type))
        srch_frm_title.pack()
        global search_menu_it
        # if len(db_movies) < 14:
        #     for lindex, row in db_movies.iterrows():
        #         btn_text = row.astype(str).title + ' (' + str(int(row.year)) + ')'
        #         btn_othres = tk.Button(master=search_frame,   
        #             command=partial(display_movie, db_movies, lindex),
        #             text=btn_text,
        #             width=25,
        #             font=buttonFont,
        #             height=1,
        #             # bg="blue",
        #             # fg="yellow",
        #         )
        #         btn_othres.pack()
        if (len(db_movies) - search_menu_it) < 14:
            for lindex, row in db_movies.iloc[search_menu_it:].iterrows():
                btn_text = row.astype(str).title + ' (' + str(int(row.year)) + ')'
                btn_othres = tk.Button(master=search_frame,   
                    command=partial(display_movie, db_movies, lindex),
                    text=btn_text,
                    width=25,
                    font=buttonFont,
                    height=1,
                    # bg="blue",
                    # fg="yellow",
                )
                btn_othres.pack()
        else:
            for lindex, row in db_movies.iloc[search_menu_it:search_menu_it+12].iterrows():
                btn_text = row.astype(str).title + ' (' + str(int(row.year)) + ')'
                btn_othres = tk.Button(master=search_frame,   
                    command=partial(display_movie, db_movies, lindex),
                    text=btn_text,
                    width=25,
                    font=buttonFont,
                    height=1,
                    # bg="blue",
                    # fg="yellow",
                )
                btn_othres.pack()
            btn_more = tk.Button(master=search_frame,   
                command=partial(more_search),
                text='ˇ more ˇ',
                width=25,
                font=buttonFont,
                height=1,
                # bg="blue",
                # fg="yellow",
            )
            btn_more.pack(side='bottom')
            
            
    set_others_menu()
    
    if index == -1:
        df_movie = db_movies.iloc[0]
    else:
        df_movie = db_movies[db_movies.index == index].iloc[0]
    
    PILFile = Image.open(os.path.join(path_main + df_movie.path_to_file, 'poster.jpg'))
    poster = ImageTk.PhotoImage(PILFile)
    ImageLabel = tk.Label(poster_frame, image=poster)
    ImageLabel.image = poster
    ImageLabel.pack()
    
    meta_txt_frame = tk.Frame(meta_frame, width=505, height=422-30)
    meta_txt_frame.pack(side='top')
    meta_txt_frame.propagate(0)
    
    title = tk.Label(master=meta_txt_frame, font=(meta_txt_font,meta_title_size, 'bold'), text=textwrap.fill(df_movie.astype(str).title, meta_title_break))
    title.pack()
    if df_movie.astype(str).original_title != 'nan' and df_movie.astype(str).original_title != '':
        original_title = tk.Label(master=meta_txt_frame, font=(meta_txt_font, meta_txt_size, meta_txt_type), text='Original title: ' + textwrap.fill(df_movie.astype(str).original_title, meta_txt_break))
        original_title.pack()
    director = tk.Label(master=meta_txt_frame, font=(meta_txt_font, meta_txt_size, meta_txt_type), text='\nDirector: ' + textwrap.fill(df_movie.astype(str).director.replace(',',', '), meta_txt_break))
    director.pack()
    actors = tk.Label(master=meta_txt_frame, font=(meta_txt_font, meta_txt_size, meta_txt_type), text='Actors: ' + textwrap.fill(df_movie.astype(str).actors.replace(',',', '), meta_txt_break))
    actors.pack()
    genre = tk.Label(master=meta_txt_frame, font=(meta_txt_font, meta_txt_size, meta_txt_type), text='\nGenre: ' + textwrap.fill(df_movie.astype(str).genre.replace(',',', '), meta_txt_break))
    genre.pack()
    year = tk.Label(master=meta_txt_frame, font=(meta_txt_font, meta_txt_size, meta_txt_type), text='Year: ' + textwrap.fill(str(int(df_movie.year)), meta_txt_break))
    year.pack()
    country_origin = tk.Label(master=meta_txt_frame, font=(meta_txt_font, meta_txt_size, meta_txt_type), text='\nCountry of origin: ' + textwrap.fill(df_movie.astype(str).country_origin.replace(',',', '), meta_txt_break))
    country_origin.pack()
    original_language = tk.Label(master=meta_txt_frame, font=(meta_txt_font, meta_txt_size, meta_txt_type), text='Language: ' + textwrap.fill(df_movie.astype(str).original_language.replace(',',', '), meta_txt_break))
    original_language.pack()
    duration = tk.Label(master=meta_txt_frame, font=(meta_txt_font, meta_txt_size, meta_txt_type), text='Runtime: ' + textwrap.fill(df_movie.astype(str).duration, meta_txt_break))
    duration.pack()
    synopsys = tk.Label(master=meta_txt_frame, font=(meta_txt_font, meta_txt_size, meta_txt_type), text='\nSynopsys: ' + textwrap.fill(df_movie.astype(str).synopsys, meta_txt_break))
    synopsys.pack()
    
    def to_imdb(url):
        webbrowser.open(url, new=2)
    def to_video(path):
        subprocess.run('xdg-open "' + str(path) + '"', shell=True)
    def to_download(path,title,year):
        
        default_path_to = os.path.expanduser("~/Desktop/")
        def check_to():
            path_to = ent_to.get()
            if os.path.isdir(path_to):
                path_to = os.path.join(path_to, df_movie.astype(str).path_to_file.split("/")[-1])
                for widgets in frm_prog_top.winfo_children():
                    widgets.destroy()
                for widgets in frm_prog_bottom.winfo_children():
                    widgets.destroy()
                def thread_downloading(path, path_to):
                    shutil.copytree(path, path_to)      
                threading.Thread(target=thread_downloading, args=(path,path_to,)).start()
                
                def set_label(path,path_to,title,year):
                    def get_size(location):
                        print(location)
                        if os.path.exists(location):
                            return sum(d.stat().st_size for d in os.scandir(location) if d.is_file())
                        else:
                            return -1
                    try:
                        prog_perc = int(get_size(path_to)/get_size(path)*100)
                    except:
                        prog_perc = 0
                    lbl_progress['text'] = 'Downloading ' + title + ' (' + year + ') ' + str(prog_perc) + '%'
                    progress.after(2000, set_label,path,path_to,title,year)
                    if prog_perc == 100:
                        progress.destroy()
                
                # progress = tk.Tk(className='Дми́трий progress')
                lbl_progress = tk.Label(master=frm_prog_top, text='placeholder')
                lbl_progress.pack()
                lbl_dnc = tk.Label(master=frm_prog_bottom, text='Do not close!')
                lbl_dnc.pack()
                
                set_label(path,path_to,title,year)
            else:
                for widgets in frm_prog_bottom.winfo_children():
                    widgets.destroy()
                lbl_nodir = tk.Label(master=frm_prog_bottom, text='Please put an existing directory')
                lbl_nodir.pack()
        progress = tk.Tk(className='Дми́трий progress')
        frm_prog_top = tk.Frame(master=progress)
        frm_prog_bottom = tk.Frame(master=progress)
        frm_prog_top.pack(side='top')
        frm_prog_bottom.pack(side='bottom')
        lbl_to = tk.Label(master=frm_prog_top, text='Copy to: ')
        ent_to = tk.Entry(master=frm_prog_top, width=65)
        ent_to.insert(0, default_path_to)
        def enter_path_to(info): #has to have an argument
            check_to()
        ent_to.bind('<Return>', enter_path_to)
        btn_to = tk.Button(master=frm_prog_top,
            command=partial(check_to),
            text="ok",
            width=5,
            font=buttonFont
            # height=5,
            # bg="blue",
            # fg="yellow",
        )
        lbl_to.pack(side='left')
        ent_to.pack(side='left')
        btn_to.pack(side='left')
               
    
    btn_frame = tk.Frame(meta_frame, width=505, height=30)
    btn_frame.pack(side='bottom')
    btn_frame.propagate(0)
    
    btn_watch = tk.Button(master=btn_frame,
        command=partial(to_video, os.path.join(path_main + df_movie.astype(str).path_to_file, df_movie.astype(str).file)),
        text="Watch!",
        width=18,
        font=buttonFont
        # height=5,
        # bg="blue",
        # fg="yellow",
    )
    btn_download = tk.Button(master=btn_frame,
        command=partial(to_download, os.path.join(path_main + df_movie.astype(str).path_to_file), df_movie.astype(str).title, str(int(df_movie.year))),
        text="Download",
        width=18,
        font=buttonFont
        # height=5,
        # bg="blue",
        # fg="yellow",
    )
    btn_imdb = tk.Button(master=btn_frame,
        command=partial(to_imdb, df_movie.astype(str).imdb_link),
        text="On imdb",
        width=18,
        font=buttonFont
        # height=5,
        # bg="blue",
        # fg="yellow",
    )
    btn_watch.pack(side='left')
    btn_download.pack(side='left')
    btn_imdb.pack(side='left')

### define widow and frames

window = tk.Tk(className='Дми́трий Movie Explorer')
window.geometry("1200x600")

frm_title = tk.Frame()
frm_search = tk.Frame()
frm_result = tk.Frame(width=1100, height=500)
frm_spacer = tk.Frame()
frm_title.pack()
frm_search.pack()
frm_spacer.pack()
frm_result.pack()
frm_result.propagate(0)

# cva_movie = tk.Canvas(window, width = 300, height = 300)  
# poster = ImageTk.PhotoImage(Image.open(os.path.join(df_movie.path_to_file, 'poster.jpg')))
# cva_movie.create_image(20,20, anchor='nw', image=poster)
# cva_movie.pack()
# display_movie(db.iloc[0])

#title frame
lbl_title = tk.Label(master=frm_title, text="\n")
lbl_title.pack()

#spacer frame
# lbl_spacer = tk.Label(master=frm_spacer, text="\n")
# lbl_spacer.pack()

#search frame

ent_search = tk.Entry(master=frm_search, width=86)
def enter_to_search(info): #has to have an argument
    initiate_search('search')
ent_search.bind('<Return>', enter_to_search)
ent_search.pack()

btn_search = tk.Button(master=frm_search,
    command=partial(initiate_search, 'search'),
    text="Search!",
    width=26,
    font=buttonFont,
    # height=5,
    # bg="blue",
    # fg="yellow",
)
btn_lucky = tk.Button(master=frm_search,
    command=partial(initiate_search, 'random'),
    text="I'am lucky!",
    width=26,
    font=buttonFont
    # height=5,
    # bg="blue",
    # fg="yellow",
)
btn_last = tk.Button(master=frm_search,
    command=partial(initiate_search, 'last_entry'),
    text="Last entries",
    width=26,
    font=buttonFont
    # height=5,
    # bg="blue",
    # fg="yellow",
)
btn_search.pack(side='left')
btn_lucky.pack(side='left')
btn_last.pack(side='left')

# search_spacer = tk.Label(master=frm_search, text="xdqdede\n")
# search_spacer.pack(side='bottom')

# display_movie(db.iloc[1])

# if opening_soft == True:
#     opening_soft == False
#     initiate_search(mode='default')

#initiate the frames

window.mainloop()

if platform.system() == 'Linux':
    umount = subprocess.run(('umount', path_main))
