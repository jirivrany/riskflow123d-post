#!/usr/bin/env python
'''
Searching for largest triangle created by 4 given points
'''


def vector(point_a, point_b):
    '''
    sestroji vektor ze dvou bodu
    @param {tuple} point_a / bod (x, y)
    @param {tuple} point_b / bod (x, y)
    @return {tuple} vector / vektor (vx, vy)
    '''
    return (point_b[0] - point_a[0], point_b[1] - point_a[1])


def triangle_size(vec_a, vec_b):
    '''
    vypocita obsah trojuhelnika
    @param {tuple} vec_a (vx,vy)
    @param {tuple} vec_b (vx,vy)
    @return {float} size
    '''
    return abs(vec_a[0] * vec_b[1] - vec_a[1] * vec_b[0]) / 2.0


def triangle_sizes_generator(point_a, point_b, point_c, point_d):
    '''
    vypocitat velikost vsech trojuhelniku
    @param {tuple} point_a, b, c, d - body (x, y)
    @return {dictionary} triangle sizes
    '''
    import itertools
    combs = itertools.combinations((point_a, point_b, point_c, point_d), 3)

    for triangle in combs:
        yield triangle, triangle_size(vector(triangle[1], triangle[0]), vector(triangle[1], triangle[2]))


def get_triangle(point_a, point_b, point_c, point_d):
    '''
    @param: celkem 4 body ve formatu (x, y)
    @return: 3 body ktere tvori nejvetsi trojuhelnik
    '''
    max_size = 0
    biggest_triangle = None
    triangle_sizes = triangle_sizes_generator(
        point_a, point_b, point_c, point_d)
    # Find the triangle wit the biggest size
    for triangle, size in triangle_sizes:
        if size > max_size:
            max_size = size
            biggest_triangle = triangle

    return biggest_triangle

if __name__ == '__main__':
    print(get_triangle((1, 1), (3, 1), (2, 2), (2, 3)))
    #compute_triangle_sizes((1, 1), (3, 1), (2, 2), (2, 3))
