from OpenGL.GL import *
from PyQt5 import QtOpenGL
from PyQt5.QtWidgets import *
import PyQt5.QtCore as QtCore

from random import random

from he.hecontroller import HeController
from he.hemodel import HeModel
from geometry.segments.line import Line
from geometry.point import Point
from compgeom.tesselation import Tesselation


class MyCanvas(QtOpenGL.QGLWidget):
    def __init__(self, radius_getter):
        super(MyCanvas, self).__init__()
        self.model = None
        self.w = 0 # width: GL canvas horizontal size
        self.h = 0 # height: GL canvas vertical size
        self.l = -1000.0
        self.r =  1000.0
        self.b = -1000.0
        self.t =  1000.0
        self.list = None
        self.m_buttonPressed = False
        self.m_pt0 = QtCore.QPointF(0.0,0.0)
        self.m_pt1 = QtCore.QPointF(0.0,0.0)
        self.h_model = HeModel()
        self.h_controller = HeController(self.h_model)

        self.previous_mpt = QtCore.QPointF(0.0,0.0)
        self.isPanAllowed = False
        
        self.fence_model = HeModel()
        self.fence_controller = HeController(self.fence_model)
        self.isFenceColectorOn = False
        self.numPatches = 0

        self.colorController = ColorController()

        self.radius_getter = radius_getter
        self.mesh = []

    def initializeGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_LINE_SMOOTH)
        
        self.list = glGenLists(1)
    
    def resizeGL(self, width, height):
        # store GL canvas sizes in object properties
        self.w = width
        self.h = height
        
        # Setup world space window limits (bounding box?)
        if(self.model==None)or(self.model.isEmpty()):
             self.scaleWorldWindow(1.0)
        else:
            self.l,self.r,self.b,self.t = self.model.getBoundBox()
            self.scaleWorldWindow(1.1)

        # setup the viewport to canvas dimensions
        glViewport(0, 0, self.w, self.h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # establish the clipping volume by setting up an orthographic projection
        glOrtho(self.l,self.r,self.b,self.t,-1.0,1.0)

        # setup display in model coordinates
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        # clear the buffer with the current clear color
        glClear(GL_COLOR_BUFFER_BIT)

        # draw the model

        glCallList(self.list)
        glDeleteLists(self.list, 1)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)

        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)

        if not self.isPanAllowed and not self.isFenceColectorOn:
            glColor3f(0, 0, 4)
            glBegin(GL_LINE_STRIP)
            glVertex2f(pt0_U.x(), pt0_U.y())
            glVertex2f(pt1_U.x(), pt1_U.y())
            glEnd()
        
        if not (self.h_model.isEmpty()) and not (self.isFenceColectorOn):
            patches = self.h_model.getPatches()
            for pat in patches:
                pts = pat.getPoints()
                triangs = Tesselation.tessellate(pts)
                for j in range(len(triangs)):
                    #glColor3fv(pts[triangs[j][2]].getColor()) #color
                    glColor3fv([200,1,1])
                    glBegin(GL_TRIANGLES)
                    glVertex2d(pts[triangs[j][0]].getX(), pts[triangs[j][0]].getY())
                    glVertex2d(pts[triangs[j][1]].getX(), pts[triangs[j][1]].getY())
                    glVertex2d(pts[triangs[j][2]].getX(), pts[triangs[j][2]].getY())
                    glEnd()

            #for the line not be under the seg while drawing
            if not self.isPanAllowed and not self.isFenceColectorOn:
                glColor3f(40, 20, 0.5)
                glBegin(GL_LINE_STRIP)
                glVertex2f(pt0_U.x(), pt0_U.y())
                glVertex2f(pt1_U.x(), pt1_U.y())
                glEnd()
            
            segments = self.h_model.getSegments()
            for curv in segments:
                ptc = curv.getPointsToDraw()
                glColor3f(70, 0.5, 20)
                glBegin(GL_LINES)
                for curv in segments:
                    glVertex2f(ptc[0].getX(), ptc[0].getY())
                    glVertex2f(ptc[1].getX(), ptc[1].getY())
                glEnd()
            
            if self.radius_getter.okClicked:
                self.radius_getter.okClicked = False
                self.model.calcMesh(self.h_model, self.radius_getter.r_value)
                self.update()
  
        if len(self.model.getMesh()) > 0:
            pts = self.model.getMesh()
            glColor3f(0, 0, 55)
            glPointSize(2)
            glBegin(GL_POINTS)
            for i in range(len(pts)):
                glVertex2f(pts[i][0], pts[i][1])
            glEnd()


        if not self.isPanAllowed and self.isFenceColectorOn:
            glColor3f(20, 20, 20)
            glBegin(GL_LINE_STRIP)
            glVertex2f(pt0_U.x(), pt0_U.y())
            glVertex2f(pt1_U.x(), pt1_U.y())
            glEnd()

        if not (self.fence_model.isEmpty()):
            segments = self.fence_model.getSegments()
            for curv in segments:
                ptc = curv.getPointsToDraw()
                glColor3f(20, 20, 20)
                glBegin(GL_LINES)
                for curv in segments:
                    glVertex2f(ptc[0].getX(), ptc[0].getY())
                    glVertex2f(ptc[1].getX(), ptc[1].getY())
                glEnd()
            
        glEndList()
    
    def convertPtCoordsToUniverse(self, pt):
        dX = self.r - self.l
        dY = self.t - self.b
        mX = pt.x() * dX / self.w
        mY = (self.h - pt.y()) * dY / self.h
        x = self.l + mX
        y = self.b + mY
        return QtCore.QPointF(x,y)
    
    def removeFence(self):
        self.fence_model.clearAll()
        self.update()
        self.updateGL()

    def setModel(self,model):
        self.model = model

    def panWorldWindow(self, panFacX, panFacY):
        # Compute pan distances in horizontal and vertical directions.
        panX = (self.r - self.l) * panFacX
        panY = (self.t - self.b) * panFacY

        # Shift current window.
        self.l += panX
        self.r += panX
        self.b += panY
        self.t += panY

        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.l, self.r, self.b, self.t, -1.0, 1.0)
        self.update()
      
    def fitWorldToViewport(self):
        print("fitWorldToViewport")
        if self.model == None:
            return
        self.l ,self.r ,self.b ,self.t = self.model.getBoundBox()
        self.scaleWorldWindow(1.10)
        self.update()
    
    def scaleWorldWindow(self, scaleFac):
        # Compute canvas viewport distortion ratio.
        vpr = self.h / self.w

        # Get current window center.
        cx = (self.l + self.r) / 2.0
        cy = (self.b + self.t) / 2.0

        # Set new window sizes based on scaling factor.
        sizex = (self.r - self.l) * scaleFac
        sizey = (self.t - self.b) * scaleFac

        # Adjust window to keep the same aspect ratio of the viewport.
        if sizey > (vpr*sizex): sizex = sizey / vpr
        else: sizey = sizex * vpr

        self.l = cx - (sizex * 0.5)
        self.r = cx + (sizex * 0.5)
        self.b = cy - (sizey * 0.5)
        self.t = cy + (sizey * 0.5)

        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.l, self.r, self.b, self.t, -1.0, 1.0)

    def mousePressEvent(self, event):
        self.m_buttonPressed = True
        self.m_pt0 = self.m_pt1 = event.pos()

    def mouseMoveEvent(self, event):
        if self.m_buttonPressed:
            self.previous_mpt = self.m_pt1 # to pan function

            #print(self.m_pt1)

            self.m_pt1 = event.pos()

            if self.isPanAllowed: self.executePan()

        self.update()

    def mouseReleaseEvent(self, event):
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)

        if (not self.isPanAllowed and not self.isFenceColectorOn) and not (pt0_U == pt1_U):

            self.model.setCurve(pt0_U.x(), pt0_U.y(), pt1_U.x(), pt1_U.y())

            p0 = Point(pt0_U.x(), pt0_U.y())
            p1 = Point(pt1_U.x(), pt1_U.y())

            segment = Line(p0, p1)

            self.h_controller.insertSegment(segment, 0.01)

            self.update()
            self.repaint()
        
        if self.isFenceColectorOn and not (pt0_U == pt1_U):
            self.model.setCurve(pt0_U.x(), pt0_U.y(), pt1_U.x(), pt1_U.y())

            p0 = Point(pt0_U.x(), pt0_U.y())
            p1 = Point(pt1_U.x(), pt1_U.y())

            segment = Line(p0, p1)

            self.fence_controller.insertSegment(segment, 0.01)

            self.update()
            self.repaint()


        self.m_buttonPressed = False
        #python 3.10 has an issue with set floats even if QpointF is used
        self.m_pt0 = QtCore.QPointF(0.0,0.0)
        self.m_pt0 = QtCore.QPointF(0.0,0.0)
        self.m_pt1 = QtCore.QPointF(0.0,0.0)
        self.m_pt1 = QtCore.QPointF(0.0,0.0)
        self.previous_mpt = QtCore.QPointF(0.0,0.0)
        self.previous_mpt = QtCore.QPointF(0.0,0.0)

    def executePan(self):
        panx_fac, pany_fac = 0, 0
        if (abs(self.m_pt1.x() - self.previous_mpt.x()) > 5):
            panx_fac = -0.01 if self.m_pt1.x() > self.previous_mpt.x() else 0.01

        if (abs(self.m_pt1.y() - self.previous_mpt.y()) > 5):
            pany_fac = 0.01 if self.m_pt1.y() > self.previous_mpt.y() else -0.01
            
        self.panWorldWindow(panx_fac, pany_fac)

class ColorController():
    def __init__(self):
        # Substitua as cores aleatórias por amarelo e roxo
        self.colors = [[1.0, 1.0, 0.0], [0.5, 0.0, 0.5]]
        self.index = 0
    
    def getColor(self):
        if self.index == len(self.colors):
            self.index = 0
        cor = self.colors[self.index]

        self.index += 1
        return cor

