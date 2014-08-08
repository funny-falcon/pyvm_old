#*  aaindex.c
#*  This program draws shows how to draw anti-aliased lines in color
#*  index mode. It draws two diagonal lines to form an X; when 'r' 
#*  is typed in the window, the lines are rotated in opposite 
#*  directions.

from OpenGL import *

RAMPSIZE=16
RAMP1START=32
RAMP2START=48

rotAngle = 0.0

#*  Initialize antialiasing for color index mode,
#*  including loading a green color ramp starting
#*  at RAMP1START, and a blue color ramp starting
#*  at RAMP2START. The ramps must be a multiple of 16.
def init ():
    for i in xrange (RAMPSIZE):
	shade = (1.0 * i) / RAMPSIZE
	glutSetColor (RAMP1START + i, 0.0, shade, 0.0)
	glutSetColor (RAMP2START + i, 0.0, 0.0, shade)

    glEnable (GL_LINE_SMOOTH)
    glHint (GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
    glLineWidth (1.5)
    glClearIndex (RAMP1START)

#*  Draw 2 diagonal lines to form an X
def display():
    glClear (GL_COLOR_BUFFER_BIT)

    glIndexi (RAMP1START)
    glPushMatrix ()
    glRotatef (-rotAngle, 0.0, 0.0, 0.1)
    glBegin (GL_LINES)
    glVertex2f (-0.5, 0.5)
    glVertex2f (0.5, -0.5)
    glEnd ()
    glPopMatrix()

    glIndexi (RAMP2START)
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
    else :
        gluOrtho2D ((-1.0*w)/h, (1.0*w)/h, -1.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity ()

def keyboard(key, x, y):
    global rotAndle
    if key in 'rR':
        rotAngle += 20.0
        if rotAngle >= 360.0:
	     rotAngle = 0.0
        glutPostRedisplay ()
    elif key == chr (27):
	raise SystemExit

#*  Main Loop
#*  Open window with initial window size, title bar, 
#*  color index display mode, and handle input events.
def main():
    glutInit ()
    glutInitDisplayMode (GLUT_SINGLE | GLUT_INDEX)
    glutInitWindowSize (200, 200)
    glutCreateWindow ('aaindex')
    init ()
    glutReshapeFunc (reshape)
    glutKeyboardFunc (keyboard)
    glutDisplayFunc (display)
    glutMainLoop ()

main ()
