'''
Created on 21 Nov 2013

@author: albert

Module for mesh section - plane cut
'''
import numpy as np
from scipy.spatial import Delaunay
from functools import wraps


def all_parameters_as_numpy_arrays( fn ):
    """Converts all of a function's arguments to numpy arrays.

    Used as a decorator to reduce duplicate code.
    """
    # wraps allows us to pass the docstring back
    # or the decorator will hide the function from our doc generator
    @wraps( fn )
    def wrapper( *args, **kwargs ):
        np_args = [
            np.array( arg ) if arg is not None else arg
            for arg in args
            ]
        np_kwargs = dict(
            (
                key,
                np.array( value ) if value is not None else value
                )
            for (key, value) in kwargs
            )
        return fn( *np_args, **np_kwargs )
    return wrapper


@all_parameters_as_numpy_arrays
def isect_line_plane(p0, p1, p_co, p_no):
    """
    p0, p1: define the line
    p_co, p_no: define the plane:
        p_co is a point on the plane (plane coordinate).
        p_no is a normal vector defining the plane direction; does not need to be normalized.

    return a Vector or None (when the intersection can't be found).
    """
    epsilon=0.000001
    u = p1 - p0 #sub_v3v3(p1, p0)
    w = p0 - p_co #sub_v3v3(p0, p_co)
    dot = np.dot(p_no, u) #dot_v3v3(p_no, u)

    if abs(dot) > epsilon:
        # the factor of the point between p0 -> p1 (0 - 1)
        # if 'fac' is between (0 - 1) the point intersects with the segment.
        # otherwise:
        #  < 0.0: behind p0.
        #  > 1.0: infront of p1.
        fac = -1 * np.dot(p_no, w) / dot #-dot_v3v3(p_no, w) / dot
        u = u * fac #mul_v3_fl(u, fac)
        return p0 + u #add_v3v3(p0, u)
    else:
        # The segment is parallel to plane
        return None
    
    
def nad_a_pod(plane, point_a, point_b):
    '''
    Kdyz ma byt jeden bod nad a druhy pod carou 
    tak je odecteme od cary a vysledny soucin musi byt zaporny
    '''
    prvni = point_a[2] - plane[2]
    druhy = point_b[2] - plane[2]
    if prvni * druhy < 0:
        return True
    else:
        return False    
    
def cut_tetrahedra(height, points):
    '''
    Cut the tetrahedra defined by points by horizontal plane in height 
    '''
    import itertools
    combs = itertools.combinations((points[0], points[1], points[2], points[3]), 2)
    
    p_plane = (0.0, 0.0, height)
    n_plane = (0.0, 0.0, 1.0)
    
    return [isect_line_plane(segment[0], segment[1], p_plane, n_plane)[:2] for segment in combs if nad_a_pod(p_plane, *segment) ]
    
def triangles_from_cut(height, points):
    '''
    as the cut can be triangle, or quadrilateral we shall
    check the result and do Delaunay triangluation if neccessary
    '''
    cut = cut_tetrahedra(height, points)
    
    points_found = len(cut)
    
    if points_found == 3:
        # 3 points means triangle
        return cut
    elif points_found == 4:
        # 4 points need triangulation first
        tri = Delaunay(cut)
        triangles = [[cut[idx] for idx in simpl] for simpl in tri.simplices]
        return triangles
    elif points_found in [1, 2]:
        # 2 points => third lays directly in the plane
        # 1 point => second and third in the plane
        index_iterator = (i for i, sublist in enumerate(points) if height in sublist)
        while points_found < 3:
            hledany = next(index_iterator, -1)
            cut.append(np.asarray(points[hledany][:2]))
            points_found += 1
            
        return cut
    else:
        #it can be 1 or 3  points in the plane
        in_plane = [i for i, sublist in enumerate(points) if height in sublist]
        if len(in_plane) == 3:
            cut = [np.asarray(points[plp][:2]) for plp in in_plane]
            return cut
        else:
            #directly one point in the plane => nothing to draw    
            return None    
        

def test_4points_section():
    points = [ [1437.0, 5398.0, -46.0], [1267.0, 5320.0, 270.0], [1460.0, 5138.0, 27.0], [1522.0, 5331.0, 125.0]]                
    res = triangles_from_cut(100.0, points)
    assert list(res[1][2]) == [ 1358.4556962025317 ,  5361.9620253164558]

def test_3points_section(): 
    points = [ [7056.0, 3362.0, 478.0], [7056.0, 3362.0, 317.0], [6936.0, 3266.0, 481.0], [6854.0, 3373.0, 392.0] ]
    
    res = triangles_from_cut(350.0, points)
    assert list(res[2]) == [ 6967.12,  3366.84]
    
def test_bod_lezi_v_rezu():
    points = [ (1518.0, 3360.0, 314.0), (1186.0, 3440.0, 286.0), (1431.0, 3554.0, 165.0), (1360.0, 3711.0, 300.0)]
    res = triangles_from_cut(300.0, points)
    assert list(res[2]) == [ 1360.,  3711.]
    
def test_dva_body_lezi_v_rezu():
    points = [(1574.0, 9278.0, 300.0), (1687.0, 8871.0, 300.0), (1665.0, 9114.0, 379.0), (1411.0, 8971.0, 291.0)]
    res = triangles_from_cut(300.0, points)
    assert list(res[0]) == [1436.9772727272727,  8985.625]
    
def test_tri_body_lezi_v_rezu():
    points = [(1574.0, 9278.0, 300.0), (1687.0, 8871.0, 300.0), (1665.0, 9114.0, 300.0), (1411.0, 8971.0, 291.0)]
    res = triangles_from_cut(300.0, points)
    assert list(res[0]) == [ 1574.,  9278.]    
    
if __name__ == "__main__":
    test_tri_body_lezi_v_rezu()
    