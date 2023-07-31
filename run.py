from app import *
from img_utils import *

def main():
    app = App("images/ezgif-frame-011.jpg")

    str_path = "model/model_struct.json"
    weight_path = "model/weights.h5"
    app.load_model(str_path, weight_path)

    app.add_patch("images/patch3.png")
    app.add_patch("images/patch2.png")

    app.run()

if __name__ == "__main__":
    main()