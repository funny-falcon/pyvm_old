#*  mipmap.c
#*  This program demonstrates using mipmaps for texture maps.
#*  To overtly show the effect of mipmaps, each mipmap reduction
#*  level has a solidly colored, contrasting texture image.
#*  Thus, the quadrilateral which is drawn is drawn with several
#*  different colors.

from array import array
from OpenGL import *

def multidim (X, Y, Z):
    return [[Z*[0] for i in range (Y)] for j in range (X)]

mipmapImage32 = multidim (32, 32, 3)
mipmapImage16 = multidim (16, 16, 3)
mipmapImage8 = multidim (8, 8, 3)
mipmapImage4 = multidim (4, 4, 3)
mipmapImage2 = multidim (2, 2, 3)
mipmapImage1 = multidim (1, 1, 3)

# makeImages

for i in range (32):
    for j in range (32):
	mipmapImage32[i][j][0] = 255;
	mipmapImage32[i][j][1] = 255;
	mipmapImage32[i][j][2] = 0;

for i in range (16):
    for j in range (16):
	mipmapImage16[i][j][0] = 255;
	mipmapImage16[i][j][1] = 0;
	mipmapImage16[i][j][2] = 255;

for i in range (8):
    for j in range (8):
	mipmapImage8[i][j][0] = 255;
	mipmapImage8[i][j][1] = 0;
	mipmapImage8[i][j][2] = 0;

for i in range (4):
    for j in range (4):
	mipmapImage4[i][j][0] = 0;
	mipmapImage4[i][j][1] = 255;
	mipmapImage4[i][j][2] = 0;

for i in range (2):
    for j in range (2):
	mipmapImage2[i][j][0] = 0;
	mipmapImage2[i][j][1] = 0;
	mipmapImage2[i][j][2] = 255;

mipmapImage1[0][0][0] = 255;
mipmapImage1[0][0][1] = 255;
mipmapImage1[0][0][2] = 255;

def mipmap2array (m):
    return array ('c', [x for y in m for z in y for x in z])

mipmapImage32 = mipmap2array (mipmapImage32)
mipmapImage16 = mipmap2array (mipmapImage16)
mipmapImage8 = mipmap2array (mipmapImage8)
mipmapImage4 = mipmap2array (mipmapImage4)
mipmapImage2 = mipmap2array (mipmapImage2)
mipmapImage1 = mipmap2array (mipmapImage1)

def myinit():
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LESS);
    glShadeModel(GL_FLAT);

    glTranslatef(0.0, 0.0, -3.6);
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
    glTexImage2D(GL_TEXTURE_2D, 0, 3, 32, 32, 0,
		 GL_RGB, GL_UNSIGNED_BYTE, mipmapImage32);
    glTexImage2D(GL_TEXTURE_2D, 1, 3, 16, 16, 0,
		 GL_RGB, GL_UNSIGNED_BYTE, mipmapImage16);
    glTexImage2D(GL_TEXTURE_2D, 2, 3, 8, 8, 0,
		 GL_RGB, GL_UNSIGNED_BYTE, mipmapImage8);
    glTexImage2D(GL_TEXTURE_2D, 3, 3, 4, 4, 0,
		 GL_RGB, GL_UNSIGNED_BYTE, mipmapImage4);
    glTexImage2D(GL_TEXTURE_2D, 4, 3, 2, 2, 0,
		 GL_RGB, GL_UNSIGNED_BYTE, mipmapImage2);
    glTexImage2D(GL_TEXTURE_2D, 5, 3, 1, 1, 0,
		 GL_RGB, GL_UNSIGNED_BYTE, mipmapImage1);
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
	GL_NEAREST_MIPMAP_NEAREST);
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL);
    glEnable(GL_TEXTURE_2D);

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glBegin(GL_QUADS);
    glTexCoord2f(0.0, 0.0); glVertex3f(-2.0, -1.0, 0.0);
    glTexCoord2f(0.0, 8.0); glVertex3f(-2.0, 1.0, 0.0);
    glTexCoord2f(8.0, 8.0); glVertex3f(2000.0, 1.0, -6000.0);
    glTexCoord2f(8.0, 0.0); glVertex3f(2000.0, -1.0, -6000.0);
    glEnd();
    glFlush();

def myReshape(w, h):
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(60.0, (1.0*w)/h, 1.0, 30000.0);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

def key(k, x, y):
    if k == chr (27):
	raise SystemExit

def main():
    import sys
    glutInit();
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize (500, 500);
    glutCreateWindow (sys.argv[0]);
    myinit();
    glutReshapeFunc (myReshape);
    glutDisplayFunc(display);
    glutKeyboardFunc(key);
    glutMainLoop();

main ()
