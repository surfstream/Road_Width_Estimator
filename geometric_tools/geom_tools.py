import numpy as np

def line_intersection(line1, line2):
    """
    Return the coordinates of a point of intersection given two lines.
    Return None if the lines are parallel, but non-collinear.
    Return an arbitrary point of intersection if the lines are collinear.

    Parameters:
    line1 and line2: lines given by 2 points (a 2-tuple of (x,y)-coords).
    """
    p1, p2 = [np.array(p) for p in line1]
    # dist_p = np.linalg.norm(p2 - p1)
    q1, q2 = [np.array(p) for p in line2]
    # dist_q = np.linalg.norm(q2 - q1)

    # If both points of a segment lie on the same side
    # of another segment, there's no intersection.
    if sum([get_direction(*line1, q) for q in line2]) != 0 or \
       sum([get_direction(*line2, q) for q in line1]) != 0:
        return None

    # Collinear segments can overlap.
    # But if a candidate road segment is collinear with
    # one bounding box segment, it will be perpendicular to
    # another bounding box segment. So we can ignore this case.
    if get_direction(*line1, line2[0]) == 0 and \
       get_direction(*line1, line2[1]) == 0:
        return None

    # Gotta find the sweet point of intersection now!
    # Usual formula:
    #    
    (x1,y1), (x2,y2) = line1
    (u1,v1), (u2,v2) = line2
    (a,b), (c,d) = (x2-x1, u1-u2), (y2-y1, v1-v2)
    e, f = u1-x1, v1-y1
    denom = float(a*d - b*c)
    t = (e*d - b*f)/denom
    px = x1 + t*(x2-x1)
    py = y1 + t*(y2-y1)

    return px, py


def bound_segment(line_seg, bbox):
    """
    Given a line segment and a bounding box, bound the
    segment such that when the line segment crosses the
    boundaries, the segment is chopped at the intersection.
    """
    p1, p2 = line_seg
    out_points = [p1, p2]
    inside_flags = [point_in_box(p, bbox) for p in out_points]
    if sum(inside_flags) == 2:    # if both points are inside, we good!
        return out_points

    if sum(inside_flags) == 0:
        out_points = [None, None]
    else:
        out_points[inside_flags.index(False)] = None

    bound_segs = [
                  ((bbox[0], bbox[1]), (bbox[2], bbox[1])),
                  ((bbox[2], bbox[1]), (bbox[2], bbox[3])),
                  ((bbox[2], bbox[3]), (bbox[0], bbox[3])),
                  ((bbox[0], bbox[3]), (bbox[0], bbox[1])),
                 ]

    xings = [line_intersection(line_seg, b_seg) for b_seg in bound_segs]
    for v in xings:
        if v is not None:
            out_points[inside_flags.index(False)] = v

    return out_points


def point_in_box(p, box):
    """
    Returns True if point p is within a bounding box.

    Arguments:
        p: tuple of two floats
            2D space. Here it's longitude (long) and latitude (lat)

        box: list of 4 floats
            lower left (ll) long, ll lat, upper-right (ur) long, ur lat
    """
    inside = False
    if (box[0] <= p[0] <= box[2]) and (box[1] <= p[1] <= box[3]):
        inside = True

    return inside


def thicken_line_segment(p1, p2, wide):
    '''
    Given a line segment as a pair of points and a width, return
    a rectangle with that width.
    '''
    # perpendicular
    perp1 = np.array([p1[1] - p2[1], p2[0] - p1[0]])
    perp2 = np.array([p2[1] - p1[1], p1[0] - p2[0]])

    unit_perp1 = perp1 / np.linalg.norm(perp1)
    unit_perp2 = perp2 / np.linalg.norm(perp2)

    polygon = [tuple(item) for item in [p1 + unit_perp1 * wide, p2 + unit_perp1 * wide, p2 + unit_perp2 * wide, p1 + unit_perp2 * wide]]
    # points = check_within_bound(polygon[0:2], bound_box) + check_within_bound(polygon[2:], bound_box)

    return polygon


def get_direction(a, b, c):
    """
    Check if 3 points form counter clockwise direction.
    """
    cosine = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
    return np.sign(cosine)


def crosses(line1, line2):
    """
    Return True if line segment line1 intersects line segment line2 and 
    line1 and line2 are not parallel.
    """
    (x1,y1), (x2,y2) = line1
    (u1,v1), (u2,v2) = line2
    (a,b), (c,d) = (x2-x1, u1-u2), (y2-y1, v1-v2)
    e, f = u1-x1, v1-y1
    denom = float(a*d - b*c)
    if near(denom, 0):
        # parallel
        return False
    else:
        t = (e*d - b*f)/denom
        s = (a*f - e*c)/denom
        # When 0<=t<=1 and 0<=s<=1 the point of intersection occurs within the
        # line segments
        return 0<=t<=1 and 0<=s<=1


def near(a, b, rtol=1e-5, atol=1e-8):
    return abs(a - b) < (atol + rtol * abs(b))

