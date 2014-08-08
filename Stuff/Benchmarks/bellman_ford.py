"""
Magnus Lie Hetland.

The Bellman-Ford algorithm

Graph API:

    iter(graph) gives all nodes
    iter(graph[u]) gives neighbours of u
    graph[u][v] gives weight of edge (u, v)
    
"""

# Oi really have *no* idea what bellman-ford is ! -- sxanth

import sys

#DEJAVU
'''
{
'NAME':"Bellman-Ford",
'DESC':"Bellman Ford from Magnus Lie Hetland",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"4 SEM",
'BARGS':"523"
}
'''


def initialize(graph, source):
    d = {}
    p = {}
    for node in graph:
        d[node] = float('Inf')
        p[node] = None
    d[source] = 0
    return d, p

def relax(u, v, graph, d, p):
    if d[v] > d[u] + graph[u][v]:
        d[v]  = d[u] + graph[u][v]
        p[v] = u

def bellman_ford(graph, source):
    d, p = initialize(graph, source)
    for i in range(len(graph)-1):
        for u in graph:
            for v in graph[u]:
                relax(u, v, graph, d, p)
    for u in graph:
        for v in graph[u]:
            assert d[v] <= d[u] + graph[u][v]
    return d, p

SEMANTIC = 'SEM' in sys.argv
N = int (sys.argv [1])

def test():
    from random import seed, randint
    seed (1337)
    X = range (N)
    graph = {}
    for i in X:
	graph [i] = {}
	for j in xrange (randint (2, 9)):
 	    graph [i][randint (1, N-1)] = randint (1,13)

    d, p = bellman_ford(graph, 0)
    if SEMANTIC:
	for i in d: print i, d[i]
	for i in p: print i, p[i]
    
if __name__ == '__main__': test()
