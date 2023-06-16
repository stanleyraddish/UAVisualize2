# @param{float * float} location: (x, y)
# @params{int} x_min, x_max, y_min, y_max: [x_min, x_max) and [y_min, y_max) give bounds for returned pixel
# @return{int * int}:
#   - closest integer pixel coordinate if in valid range
#   - otherwise None
def closest_pixel(location, x_min, x_max, y_min, y_max):
    x = round(location[0])
    y = round(location[1])
    if x < x_min or x >= x_max or y < y_min or y >= y_max:
        return None
    else:
        return x, y