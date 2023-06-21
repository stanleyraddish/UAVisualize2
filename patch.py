import numpy as np

from math_utils import *
from transformation_utils import *
from img_utils import *
from losses import *

from shapely import Point, Polygon
from tkinter import *
from PIL import Image, ImageTk
import tensorflow as tf


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
        if self.in_bounds(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            self.parent.move(self.tag, dx, dy)

    def in_bounds(self, x, y):
        if x < 0:
            return False
        if y < 0:
            return False
        if x + self.overlay_width >= self.parent.winfo_width():
            return False
        if y + self.overlay_height >= self.parent.winfo_height():
            return False
        return True

    def get_frame(self):
        return self.parent.master.master

    def bind(self):
        if self.movable:
            self.parent.tag_bind(self.tag, "<Button-1>", self.mouse_click)
            self.parent.tag_bind(self.tag, "<B1-Motion>", self.mouse_drag)


class QuadAttackPatch(Patch):
    def __init__(self, corners, parent, movable, model):
        self.parent = parent
        self.base_array, self.x, self.y, self.overlay_quad_points = self.calculate_4d_base_array(corners, model)

        self.base_corners = [(x - self.x, y - self.y) for (x, y) in corners]
        self.tag = None
        self.movable = movable

        self.base_height = self.base_array.shape[0]
        self.base_width = self.base_array.shape[1]

        # RGBA channels
        self.overlay_array = np.copy(self.base_array)
        self.overlay_height = self.base_array.shape[0]
        self.overlay_width = self.base_array.shape[1]

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
                    patch_x, patch_y = quad_to_quad(self.base_corners, overlay_corners, (x, y), (self.base_height, self.base_width))
                    overlay[y, x, :3] = self.base_array[patch_y, patch_x, :3]
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

    def calculate_4d_base_array(self, corners, model):
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
                else:
                    overlay[y, x, 3] = 0

        arr = self.get_frame().generate_array()
        arr = np.expand_dims(arr, axis=0) / 255

        img_quad_points = {(x + xmin, y + ymin) for (x, y) in overlay_quad_points}

        overall_atk_img = self.quadPGD(model, arr, img_quad_points)

        for (x, y) in overlay_quad_points:
            overlay[y, x, :3] = overall_atk_img[0, y + ymin, x + xmin, :]

        return overlay, xmin, ymin, overlay_quad_points

    def quadPGD(self, model, arr, img_quad_points, loss_func=multi_right_loss, epochs=1000, eps=2):
        patch = np.zeros(arr.shape)

        for step in range(epochs):
            tfX = np.copy(arr)
            for (x, y) in img_quad_points:
                tfX[0, y, x] = patch[0, y, x]

            tfX = np.clip(tfX, 0, 1)
            tfX = tf.convert_to_tensor(tfX)

            with tf.GradientTape() as tape:
                tape.watch(tfX)
                y_pred = model(tfX)
                loss = loss_func(None, y_pred)

            gradient = tape.gradient(loss, tfX).numpy()

            for (x, y) in img_quad_points:
                patch[0, y, x] += gradient[0, y, x] * eps
            patch = np.clip(patch, 0, 1)

        X = np.copy(arr)
        for (x, y) in img_quad_points:
            X[0, y, x] = patch[0, y, x]

        return np.clip(X, 0, 1) * 255





