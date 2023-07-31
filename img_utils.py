import cv2


def show_and_wait(img, RGB2BGR=True, name = ""):
    # RGB to BGR
    if RGB2BGR:
        img = img[:,:,::-1]
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()