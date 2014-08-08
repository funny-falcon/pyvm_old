#*  aargb.c
#*  This program draws shows how to draw anti-aliased lines. It draws
#*  two diagonal lines to form an X; when 'r' is typed in the window, 
#*  the lines are rotated in opposite directions.

from array import array

from OpenGL import *

rotAngle = 0.0

#*  Initialize antialiasing for RGBA mode, including alpha
#*  blending, hint, and line width.  Print out implementation
#*  specific info on line width granularity and width.
def init():
    values = array ('f', [0, 0])
    glGetFloatv (GL_LINE_WIDTH_GRANULARITY, values);
    print "GL_LINE_WIDTH_GRANULARITY value is %3.1f" %values [0]

    glGetFloatv (GL_LINE_WIDTH_RANGE, values)
    print "GL_LINE_WIDTH_RANGE values are %3.1f %3.1f", (values[0], values[1])

    glEnable (GL_LINE_SMOOTH)
    glEnable (GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint (GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
    glLineWidth (1.5)

    glClearColor(0.0, 0.0, 0.0, 0.0)

#* Draw 2 diagonal lines to form an X
def display():
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f (0.0, 1.0, 0.0)
    glPushMatrix ()
    glRotatef (-rotAngle, 0.0, 0.0, 0.1)
    glBegin (GL_LINES)
    glVertex2f (-0.5, 0.5)
    glVertex2f (0.5, -0.5)
    glEnd ()
    glPopMatrix()

    glColor3f (0.0, 0.0, 1.0)
    glPushMatrix ()
    glRotatef (rotAngle, 0.0, 0.0, 0.1)
    glBegin (GL_LINES)
    glVertex2f (0.5, 0.5)
    glVertex2f (-0.5, -0.5)
    glEnd ()
    glPopMatrix()

    glFlush()

def reshape(w, h):
    glViewport (0, 0, w, h)
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity ()
    if w <= h: 
        gluOrtho2D (-1.0, 1.0, (-1.0*h)/w, (1.0*h)/w)
    else:
        gluOrtho2D ((-1.0*w)/h, (1.0*w)/h, -1.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity ()

def keyboard(key, x, y):
    global rotAngle
    if key == 'r':
         rotAngle += 4.0
         if rotAngle >= 360.0:
	     rotAngle = 0.0
         glutPostRedisplay ()
    elif key == chr (27):
	raise SystemExit

#*  Main Loop
#*  Open window with initial window size, title bar, 
#*  RGBA display mode, and handle input events.
def main():
    glutInit ()
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize (200, 200)
    glutCreateWindow ('aargb')
    init()
    glutReshapeFunc (reshape)
    glutKeyboardFunc (keyboard)
    glutDisplayFunc (display)
    glutMainLoop ()

main ()
