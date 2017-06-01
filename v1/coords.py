import numpy as np

boatWidth = 0.000076
boatLength = 0.000136
bowWidth = 0.000009
trampOffset = 0.000027
bowTip = 0.000002

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

boatOrigin = [bowL, tip, bowR, sternR, sternL]

def rotate(theta, pt):
    x, y = pt
    cos = np.cos(theta)
    sin = np.sin(theta)
    return [x * cos - y * sin, x * sin + y * cos]

def translate(pt, vec):
    pt[0] += vec[0]
    pt[1] += vec[1]
    return pt

def drawBoat(pos, theta):
    theta = np.radians(theta)
    theta = (theta - np.pi / 2 % (2.0 * np.pi))
    pts = [translate(rotate(theta, x), pos) for x in boatOrigin]
    return pts
