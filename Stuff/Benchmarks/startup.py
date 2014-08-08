import random

#DEJAVU
'''
{
'NAME':"Startup",
'DESC':"startup time. Also verifies compatible random number generators",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"",
'BARGS':""
}
'''

random.seed (2233)
print random.randint (0, 1000)
