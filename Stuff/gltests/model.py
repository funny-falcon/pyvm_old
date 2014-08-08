#*  model.c
#*  This program demonstrates modeling transformations

from OpenGL import *

def init():
    glClearColor (0.0, 0.0, 0.0, 0.0);
    glShadeModel (GL_FLAT);

def draw_triangle():
    glBegin (GL_LINE_LOOP);
    glVertex2f(0.0, 25.0);
    glVertex2f(25.0, -25.0);
    glVertex2f(-25.0, -25.0);
    glEnd();

def display():
    glClear (GL_COLOR_BUFFER_BIT);
    glColor3f (1.0, 1.0, 1.0);

    glLoadIdentity ();
    glColor3f (1.0, 1.0, 1.0);
    draw_triangle ();

    glEnable (GL_LINE_STIPPLE);
    glLineStipple (1, 0xF0F0);
    glLoadIdentity ();
    glTranslatef (-20.0, 0.0, 0.0);
    draw_triangle ();

    glLineStipple (1, 0xF00F);
    glLoadIdentity ();
    glScalef (1.5, 0.5, 1.0);
    draw_triangle ();

    glLineStipple (1, 0x8888);
    glLoadIdentity ();
    glRotatef (90.0, 0.0, 0.0, 1.0);
    draw_triangle ();
    glDisable (GL_LINE_STIPPLE);

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
