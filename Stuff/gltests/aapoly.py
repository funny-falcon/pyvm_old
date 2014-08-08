#*  aapoly.c
#*  This program draws filled polygons with antialiased
#*  edges.  The special GL_SRC_ALPHA_SATURATE blending 
#*  function is used.
#*  Pressing the 't' key turns the antialiasing on and off.

from array import array

from OpenGL import *

polySmooth = GL_TRUE

def init():
   glCullFace (GL_BACK)
   glEnable (GL_CULL_FACE)
   glBlendFunc (GL_SRC_ALPHA_SATURATE, GL_ONE)
   glClearColor (0.0, 0.0, 0.0, 0.0)

NFACE=6
NVERT=8

def flatten2D (lst):
    return [x for y in lst for x in y]

def drawCube(x0, x1, y0, y1, z0, z1):
    v = [[0,0,0] for i in range (8)]
    c = [
      [0.0, 0.0, 0.0, 1.0], [1.0, 0.0, 0.0, 1.0],
      [0.0, 1.0, 0.0, 1.0], [1.0, 1.0, 0.0, 1.0],
      [0.0, 0.0, 1.0, 1.0], [1.0, 0.0, 1.0, 1.0],
      [0.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0]]

    indices = [
      [4, 5, 6, 7], [2, 3, 7, 6], [0, 4, 7, 3],
      [0, 1, 5, 4], [1, 5, 6, 2], [0, 3, 2, 1]]

    v[0][0] = v[3][0] = v[4][0] = v[7][0] = x0
    v[1][0] = v[2][0] = v[5][0] = v[6][0] = x1
    v[0][1] = v[1][1] = v[4][1] = v[5][1] = y0
    v[2][1] = v[3][1] = v[6][1] = v[7][1] = y1
    v[0][2] = v[1][2] = v[2][2] = v[3][2] = z0
    v[4][2] = v[5][2] = v[6][2] = v[7][2] = z1

    v = array ('f', flatten2D (v))
    c = array ('f', flatten2D (c))
    indices = array ('c', flatten2D (indices))

    glEnableClientState (GL_VERTEX_ARRAY)
    glEnableClientState (GL_COLOR_ARRAY)
    glVertexPointer (3, GL_FLOAT, 0, v)
    glColorPointer (4, GL_FLOAT, 0, c)
    glDrawElements (GL_QUADS, NFACE*4, GL_UNSIGNED_BYTE, indices)
    glDisableClientState (GL_VERTEX_ARRAY)
    glDisableClientState (GL_COLOR_ARRAY)

#*  Note:  polygons must be drawn from front to back
#*  for proper blending.
def display():
    if polySmooth:
        glClear (GL_COLOR_BUFFER_BIT)
        glEnable (GL_BLEND)
        glEnable (GL_POLYGON_SMOOTH)
        glDisable (GL_DEPTH_TEST)
    else:
        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable (GL_BLEND)
        glDisable (GL_POLYGON_SMOOTH)
        glEnable (GL_DEPTH_TEST)

    glPushMatrix ()
    glTranslatef (0.0, 0.0, -8.0)
    glRotatef (30.0, 1.0, 0.0, 0.0)
    glRotatef (60.0, 0.0, 1.0, 0.0)
    drawCube(-0.5, 0.5, -0.5, 0.5, -0.5, 0.5)
    glPopMatrix ()

    glFlush ();

def reshape(w, h):
    glViewport (0, 0, w, h)
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity ()
    gluPerspective (30.0, w/(h * 1.0), 1.0, 20.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity ()

def keyboard(key, x, y):
    global polySmooth
    if key in 'tT':
        polySmooth = not polySmooth
        glutPostRedisplay ()
    elif key == chr (27):
	raise SystemExit

#*  Main Loop
def main():
    glutInit ()
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB 
                        | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize (200, 200)
    glutCreateWindow ('aapoly')
    init ()
    glutReshapeFunc (reshape)
    glutKeyboardFunc (keyboard)
    glutDisplayFunc (display)
    glutMainLoop ()

main ()
