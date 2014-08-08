
#*  fogindex.c
#*  This program demonstrates fog in color index mode.
#*  Three cones are drawn at different z values in a linear
#*  fog.  32 contiguous colors (from 16 to 47) are loaded
#*  with a color ramp.

from OpenGL import *

#*  Initialize color map and fog.  Set screen clear color
#*  to end of color ramp.
NUM_COLORS=32
RAMPSTART=16

def myinit():
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LESS);
    for i in range (NUM_COLORS):
        shade = (NUM_COLORS - i) / float (NUM_COLORS);
        glutSetColor(16 + i, shade, shade, shade);
    glEnable(GL_FOG);

    glFogi(GL_FOG_MODE, GL_LINEAR);
    glFogi(GL_FOG_INDEX, NUM_COLORS);
    glFogf(GL_FOG_START, 0.0);
    glFogf(GL_FOG_END, 4.0);
    glHint(GL_FOG_HINT, GL_NICEST);
    glClearIndex((NUM_COLORS + RAMPSTART - 1));

#*  display() renders 3 cones at different z positions.
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glPushMatrix();
    glTranslatef(-1.0, -1.0, -1.0);
    glRotatef(-90.0, 1.0, 0.0, 0.0);
    glIndexi(RAMPSTART);
    glutSolidCone(1.0, 2.0, 10, 10);
    glPopMatrix();

    glPushMatrix();
    glTranslatef(0.0, -1.0, -2.25);
    glRotatef(-90.0, 1.0, 0.0, 0.0);
    glIndexi(RAMPSTART);
    glutSolidCone(1.0, 2.0, 10, 10);
    glPopMatrix();

    glPushMatrix();
    glTranslatef(1.0, -1.0, -3.5);
    glRotatef(-90.0, 1.0, 0.0, 0.0);
    glIndexi(RAMPSTART);
    glutSolidCone(1.0, 2.0, 10, 10);
    glPopMatrix();
    glFlush();

def myReshape(w, h):
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    if (w <= h):
        glOrtho(-2.0, 2.0, (-2.0 * h) / w,
         (2.0 * h) / w, 0.0, 10.0);
    else:
        glOrtho((-2.0 * w) / h,
          (2.0 * w) / h, -2.0, 2.0, 0.0, 10.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

def keyboard(key, x, y):
    if key == chr (27):
	raise SystemExit

import sys

def main():
   glutInit()
   glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH);
   glutCreateWindow (sys.argv[0]);
   myinit ();
   glutDisplayFunc(display); 
   glutReshapeFunc(myReshape);
   glutKeyboardFunc(keyboard);
   glutMainLoop();

main ()
