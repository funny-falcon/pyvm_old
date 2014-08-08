#*XXX* Doesn't look good. I goofed something?

#*  alpha3D.py
#*  This program demonstrates how to intermix opaque and
#*  alpha blended polygons in the same scene, by using 
#*  glDepthMask.  Press the 'a' key to animate moving the 
#*  transparent object through the opaque object.  Press 
#*  the 'r' key to reset the scene.

from OpenGL import *

MAXZ=8.0
MINZ=-8.0
ZINC=4.0

solidZ = MAXZ
transparentZ = MINZ

def init():
    mat_specular = 1.0, 1.0, 1.0, 0.15
    mat_shininess = 100.0,
    position = 0.5, 0.5, 1.0, 0.0

    glMaterialfv (GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialfv (GL_FRONT, GL_SHININESS, mat_shininess)
    glLightfv (GL_LIGHT0, GL_POSITION, position)

    glEnable (GL_LIGHTING)
    glEnable (GL_LIGHT0)
    glEnable (GL_DEPTH_TEST)

    global sphereList, cubeList
    sphereList = glGenLists (1)
    glNewList (sphereList, GL_COMPILE)
    glutSolidSphere (0.4, 16, 16)
    glEndList ()

    cubeList = glGenLists (1)
    glNewList (cubeList, GL_COMPILE)
    glutSolidCube (0.6)
    glEndList ()

def display():
    mat_solid = 0.75, 0.75, 0.0, 1.0
    mat_zero = 0.0, 0.0, 0.0, 1.0
    mat_transparent = 0.0, 0.8, 0.8, 0.6
    mat_emission = 0.0, 0.3, 0.3, 0.6

    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPushMatrix ()
    glTranslatef (-0.15, -0.15, solidZ)
    glMaterialfv (GL_FRONT, GL_EMISSION, mat_zero)
    glMaterialfv (GL_FRONT, GL_DIFFUSE, mat_solid)
    glCallList (sphereList)
    glPopMatrix ()

    glPushMatrix ()
    glTranslatef (0.15, 0.15, transparentZ)
    glRotatef (15.0, 1.0, 1.0, 0.0)
    glRotatef (30.0, 0.0, 1.0, 0.0)
    glMaterialfv (GL_FRONT, GL_EMISSION, mat_emission)
    glMaterialfv (GL_FRONT, GL_DIFFUSE, mat_transparent)
    glEnable (GL_BLEND)
    glDepthMask (GL_FALSE)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE)
    glCallList (cubeList)
    glDepthMask (GL_TRUE)
    glDisable (GL_BLEND)
    glPopMatrix ()

    glutSwapBuffers();

def reshape(w, h):
    glViewport (0, 0, w, h)
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity ()
    if w <= h:
        glOrtho (-1.5, 1.5, (-1.5*h)/w, (1.5*h)/w, -10.0, 10.0)
    else:
        glOrtho ((-1.5*w)/h, (1.5*w)/h, -1.5, 1.5, -10.0, 10.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity ()

t0 = -1.0

def animate():
    global t0, solidZ, transparentZ
    if solidZ <= MINZ or transparentZ >= MAXZ:
        glutIdleFunc (0)
        t0 = -1.0
    else:
       t = glutGet (GLUT_ELAPSED_TIME) / 1000.0
       if t0 < 0.0:
          t0 = t
       dt = t - t0
       t0 = t
       solidZ -= ZINC*dt
       transparentZ += ZINC*dt
       glutPostRedisplay ()

def keyboard(key, x, y):
    global t0, solidZ, transparentZ
    if key in 'aA':
        solidZ = MAXZ
        transparentZ = MINZ
        glutIdleFunc (animate)
    elif key in 'rR':
        solidZ = MAXZ
        transparentZ = MINZ
        glutPostRedisplay ()
    elif key == chr (27):
	raise SystemExit

def main():
    glutInit ()
    glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize (500, 500)
    glutCreateWindow (sys.argv[0])
    init ()
    glutReshapeFunc (reshape)
    glutKeyboardFunc (keyboard)
    glutDisplayFunc (display)
    glutMainLoop ()

main()
