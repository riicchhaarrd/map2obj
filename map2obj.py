from parse import parse_map
import numpy as np
from scipy.spatial import ConvexHull
import math
import os

#path = "/mnt/f/SteamLibrary/steamapps/common/Call of Duty 2/map_source/cornell.map"
path = "/mnt/f/SteamLibrary/steamapps/common/Call of Duty 2/map_source/mp_big.map"
#path = "/mnt/f/maps/mp_crash_map_source/mp_crash_map_source/map_source/mp_crash.map"

INCH_TO_CM = 0.0254

def unique(verts):
    u = []
    for v in verts:
        f = False
        for v2 in verts:
            if v2 == v:
                continue
            d = [v2[0] - v[0], v2[1] - v[1], v2[2] - v[2]]
            dist = math.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2])
            if dist < 0.1:
                f = True
                break
        if f == False:
            u.append(v)
    print(f'removed {len(verts) - len(u)} vertices')
    return u
    
ents = parse_map(path)

def rotation_matrix_from_angles(angles):        
    x = np.radians(float(angles[2])) # pitch
    y = np.radians(float(angles[0])) # yaw
    z = np.radians(float(angles[1])) # roll
    
    #X
    R_pitch = np.array([[1, 0, 0],
                        [0, np.cos(x), -np.sin(x)],
                        [0, np.sin(x), np.cos(x)]])
    #Y
    R_yaw = np.array([[np.cos(y), 0, np.sin(y)],
                    [0, 1, 0],
                    [-np.sin(y), 0, np.cos(y)]])
    #Z
    R_roll = np.array([[np.cos(z), -np.sin(z), 0],
                    [np.sin(z), np.cos(z), 0],
                    [0, 0, 1]])
                    
    R = np.dot(np.dot(R_yaw, R_pitch), R_roll)
    return R
    

for e in ents:
    if e.keyvalues['classname'] == 'misc_prefab':
        prefab_path = os.path.dirname(path) + '/' + e.keyvalues['model']
        if not os.path.isfile(prefab_path):
            continue
        origin = e.keyvalues['origin'].split(' ')
        R = np.array([[1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0]])
        if 'angles' in e.keyvalues:
            angles = e.keyvalues['angles'].split(' ')
            R = rotation_matrix_from_angles(angles)
        
        prefab = parse_map(prefab_path)
        for pe in prefab:
            pe.translation = np.array([float(origin[0]), float(origin[1]), float(origin[2])])
            pe.rotation = R
            ents.append(pe)

class Polygon():
    def __init__(self):
        self.points = []
        self.indices = []
    def sort(self):
        points = self.points.copy()
        epsilon = np.random.normal(scale=1e-8, size=len(points))
        for i in range(len(points)):
            points[i][0] += epsilon[i]
            points[i][1] += epsilon[i]
            points[i][2] += epsilon[i]
        try:
            hull = ConvexHull(points)
            self.indices = hull.simplices
        except:
            pass

def build_geom(ent):
    vertices = []
    tris = []

    polys = []

    for brush in ent.brushes:
        for p0 in brush.planes: #could optimize loop
            poly = Polygon()
            for p1 in brush.planes:
                for p2 in brush.planes:
                    if p0 == p1 or p1 == p2 or p2 == p0:
                        continue
                    P = np.array([
                        [p0.normal[0], p0.normal[1], p0.normal[2]],
                        [p1.normal[0], p1.normal[1], p1.normal[2]],
                        [p2.normal[0], p2.normal[1], p2.normal[2]]
                    ])
                    tolerance = 1e-9
                    #tolerance = np.finfo(np.longdouble).eps
                    det = np.linalg.det(P)
                    if abs(det) < tolerance:
                        continue
                    b = np.array([p0.distance, p1.distance, p2.distance])
                    #P * v = -b
                    #v = -inverse(P) * b
                    v = np.dot(-np.linalg.inv(P), b)
                    #breakpoint()
                    invalid = False
                    for m in brush.planes:
                        d = np.dot(m.normal, v) + m.distance
                        if d > tolerance:
                            invalid = True
                    if invalid == False:
                        poly.points.append(v)
            if len(poly.points) < 3:
                continue
            poly.sort()
            polys.append(poly)
    return polys
    
with open("test.obj", "w") as f:
    total_face = 1
    for e in ents:
        if len(e.brushes) == 0:
            continue
        polys = build_geom(e)
        
        center = np.array([0.0,0.0,0.0])
        numpoints = 0
        for p in polys:
            for v in p.points:
                center += v
                numpoints += 1
        if numpoints == 0:
            continue
        center /= float(numpoints)
        
        for p in polys:
            for face in p.indices:
                for k in range(3):
                    vo = p.points[face[k]]
                    v = vo.copy()
                    v = e.rotation @ v
                    v -= e.translation
                    f.write("v %f %f %f\n" % (-v[0] * INCH_TO_CM, -v[1] * INCH_TO_CM, -v[2] * INCH_TO_CM))
                    #f.write("v %f %f %f\n" % (v[0] * INCH_TO_CM, -v[2] * INCH_TO_CM, v[1] * INCH_TO_CM))
        for p in polys:
            for k in range(len(p.indices)):                    
                f.write("f %d %d %d\n" % (total_face, total_face + 1, total_face + 2))
                total_face += 3