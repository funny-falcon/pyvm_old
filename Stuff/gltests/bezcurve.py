#*  bezcurve.c			
#*  This program uses evaluators to draw a Bezier curve.

import sys

from OpenGL import *

ctrlpoints = (
	( -4.0, -4.0, 0.0), ( -2.0, 4.0, 0.0), 
	(2.0, -4.0, 0.0), (4.0, 4.0, 0.0))

def init():
    glClearColor(0.0, 0.0, 0.0, 0.0);
    glShadeModel(GL_FLAT);
    glMap1f(GL_MAP1_VERTEX_3, 0.0, 1.0, 3, 4, [x for y in ctrlpoints for x in y]);
    glEnable(GL_MAP1_VERTEX_3);

def display():
    glClear(GL_COLOR_BUFFER_BIT);
    glColor3f(1.0, 1.0, 1.0);
    glBegin(GL_LINE_STRIP);
    for i in xrange (31):
         glEvalCoord1f(i/30.0);
    glEnd();
    #* The following code displays the control points as dots. *
    glPointSize(5.0);
    glColor3f(1.0, 1.0, 0.0);
    glBegin(GL_POINTS);
    for i in ctrlpoints:
         glVertex3fv (i);
    glEnd();
    glFlush();

def reshape(w, h):
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    if (w <= h):
        glOrtho(-5.0, 5.0, -(5.0*h)/w, 
               (5.0*h)/w, -5.0, 5.0);
    else:
        glOrtho((-5.0*w)/h, 
               (5.0*w)/h, -5.0, 5.0, -5.0, 5.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

def keyboard(key, x, y):
    if key == chr (27):
	raise SystemExit

def main():
    glutInit();
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB);
    glutInitWindowSize (500, 500);
    glutInitWindowPosition (100, 100);
    glutCreateWindow (sys.argv[0]);
    init ();
    glutDisplayFunc(display);
    glutReshapeFunc(reshape);
    glutKeyboardFunc (keyboard);
    glutMainLoop();

main ()
