
#*  bezsurf.c
#*  This program renders a lighted, filled Bezier surface,
#*  using two-dimensional evaluators.

from OpenGL import *

ctrlpoints = (
    (
        (-1.5, -1.5, 4.0),
        (-0.5, -1.5, 2.0),
        (0.5, -1.5, -1.0),
        (1.5, -1.5, 2.0)),
    (
        (-1.5, -0.5, 1.0),
        (-0.5, -0.5, 3.0),
        (0.5, -0.5, 0.0),
        (1.5, -0.5, -1.0)),
    (
        (-1.5, 0.5, 4.0),
        (-0.5, 0.5, 0.0),
        (0.5, 0.5, 3.0),
        (1.5, 0.5, 4.0)),
    (
        (-1.5, 1.5, -2.0),
        (-0.5, 1.5, -2.0),
        (0.5, 1.5, 0.0),
        (1.5, 1.5, -1.0))
)

def initlights():
    ambient = 0.2, 0.2, 0.2, 1.0
    position = 0.0, 0.0, 2.0, 1.0
    mat_diffuse = 0.6, 0.6, 0.6, 1.0
    mat_specular = 1.0, 1.0, 1.0, 1.0
    mat_shininess = 50.0,

    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);

    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient);
    glLightfv(GL_LIGHT0, GL_POSITION, position);

    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse);
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular);
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess);

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glPushMatrix();
    glRotatef(85.0, 1.0, 1.0, 1.0);
    glEvalMesh2(GL_FILL, 0, 20, 0, 20);
    glPopMatrix();
    glFlush();

def flatten3D (lst):
    return [x for y in lst for z in y for x in z]

def myinit():
    glClearColor(0.0, 0.0, 0.0, 1.0);
    glEnable(GL_DEPTH_TEST);
    glMap2f(GL_MAP2_VERTEX_3, 0, 1, 3, 4,
        0, 1, 12, 4, flatten3D (ctrlpoints));
    glEnable(GL_MAP2_VERTEX_3);
    glEnable(GL_AUTO_NORMAL);
    glEnable(GL_NORMALIZE);
    glMapGrid2f(20, 0.0, 1.0, 20, 0.0, 1.0);
    initlights();       #* for lighted version only *

def myReshape(w, h):
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    if (w <= h):
        glOrtho(-4.0, 4.0, (-4.0 * h) / w,
            (4.0 * h) / w, -4.0, 4.0);
    else:
        glOrtho(-(4.0 * w) / h,
            (4.0 * w) / h, -4.0, 4.0, -4.0, 4.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

def key(k, x, y):
    if k == chr (27):
	raise SystemExit

import sys

def main():
    glutInit();
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH);
    glutCreateWindow(sys.argv[0]);
    myinit();
    glutReshapeFunc(myReshape);
    glutDisplayFunc(display);
    glutKeyboardFunc(key);
    glutMainLoop();

main ()
