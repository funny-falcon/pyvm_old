#*  accpersp.c
#*  Use the accumulation buffer to do full-scene antialiasing
#*  on a scene with perspective projection, using the special
#*  routines accFrustum() and accPerspective().

from OpenGL import *
import jitter
from array import array
import math

PI_=3.14159265358979323846

#* accFrustum()
#* The first 6 arguments are identical to the glFrustum() call.
#*  
#* pixdx and pixdy are anti-alias jitter in pixels. 
#* Set both equal to 0.0 for no anti-alias jitter.
#* eyedx and eyedy are depth-of field jitter in pixels. 
#* Set both equal to 0.0 for no depth of field effects.
#*
#* focus is distance from eye to plane in focus. 
#* focus must be greater than, but not equal to 0.0.
#*
#* Note that accFrustum() calls glTranslatef().  You will 
#* probably want to insure that your ModelView matrix has been 
#* initialized to identity before calling accFrustum().

def accFrustum(left, right, bottom, top, nnear, ffar, pixdx, pixdy, eyedx, eyedy, focus):
    viewport = array ('i', [0,0,0,0])

    glGetIntegerv (GL_VIEWPORT, viewport)
	
    xwsize = right - left;
    ywsize = top - bottom;
	
    dx = -(pixdx*xwsize/float (viewport[2]) + eyedx*nnear/focus);
    dy = -(pixdy*ywsize/float (viewport[3]) + eyedy*nnear/focus);
	
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity ()
    glFrustum (left + dx, right + dx, bottom + dy, top + dy, nnear, ffar)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity ()
    glTranslatef (-eyedx, -eyedy, 0.0)

#* accPerspective()
#* 
#* The first 4 arguments are identical to the gluPerspective() call.
#* pixdx and pixdy are anti-alias jitter in pixels. 
#* Set both equal to 0.0 for no anti-alias jitter.
#* eyedx and eyedy are depth-of field jitter in pixels. 
#* Set both equal to 0.0 for no depth of field effects.
#*
#* focus is distance from eye to plane in focus. 
#* focus must be greater than, but not equal to 0.0.
#*
#* Note that accPerspective() calls accFrustum().
def accPerspective(fovy, aspect, nnear, ffar, pixdx, pixdy, eyedx, eyedy, focus):
    fov2 = ((fovy*PI_) / 180.0) / 2.0;

    top = nnear / (math.cos(fov2) / math.sin(fov2))
    bottom = -top

    right = top * aspect
    left = -right

    accFrustum (left, right, bottom, top, nnear, ffar,
               pixdx, pixdy, eyedx, eyedy, focus)

#*  Initialize lighting and other values.
def init():
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
    glTranslatef (0.0, 0.0, -5.0)
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
    glMaterialfv (GL_FRONT, GL_DIFFUSE, cube_diffuse)
    glutSolidCube (1.5)
    glPopMatrix ()

    glPushMatrix ()
    glTranslatef (0.75, 0.60, 0.0)
    glRotatef (30.0, 1.0, 0.0, 0.0)
    glMaterialfv (GL_FRONT, GL_DIFFUSE, sphere_diffuse)
    glutSolidSphere (1.0, 16, 16)
    glPopMatrix ()

    glPushMatrix ()
    glTranslatef (0.70, -0.90, 0.25)
    glMaterialfv (GL_FRONT, GL_DIFFUSE, octa_diffuse)
    glutSolidOctahedron ()
    glPopMatrix ()

    glPopMatrix ()

def display():
    viewport = array ('i', [0,0,0,0])

    glGetIntegerv (GL_VIEWPORT, viewport)

    glClear (GL_ACCUM_BUFFER_BIT)
    for j in jitter.j8:
        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        accPerspective (50.0, viewport[2] / (1.0 * viewport[3]), 1.0, 15.0, j[0], j[1], 0.0, 0.0, 1.0)
        displayObjects ()
        glAccum (GL_ACCUM, 1.0/len (jitter.j8))
    glAccum (GL_RETURN, 1.0)
    glFlush()

def reshape(w, h):
    glViewport(0, 0, w, h)

def keyboard(key, x, y):
    if key == chr (27):
	raise SystemExit

#*  Main Loop
#*  Be certain you request an accumulation buffer.
def main():
    glutInit ()
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB | GLUT_ACCUM | GLUT_DEPTH)
    glutInitWindowSize (250, 250)
    glutInitWindowPosition (100, 100)
    glutCreateWindow ('accpersp')
    init ()
    glutReshapeFunc (reshape)
    glutDisplayFunc (display)
    glutKeyboardFunc (keyboard)
    glutMainLoop ()
main ()
