from app import *
from img_utils import *

def main():
    app = App("images/x5-loc2.png")

    str_path = "model/model_struct.json"
    weight_path = "model/weights.h5"
    app.load_model(str_path, weight_path)


    # app.current_frame.add_patch_from_file("images/jiggly.png")
    # app.current_frame.add_patch_from_file("images/9.png")
    #
    # corners = [(60, 10), (20, 20), (50, 90), (100, 95)]
    # corners = [(y, x) for (x, y) in corners]
    #
    # app.current_frame.patches[1].recalculate_overlay(corners)
    #
    # app.current_frame.add_patch_from_file("images/jiggly.png")
    #
    # corners = [(150, 10), (60, 50), (110, 130), (150, 160)]
    # corners = [(y, x) for (x, y) in corners]
    #
    # app.current_frame.patches[2].recalculate_overlay(corners)

    app.run()

if __name__ == "__main__":
    main()