import shlex
import numpy as np

class Entity():
    def __init__(self):
        self.brushes = []
        self.keyvalues = {}
        self.translation = np.array([0.0, 0.0, 0.0])
        self.rotation = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    def bounds(self):
        mins = np.array([99999, 99999, 99999])
        maxs = np.array([-99999, -99999, -99999])
        for b in self.brushes:
            for p in b.planes:
                for v in p.points:
                    if v[0] < mins[0]:
                        mins[0] = v[0]
                    if v[1] < mins[1]:
                        mins[1] = v[1]
                    if v[2] < mins[2]:
                        mins[2] = v[2]
                    if v[0] > maxs[0]:
                        maxs[0] = v[0]
                    if v[1] > maxs[1]:
                        maxs[1] = v[1]
                    if v[2] > maxs[2]:
                        maxs[2] = v[2]
        return [mins, maxs]
        
class Plane():
    def __init__(self, a, b, c, material, scale, shift, rotation):
        self.points = []
        self.points.append(a)
        self.points.append(b)
        self.points.append(c)
        self.material = material
        
        e1 = b - a
        e2 = c - a
        
        n = np.cross(e1, e2)
        n /= np.linalg.norm(n)

        self.distance = np.dot(n, a)
        
        epsilon = np.random.normal(scale=1e-3, size=3)
        n += epsilon
        self.normal = n
        self.ignored = False
        
class Brush():
    def __init__(self):
        self.planes = []
        self.polygons = []
ignore_materials = ["lightgrid_volume","sky_mp_crash","mantle_on","portal","clip","clip_nosight","hint","portal_nodraw","clip_nosight_nothing","nodraw_decal","clip_nosight_metal","clip_nosight_rock","trigger","mantle_over","clip_player"]
def parse_map(path):
    #path = "/mnt/f/SteamLibrary/steamapps/common/Call of Duty 2/map_source/cornell.map"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        depth = 0
        entities = []
        entity = None
        brush = None
        ignored = False
        for lineno, l in enumerate(lines):
            if len(l) == 0:
                continue
            if l[0] == '/' and l[1] == '/':
                continue
            sp = shlex.split(l.strip(), posix=False)
            if len(sp) == 0:
                continue
            if len(sp) > 1 and sp[0] == "(":
                a = np.array([float(sp[1]), float(sp[2]), float(sp[3])])
                b = np.array([float(sp[6]), float(sp[7]), float(sp[8])])
                c = np.array([float(sp[11]), float(sp[12]), float(sp[13])])

                material = sp[15]
                scale = (float(sp[16]), float(sp[17]))
                shift = (float(sp[18]), float(sp[19]))
                rotation = float(sp[20])
                #print(f'{lineno + 1}: {a} {b} {c} {material} {scale} {shift} {rotation}')
                plane = Plane(a, b, c, material, scale, shift, rotation)
                if material in ignore_materials:
                    plane.ignored = True
                #    ignored = True
                brush.planes.append(plane)
                #print(sp)
            elif len(sp[0]) > 1 and sp[0][0] == "\"":
                if entity != None:
                    entity.keyvalues[sp[0][1:-1]] = sp[1][1:-1]
            elif sp[0] == "{":
                if depth == 0:
                    entities.append(Entity())
                    entity = entities[-1]
                elif depth == 1:
                    brush = Brush()
                depth += 1
            elif sp[0] == "}":
                if depth == 2:
                    if ignored == False:
                        entity.brushes.append(brush)
                depth -= 1
        #print(f'n = {len(entities)}')
        for e in entities:
            #print(f'\t{len(e.brushes)} brushes')
            b = e.bounds()
            #print(f'bounds: {b}')
    return entities
