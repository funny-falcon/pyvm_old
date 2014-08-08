# The test of the threading module if __name__==__main__
#
#
#
#
#
#

import threading


def _test():

    class BoundedQueue(threading._Verbose):

        def __init__(self, limit):
            threading._Verbose.__init__(self)
            self.mon = threading.RLock()
            self.rc = threading.Condition(self.mon)
            self.wc = threading.Condition(self.mon)
            self.limit = limit
            self.queue = []

        def put(self, item):
            self.mon.acquire()
            while len(self.queue) >= self.limit:
                self._note("put(%s): queue full", item)
                self.wc.wait()
            self.queue.append(item)
            self._note("put(%s): appended, length now %d",
                       item, len(self.queue))
            self.rc.notify()
            self.mon.release()

        def get(self):
            self.mon.acquire()
            while not self.queue:
                self._note("get(): queue empty")
                self.rc.wait()
            item = self.queue.pop(0)
            self._note("get(): got %s, %d left", item, len(self.queue))
            self.wc.notify()
            self.mon.release()
            return item

    class ProducerThread(threading.Thread):

        def __init__(self, queue, quota):
            threading.Thread.__init__(self, name="Producer")
            self.queue = queue
            self.quota = quota

        def run(self):
            from random import random
            counter = 0
            while counter < self.quota:
                counter = counter + 1
                self.queue.put("%s.%d" % (self.getName(), counter))
                threading._sleep(random() * 0.00001)


    class ConsumerThread(threading.Thread):

        def __init__(self, queue, count):
            threading.Thread.__init__(self, name="Consumer")
            self.queue = queue
            self.count = count

        def run(self):
            while self.count > 0:
                item = self.queue.get()
                print item
                self.count = self.count - 1

    NP = 3
    NP = 25
    QL = 4
    QL = 11
    NI = 5
    NI = 29

    Q = BoundedQueue(QL)
    P = []
    for i in range(NP):
        t = ProducerThread(Q, NI)
        t.setName("Producer-%d" % (i+1))
        P.append(t)
    C = ConsumerThread(Q, NI*NP)
    for t in P:
        t.start()
        threading._sleep(0.000001)
    C.start()
    for t in P:
        t.join()
    C.join()

if __name__ == '__main__':
    _test()
