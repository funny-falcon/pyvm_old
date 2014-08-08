#*  pickdepth.c
#*  Picking is demonstrated in this program.  In
#*  rendering mode, three overlapping rectangles are
#*  drawn.  When the left mouse button is pressed,
#*  selection mode is entered with the picking matrix.
#*  Rectangles which are drawn under the cursor position
#*  are "picked."  Pay special attention to the depth
#*  value range, which is returned.

from OpenGL import *

def myinit():
    glClearColor(0.0, 0.0, 0.0, 0.0);
    glDepthFunc(GL_LESS);
    glEnable(GL_DEPTH_TEST);
    glShadeModel(GL_FLAT);
    glDepthRange(0.0, 1.0);  #/* The default z mapping */

#*  The three rectangles are drawn.  In selection mode,
#*  each rectangle is given the same name.  Note that
#*  each rectangle is drawn with a different z value.
def drawRects(mode):
    if (mode == GL_SELECT):
        glLoadName(1);
    glBegin(GL_QUADS);
    glColor3f(1.0, 1.0, 0.0);
    glVertex3i(2, 0, 0);
    glVertex3i(2, 6, 0);
    glVertex3i(6, 6, 0);
    glVertex3i(6, 0, 0);
    glEnd();
    if (mode == GL_SELECT):
        glLoadName(2);
    glBegin(GL_QUADS);
    glColor3f(0.0, 1.0, 1.0);
    glVertex3i(3, 2, -1);
    glVertex3i(3, 8, -1);
    glVertex3i(8, 8, -1);
    glVertex3i(8, 2, -1);
    glEnd();
    if (mode == GL_SELECT):
        glLoadName(3);
    glBegin(GL_QUADS);
    glColor3f(1.0, 0.0, 1.0);
    glVertex3i(0, 2, -2);
    glVertex3i(0, 7, -2);
    glVertex3i(5, 7, -2);
    glVertex3i(5, 2, -2);
    glEnd();

#*  processHits() prints out the contents of the
#*  selection array.
def processHits(hits, buffer):

    print "hits = %d"% hits
    i = 0
    while i < hits:
	names = buffer [i]
        print " number of names for hit = %d" %names
	i += 1
        print "  z1 is %g;" % float(buffer [i]/0xffffffff),
	i += 1
        print " z2 is %g\n" % float(buffer [i] /0xffffffff),
	i += 1
        print "   the name is ",
	for j in range (names):
	    print "%d"%buffer [i],
	    i += 1
	print

#*  pickRects() sets up selection mode, name stack,
#*  and projection matrix for picking.  Then the objects
#*  are drawn.
BUFSIZE=512

def pickRects(button, state, x, y):
    selectBuf = array ('i', BUFSIZE * [0])
    viewport = array ('i', 4 * [0]);

    if (button != GLUT_LEFT_BUTTON or state != GLUT_DOWN):
        return;

    glGetIntegerv(GL_VIEWPORT, viewport);

    glSelectBuffer(BUFSIZE, selectBuf);
    glRenderMode(GL_SELECT);

    glInitNames();
    glPushName(-1);

    glMatrixMode(GL_PROJECTION);
    glPushMatrix();
    glLoadIdentity();
    #*  create 5x5 pixel picking region near cursor location */
    gluPickMatrix(x, (viewport[3] - y), 5.0, 5.0, viewport);
    glOrtho(0.0, 8.0, 0.0, 8.0, -0.5, 2.5);
    drawRects(GL_SELECT);
    glPopMatrix();
    glFlush();

    hits = glRenderMode(GL_RENDER);
    processHits(hits, selectBuf);

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    drawRects(GL_RENDER);
    glutSwapBuffers();

def myReshape(w, h):
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0.0, 8.0, 0.0, 8.0, -0.5, 2.5);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

def key (k, x, y):
    if k == chr (27):
	raise SystemExit

#*  Main Loop
#*  Open window with initial window size, title bar,
#*  RGBA display mode, depth buffer, and handle input events.
def main():
    import sys
    glutInitWindowSize(200, 200);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInit()
    glutCreateWindow(sys.argv[0]);
    myinit();
    glutMouseFunc(pickRects);
    glutReshapeFunc(myReshape);
    glutDisplayFunc(display);
    glutKeyboardFunc(key);
    glutMainLoop();
main ()
