#*  alpha.c
#*  This program draws several overlapping filled polygons
#*  to demonstrate the effect order has on alpha blending results.
#*  Use the 't' key to toggle the order of drawing polygons.


from OpenGL import *

leftFirst = GL_TRUE;

#*  Initialize alpha blending function.
def init():
    glEnable (GL_BLEND);
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glShadeModel (GL_FLAT);
    glClearColor (0.0, 0.0, 0.0, 0.0);

def drawLeftTriangle():
    #* draw yellow triangle on LHS of screen */
    glBegin (GL_TRIANGLES);
    glColor4f(1.0, 1.0, 0.0, 0.75);
    glVertex3f(0.1, 0.9, 0.0); 
    glVertex3f(0.1, 0.1, 0.0); 
    glVertex3f(0.7, 0.5, 0.0); 
    glEnd();

def drawRightTriangle():
    #* draw cyan triangle on RHS of screen */

    glBegin (GL_TRIANGLES);
    glColor4f(0.0, 1.0, 1.0, 0.75);
    glVertex3f(0.9, 0.9, 0.0); 
    glVertex3f(0.3, 0.5, 0.0); 
    glVertex3f(0.9, 0.1, 0.0); 
    glEnd();

def display():
    glClear(GL_COLOR_BUFFER_BIT);

    if leftFirst:
        drawLeftTriangle();
        drawRightTriangle();
    else:
        drawRightTriangle();
        drawLeftTriangle();

    glFlush();

def reshape(w, h):
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    if w <= h: 
        gluOrtho2D (0.0, 1.0, 0.0, (1.0*h)/w);
    else:
        gluOrtho2D (0.0, (1.0*w)/h, 0.0, 1.0);

def keyboard(key, x, y):
    global leftFirst
    if key == 't':
        leftFirst = not leftFirst;
        glutPostRedisplay();	
    if key == chr (27):
	raise SystemExit

#*  Main Loop
#*  Open window with initial window size, title bar, 
#*  RGBA display mode, and handle input events.
def main():
    glutInit ()
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB);
    glutInitWindowSize (200, 200);
    glutCreateWindow (sys.argv[0]);
    init();
    glutReshapeFunc (reshape);
    glutKeyboardFunc (keyboard);
    glutDisplayFunc (display);
    glutMainLoop();

main ()
