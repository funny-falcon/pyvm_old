#
# Some of the itertools are worth doing in bytecode while others
# are better done in lwc/pyvm
#

import _itertools

def chain(*iterables):
    for it in iterables:
        for element in it:
            yield element

def count(n=0):
    return xrange (n, 2147483647)

def cycle(iterable):
    saved = []
    SV = saved.append
    for element in iterable:
        yield element
        SV (element)
    while 1:
        for element in saved:
            yield element

def takewhile(predicate, iterable):
    for x in iterable:
        if predicate(x):
            yield x
        else:
	    return

def ifilter(predicate, iterable):

    # for the case predicate==None, we must implement as hybrid

    if predicate is None:
        predicate = bool
    for x in iterable:
        if predicate(x):
            yield x

def ifilterfalse(predicate, iterable):
    if predicate is None:
        predicate = bool
    for x in iterable:
        if not predicate(x):
            yield x

imap = _itertools.imap
repeat = _itertools.repeat
dropwhile = _itertools.dropwhile
izip = _itertools.izip
islice = _itertools.islice
tee = _itertools.tee

#############################################################

"""
class groupby(object):
        def __init__(self, iterable, key=None):
            if key is None:
                key = lambda x: x
            self.keyfunc = key
            self.it = iter(iterable)
            self.tgtkey = self.currkey = self.currvalue = xrange(0)
        def __iter__(self):
            return self
        def next(self):
            while self.currkey == self.tgtkey:
                self.currvalue = self.it.next() # Exit on StopIteration
                self.currkey = self.keyfunc(self.currvalue)
            self.tgtkey = self.currkey
            return (self.currkey, self._grouper(self.tgtkey))
        def _grouper(self, tgtkey):
            while self.currkey == tgtkey:
                yield self.currvalue
                self.currvalue = self.it.next() # Exit on StopIteration
                self.currkey = self.keyfunc(self.currvalue)

'''
def imap(function, *iterables):
         iterables = map(iter, iterables)
         while True:
             args = [i.next() for i in iterables]
             if function is None:
                 yield tuple(args)
             else:
                 yield function(*args)
'''

def starmap(function, iterable):
         iterable = iter(iterable)
         while True:
             yield function(*iterable.next())

def tee(iterable):
         def gen(next, data={}, cnt=[0]):
             for i in count():
                 if i == cnt[0]:
                     item = data[i] = next()
                     cnt[0] += 1
                 else:
                     item = data.pop(i)
                 yield item
         it = iter(iterable)
         return (gen(it.next), gen(it.next))

"""
if __name__ == '__main__':
    import dis
    dis.dis (imap)
