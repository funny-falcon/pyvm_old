#*  colormat.c
#*  After initialization, the program will be in
#*  ColorMaterial mode.  Interaction:  pressing the 
#*  mouse buttons will change the diffuse reflection values.

from OpenGL import *

diffuseMaterial = [ 0.5, 0.5, 0.5, 1.0 ]

#*  Initialize material property, light source, lighting model,
#*  and depth buffer.
def init():
    mat_specular = 1.0, 1.0, 1.0, 1.0
    light_position = 1.0, 1.0, 1.0, 0.0

    glClearColor (0.0, 0.0, 0.0, 0.0)
    glShadeModel (GL_SMOOTH)
    glEnable (GL_DEPTH_TEST)
    glMaterialfv (GL_FRONT, GL_DIFFUSE, diffuseMaterial)
    glMaterialfv (GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf (GL_FRONT, GL_SHININESS, 25.0)
    glLightfv (GL_LIGHT0, GL_POSITION, light_position)
    glEnable (GL_LIGHTING)
    glEnable (GL_LIGHT0)

    glColorMaterial (GL_FRONT, GL_DIFFUSE)
    glEnable (GL_COLOR_MATERIAL)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glutSolidSphere(1.0, 20, 16)
    glFlush ()

def reshape (w, h):
    glViewport (0, 0, w, h)
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity ()
    if w <= h:
      glOrtho (-1.5, 1.5, -(1.5*h)/w,
         (1.5*h)/w, -10.0, 10.0)
    else:
      glOrtho ((-1.5*w)/h,
         (1.5*w)/h, -1.5, 1.5, -10.0, 10.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity ()

def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
         if state == GLUT_DOWN:
            diffuseMaterial[0] += 0.1
            if diffuseMaterial[0] > 1.0:
                diffuseMaterial[0] = 0.0
            glColor4fv (diffuseMaterial)
            glutPostRedisplay ()
    elif button==GLUT_MIDDLE_BUTTON:
         if state == GLUT_DOWN:
            diffuseMaterial[1] += 0.1
            if diffuseMaterial[1] > 1.0:
               diffuseMaterial[1] = 0.0
            glColor4fv (diffuseMaterial)
            glutPostRedisplay ()
    elif button ==  GLUT_RIGHT_BUTTON:
         if state == GLUT_DOWN:
            diffuseMaterial[2] += 0.1
            if diffuseMaterial[2] > 1.0:
               diffuseMaterial[2] = 0.0
            glColor4fv (diffuseMaterial)
            glutPostRedisplay ()

def keyboard(key, x, y):
    if key == chr (27):
	raise SystemExit

import sys

def main():
   glutInit()
   glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
   glutInitWindowSize (500, 500)
   glutInitWindowPosition (100, 100)
   glutCreateWindow (sys.argv[0])
   init ()
   glutDisplayFunc (display)
   glutReshapeFunc (reshape)
   glutMouseFunc (mouse)
   glutKeyboardFunc (keyboard)
   glutMainLoop ()

main ()
