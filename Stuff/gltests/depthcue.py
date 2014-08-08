
#*  depthcue.c
#*  This program draws a wireframe model, which uses
#*  intensity (brightness) to give clues to distance.
#*  Fog is used to achieve this effect.

from OpenGL import *

def myinit():
    fogColor = 0.0, 0.0, 0.0, 1.0

    glEnable(GL_FOG);
    glFogi (GL_FOG_MODE, GL_LINEAR);
    glHint (GL_FOG_HINT, GL_NICEST);  #/*  per pixel   */
    glFogf (GL_FOG_START, 3.0);
    glFogf (GL_FOG_END, 5.0);
    glFogfv (GL_FOG_COLOR, fogColor);
    glClearColor(0.0, 0.0, 0.0, 1.0);

    glDepthFunc(GL_LESS);
    glEnable(GL_DEPTH_TEST);
    glShadeModel(GL_FLAT);

#*  display() draws an icosahedron.
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glColor3f (1.0, 1.0, 1.0);
    glutWireIcosahedron();
    glFlush();

def myReshape(w, h):
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective (45.0, (1.0 * w)/ h, 3.0, 5.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity ();
    glTranslatef (0.0, 0.0, -4.0); 

def keyboard(key, x, y):
    if key == chr (27):
	raise SystemExit

import sys

def main():
   glutInit()
   glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH);
   glutInitWindowSize (500, 500); 
   glutInitWindowPosition (100, 100);
   glutCreateWindow (sys.argv[0]);
   myinit ();
   glutDisplayFunc(display); 
   glutReshapeFunc(myReshape);
   glutKeyboardFunc(keyboard);
   glutMainLoop();

main ()
