"""
    John Walker's Floating Point Benchmark, derived from...

    Marinchip Interactive Lens Design System

                                 John Walker   December 1980

    By John Walker
       http://www.fourmilab.ch/

    This  program may be used, distributed, and modified freely as
    long as the origin information is preserved.

    This is a complete optical design raytracing  algorithm,
    stripped of its user interface and recast into Python.
    It not only determines execution speed on an  extremely
    floating point (including trig  function) intensive
    real-world application, it  checks accuracy on an algorithm
    that is exquisitely  sensitive to errors. The performance of
    this program is typically far more sensitive to changes in 
    the efficiency of the trigonometric library routines than the
    average floating point program.
"""
#DEJAVU
'''
{
'NAME':"fbench",
'DESC':"John Walker's Floating Point Benchmark",
'GROUP':'real-bench',
'CMPOUT':1,
'ARGS':"1",
'BARGS':"13200"
}
'''

import sys, math, string

niter = int (sys.argv [1])

spectral_line = [ 0, 
                            7621.0,         # A
                            6869.955,       # B
                            6562.816,       # C
                            5895.944,       # D
                            5269.557,       # E
                            4861.344,       # F
                            4340.477,       # G'
                            3968.494        # H
                ]

refarr = [          # Reference results.  These happen to
                    # be derived from a run on Microsoft 
                    # Quick BASIC on the IBM PC/AT.

            "Marginal ray          47.09479120920   0.04178472683",
            "Paraxial ray          47.08372160249   0.04177864821",
            "Longitudinal spherical aberration:        -0.01106960671",
            "    (Maximum permissible):                 0.05306749907",
            "Offense against sine condition (coma):     0.00008954761",
            "    (Maximum permissible):                 0.00250000000",
            "Axial chromatic aberration:                0.00448229032",
            "    (Maximum permissible):                 0.05306749907"
         ]

#   The test case used in this program is the design for a 4 inch
#   achromatic telescope objective used as the example in Wyld's
#   classic work on ray tracing by hand, given in Amateur Telescope
#   Making, Volume 3.

testcase = [
               [ 27.05, 1.5137, 63.6, 0.52 ],
               [ -16.68, 1, 0, 0.138 ],
               [ -16.68, 1.6164, 36.7, 0.38 ],
               [ -78.1, 1, 0, 0 ]
           ]

def trace_line(line, ray_h):
    global object_distance, ray_height, from_index, \
           radius_of_curvature, to_index

    object_distance = 0
    ray_height = ray_h
    from_index = 1

    for i in range(current_surfaces):
       radius_of_curvature = s[i][0]
       to_index = s[i][1]
       if to_index > 1.0:
          to_index = to_index + ((spectral_line[4] -
             spectral_line[line]) /
             (spectral_line[3] - spectral_line[6])) * ((s[i][1] - 1) /
             s[i][2])
       transit_surface()
       from_index = to_index
       if i < current_surfaces:
          object_distance = object_distance - s[i][3]

def transit_surface():
    """
        Calculate passage through surface

        If  the variable PARAXIAL is true, the trace through the
        surface will be done using the paraxial  approximations.
        Otherwise,  the normal trigonometric trace will be done.

        This subroutine takes the following global inputs:

        radius_of_curvature     Radius of curvature of surface
                                being crossed.  If 0, surface is
                                plane.

        object_distance         Distance of object focus from
                                lens vertex.  If 0, incoming
                                rays are parallel and
                                the following must be specified:

        ray_height              Height of ray from axis.  Only
                                relevant if object_distance == 0

        axis_slope_angle        Angle incoming ray makes with axis
                                at intercept

        from_index              Refractive index of medium being left

        to_index                Refractive index of medium being
                                entered.

        The outputs are the following global variables:

        object_distance         Distance from vertex to object focus
                                after refraction.

        axis_slope_angle        Angle incoming ray makes with axis
                                at intercept after refraction.
    """

    global object_distance, axis_slope_angle, ray_height
    
    if paraxial:
       if radius_of_curvature != 0:
          if object_distance == 0:
             axis_slope_angle = 0
             iang_sin = ray_height / radius_of_curvature
          else:
             iang_sin = ((object_distance - radius_of_curvature) /
                radius_of_curvature) * axis_slope_angle

          rang_sin = (from_index / to_index) * iang_sin
          old_axis_slope_angle = axis_slope_angle
          axis_slope_angle = axis_slope_angle + iang_sin - rang_sin
          if object_distance != 0:
             ray_height = object_distance * old_axis_slope_angle
          object_distance = ray_height / axis_slope_angle
          return
       object_distance = object_distance * (to_index / from_index)
       axis_slope_angle = axis_slope_angle * (from_index / to_index)
       return

    if radius_of_curvature != 0:
       if object_distance == 0:
          axis_slope_angle = 0
          iang_sin = ray_height / radius_of_curvature
       else:
          iang_sin = ((object_distance - radius_of_curvature) /
            radius_of_curvature) * math.sin(axis_slope_angle)
       iang = math.asin(iang_sin)
       rang_sin = (from_index / to_index) * iang_sin
       old_axis_slope_angle = axis_slope_angle
       axis_slope_angle = axis_slope_angle + iang - math.asin(rang_sin)
       sagitta = math.sin((old_axis_slope_angle + iang) / 2)
       sagitta = 2 * radius_of_curvature * sagitta * sagitta
       object_distance = ((radius_of_curvature * math.sin(
          old_axis_slope_angle + iang)) *
          (1 / math.tan(axis_slope_angle))) + sagitta
       return

    rang = -math.asin((from_index / to_index) * sin(axis_slope_angle))
    object_distance = object_distance * ((to_index *
       cos(-rang)) / (from_index *
       cos(axis_slope_angle)))
    axis_slope_angle = -rang
        
        
#   Main program

# Load test case into working array

clear_aperture = 4
current_surfaces = 4
s = testcase

print """Ready to begin John Walker's floating point accuracy
and performance benchmark.  %d iterations will be made.

Measured run time in seconds should be divided by %g
to normalise for reporting results.  For archival results,
adjust iteration count so the benchmark runs about five minutes.""" % (niter,
niter / 1000.0)

axis_slope_angle = 0
od_sa = [ [0, 0], [0, 0]]

def fbench ():
  global paraxial
  for itercount in range(niter):
    for paraxial in range(2):
    
          # Do main trace in D light

          trace_line(4, clear_aperture / 2)
          od_sa[paraxial][0] = object_distance
          od_sa[paraxial][1] = axis_slope_angle
          
    paraxial = 0
    
    # Trace marginal ray in C

    trace_line(3, clear_aperture / 2)
    od_cline = object_distance

    # Trace marginal ray in F

    trace_line(6, clear_aperture / 2)
    od_fline = object_distance

    aberr_lspher = od_sa[1][0] - od_sa[0][0]
    aberr_osc = (1.0 - (od_sa[1][0] * od_sa[1][1]) /
       (math.sin(od_sa[0][1]) * od_sa[0][0]))
    aberr_lchrom = od_fline - od_cline
    max_lspher = math.sin(od_sa[0][1])

     # D light

    max_lspher = 0.0000926 / (max_lspher * max_lspher)
    max_osc = 0.0025
    max_lchrom = max_lspher


  return [
            "%s   %21.11f  %14.11f" % ("Marginal ray", od_sa[0][0], od_sa[0][1]),
            "%s   %21.11f  %14.11f" % ("Paraxial ray", od_sa[1][0], od_sa[1][1]),
            "Longitudinal spherical aberration:      %16.11f" % (aberr_lspher),
            "    (Maximum permissible):              %16.11f" % (max_lspher),
            "Offense against sine condition (coma):  %16.11f" % (aberr_osc),
            "    (Maximum permissible):              %16.11f" % (max_osc),
            "Axial chromatic aberration:             %16.11f" % (aberr_lchrom),
            "    (Maximum permissible):              %16.11f" % (max_lchrom)
         ]
         
outarr = fbench ()

errors = 0
for i in range(len(refarr)):
    if refarr[i] != outarr[i]:
        errors += 1
        print "Error in results on line %d..." % (i + 1)
        print "Expected: ", refarr[i]
        print "Received: ", outarr[i]
	print refarr[i], outarr[i], refarr[i]==outarr [i]
        e = ""
        for j in range(len(refarr[i])):
            if refarr[i][j] == outarr[i][j]:
                e += " "
            else:
                e += "^"
        print "(Errors)  ", e

if errors > 0:
    print ("\n%d error%s in results.  This is VERY SERIOUS." %
        (errors, "s" * (errors > 1)))
else:
    print "\nNo errors in results."
