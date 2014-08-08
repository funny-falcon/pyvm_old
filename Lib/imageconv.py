#
# Converting image formats
#
#
# The goal of this file is to try as many alternatives as
# possible.  Right now we're using the external program
# 'convert' from ImageMagick.
#
# If this fails we could try to use:
#	SDL_image, gimp, libjpeg, or in the end
#	our own CJIT code...
#

#
# at the moment this file is messy
# we should have a polymorphic hierarchy of classes for
# different ways to convert images that fall back to alternatives....
#

import os, tempfile

class imageConvertError:
    pass

def convert (infile, outfile):
    # this should be considered 'Blocking' for multi core systems
    if os.system ('convert %s %s' %(infile, outfile)):
	raise imageConvertError
    print os.access (outfile, os.R_OK)

def convert_temp_bmp (infile):
    outfile = tempfile.mktemp ('.bmp')
    if os.system ('convert -compress None %s %s' %(infile, outfile)):
	raise imageConvertError
    return outfile

xxx='xxx.tmp'
HAVE_CONVERT = False
if os.system ('convert --version > %s' %xxx) == 0:
    if 'ImageMagick' in file (xxx).read ():
	HAVE_CONVERT = True
    os.unlink (xxx)

if not HAVE_CONVERT:
    def convert (infile, outfile):
        print "C~~~ONVERT:", infile, outfile
	raise imageConvertError
