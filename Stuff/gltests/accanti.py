#*  accanti.c

from array import array

from OpenGL import *

import jitter

#*  Initialize lighting and other values.
def myinit():
    mat_ambient = 1.0, 1.0, 1.0, 1.0
    mat_specular = 1.0, 1.0, 1.0, 1.0
    light_position = 0.0, 0.0, 10.0, 1.0
    lm_ambient = 0.2, 0.2, 0.2, 1.0

    glMaterialfv (GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv (GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf (GL_FRONT, GL_SHININESS, 50.0)
    glLightfv (GL_LIGHT0, GL_POSITION, light_position)
    glLightModelfv (GL_LIGHT_MODEL_AMBIENT, lm_ambient)

    glEnable (GL_LIGHTING)
    glEnable (GL_LIGHT0)
    glDepthFunc (GL_LESS)
    glEnable (GL_DEPTH_TEST)
    glShadeModel (GL_FLAT)

    glClearColor (0.0, 0.0, 0.0, 0.0)
    glClearAccum (0.0, 0.0, 0.0, 0.0)

def displayObjects():
    torus_diffuse = 0.7, 0.7, 0.0, 1.0
    cube_diffuse = 0.0, 0.7, 0.7, 1.0
    sphere_diffuse = 0.7, 0.0, 0.7, 1.0
    octa_diffuse = 0.7, 0.4, 0.4, 1.0

    glPushMatrix ()
    glRotatef (30.0, 1.0, 0.0, 0.0)

    glPushMatrix ()
    glTranslatef (-0.80, 0.35, 0.0)
    glRotatef (100.0, 1.0, 0.0, 0.0)
    glMaterialfv (GL_FRONT, GL_DIFFUSE, torus_diffuse)
    glutSolidTorus (0.275, 0.85, 16, 16)
    glPopMatrix ()

    glPushMatrix ()
    glTranslatef (-0.75, -0.50, 0.0)
    glRotatef (45.0, 0.0, 0.0, 1.0)
    glRotatef (45.0, 1.0, 0.0, 0.0)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, cube_diffuse)
    glutSolidCube (1.5)
    glPopMatrix ()

    glPushMatrix ()
    glTranslatef (0.75, 0.60, 0.0)
    glRotatef (30.0, 1.0, 0.0, 0.0)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, sphere_diffuse)
    glutSolidSphere (1.0, 16, 16)
    glPopMatrix ()

    glPushMatrix ()
    glTranslatef (0.70, -0.90, 0.25)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, octa_diffuse)
    glutSolidOctahedron ()
    glPopMatrix ()

    glPopMatrix ()

def display():
    viewport = array ('i', [0,0,0,0])

    glGetIntegerv (GL_VIEWPORT, viewport)

    glClear(GL_ACCUM_BUFFER_BIT)

    for j in jitter.j8:
	glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glPushMatrix ()
	#*	Note that 4.5 is the distance in world space between
	#*	left and right and bottom and top.
	#*	This formula converts fractional pixel movement to
	#*	world coordinates.
	glTranslatef (j[0]*4.5/viewport[2], j[1]*4.5/viewport[3], 0.0)
	displayObjects ()
	glPopMatrix ()
	glAccum (GL_ACCUM, 1.0/len (jitter.j8))
    glAccum (GL_RETURN, 1.0)
    glFlush ()

def myReshape(w, h):
    glViewport (0, 0, w, h)
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity ()
    if w <= h:
	glOrtho (-2.25, 2.25, -2.25*h/w, 2.25*h/w, -10.0, 10.0)
    else:
	glOrtho (-2.25*w/h, 2.25*w/h, -2.25, 2.25, -10.0, 10.0)
    glMatrixMode (GL_MODELVIEW)

def key(k, x, y):
    if k == chr (27):
	raise SystemExit
    glutPostRedisplay()

#*  Main Loop
#*  Open window with initial window size, title bar,
#*  RGBA display mode, and handle input events.
def main():
    glutInit ()
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB
			| GLUT_ACCUM | GLUT_DEPTH)
    glutInitWindowSize (250, 250)
    glutCreateWindow ('accanti')
    myinit()
    glutReshapeFunc (myReshape)
    glutDisplayFunc(display)
    glutKeyboardFunc(key)
    glutMainLoop()

main()
