from tkinter import *
import numpy as np

from img_utils import *
from patch import *

class EditorFrame(Frame):
    def __init__(self, parent, controller, base_img_file, width, height):
        Frame.__init__(self, parent, width=width, height=height)
        self.pack_propagate(0)

        # Set up base image
        img = Image.open(base_img_file)
        self.screen_w, self.screen_h = img.size

        # Image display
        self.border = Canvas(self, width=self.screen_w+4, height=self.screen_h+4, highlightthickness=2, highlightbackground="black")
        self.border.pack(pady=0)

        self.canvas = Canvas(self.border, width=self.screen_w, height=self.screen_h)
        self.canvas.place(x=2, y=2, anchor=NW)
        self.master.bind("<Escape>", self.clear_selection)

        self.patches = []
        self.add_patch_from_file(base_img_file, movable=False)

        self.active_patch = None

        # Buttons
        self.corner_button = Button(self, text="Select Corners", command=self.start_select_corners)
        self.corner_button.place(relx=0.5, rely=0.7, anchor=CENTER)

    def add_patch_from_file(self, file_path, movable=True):
        img = Image.open(file_path)
        img = img.convert("RGB")
        np_img = np.asarray(img).astype(np.uint8)
        patch = Patch(np_img, self.canvas, movable)
        self.patches.append(patch)

    def select_patch(self, patch):
        self.active_patch = patch
        for p in self.patches[1:]:
            if p != patch:
                self.canvas.delete(p.tag)

    def clear_selection(self, event):
        self.active_patch = None
        self.master.unbind("<a>")
        for p in self.patches[1:]:
            p.draw()

    def start_select_corners(self):
        if self.active_patch is not None:
            self.corner_count = 4
            self.corner_list = []
            self.master.bind("<a>", self.select_corners)

    def select_corners(self, event):
        print("Corner selected")
        x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        self.corner_list.append((x, y))
        print(x, y)

        self.corner_count -= 1
        if self.corner_count == 0:
            self.active_patch.recalculate_overlay(self.corner_list)
            self.clear_selection(None)


