from tkinter import *
from frames import *
from model_utils import *


class App:
    def __init__(self, base_img_file, w=600, h=600):
        self.win_w = w
        self.win_h = h
        self.base_img_file = base_img_file
        self.initialize_app()

        self.model = None

    def initialize_app(self):
        self.root = Tk()
        self.root.title("UAVisualize")
        self.root.geometry(f"{self.win_w}x{self.win_h}+500+0")

        self.current_frame = EditorFrame(self.root, self, self.base_img_file, self.win_w, self.win_h)
        self.current_frame.pack()

    def show_frame(self, frame):
        frame.tkraise()

    def run(self):
        self.root.mainloop()

    def load_model(self, struct_path, weights_path):
        self.model = load_network_from_json_and_h5(struct_path, weights_path)
