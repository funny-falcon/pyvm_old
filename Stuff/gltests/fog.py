
#*  fog.py
#*  This program draws 5 red spheres, each at a different 
#*  z distance from the eye, in different types of fog.  
#*  Pressing the f key chooses between 3 types of 
#*  fog:  exponential, exponential squared, and linear.  
#*  In this program, there is a fixed density value, as well 
#*  as fixed start and end values for the linear fog.
 
import sys
from OpenGL import *

fogMode = 0

def selectFog (mode):
    if mode == 0:
	import sys
	sys.exit (0)
    print "TEH MODE IST:", mode
    if mode == GL_LINEAR:
        glFogf (GL_FOG_START, 1.0)
        glFogf (GL_FOG_END, 5.0)
	glFogi (GL_FOG_MODE, mode)
	glutPostRedisplay ()
    elif mode in (GL_EXP2, GL_EXP):
	glFogi (GL_FOG_MODE, mode)
	glutPostRedisplay ()

#*  Initialize z-buffer, projection matrix, light source,
#*  and lighting model.  Do not specify a material property here.
def myinit ():
    global fogMode

    position = 0.0, 3.0, 3.0, 0.0
    local_view = 0.0,

    glEnable (GL_DEPTH_TEST)
    glDepthFunc (GL_LESS)

    glLightfv (GL_LIGHT0, GL_POSITION, position)
    glLightModelfv (GL_LIGHT_MODEL_LOCAL_VIEWER, local_view)

    glFrontFace (GL_CW)
    glEnable (GL_LIGHTING)
    glEnable (GL_LIGHT0)
    glEnable (GL_AUTO_NORMAL)
    glEnable (GL_NORMALIZE)
    glEnable (GL_FOG)
    fogColor = 0.5, 0.5, 0.5, 1.0

    fogMode = GL_EXP;
    glFogi (GL_FOG_MODE, fogMode)
    glFogfv (GL_FOG_COLOR, fogColor)
    glFogf (GL_FOG_DENSITY, 0.35)
    glHint (GL_FOG_HINT, GL_DONT_CARE)
    glClearColor (0.5, 0.5, 0.5, 1.0)

def renderRedTeapot (x, y, z):
    glPushMatrix ();
    glTranslatef (x, y, z);
    mat = [0.1745, 0.01175, 0.01175, 1.0]
    glMaterialfv (GL_FRONT, GL_AMBIENT, mat)
    mat[0] = 0.61424
    mat[1] = 0.04136
    mat[2] = 0.04136
    glMaterialfv (GL_FRONT, GL_DIFFUSE, mat)
    mat[0] = 0.727811
    mat[1] = 0.626959
    mat[2] = 0.626959
    glMaterialfv (GL_FRONT, GL_SPECULAR, mat)
    glMaterialf (GL_FRONT, GL_SHININESS, 0.6 * 128.0)
    glutSolidTeapot (1.0)
    glPopMatrix ()

#*  display() draws 5 teapots at different z positions.
def display():
    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    renderRedTeapot (-4.0, -0.5, -1.0)
    renderRedTeapot (-2.0, -0.5, -2.0)
    renderRedTeapot (0.0, -0.5, -3.0)
    renderRedTeapot (2.0, -0.5, -4.0)
    renderRedTeapot (4.0, -0.5, -5.0)
    glFlush ()

def myReshape (w, h):
    glViewport (0, 0, w, h)
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity ()
    if w <= (h * 3):
        glOrtho (-6.0, 6.0, -2.0 * (h * 3.0) / w,
            2.0 * (h * 3.0) / w, 0.0, 10.0)
    else:
        glOrtho(-6.0 * w / (h * 3.0),
            6.0 * w / (h * 3.0), -2.0, 2.0, 0.0, 10.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity ()

def key (k, x, y):
    if k == chr (27):
	raise SystemExit
    glutPostRedisplay()

#*  Main Loop
#*  Open window with initial window size, title bar,
#*  RGBA display mode, depth buffer, and handle input events.
def main ():
    glutInit ()#(&argc, argv)
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize (450, 150)
    glutCreateWindow ('fog')
    myinit ()
    glutReshapeFunc (myReshape)
    glutDisplayFunc (display)
    glutCreateMenu (selectFog)
    glutAddMenuEntry ("Fog EXP", GL_EXP)
    glutAddMenuEntry ("Fog EXP2", GL_EXP2)
    glutAddMenuEntry ("Fog LINEAR", GL_LINEAR)
    glutAddMenuEntry ("Quit", 0)
    glutAttachMenu (GLUT_RIGHT_BUTTON)
    glutKeyboardFunc (key)
    glutMainLoop ()

main ()
