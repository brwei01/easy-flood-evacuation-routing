#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
import tkinter as tk
import hashlib
import time
#import GUI# the final plotter py file
from input_version_1 import UserInput


LOG_LINE_NUM = 0
# https://www.runoob.com/python/python-gui-tkinter.html
class MY_GUI():
    def __init__(self, init_window_name, new_window):
        self.init_window_name = init_window_name
        self.new_window = new_window



    # set window
    def set_init_window(self):
        self.init_window_name.title("main_window")           # the name of the window
        # self.init_window_name.geometry('50x35')                         #290 160 window size，+10 +10 Define the default display position of the window when it pops up
        self.init_window_name.geometry('700x340+100+100')
        #self.init_window_name["bg"] = "#000080"                                    # background color of the window，other color：blog.csdn.net/chl0000/article/details/7657887
        #self.init_window_name.attributes("-alpha",0.9)                          # Window vignetting, the smaller the value the higher the vignetting

        # Label
        # self.intro_label = Label(self.init_window_name,width = 200,height = 30,wraplength = 80, text="This program will quickly calculate the highest point within a 5km radius and the fastest way out, please enter your current location exactly. Please use OSGB36 / British National Grid - EPSG:27700 for your location.",justify="left").pack()
        # self.intro_label.grid(row=5, column=0)
        self.intro_label = Label(self.init_window_name, text="This program will quickly calculate the highest point within a 5km radius",justify="center")
        self.intro_label.grid(row=0, column=1)
        self.intro_label = Label(self.init_window_name,text="and the fastest way out, please enter your current location exactly.",justify="center")
        self.intro_label.grid(row=1, column=1)
        self.intro_label = Label(self.init_window_name,text="Please use OSGB36 / British National Grid",justify="center")
        self.intro_label.grid(row=2, column=1)
        self.intro_label = Label(self.init_window_name,text="- EPSG:27700 for your location.",justify="center")
        self.intro_label.grid(row=3, column=1)
        self.zz_label = Label(self.init_window_name, text="  ", justify="left")
        self.zz_label.grid(row=4, column=0)
        self.lat_label = Label(self.init_window_name, text="Please enter your longitude:", justify="left")
        self.lat_label.grid(row=5, column=0)
        self.lon_label = Label(self.init_window_name, text="Please enter your latitude:")
        self.lon_label.grid(row=6, column=0)  # label position, how far from the top left corner
        self.zz_label = Label(self.init_window_name, text="  ", justify="left")
        self.zz_label.grid(row=7, column=0)

        # text area
        self.lat_Text = Text(self.init_window_name, width=30, height=1)  # lat
        self.lat_Text.grid(row=5, column=1) # input text 位置，离左上角多远
        self.lon_Text = Text(self.init_window_name, width=30, height=1)  # lon
        self.lon_Text.grid(row=6, column=1)
        # Button
        self.confirm_button = Button(self.init_window_name, text="Confirm", bg="lightblue", width=8,command = self.openNewWindow)#,command=lambda:[tk.Tk().destroy(),jiemian1()]
        self.confirm_button.grid(row=8, column=1)

    def openNewWindow(self):

        self.new_window.title("main_window")  # name of the window
        self.new_window.geometry('700x340+150+150')# Window Size + Offset
        self.new_window.wm_attributes('-topmost', 1)

        # A Label widget to show in toplevel
        Label(self.new_window, text="This is a new window").pack()
        # GUI.show() # %%%%%%%%Just put the last picture shown here%%%%%%%%%
#xxxxxxxxxx
    # present time
    def get_current_time(self):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return current_time


    # Dynamic printing of logs
    def write_log_to_Text(self,logmsg):
        global LOG_LINE_NUM
        current_time = self.get_current_time()
        logmsg_in = str(current_time) +" " + str(logmsg) + "\n"      #换行
        if LOG_LINE_NUM <= 7:
            self.log_data_Text.insert(END, logmsg_in)
            LOG_LINE_NUM = LOG_LINE_NUM + 1
        else:
            self.log_data_Text.delete(1.0, 2.0)
            self.log_data_Text.insert(END, logmsg_in)


def gui_start():
    init_window = Tk()
    new_window = Tk()
    # Instantiate a parent window
    window = MY_GUI(init_window, new_window)
    # Setting the default properties of the root window
    window.set_init_window()

    init_window.mainloop()          # The parent window enters the event loop,
    # which can be interpreted as keeping the window running, otherwise the interface is not displayed

# main
gui_start()