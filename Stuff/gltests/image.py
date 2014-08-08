
#*  image.c
#*  This program demonstrates drawing pixels and shows the effect
#*  of glDrawPixels(), glCopyPixels(), and glPixelZoom().
#*  Interaction: moving the mouse while pressing the mouse button
#*  will copy the image in the lower-left corner of the window
#*  to the mouse position, using the current pixel zoom factors.
#*  There is no attempt to prevent you from drawing over the original
#*  image.  If you press the 'r' key, the original image and zoom
#*  factors are reset.  If you press the 'z' or 'Z' keys, you change
#*  the zoom factors.

from array import array
from OpenGL import *

#*	Create checkerboard image	*/
checkImageWidth=64
checkImageHeight=64

checkImage = [[ [0,0,0] for i in range (checkImageHeight)] for j in
 range (checkImageWidth)]


def makeCheckImage():
    for i in range (checkImageWidth):
	for j in range (checkImageHeight):
	    c = ((((i&0x8)==0)^((j&0x8)==0)))*255;
	    checkImage[i][j][0] = c;
	    checkImage[i][j][1] = c;
	    checkImage[i][j][2] = c;

def flatten3D (lst):
    return [x for y in lst for z in y for x in z]

zoomFactor = 1.0;

def init():
    glClearColor (0.0, 0.0, 0.0, 0.0);
    glShadeModel(GL_FLAT);
    makeCheckImage();
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1);

def display():
    glClear(GL_COLOR_BUFFER_BIT);
    glRasterPos2i(0, 0);
    glDrawPixels(checkImageWidth, checkImageHeight, GL_RGB, 
                GL_UNSIGNED_BYTE, array ('c', flatten3D (checkImage)));
    glFlush();

def reshape(w, h):
    glViewport(0, 0, w, h);
    global height
    height = h;
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluOrtho2D(0.0, w, 0.0, h);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

def motion(x,y):
   global screeny;
   
   screeny = height - y;
   glRasterPos2i (x, screeny);
   glPixelZoom (zoomFactor, zoomFactor);
   glCopyPixels (0, 0, checkImageWidth, checkImageHeight, GL_COLOR);
   glPixelZoom (1.0, 1.0);
   glFlush ();

def keyboard(key,x,y):
    global zoomFactor
    if key == 'r':
         zoomFactor = 1.0;
         glutPostRedisplay();
         print "zoomFactor reset to 1.0"
    elif key == 'z':
         zoomFactor += 0.5;
         if (zoomFactor >= 3.0) :
            zoomFactor = 3.0;
         print "zoomFactor is now %4.1f" %zoomFactor
    elif key == 'Z':
         zoomFactor -= 0.5;
         if (zoomFactor <= 0.5) :
            zoomFactor = 0.5;
         print "zoomFactor is now %4.1f" %zoomFactor
    elif key == chr (27):
	raise SystemExit

import sys

def main():
   glutInit();
   glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB);
   glutInitWindowSize(250, 250);
   glutInitWindowPosition(100, 100);
   glutCreateWindow(sys.argv[0]);
   init();
   glutDisplayFunc(display);
   glutReshapeFunc(reshape);
   glutKeyboardFunc(keyboard);
   glutMotionFunc(motion);
   glutMainLoop();

main ()
