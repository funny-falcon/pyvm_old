
#DEJAVU
'''
{
'NAME':"linalg_brute",
'DESC':"Bill Mill's linalg_brute from c.l.p",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"",
'BARGS':""
}
'''

#--------------------linalg_brute.py------------------------------
def mkrow(ns, limit):
    return [(a,b,c) for a in ns for b in ns for c in ns if a + b + c == limit]

def main():
 ns = range(1,10)
 row1 = mkrow(ns, 19)
 row2 = mkrow(ns, 18)
 row3 = mkrow(ns, 23)
 row4 = mkrow(ns, 18)
 for b,c,d in row1:
    for e,f,h in row2:
        for i,j,k in row3:
            for m,o,p in row4:
                if 3 + e + i + m == 24 and 7 + b + f + j == 18 \
                and 8 + c + k + o == 31 and 8 + d + h + p == 31 \
                and 3 + f + k + p == 24 and m + j + 8 + d == 24:
                    print 3,b,c,d
                    print e,f,8,h
                    print i,j,k,8
                    print m,7,o,p
                    print '-------------'
main()
#--------------end linalg_brute.py-----------------------------
