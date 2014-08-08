#
# What is GL, GLX, GLU and GLUT?
# What's their relation with OpenGL?
# What's Mesa? Where do video card acceleration gets in? What about X?
#
# If you are not into graphics these questions will seem very complicated.
# Here's a clue:
#	Mesa is an open source implementation of the openGL API/ABI
#	Mesa can talk to X windows DRI and use card vendor libraries
#	and hardware features.  However, Mesa is still the API.
#	Mesa gives gl.h and glx.h
#	GLU is another package that has AFAIK some 3D torus stuff.
#	GLUT is yet another package, freeglut which gives menus and
#	I/O on top of OpenGL
#	
#	By linking against glut, we also get gl, glx, glu.
#	I think that glut is as standard as the rest; i.e. you won't
#	find a system that gives GL but not GLUT.
#	So I think getting all the symbols from libglut will suffice.
#
import sys, os
import DLL

import GLCONSTS, GLUCONSTS, GLUTCONSTS
from GLCONSTS import *
from GLUTCONSTS import *
from GLUCONSTS import *

# we really need __all__

__all__ = GLCONSTS.__all__ + GLUCONSTS.__all__ + GLUTCONSTS.__all__

# for linux, for windows something else here,
# like DLL.dllopen ('glut32.DLL')

GLUTlib = DLL.dllopen ('libglut.so')

#

def DF (name, spec, ret=''):
    print "ADD NAME:", name
    globals() [name] = GLUTlib.get ((ret, name, spec))
    __all__.append (name)

DF ('glAccum', 'if')
DF ('glBegin', 'i')
DF ('glBitmap', 'iiffffp8')
DF ('glBlendFunc', 'ii')
DF ('glCallList', 'i')
DF ('glCallLists', 'iiv')
DF ('glClearColor', 'ffff')
DF ('glClearAccum', 'ffff')
DF ('glClear', 'i')
DF ('glClearIndex', 'f')
DF ('glClipPlane', 'ipd')
DF ('glColor3f', 'fff')
DF ('glColor3fv', 'pf')
DF ('glColor4f', 'ffff')
DF ('glColor4fv', 'pf')
DF ('glColorPointer', 'iiiv')
DF ('glColorMaterial', 'ii')
DF ('glCopyPixels', 'iiiii')
DF ('glCullFace', 'i')
DF ('glDepthFunc', 'i')
DF ('glDepthMask', 'i')
DF ('glDisable', 'i')
DF ('glDrawElements', 'iiiv')
DF ('glDrawPixels', 'iiiiv')
DF ('glDisableClientState', 'i')
DF ('glEnable', 'i')
DF ('glEnableClientState', 'i')
DF ('glEnd', '')
DF ('glEndList', '')
DF ('glEvalMesh2', 'iiiii')
DF ('glEvalCoord1f', 'f')
DF ('glFeedbackBuffer', 'iipf')
DF ('glFinish', '')
DF ('glFlush', '')
DF ('glFrustum', 'dddddd')
DF ('glFrontFace', 'i')
DF ('glFogi', 'ii')
DF ('glFogfv', 'ipf')
DF ('glFogf', 'if')
DF ('glGetFloatv', 'ipf')
DF ('glGetIntegerv', 'ip32')
DF ('glGenLists', 'i', 'i') ##
DF ('glHint', 'ii')
DF ('glIndexi', 'i')
DF ('glInitNames', '')
DF ('glLightfv', 'iipf')
DF ('glLightModelfv', 'ipf')
DF ('glLineStipple', 'ii')
DF ('glLineWidth', 'f')
DF ('glListBase', 'i')
DF ('glLoadIdentity', '')
DF ('glLoadName', 'i')
DF ('glMap1f', 'iffiipf')
DF ('glMap2f', 'iffiiffiipf')
DF ('glMapGrid2f', 'iffiff')
DF ('glMaterialfv', 'iipf')
DF ('glMaterialf', 'iif')
DF ('glMatrixMode', 'i')
DF ('glNormal3f', 'fff')
DF ('glNewList', 'ii')
DF ('glOrtho', 'dddddd')
DF ('glPassThrough', 'f')
DF ('glPushMatrix', '')
DF ('glPopMatrix', '')
DF ('glPixelStorei', 'ii')
DF ('glPixelZoom', 'ff')
DF ('glPointSize', 'f')
DF ('glPushAttrib', 'i')
DF ('glPopAttrib', '')
DF ('glRotatef', 'ffff')
DF ('glRotated', 'dddd')
DF ('glRectf', 'ffff')
DF ('glRecti', 'iiii')
DF ('glRasterPos2i', 'ii')
DF ('glRenderMode', 'i', 'i') ##
DF ('glShadeModel', 'i')
DF ('glScalef', 'fff')
DF ('glTranslatef', 'fff')
DF ('glTranslated', 'ddd')
DF ('glTexImage2D', 'iiiiiiiiv')
DF ('glTexParameterf', 'iif')
DF ('glTexEnvf', 'iif')
DF ('glTexCoord2f', 'ff')
DF ('glViewport', 'iiii')
DF ('glVertex3f', 'fff')
DF ('glVertex2f', 'ff')
DF ('glVertex2i', 'ii')
DF ('glVertex3fv', 'pf')
DF ('glVertexPointer', 'iiiv')


DF ('gluBeginSurface', 'i')
DF ('gluEndSurface', 'i')
DF ('gluNewNurbsRenderer', '', 'i')	## returns ptr. we take int
DF ('gluNewQuadric', '', 'i')		## GLUquadricObj
DF ('gluQuadricDrawStyle', 'ii')
DF ('gluQuadricNormals', 'ii')
DF ('gluSphere', 'idii')
DF ('gluCylinder', 'idddii')
DF ('gluDisk', 'iddii')
DF ('gluPartialDisk', 'iddiidd')
DF ('gluNurbsProperty', 'iif')
DF ('gluNurbsSurface', 'iipfipfiipfiii')
DF ('gluLookAt', 'ddddddddd')
DF ('gluOrtho2D', 'dddd')
DF ('gluPerspective', 'dddd')
DF ('gluPickMatrix', 'ddddp32')

DF ('glutSetColor', 'ifff')
DF ('glutGet', 'i', 'i')
DF ('glutSwapBuffers', '')
DF ('glutPostRedisplay', '')
DF ('glutInitDisplayMode', 'i')
DF ('glutInitWindowSize', 'ii')
DF ('glutInitWindowPosition', 'ii')
DF ('glutMainLoop', '')
DF ('glutCreateWindow', 's')

DF ('glutAddMenuEntry', 'si')
DF ('glutAttachMenu', 'i')

DF ('glutWireCube', 'd')
DF ('glutWireSphere', 'dii')
DF ('glutSolidCube', 'd')
DF ('glutSolidTeapot', 'd')
DF ('glutSolidTorus', 'ddii')
DF ('glutSolidCone', 'ddii')
DF ('glutSolidSphere', 'dii')
DF ('glutSolidOctahedron', '')
DF ('glutWireIcosahedron', '')

class glutCallableObj:
    def __init__ (self, fname, argspec, converter=None):
	self.glFunc = GLUTlib.get (('', fname, 'i'))
	__all__.append (fname)
	self.argspec = argspec
	self.callable = None
	self.converter = converter
    def __call__ (self, func):
	if not self.callable:
	    self.callable = DLL.Callback (self.argspec)
	if func:
	    if self.converter:
		real_func = func
		def proxy (*args):
		    self.converter (real_func, *args)
		func = proxy
	    self.callable.set_callback (func)
	    self.glFunc (self.callable.fptr ())
	else:
	    self.glFunc (0)
	    

def keyconv (f, k, x, y):
    return f (chr (k), x, y)

glutDisplayFunc = glutCallableObj ('glutDisplayFunc', ('', ''))
glutIdleFunc = glutCallableObj ('glutIdleFunc', ('', ''))
glutReshapeFunc = glutCallableObj ('glutReshapeFunc', ('', 'ii'))
glutKeyboardFunc = glutCallableObj ('glutKeyboardFunc', ('', 'iii'), keyconv)
glutMouseFunc = glutCallableObj ('glutMouseFunc', ('', 'iiii'))
glutMotionFunc = glutCallableObj ('glutMotionFunc', ('', 'ii'))
glutCreateMenu = glutCallableObj ('glutCreateMenu', ('', 'i'))
glutSpecialFunc = glutCallableObj ('glutSpecialFunc', ('', 'iii'))
glutVisibilityFunc = glutCallableObj ('glutVisibilityFunc', ('', 'i'))

##########glutInit##############
PROG = r"""
	void myGlutInit ()
	{
		char argv [1];
		int argc = 0;
		glutInit (&argc, &argv);
	}
"""
mylib = DLL.CachedLib ('wrapgl', PROG, ['-lglut'])
glutInit = mylib.get (('', 'myGlutInit', ''))
__all__.append ('glutInit')
################################

#############gcc dd.c -fpic -Os -shared -o dd.so
#############gcc dd.c -fPIC -Os -shared -o dd.so
