#*  light.c
#*  This program demonstrates the use of the OpenGL lighting
#*  model.  A sphere is drawn using a grey material characteristic.
#*  A single light source illuminates the object.

from OpenGL import *

#*  Initialize material property, light source, lighting model,
#*  and depth buffer.
def init():
    mat_specular = 1.0, 1.0, 1.0, 1.0
    mat_shininess = 50.0, 
    light_position = 1.0, 1.0, 1.0, 0.0

    glClearColor (0.0, 0.0, 0.0, 0.0);
    glShadeModel (GL_SMOOTH);

    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular);
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess);
    glLightfv(GL_LIGHT0, GL_POSITION, light_position);

    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);
    glEnable(GL_DEPTH_TEST);

def display():
    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glutSolidSphere (1.0, 20, 16);
    glFlush ();

def reshape(w, h):
    glViewport (0, 0, w, h)
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity ()
    if w <= h:
        glOrtho (-1.5, 1.5, (-1.5*h)/w, (1.5*h)/w, -10.0, 10.0)
    else:
        glOrtho ((-1.5*w)/h, (1.5*w)/h, -1.5, 1.5, -10.0, 10.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity ()

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
   init ();
   glutDisplayFunc(display); 
   glutReshapeFunc(reshape);
   glutKeyboardFunc(keyboard);
   glutMainLoop();

main ()
