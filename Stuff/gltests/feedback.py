#* feedback.c
#* This program demonstrates use of OpenGL feedback.  First,
#* a lighting environment is set up and a few lines are drawn.
#* Then feedback mode is entered, and the same lines are 
#* drawn.  The results in the feedback buffer are printed.

from array import array
from OpenGL import *

#*  Initialize lighting.
def init():
    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);

#* Draw a few lines and two points, one of which will 
#* be clipped.  If in feedback mode, a passthrough token 
#* is issued between the each primitive.
def drawGeometry (mode):
    glBegin (GL_LINE_STRIP);
    glNormal3f (0.0, 0.0, 1.0);
    glVertex3f (30.0, 30.0, 0.0);
    glVertex3f (50.0, 60.0, 0.0);
    glVertex3f (70.0, 40.0, 0.0);
    glEnd ();
    if (mode == GL_FEEDBACK):
        glPassThrough (1.0);
    glBegin (GL_POINTS);
    glVertex3f (-100.0, -100.0, -100.0);  #/*  will be clipped  */
    glEnd ();
    if (mode == GL_FEEDBACK):
        glPassThrough (2.0);
    glBegin (GL_POINTS);
    glNormal3f (0.0, 0.0, 1.0);
    glVertex3f (50.0, 50.0, 0.0);
    glEnd ();

#* Write contents of one vertex to stdout.	*/
def print3DcolorVertex (size, count, buffer):
   print "  ",
   for i in xrange (7):
      print "%4.2f " %buffer[size-count],
      count = count - 1;
   print 
   return count

#*  Write contents of entire buffer.  (Parse tokens!)	*/
def printBuffer(size, buffer):
   count = size;
   while count:
      token = buffer[size-count];
      count -= 1
      if token == GL_PASS_THROUGH_TOKEN:
         print "GL_PASS_THROUGH_TOKEN"
         print "  %4.2f\n"% buffer[size-count]
         count -= 1
      elif token == GL_POINT_TOKEN:
         print "GL_POINT_TOKEN"
         count = print3DcolorVertex (size, count, buffer)
      elif (token == GL_LINE_TOKEN): 
         print "GL_LINE_TOKEN"
         count = print3DcolorVertex (size, count, buffer)
         count = print3DcolorVertex (size, count, buffer)
      elif token == GL_LINE_RESET_TOKEN:
         print "GL_LINE_RESET_TOKEN"
         count = print3DcolorVertex (size, count, buffer)
         count = print3DcolorVertex (size, count, buffer)

def display():
    feedBuffer = array ('f', 1024 * [0])

    glMatrixMode (GL_PROJECTION);
    glLoadIdentity ();
    glOrtho (0.0, 100.0, 0.0, 100.0, 0.0, 1.0);

    glClearColor (0.0, 0.0, 0.0, 0.0);
    glClear(GL_COLOR_BUFFER_BIT);
    drawGeometry (GL_RENDER);

    glFeedbackBuffer (1024, GL_3D_COLOR, feedBuffer);
    glRenderMode (GL_FEEDBACK);
    drawGeometry (GL_FEEDBACK);

    size = glRenderMode (GL_RENDER);
    printBuffer (size, feedBuffer);

    glFinish();

def keyboard(key, x, y):
    if key == chr (27):
	raise SystemExit

import sys

def main():
   glutInit()
   glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB);
   glutInitWindowSize (100, 100); 
   glutInitWindowPosition (100, 100);
   glutCreateWindow (sys.argv[0]);
   init ();
   glutDisplayFunc(display); 
   glutKeyboardFunc(keyboard);
   glutMainLoop();

main ()
