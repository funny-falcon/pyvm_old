# takfp
import sys

#DEJAVU
'''
{
'NAME':"Takfp (?)",
'DESC':"Takfp from computer language shootout",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"6",
'BARGS':"8"
}
'''


# Boah! this is unacceptably slow man!

def takfp(x, y, z):
    if y >= x:
        return z
    return takfp(takfp(x - 1.0, y, z), takfp(y - 1.0, z, x), takfp(z - 1.0, x, y))

def main():
    try:
        n = float(sys.argv[1])
    except:
        print "Usage: %s <N>" % sys.argv[0]

    print "%.3f" % takfp(n * 3.0, n * 2.0, n * 1.0)

if __name__ == '__main__':
    main()
