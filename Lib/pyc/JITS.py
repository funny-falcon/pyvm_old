#
# static typed, JITted code
#
# This doesn't give any impressive speedup. But it is good
# to check the JITer in the bootstrap.
#

try:
	import DLL
	count_idnt = DLL.CachedLib ('pyc-jit', """
		int count_idnt (const char *s)
		{
			int cnt = 0;
			for (;;)
				switch (*s++) {
				case ' ': cnt += 1; break;
				case '\t': cnt = ((cnt + 8) / 8) * 8; break;
				default: return cnt;
				}
		}
""", ['-O3']).get (('i', "count_idnt", 's'))
	del DLL
except:
	def count_idnt (line):
		cnt = 0
		for i in line:
			if i == ' ': cnt += 1
			elif i == '\t': cnt = ((cnt + 8) / 8) * 8
			else: return cnt
