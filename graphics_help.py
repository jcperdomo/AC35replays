import numpy as np

# constants corresponding to the boat dimensions
boatWidth = 8.47
boatLength = 15.00
bowWidth = 1.0
trampOffset = 3.0
bowTip = .2


sr = [boatWidth / 2.0, 0.0]
sl = [-boatWidth / 2.0, 0.0]
brr = [boatWidth / 2.0, boatLength]
bru = [boatWidth / 2.0 - bowWidth / 2.0, boatLength + bowTip]
brl = [boatWidth / 2.0 - bowWidth, boatLength]
trampr = [boatWidth / 2.0 - bowWidth, boatLength - tramp_offset]
trampl = [-(boatWidth / 2.0 - bowWidth), boatLength - tramp_offset]
bll = [-boatWidth / 2.0, boatLength]
blu = [-(boatWidth / 2.0 - bowWidth / 2.0), boatLength + bowTip]
blr = [-(boatWidth / 2.0 - bowWidth), boatLength]

boatOrigin = [sr, brr, bru, brl, trampr, trampl, blr, blu, bll, sl]


def rotate(theta, pt):
    """
    rotates a point accross the origin by theta radians

    params:
    theta = radians (float)
    pt = [x,y] (floats)

    returns: [new_x, new_y]
    """
    x, y = pt
    cos = np.cos(theta)
    sin = np.sin(theta)
    return [x * cos - y * sin, x * sin + y * cos]


def translate(pt, vec):
    """
    translates a point by vector

    params:
    pt = [x,y]
    vec = [x,y]

    returns: [new_x, new_y]
    """
    pt[0] += vec[0]
    pt[1] += vec[1]
    return pt


def drawBoat(pos, theta):
    """
    Manipulates boatOrigin points to set them at a given position and heading

    params:
    pos = (x,y)
    theta = angle heading (in Radians)

    returns: list of 5 boat corners at position pos with heading = theta
    """
    theta = (theta - np.pi / 2 % (2.0 * np.pi))
    pts = [translate(rotate(theta, x), pos) for x in boatOrigin]
    return pts
