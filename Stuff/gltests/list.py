#*  list.c
#*  This program demonstrates how to make and execute a 
#*  display list.  Note that attributes, such as current 
#*  color and matrix, are changed.

from OpenGL import *

def init ():
    global listName
    listName = glGenLists (1);
    glNewList (listName, GL_COMPILE);
    glColor3f (1.0, 0.0, 0.0);  #/*  current color red  */
    glBegin (GL_TRIANGLES);
    glVertex2f (0.0, 0.0);
    glVertex2f (1.0, 0.0);
    glVertex2f (0.0, 1.0);
    glEnd ();
    glTranslatef (1.5, 0.0, 0.0); #/*  move position  */
    glEndList ();
    glShadeModel (GL_FLAT);

def drawLine ():
    glBegin (GL_LINES);
    glVertex2f (0.0, 0.5);
    glVertex2f (15.0, 0.5);
    glEnd ();

def display():
    glClear (GL_COLOR_BUFFER_BIT);
    glColor3f (0.0, 1.0, 0.0);  #/*  current color green  */
    for i in xrange (10):
        glCallList (listName);
    drawLine (); # /*  is this line green?  NO!  */
                 #/*  where is the line drawn?  */
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
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB);
    glutInitWindowSize (650, 50); 
    glutCreateWindow (sys.argv[0]);
    init ();
    glutDisplayFunc(display); 
    glutReshapeFunc(reshape);
    glutKeyboardFunc(keyboard);
    glutMainLoop();

main ()
