
#*  drawf.c
#*  Draws the bitmapped letter F on the screen(several times).
#*  This demonstrates use of the glBitmap() call.

import sys
from OpenGL import *

rasterBytes = (
    0xc0, 0x00, 0xc0, 0x00, 0xc0, 0x00, 0xc0, 0x00, 0xc0, 0x00,
    0xff, 0x00, 0xff, 0x00, 0xc0, 0x00, 0xc0, 0x00, 0xc0, 0x00,
    0xff, 0xc0, 0xff, 0xc0
)

# should be array('c', ''.join (...))
rasters = ''.join ([chr (i) for i in rasterBytes])

def init():
    glPixelStorei (GL_UNPACK_ALIGNMENT, 1)
    glClearColor (0.0, 0.0, 0.0, 0.0)

def display():
    glClear (GL_COLOR_BUFFER_BIT)
    glColor3f (1.0, 1.0, 1.0)
    glRasterPos2i (20, 20)
    glBitmap (10, 12, 0.0, 0.0, 11.0, 0.0, rasters)
    glBitmap (10, 12, 0.0, 0.0, 11.0, 0.0, rasters)
    glBitmap (10, 12, 0.0, 0.0, 11.0, 0.0, rasters)
    glFlush ()

def reshape(w, h):
    glViewport (0, 0, w, h)
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity ()
    glOrtho (0, w, 0, h, -1.0, 1.0)
    glMatrixMode (GL_MODELVIEW)

def keyboard(key, x, y):
    if key == chr (27):
	raise SystemExit

#  Main Loop
#  Open window with initial window size, title bar, 
#  RGBA display mode, and handle input events.

glutInit ()#(sys.argv)
glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize (100, 100)
glutInitWindowPosition (100, 100)
glutCreateWindow ('drawf')
init ()
glutReshapeFunc (reshape)
glutKeyboardFunc (keyboard)
glutDisplayFunc (display)
glutMainLoop ()
