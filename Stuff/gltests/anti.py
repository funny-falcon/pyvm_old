#*  anti.c
#*  This program draws antialiased lines in RGBA mode.

import sys
from array import array
from OpenGL import *

#*  Initialize antialiasing for RGBA mode, including alpha
#*  blending, hint, and line width.  Print out implementation
#*  specific info on line width granularity and width.
def myinit():
    values = array ('f', [0,0]);
    glGetFloatv (GL_LINE_WIDTH_GRANULARITY, values);
    print "GL_LINE_WIDTH_GRANULARITY value is %3.1f" %values[0]

    glGetFloatv (GL_LINE_WIDTH_RANGE, values);
    print "GL_LINE_WIDTH_RANGE values are %3.1f %3.1f" %(values[0], values[1]);

    glEnable (GL_LINE_SMOOTH);
    glEnable (GL_BLEND);
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glHint (GL_LINE_SMOOTH_HINT, GL_DONT_CARE);
    glLineWidth (1.5);

    glShadeModel(GL_FLAT);
    glClearColor(0.0, 0.0, 0.0, 0.0);
    glDepthFunc(GL_LESS);
    glEnable(GL_DEPTH_TEST);

#*  display() draws an icosahedron with a large alpha value, 1.0.
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glColor4f (1.0, 1.0, 1.0, 1.0);
    glutWireIcosahedron();
    glFlush();

def myReshape(w, h):
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective (45.0, (1.0 * w)/h, 3.0, 5.0);

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity ();
    glTranslatef (0.0, 0.0, -4.0);  #/*  move object into view   */

def key(k, x, y):
    if k == chr (27):
	raise SystemExit
    glutPostRedisplay();

#*  Main Loop
#*  Open window with initial window size, title bar,
#*  RGBA display mode, and handle input events.
def main():
    glutInit();
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH);
    glutCreateWindow (sys.argv[0]);
    myinit();
    glutReshapeFunc (myReshape);
    glutDisplayFunc(display);
    glutKeyboardFunc(key);
    glutMainLoop();
main ()
