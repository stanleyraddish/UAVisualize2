from math_utils import *
from transformation_utils import *
from img_utils import *

from shapely import Point, Polygon
from tkinter import *
from PIL import Image, ImageTk


class Patch:
    # @param{np.array[float[0,255]]} base_array: dimension h x w x 3
    # @param parent: tkinter Object that current Object should be placed on
    # @params{int} x_init, y_init: location of object within parent
    def __init__(self, base_array, parent, movable, x_init=0, y_init=0):
        self.parent = parent
        self.tag = None
        self.movable = movable

        # Position of NW corner of overlay image in parent object
        self.x = x_init
        self.y = y_init

        # RGBA channels
        self.base_array = base_array
        self.base_height = base_array.shape[0]
        self.base_width = base_array.shape[1]

        # RGBA channels
        alpha_channel = np.ones((base_array.shape[0], base_array.shape[1]), dtype=np.uint8) * 255
        self.overlay_array = np.dstack((base_array, alpha_channel))
        self.overlay_height = base_array.shape[0]
        self.overlay_width = base_array.shape[1]
        self.overlay_quad_points = {(x, y) for x in range(base_array.shape[1]) for y in range(base_array.shape[0])}

        self.overlay_img = ImageTk.PhotoImage(Image.fromarray(self.overlay_array))
        self.draw()

    def recalculate_overlay(self, corners):
        xmin, xmax, ymin, ymax = get_bounds(corners)

        overlay_height = ymax - ymin + 1
        overlay_width = xmax - xmin + 1

        overlay = np.ones((overlay_height, overlay_width, 4), dtype=np.uint8) * 255
        overlay_corners = [(x - xmin, y - ymin) for (x, y) in corners]
        overlay_array_quad = Polygon(overlay_corners)
        overlay_quad_points = set()

        for y in range(overlay_height):
            for x in range(overlay_width):
                pixel = Point(x, y)
                if pixel.within(overlay_array_quad):
                    overlay_quad_points.add((x, y))
                    patch_x, patch_y = find_patch_point((self.base_height, self.base_width), overlay_corners, (x, y))
                    overlay[y, x, :3] = self.base_array[patch_y, patch_x]
                else:
                    overlay[y, x, 3] = 0

        self.overlay_array = overlay
        self.overlay_height = overlay_height
        self.overlay_width = overlay_width
        self.overlay_quad_points = overlay_quad_points

        self.x = xmin
        self.y = ymin

        self.overlay_img = ImageTk.PhotoImage(Image.fromarray(self.overlay_array))
        self.draw()

    def draw(self):
        if self.tag != None:
            self.parent.delete(self.tag)
        self.tag = self.parent.create_image(self.x, self.y, anchor=NW, image=self.overlay_img)
        self.bind()

    def mouse_click(self, event):
        self.prev_mouse_X = event.x
        self.prev_mouse_Y = event.y
        self.get_frame().select_patch(self)

    def mouse_drag(self, event):
        dx = event.x - self.prev_mouse_X
        dy = event.y - self.prev_mouse_Y
        self.prev_mouse_X = event.x
        self.prev_mouse_Y = event.y
        self.x += dx
        self.y += dy
        self.parent.move(self.tag, dx, dy)

    def get_frame(self):
        return self.parent.master.master

    def bind(self):
        if self.movable:
            self.parent.tag_bind(self.tag, "<Button-1>", self.mouse_click)
            self.parent.tag_bind(self.tag, "<B1-Motion>", self.mouse_drag)


