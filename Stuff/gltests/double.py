#*  double.py
#*  This is a simple double buffered program.
#*  Pressing the left mouse button rotates the rectangle.
#*  Pressing the middle mouse button stops the rotation.

from OpenGL import *

spin = 0.0
t0 = 0.0

def display ():
    glClear (GL_COLOR_BUFFER_BIT)
    glPushMatrix ()
    glRotatef (spin, 0.0, 0.0, 1.0)
    glColor3f (1.0, 1.0, 1.0)
    glRectf (-25.0, -25.0, 25.0, 25.0)
    glPopMatrix ()
    glutSwapBuffers ()

def gettime ():
    return glutGet (GLUT_ELAPSED_TIME) / 1000.0

def spinDisplay ():
    global spin, t0
    t = gettime ()
    dt = t - t0
    t0 = t
    spin = spin + 120.0*dt
    if spin > 360.0:
        spin = spin - 360.0
    glutPostRedisplay()

def init ():
    glClearColor (0.0, 0.0, 0.0, 0.0)
    glShadeModel (GL_FLAT)

def reshape (w, h):
    glViewport (0, 0, w, h)
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity ()
    glOrtho (-50.0, 50.0, -50.0, 50.0, -1.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity ()

def mouse (button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
	    global t0
	    t0 = gettime ()
            glutIdleFunc (spinDisplay)
    elif button == GLUT_MIDDLE_BUTTON or button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            glutIdleFunc (None)
   

def key (k, x, y):
    if k == chr (27):
	raise SystemExit
    glutPostRedisplay ()

#  Request double buffer display mode.
#  Register mouse input callback functions
glutInit ()#(sys.argv)
glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize (250, 250)
glutInitWindowPosition (100, 100)
glutCreateWindow ('Double')
init ()
glutDisplayFunc (display)
glutReshapeFunc (reshape)
glutMouseFunc (mouse)
glutKeyboardFunc (key)
glutMainLoop ()
