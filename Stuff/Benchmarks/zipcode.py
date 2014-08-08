#!/usr/bin/python
#
# Author:    Kevin T. Ryan, kevryan0701@yahoo.com
# Date:      03/29/2005
#
# dist computes the distance between two points on the earth, as identified by their
# longitude and latitude identifications in MILES.  If you would like to change the 
# distance (to, perhaps, calculate the distance in km) you should change the last line
# of the function.  For example, for km, use 6399 instead of 3956 (the approximate
# distance of the earth).
#
# Obtained distance formula from "http://www.census.gov/cgi-bin/geo/gisfaq?Q5.1" and 
# more information is available at "http://en.wikipedia.org/wiki/Great_circle_distance".
#
# Zip code data obtained from "http://www.census.gov/tiger/tms/gazetteer/"

import sys

#DEJAVU
'''
{
'NAME':"ZIPcode",
'DESC':"zipcode distance ASPN recipe",
'GROUP':'real-bench',
'CMPOUT':1,
'DATA':'DATA/zips.txt',
'ARGS':"SEM",
'BARGS':""
}
'''

import math

def dist(long_1, lat_1, long_2, lat_2):
    '''Returns the distance between two points on the earth.
    
    Inputs are:
        Longitude (in radians) of the first location,
        Latitude (in radians) of the first location,
        Longitude (in radians) of the second location, and
        Latitude (in radians) of the second location.
    To convert to radians (from degrees), use pythons math.radian 
    function.  Returns the distance in miles.'''

    dlong = long_2 - long_1
    dlat = lat_2 - lat_1
    a = (math.sin(dlat / 2))**2 + math.cos(lat_1) * math.cos(lat_2) * (math.sin(dlong / 2))**2
    c = 2 * math.asin(min(1, math.sqrt(a)))
    dist = 3956 * c
    return dist

def close_zips(zip_to_lookup, radius, zips):
    '''For any given zip code (assuming it's valid), returns any zip codes within a 'radius' mile radius.'''
    zip_long, zip_lat = [zip[4:6] for zip in zips if zip[1] == zip_to_lookup][0]
    close_zips = [zip[1] for zip in zips if dist(zip[4], zip[5], zip_long, zip_lat) < radius]
    return close_zips

def read_zips(filename):
    f = file(filename, 'r')
    zips = []

    for line in f:
        zips.append(line[:-2].replace('"', '').split(","))
        zips[-1][4] = math.radians(float(zips[-1][4]))
        zips[-1][5] = math.radians(float(zips[-1][5]))
    f.close()
    return zips

if __name__ == "__main__":
    # A test run.  See above for the reference for the file 'zips.txt'.  This
    # part of the script opens the file, creates a list of all zip codes and then
    # randomly calculates the distance between randomly selected zip codes.

    import sys
    SEM = 'SEM' in sys.argv
    import random
    random.seed (2171073)

    zips = read_zips ('DATA/zips.txt')
    num_zips = len(zips)
    if SEM:
      for i in range(17):
        record1 = int(random.random() * num_zips)
        record2 = int(random.random() * num_zips)
	print "The distance between %s,%s %s and %s,%s %s is %.5f" % (
            zips[record1][3].strip(), zips[record1][2].strip(), zips[record1][1].strip(),
            zips[record2][3].strip(), zips[record2][2].strip(), zips[record2][1].strip(),
            dist(zips[record1][4], zips[record1][5], zips[record2][4], zips[record2][5]))
      print close_zips ("35005" ,100, zips)
    else:
	close_zips (str (close_zips ("35005", 1000, zips)[-1]), 100, zips)
