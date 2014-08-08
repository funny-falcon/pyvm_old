#! /usr/bin/env python

#DEJAVU
'''
{
'NAME':"Primes",
'DESC':"primes.py from Python/Demos/scripts",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"10 1000 SEM",
'BARGS':"10 383000"
}
'''

# Print prime numbers in a given range

def main():
    import sys
    min, max = 2, 0x7fffffff
    if sys.argv[1:]:
        min = int(eval(sys.argv[1]))
        if sys.argv[2:]:
            max = int(eval(sys.argv[2]))
    primes(min, max, 'SEM' in sys.argv)

def primes(min, max, doprint):
    if 2 >= min: print 2
    primes = [2]
    i = 3
    while i <= max:
        for p in primes:
            if i%p == 0 or p*p > i: break
        if i%p <> 0:
            primes.append(i)
            if i >= min and doprint: print i
        i = i+2

if __name__ == "__main__":
    main()
