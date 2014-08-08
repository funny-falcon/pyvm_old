from random import randint

import sys

# ======================================================================
#   Pollard Rho factorization from Kirby Urner,
#   http://www.mathforum.org/epigone/math-teach/blerlplerdghi
# ======================================================================

def gen(n,c=1):
    """
    Generate sequence x_i = (x_{i-1}^2 + c) mod n
    Where n is the target composite we want to factor.
    """
    x = 1
    while True:
        x = (x**2 + c) % n
        yield x

def rho(n, maxt=500, maxc=10):
    """
    Pollard's Rho method for factoring n.
    Returns a list of factors (not necessarily prime) of n.
    Tests each polynomial x^2+c (c in range(1,maxc))
    by following the sequence gen(n,c) for maxt steps.
    If the sequence is cyclic modulo a factor of n
    with a smaller cycle length than its cycle modulo n,
    we can identify a factor of n as the gcd of n
    with the difference of two sequence values separated
    by the smaller cycle length in the sequence.
    """
    if millrab(n):  # don't bother with probable primes
        return [n]
    for c in range(1,maxc):
        seqslow = gen(n,c) 
        seqfast = gen(n,c)
        for trial in range(maxt):
            xb = seqslow.next()     # slow generator goes one step
            seqfast.next()
            xk = seqfast.next()     # while fast generator goes two
            diff = abs(xk-xb)
            if not diff:
                continue
            d = gcd(diff,n)         # have a factor?
            if n>d>1:                
#		if n/d != n//d:
#			print "FUCK"
                return [d,n/d]
    return [n]    # failure to factor
    
def gcd(a,b):
    """
    Euclid's algorithm for integer greatest common divisors.
    """
    while b:
        a,b = b,a%b
    return a

def millrab(n, max=30):
    """
    Miller-Rabin primality test as per the following source:
    http://www.wikipedia.org/wiki/Miller-Rabin_primality_test
    Returns probability p is prime: either p = 0 or ~1,
    """
    if not n%2: return 0
    k = 0
    z = n - 1

    # compute m,k such that (2**k)*m = n-1
    while not z % 2:
      k += 1
      z /= 2
    m = z

    # try tests with max random integers between 2,n-1
    ok = 1
    trials = 0
    p = 1
    while trials < max and ok:
        a = randint(2,n-1)
        trials += 1
        test = pow(a,m,n)
        if (not test == 1) and not (test == n-1):
            # if 1st test fails, fall through
            ok = 0
            for r in range(1,k):
                test = pow(a, (2**r)*m, n)
                if test == (n-1):
                    ok = 1 # 2nd test ok
                    break
        else: ok = 1  # 1st test ok
        if ok==1:  p *= 0.25
            
    if ok:  return 1 - p
    else:   return 0


# ======================================================================
#   Integer factorization and divisor enumeration
# ======================================================================

# Find all factors and divisors
# Fix rho (doesn't handle powers of two correctly) and speed up small primes

def factors(n):
    """
    Return a list of the factors of n.
    Uses trial division for small primes before switching to Pollard's Rho method.
    """
    f = []
    for p in [2,3,5,7,11,13,17,19]:
        while n % p == 0:
            f.append(p)
            n /= p
    if n == 1:
        return f
    if millrab(n):
	f.append (n)
	return f
        #return f + [n]
    maxt,maxc = 100,5
    rho_results = [n]
    while len(rho_results) == 1:
        rho_results = rho(n,maxt,maxc)
        maxt *= 2
        maxc *= 2
    for factor in rho_results:
        f += factors(factor)
    return f

def itemCounts(S):
    """
    Return dictionary mapping items in S to how many times they occur in S.
    """
    items = {}
    for x in S:
        items[x] = items.get(x,0) + 1
    return items

def subcounts(D):
    """
    Generates sequence of all maps dominated by a map D from items to numbers.
    That is, each output is a dictionary that maps the same items to numbers,
    and all numbers in each output dictionary are at most equal to the
    corresponding number in the input dictionary.
    """
    if not D:
        yield {}
        return
    x = min(D)
    n = range(D[x]+1)
    del D[x]
    for dd in subcounts(D):
        for i in n:
            dd[x] = i
            yield dd

def prod(seq):
    x = 1
    for i in seq:
	x *= i
    return x

def divisors(n):
    """
    Generate sequence of all divisors of n.
    """
    for dd in subcounts(itemCounts(factors(n))):
#        yield reduce(operator.mul,[x**i for x,i in dd.items()],1)
        yield prod([x**i for x,i in dd.items()])
        #yield prod(x**i for x,i in dd.items())


#DEJAVU
'''
{
'NAME':"Divisors",
'DESC':"D. Eppstein's divisors",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"SEM",
'BARGS':"7470"
}
'''

import sys
SEMANTIC = 'SEM' in sys.argv

def main ():
 if SEMANTIC:
  for j in xrange (4, 1001):
   print "Divisors of:", j
   for i in divisors(j):
     print i,
   print
 else:
  for j in xrange (4, int (sys.argv [1])):
   for i in divisors(j):
     pass

main ()

