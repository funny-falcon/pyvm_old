import sys

#DEJAVU
'''
{
'NAME':"Fannkuchen 2",
'DESC':"Bearophile's version",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"6",
'BARGS':"8"
}
'''

def fannkuch(n):
   perm = [0] * n
   perm1 = range(n)
   count = [0] * n
   m = n - 1
   r = n
   maxFlipsCount = 0

   while True:
     while r != 1:
       count[r-1] = r
       r -= 1

     # SS v.0.0.5 has a problem with this line:
     if not (perm1[0]==0 or perm1[m]==m):
       #perm = list(perm1)
       # to not produce memory garbage
       for i in xrange(n):
         perm[i] = perm1[i]

       i = perm[0]
       flips = 0
       while i:
         temp = perm[i]
         perm[i] = i
         i = temp
         j = 1
         k = i - 1
         while j < k:
           temp = perm[j]
           perm[j] = perm[k]
           perm[k] = temp
           j += 1
           k -= 1
         flips += 1

       if flips > maxFlipsCount:
         maxFlipsCount = flips

     while True:
       if r == n:
         return maxFlipsCount
       temp = perm1[0]
       i = 0
       while i < r:
         j = i + 1
         perm1[i] = perm1[j]
         i = j
       perm1[r] = temp

       count[r] -= 1
       if count[r] > 0:
         break
       r += 1


 #import psyco
 #psyco.bind(fannkuch)

if len(sys.argv) > 1:
   n = int(sys.argv[1])
else:
   n = 1
print "Pfannkuchen(%d) = %d" % (n, fannkuch(n))
