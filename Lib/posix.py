#
# Our main problem is 'structseq' which is a tuple whos
# values can be accessed as attributes too.  This can be
# easilly done in py, and that's what we'll do.
#
#

from _posix import *
import _posix


class structseq:
    def __init__ (self, seq):
	self.seq = seq
    def __getattr__ (self, attr):
	return self.seq [self.attr_names.index (attr)]
    def __str__ (self):
	return str (self.seq)
    def __getitem__ (self, i):
	return self.seq [i]
    def __iter__(self):
	return iter (self.seq)
    def __len__(self):
	return len (self.seq)

#
# Do not call this 'stat_result'. module os tries to pickle stat_result
# and copy_reg complains that pickle can't pickle classes and it all fails
# Grrr.
#
class __stat_result (structseq):
    attr_names = ['st_mode', 'st_ino', 'st_dev', 'st_nlink',
		  'st_uid', 'st_gid', 'st_size',
		  'st_atime', 'st_mtime', 'st_ctime', 'st_blksize',
		  'st_blocks', 'st_rdev']

def stat (path):
    return __stat_result (_posix._stat (path))
def lstat (path):
    return __stat_result (_posix._lstat (path))

#
# fdopen
#
def fdopen (fd, mode):
    return file (fd, mode)
