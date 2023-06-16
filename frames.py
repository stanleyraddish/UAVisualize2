from tkinter import *
import numpy as np

from img_utils import *
from patch import *

class EditorFrame(Frame):
    def __init__(self, parent, controller, base_img_file, width, height):
        Frame.__init__(self, parent, width=width, height=height)
        self.pack_propagate(0)

        self.parent = parent
        self.controller = controller

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

        self.predict_button = Button(self, text="Predict", command=self.predict)
        self.predict_button.place(relx=0.5, rely=0.75, anchor=CENTER)

        self.metric_label = None

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

    def generate_array(self):
        arr = np.zeros((self.screen_h, self.screen_w, 3), dtype=np.float32)
        for patch in self.patches:
            for o_y in range(patch.overlay_height):
                for o_x in range(patch.overlay_width):
                    if (o_x, o_y) in patch.overlay_quad_points:
                        arr[o_y + patch.y, o_x + patch.x] = patch.overlay_array[o_y, o_x, :3]
        return arr[:,:,::-1]

    def predict(self):
        if self.controller.model is None:
            print("No model loaded")
        else:
            model = self.controller.model
            arr = self.generate_array()
            cv2.imwrite("images/TEST.png", arr)
            arr = np.expand_dims(arr, axis=0) / 255
            y_pred = np.array(model.predict(arr))[:, :, 0]

            if self.metric_label is not None:
                self.metric_label.destroy()

            var=StringVar()
            self.metric_label = Label(self, textvariable=var)

            steer = y_pred[0][0]
            col = y_pred[1][0]
            s = f"Steering Angle: {steer:.3f}, Collision Probability: {col:.3f}"

            var.set(s)
            self.metric_label.place(relx=0.5, rely=0.8, anchor=CENTER)


