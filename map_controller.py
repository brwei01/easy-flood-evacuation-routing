from map_plotting_version_1 import *
import tkinter as tk
from tkinter import ttk


class MapController(object):

    def __init__(self, mp, background_path, final_decision_path, user_input, evacu_points,
                                      start_itn, end_itn, raster_img, out_transform):
        self.mp = mp
        self.background_path = background_path
        self.final_decision_path = final_decision_path
        self.start_itn = start_itn
        self.end_itn = end_itn
        self.raster_img = raster_img
        self.out_transform = out_transform
        self.user_input = user_input
        self.evacu_points = evacu_points
        self.plot_elements = []

    # after selecting a checkbox, update the new map
    def getselect(self, item, mp):
        print(item, 'selected')
        selected = [i.get() for i in self.plot_elements if i.get()]
        print(selected)

        # close the old map
        mp.close()

        # initialize the new map
        # show the new map based on the selection
        mp = MapPlotting(self.background_path, self.final_decision_path, self.user_input, self.evacu_points,
                         self.start_itn, self.end_itn, self.raster_img, self.out_transform)
        mp.init_fig()
        mp.add_background()
        if 'Start point' in selected:
            mp.add_start_points()
        if 'End point' in selected:
            mp.add_end_points()
        if 'User input' in selected:
            mp.add_user_points()
        if 'Highest point' in selected:
            mp.add_evacu_points()
        mp.add_north_arrow()
        if 'Elevation' in selected:
            mp.add_elevation()
        if 'Path' in selected:
            mp.add_path()
        mp.show()

    def showwindow(self):
        """
        Referenced from https://blog.csdn.net/chaodaibing/article/details/108749234
        Author: chaodaibing, 2022
        """
        window = tk.Tk()
        window.geometry('500x100')
        window.title('Map Selector')
        frame = tk.Frame(window, pady=10, padx=15)
        frame.grid(row=0, column=0)

        list1 = ['Start point', 'End point', 'User input', 'Highest point', 'Path', 'Elevation']
        # set the checkbox
        for index, item in enumerate(list1):
            self.plot_elements.append(tk.StringVar())
            ttk.Checkbutton(frame, text=item, variable=self.plot_elements[-1], onvalue=item, offvalue='',
                            command=lambda item=item: self.getselect(item, self.mp)).grid(row=index // 4 + 1,
                                                                                          column=index % 4,
                                                                                          sticky='w')
        window.mainloop()
