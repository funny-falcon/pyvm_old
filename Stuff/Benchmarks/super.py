# http://spoj.sphere.pl/problems/SUPPER/

#DEJAVU
'''
{
'NAME':"Super Numbers",
'DESC':"super efficient python solution for the 'SUPERNUMBER' challenge from the shpere programming competition, written by Tim Peters",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"SEM",
'BARGS':"39000"
}
'''

def crack(xs):
    from bisect import bisect_right as find
    smallest = []
    all = []
    n = 0
    for index, x in enumerate(xs):
        i = find(smallest, x)
        if i == n:
            smallest.append(x)
            all.append([(index, x)])
            n += 1
        else:
            all[i].append((index, x))
            if x < smallest[i]:
                smallest[i] = x
    return all

def findall(all):
    constraints = all[-1]
    allints = [pair[1] for pair in constraints]
    for i in xrange(len(all) - 2, -1, -1):
        survivors = []
        for pair in all[i]:
            index, value = pair
            for index_limit, value_limit in constraints:
                if index < index_limit and value < value_limit:
                    survivors.append(pair)
                    allints.append(value)
                    break
        constraints = survivors
    return sorted(allints)

def main():
    import sys
    for n in sys.stdin:
        n = int(n)
        perm = map(int, sys.stdin.next().split())
        assert n == len(perm)
        supers = findall(crack(perm))
        perm = None # just to free memory
        print len(supers)
        print " ".join(map(str, supers))

if __name__ == "__main__":
##    main()
    #
    #
    import random, sys
    SEM = 'SEM' in sys.argv
    if SEM:
	N = 200
    else:
	N = int (sys.argv [1])
    random.seed (102030)
    for i in range (10):
	seq = range (N)
	random.shuffle (seq)
	if SEM:
	    print ''.join (map (str, findall (crack (seq))))
	else:
	    findall (crack (seq))
