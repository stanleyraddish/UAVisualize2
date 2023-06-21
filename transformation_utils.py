import math
from shapely.geometry import Point, Polygon
import numpy as np

# Returns min and max x and y values appearing in list of coordinates
def get_bounds(points):
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), max(xs), min(ys), max(ys)


def in_triangle(x, y, triangle_corners):
    point = Point(x, y)
    poly = Polygon(triangle_corners)
    return poly.intersects(point)

def find_patch_point(patch_size, corners, img_point):
    # (Note: First corner is bottom left and then move clockwise around quadrilateral)

    # Corner points of quadrilateral
    (q1_x, q1_y) = corners[0]
    (q2_x, q2_y) = corners[1]
    (q3_x, q3_y) = corners[2]
    (q4_x, q4_y) = corners[3]

    qcenter_x = (q1_x + q2_x + q3_x + q4_x) / 4
    qcenter_y = (q1_y + q2_y + q3_y + q4_y) / 4

    (patch_h, patch_w) = patch_size
    # Corner points of patch
    p1_x, p1_y = 0, patch_h - 1
    p2_x, p2_y = 0, 0
    p3_x, p3_y = patch_w - 1, 0
    p4_x, p4_y = patch_w - 1, patch_h - 1

    patch_corners = [(p1_x, p1_y), (p2_x, p2_y), (p3_x, p3_y), (p4_x, p4_y)]

    pcenter_x = (patch_w - 1) / 2
    pcenter_y = (patch_h - 1) / 2

    x, y = img_point[0], img_point[1]

    # Determine which triangular quadrant the point lies in
    for i in range(4):
        left_corner = corners[i % 4]
        right_corner = corners[(i + 1) % 4]
        if in_triangle(x, y, [(qcenter_x, qcenter_y), left_corner, right_corner]):
            break

    patch_left_corner = patch_corners[i % 4]
    patch_right_corner = patch_corners[(i + 1) % 4]

    a, b, c = find_convex(qcenter_x, qcenter_y, left_corner[0], left_corner[1], right_corner[0], right_corner[1], x, y)

    res_x = int(a * pcenter_x + b * patch_left_corner[0] + c * patch_right_corner[0])
    res_y = int(a * pcenter_y + b * patch_left_corner[1] + c * patch_right_corner[1])

    return np.clip(res_x, 0, patch_w - 1), np.clip(res_y, 0, patch_h - 1)


def points_to_linemb(x1, y1, x2, y2):
    m = (y2 - y1) / (x2 - x1 + 0.0001)
    b = y2 - m * x2
    return m, b

def lines_interesection(m1, b1, m2, b2):
    x = (b2 - b1) / (m1 - m2 + 0.0001)
    y = m1 * x + b1
    return x, y

def get_2_convex(x1, y1, x2, y2, x, y):
    total_dist = math.dist((x1, y1), (x2, y2))
    dist = math.dist((x1, y1), (x, y))
    p = dist / total_dist
    return 1 - p, p


def find_convex(c_x, c_y, l_x, l_y, r_x, r_y, x, y):
    # Center to target point
    m1, b1 = points_to_linemb(c_x, c_y, x, y)

    # Left to right corners
    m2, b2 = points_to_linemb(l_x, l_y, r_x, r_y)

    i_x, i_y = lines_interesection(m1, b1, m2, b2)

    p, q = get_2_convex(l_x, l_y, r_x, r_y, i_x, i_y)

    s, t = get_2_convex(c_x, c_y, i_x, i_y, x, y)

    # convex combination for center, left, right
    return s, p * t, q * t

def quad_to_quad(patch_corners, corners_to, point, patch_size):
    # (Note: First corner is bottom left and then move clockwise around quadrilateral)
    (patch_h, patch_w) = patch_size

    # Corner points of quadrilateral
    (q1_x, q1_y) = corners_to[0]
    (q2_x, q2_y) = corners_to[1]
    (q3_x, q3_y) = corners_to[2]
    (q4_x, q4_y) = corners_to[3]

    (p1_x, p1_y) = patch_corners[0]
    (p2_x, p2_y) = patch_corners[1]
    (p3_x, p3_y) = patch_corners[2]
    (p4_x, p4_y) = patch_corners[3]

    qcenter_x = (q1_x + q2_x + q3_x + q4_x) / 4
    qcenter_y = (q1_y + q2_y + q3_y + q4_y) / 4

    pcenter_x = (p1_x + p2_x + p3_x + p4_x) / 4
    pcenter_y = (p1_y + p2_y + p3_y + p4_y) / 4

    x, y = point[0], point[1]

    # Determine which triangular quadrant the point lies in
    for i in range(4):
        left_corner = corners_to[i % 4]
        right_corner = corners_to[(i + 1) % 4]
        if in_triangle(x, y, [(qcenter_x, qcenter_y), left_corner, right_corner]):
            break

    patch_left_corner = patch_corners[i % 4]
    patch_right_corner = patch_corners[(i + 1) % 4]

    a, b, c = find_convex(qcenter_x, qcenter_y, left_corner[0], left_corner[1], right_corner[0], right_corner[1], x, y)

    res_x = int(a * pcenter_x + b * patch_left_corner[0] + c * patch_right_corner[0])
    res_y = int(a * pcenter_y + b * patch_left_corner[1] + c * patch_right_corner[1])

    return np.clip(res_x, 0, patch_w - 1), np.clip(res_y, 0, patch_h - 1)