import json
from geometry.point import Point

class MyPoint:
    def __init__(self):
        self.x = 0
        self.y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y

    def getX(self):
        return self.x
    def getY(self):
        return self.y

class MyCurve:
    def __init__(self, p1=None, p2=None):
        self.p1 = p1
        self.p2 = p2

    def setP1(self, p1):
        self.p1 = p1

    def setP2(self, p2):
        self. p2 = p2

    def getP1(self):
        return self.p1

    def getP2(self):
        return self.p2


class MyModel:
    def __init__(self):
        self.verts = []
        self.mesh = []
        self.connect = []
        self.conditions = []
        self.forces = []
        self.restrs = []

        self.fenceCurves = []

        self.curves = []

    def setVerts(self,x,y):
        self.verts.append(MyPoint(x,y))

    def getVerts(self):
        return self.verts
    
    def getMesh(self):
        return self.mesh
    
    def setCurve(self,x1,y1,x2,y2):
        self.curves.append(MyCurve(MyPoint(x1,y1),MyPoint(x2,y2)))

    def setFenceCurves(self, x1, y1, x2, y2):
        self.fenceCurves.append(MyCurve(MyPoint(x1,y1),MyPoint(x2,y2)))

    def getCurves(self):
        return self.curves

    def isEmpty(self):
        return len(self.verts) == 0

    def getBoundBox(self):
        if (len(self. verts) < 1) and (len(self. curves) < 1):
            return 0.0,10.0,0.0,10.0

        if len(self.verts) > 0:
            xmin = self.verts[0].getX()
            xmax = xmin
            ymin = self.verts[0].getY()
            ymax = ymin
            for i in range(1,len(self. verts)):
                if self.verts[i].getX() < xmin:
                    xmin = self. verts[i].getX()
                if self.verts[i].getX() > xmax:
                    xmax = self.verts[i].getX()
                if self.verts[i].getY() < ymin:
                    ymin = self.verts[i].getY()
                if self.verts[i].getY() > ymax:
                    ymax = self.verts[i].getY()

        if len(self.curves) > 0:
            if len(self.verts) == 0:
                xmin = min(self.curves[0].getP1().getX(),self.curves[0].getP2().getX())
                xmax = max(self.curves[0].getP1().getX(),self.curves[0].getP2().getX())
                ymin = min(self.curves[0].getP1().getY(),self.curves[0].getP2().getY())
                ymax = max(self.curves[0].getP1().getY(),self.curves[0].getP2().getY())

            for i in range(1,len(self.curves)):
                temp_xmin = min(self.curves[i].getP1().getX(),self.curves[i].getP2().getX())
                temp_xmax = max(self.curves[i].getP1().getX(),self.curves[i].getP2().getX())
                temp_ymin = min(self.curves[i].getP1().getY(),self.curves[i].getP2().getY())
                temp_ymax = max(self.curves[i].getP1().getY(),self.curves[i].getP2().getY())

                if temp_xmin < xmin:
                    xmin = temp_xmin
                if temp_xmax > xmax:
                    xmax = temp_xmax
                if temp_ymin < ymin:
                    ymin = temp_ymin
                if temp_ymax > ymax:
                    ymax = temp_ymax

        return xmin,xmax,ymin,ymax
    
    def findNH(self, x, y):
        try:
            return (self.mesh.index([x, y, 0, 0]) + 1)
        except:
            return 0

    
    def saveMesh(self, N, mass, kspr, h):
        coords_subset = [[p[0], p[1]] for p in self.mesh]

        if len(coords_subset) > 0: 
            file = open("input.json", "w")
            print(len(self.connect))

            entities = {
                'connection_map': self.connect,
                'forces': self.forces,
                'restrs': self.restrs,
                'coords': coords_subset,
            }

            json.dump(entities, file, indent=4)
            file.close()

    def calcMesh(self, h_model, radius):
        self.radius = radius
        self.mesh = []
        self.connect = []
        self.forces = []
        self.restrs = []
        if not (h_model.isEmpty()):
            patches = h_model.getPatches()
            for pat in patches:
                pts = pat.getPoints()

                xmin = pts[0].getX()
                xmax = xmin
                ymin = pts[0].getY()
                ymax = ymin
                for i in range(1,len(pts)):
                    if pts[i].getX() < xmin:
                        xmin = pts[i].getX()
                    if pts[i].getX() > xmax:
                        xmax = pts[i].getX()
                    if pts[i].getY() < ymin:
                        ymin = pts[i].getY()
                    if pts[i].getY() > ymax:
                        ymax = pts[i].getY()

                coord_x = []
                coord_y = []
                delta = radius

                while xmin < xmax:
                    coord_x.append(xmin)
                    xmin += delta 
                while ymin < ymax:
                    coord_y.append(ymin)
                    ymin += delta
                
                for x in coord_x:
                    for y in coord_y:
                        if pat.isPointInside(Point(x, y)): self.mesh.append([x, y, 0, 0])
                
                for i in range(len(self.mesh)): 
                    p1 = self.findNH(self.mesh[i][0] - delta, self.mesh[i][1])
                    p2 = self.findNH(self.mesh[i][0], self.mesh[i][1] - delta)
                    p3 = self.findNH(self.mesh[i][0], self.mesh[i][1] + delta)
                    p4 = self.findNH(self.mesh[i][0] + delta, self.mesh[i][1])

                    c = min(1, p1) + min(1, p2) + min(1, p3) + min(1, p4)
                    self.connect.append([c] + sorted([p1, p2, p3, p4], reverse=True))
                    self.forces.append([0, 0])
                    self.restrs.append([0.0, 0.0])

                
                #self.forces = [[0]*(len(self.mesh)*2)]
                #self.restrs = [[0]*(len(self.mesh)*2)]

    def setForces(self, fence_model, x_force, y_force):
        if self.mesh != []:
            if not (fence_model.isEmpty()):
                patches = fence_model.getPatches()
                print(len(patches))
                i = 0
                for p in self.mesh:
                    if self.isPointInsideAPat(Point(p[0], p[1]), patches):
                        self.forces[i][0], self.forces[i+1][0] = x_force, y_force
                    else:
                        self.forces[i][0], self.forces[i+1][0] = 0, 0
                    
                    i += 2

        fence_model.clearAll()

    def isPointInsideAPat(self, p, patches):
        return True in [pat.isPointInside(p) for pat in patches]

    def setCondition(self, fence_model, dir_value, neu_value):
        if self.mesh != []:
            if not (fence_model.isEmpty()):
                patches = fence_model.getPatches()
                print(len(patches))
                for p in self.mesh:
                    if self.isPointInsideAPat(Point(p[0], p[1]), patches):
                        if dir_value != None:
                           p[2], p[3] = 1, dir_value
                        elif neu_value != None:
                            p[2], p[3] = 2, neu_value

        fence_model.clearAll()

    def setRestr(self, fence_model):
        if self.mesh != []:
            if not (fence_model.isEmpty()):
                patches = fence_model.getPatches()
                print(len(patches))
                i = 0
                for p in self.mesh:
                    if self.isPointInsideAPat(Point(p[0], p[1]), patches):
                        self.restrs[i], self.restrs[i+1] = 1, 1
                    else:
                        self.restrs[i], self.restrs[i+1] = 0, 0
                    
                    i += 2

        fence_model.clearAll()


