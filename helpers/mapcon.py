'''
Created on 20 Nov 2013

@author: albert
'''
import matplotlib.pyplot as plt
import numpy as np
import toptriangle

def dump_test(data):
    '''
    data dump for testing / can be deleted from production
    '''
    with open('output.txt', 'w') as f:
        for row in data:
            print >> f, row
            
def conc_at_time(elid, ctime, dict_concentrations):
    '''
    get the concentration on element in given time
    '''
    if dict_concentrations.has_key(str(elid)):
        conc = dict_concentrations[str(elid)][ctime]
        return conc
    
    return 0.0

def get_triangle_from_node_coords(elem, nodes):
    '''
    get the node x,y coordinates from node structure
    node has 4 points in 3D - we need 3 of it, composing largest triangle
    '''
    
    node_coords = [tuple(nodes[node_id][:2]) for node_id in elem[2]]
    
    return toptriangle.get_triangle(*node_coords)

def get_triangles(mesh, dict_concentrations):
    '''
    transform the mesh coordinates to the list 
    of tuples (concentration, triangle)
    only 3D elements are valid
    '''
    
            
    triangles = [ (conc_at_time(elid, "500.0", dict_concentrations), 
                   get_triangle_from_node_coords(elem, mesh.nodes)) 
                 for elid, elem in mesh.elements.iteritems() 
                 if elem[0] > 2]
    
    dump_test(triangles)
    return triangles

def draw_map(triangles):
    '''
    get the triangle tuple (concentration, triangle] prepared before
    and draw the map of triangles
    '''
    
    conc_list = []
    grid = []
    tri_list = []
    ctr = 0
    
    for conc, tria in triangles:
        conc_list.append(conc)
        grid.extend(tria)
        tri_list.append([ctr, ctr+1, ctr+2])
        ctr += 3
        
    xy = np.asarray(grid)
    
    x = xy[:,0]
    y = xy[:,1]
    
    triangles = np.asarray(tri_list)
    
    zfaces = np.asarray(conc_list)
    
    plt.figure()
    plt.gca().set_aspect('equal')
    plt.tripcolor(x, y, triangles, facecolors=zfaces, edgecolors='k')
    plt.colorbar()
    plt.title('Map of concentrations')
    plt.xlabel('mesh X coord')
    plt.ylabel('mesh Y coord')
    
    plt.savefig('mapa', format="svg")               
            
    

if __name__ == '__main__':
    pass