#*
#*  clip.c
#*  This program demonstrates arbitrary clipping planes.

from OpenGL import *

def init():
    glClearColor (0.0, 0.0, 0.0, 0.0);
    glShadeModel (GL_FLAT);

def display():
    eqn = 0.0, 1.0, 0.0, 0.0
    eqn2 = 1.0, 0.0, 0.0, 0.0

    glClear(GL_COLOR_BUFFER_BIT);

    glColor3f (1.0, 1.0, 1.0);
    glPushMatrix();
    glTranslatef (0.0, 0.0, -5.0);

    #*    clip lower half -- y < 0          *
    glClipPlane (GL_CLIP_PLANE0, eqn);
    glEnable (GL_CLIP_PLANE0);
    #*    clip left half -- x < 0           */
    glClipPlane (GL_CLIP_PLANE1, eqn2);
    glEnable (GL_CLIP_PLANE1);

    glRotatef (90.0, 1.0, 0.0, 0.0);
    glutWireSphere(1.0, 20, 16);
    glPopMatrix();

    glFlush ();

def reshape (w, h):
    glViewport (0, 0, w, h); 
    glMatrixMode (GL_PROJECTION);
    glLoadIdentity ();
    gluPerspective(60.0, w/(1.0*h), 1.0, 20.0);
    glMatrixMode (GL_MODELVIEW);

def keyboard(key, x, y):
    if key == chr (27):
	raise SystemExit

import sys

def main():
    glutInit();
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB);
    glutInitWindowSize (500, 500); 
    glutInitWindowPosition (100, 100);
    glutCreateWindow (sys.argv[0]);
    init ();
    glutDisplayFunc(display); 
    glutReshapeFunc(reshape);
    glutKeyboardFunc(keyboard);
    glutMainLoop();

main ()
