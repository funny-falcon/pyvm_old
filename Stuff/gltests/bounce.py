
#*
#* Bouncing ball demo.
#*
#* This program is in the public domain
#*
#* Brian Paul
#*
#* Conversion to GLUT by Mark J. Kilgard
#*/


import math
from OpenGL import *

def COS (X):
    return math.cos (X * 3.14159/180.0)
def SIN (X):
    return math.sin (X * 3.14159/180.0)

RED = 1
WHITE = 2
CYAN = 3

IndexMode = GL_FALSE
##GLuint Ball
##GLenum Mode
Zrot = 0.0
Zstep = 180.0
Xpos = 0.0
Ypos = 1.0
Xvel = 2.0
Yvel = 0.0
Xmin = -4.0
Xmax = 4.0
Ymin = -3.8
Ymax = 4.0
G = -9.8

def make_ball():
    da = 18.0
    db = 18.0
    radius = 1.0

    list = glGenLists(1)

    glNewList(list, GL_COMPILE)

    color = 0
    a = -90.0
    while a + da < 90.0:
	glBegin(GL_QUAD_STRIP)
	b = 0.0
	while b <= 360.0:
	    if color:
		glIndexi(RED)
		glColor3f(1, 0, 0)
	    else:
		glIndexi(WHITE)
		glColor3f(1, 1, 1)

	    x = radius * COS(b) * COS(a)
	    y = radius * SIN(b) * COS(a)
	    z = radius * SIN(a)
	    glVertex3f(x, y, z)

	    x = radius * COS(b) * COS(a + da)
	    y = radius * SIN(b) * COS(a + da)
	    z = radius * SIN(a + da)
	    glVertex3f(x, y, z)

	    color = 1 - color
	    b += db
	glEnd()
	a += da

    glEndList()
    return list

def reshape(width, height):
    aspect = float (width) /height
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-6.0 * aspect, 6.0 * aspect, -6.0, 6.0, -6.0, 6.0)
    glMatrixMode(GL_MODELVIEW)

def key (k, x, y):
    if k == chr (27):
	raise SystemExit

def draw():
    glClear(GL_COLOR_BUFFER_BIT)

    glIndexi(CYAN)
    glColor3f(0, 1, 1)
    glBegin(GL_LINES)
    for i in range (-5,6):
      glVertex2i(i, -5)
      glVertex2i(i, 5)
    for i in range (-5,6):
      glVertex2i(-5, i)
      glVertex2i(5, i)
    for i in range (-5,6):
      glVertex2i(i, -5)
      glVertex2f(i * 1.15, -5.9)
    glVertex2f(-5.3, -5.35)
    glVertex2f(5.3, -5.35)
    glVertex2f(-5.75, -5.9)
    glVertex2f(5.75, -5.9)
    glEnd()

    glPushMatrix()
    glTranslatef(Xpos, Ypos, 0.0)
    glScalef(2.0, 2.0, 2.0)
    glRotatef(8.0, 0.0, 0.0, 1.0)
    glRotatef(90.0, 1.0, 0.0, 0.0)
    glRotatef(Zrot, 0.0, 0.0, 1.0)

    glCallList(Ball)

    glPopMatrix()

    glFlush()
    glutSwapBuffers()

vel0 = -100.0
t0 = -1.0

def idle():
    global vel0, Zrot, Xpos, Xvel, Zstep 
    global t0, Ypos, Yvel
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    if (t0 < 0.):
       t0 = t
    dt = t - t0
    t0 = t

    Zrot += Zstep*dt

    Xpos += Xvel*dt
    if (Xpos >= Xmax):
      Xpos = Xmax
      Xvel = -Xvel
      Zstep = -Zstep
    if (Xpos <= Xmin):
      Xpos = Xmin
      Xvel = -Xvel
      Zstep = -Zstep
    Ypos += Yvel*dt
    Yvel += G*dt
    if (Ypos < Ymin):
      Ypos = Ymin
      if (vel0 == -100.0):
        vel0 = abs(Yvel)
      Yvel = vel0
    glutPostRedisplay()

def visible(vis):
    if (vis == GLUT_VISIBLE):
      glutIdleFunc(idle)
    else:
      glutIdleFunc(0)

def main():
    glutInit ()
    glutInitWindowPosition(0, 0)
    glutInitWindowSize(600, 450)
    global IndexMode, Ball


    IndexMode = sys.argv [1:] and sys.agv [1] == '-ci'
    if (IndexMode):
       glutInitDisplayMode(GLUT_INDEX | GLUT_DOUBLE)
    else:
       glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)

    glutCreateWindow("Bounce")
    Ball = make_ball()
    glCullFace(GL_BACK)
    glEnable(GL_CULL_FACE)
    glDisable(GL_DITHER)
    glShadeModel(GL_FLAT)

    glutDisplayFunc(draw)
    glutReshapeFunc(reshape)
    glutVisibilityFunc(visible)
    glutKeyboardFunc(key)

    if (IndexMode):
      glutSetColor(RED, 1.0, 0.0, 0.0)
      glutSetColor(WHITE, 1.0, 1.0, 1.0)
      glutSetColor(CYAN, 0.0, 1.0, 1.0)

    glutMainLoop()

main ()
