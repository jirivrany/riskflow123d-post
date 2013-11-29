'''
Created on 20 Nov 2013

@author: albert
'''
import matplotlib.pyplot as plt
import numpy as np
import toptriangle
import section

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
    try:
        conc = dict_concentrations[str(elid)][ctime]
    except KeyError:
        return 0.0
    else:    
        return conc
    
    
def get_triangle_from_node_coords(elem, nodes):
    '''
    get the node x,y coordinates from node structure
    node has 4 points in 3D - we need 3 of it, composing largest triangle
    '''
    
    node_coords = [tuple(nodes[node_id][:2]) for node_id in elem[2]]
    
    return toptriangle.get_triangle(*node_coords)

def get_triangle_from_cut(elem, nodes, height):
    '''
    get the triangle from tetrahedra cut
    '''
    node_coords = [tuple(nodes[node_id]) for node_id in elem[2]]
    return section.triangles_from_cut(height, node_coords)
    

def get_triangles_section(mesh_elements, nodes, dict_concentrations, height, sim_time):
    '''
    transform the mesh coordinates to the list 
    of tuples (concentration, triangle)
    only 3D elements are valid
    '''
    triangles = []
    conc = []
    for elid, elem in mesh_elements.iteritems():
        if elem[0] > 2:
            sub_result = get_triangle_from_cut(elem, nodes, height)
            if sub_result:
                if len(sub_result) == 2:
                    #pak jde o pole se dvema trojuhleniky, 
                    #udelame extend a pridame 2x stejnou koncentraci
                    triangles.extend(sub_result)
                    conc.append(conc_at_time(elid, sim_time, dict_concentrations))
                    conc.append(conc_at_time(elid, sim_time, dict_concentrations))
                if len(sub_result) == 3:
                    #pak jde o jeden trojuhelnik a muzem udelat normalni append
                    triangles.append(sub_result)    
                    conc.append(conc_at_time(elid, sim_time, dict_concentrations))
    
    return zip(conc, triangles)        

def get_triangles_surface(mesh_elements, nodes, dict_concentrations, sim_time):
    '''
    transform the mesh coordinates to the list 
    of tuples (concentration, triangle)
    only 3D elements are valid
    '''
            
    triangles = [ (conc_at_time(elid, sim_time, dict_concentrations), 
                   get_triangle_from_node_coords(elem, nodes)) 
                 for elid, elem in mesh_elements.iteritems() 
                 if elem[0] > 2]
    
    return triangles


def prepare_triangulation(triangles):
    '''
    get the triangles and prepare pyplot data from them
    '''
    conc_list = []
    grid = []
    tri_list = []
    ctr = 0
    
    for conc, tria in triangles:
        if tria:
            conc_list.append(conc)
            grid.extend(tria)
            tri_list.append([ctr, ctr+1, ctr+2])
            ctr += 3
        
    xy = np.asarray(grid)
    
    x_np = xy[:,0]
    y_np = xy[:,1]
    
    triangles = np.asarray(tri_list)
    
    zfaces = np.asarray(conc_list)
    
    return {'x_np': x_np,
            'y_np' : y_np,
            'triangles': triangles,
            'zfaces': zfaces} 

def draw_map(triangulation, options):
    '''
    get the triangle tuple (concentration, triangle] prepared before
    and draw the map of triangles
    options :
    "map_format": "svg",
    "map_file": "../../mapa"
    '''
    
    plt.figure()
    plt.gca().set_aspect('equal')
    plt.tripcolor(triangulation['x_np'],
                  triangulation['y_np'],
                  triangulation['triangles'],
                  facecolors=triangulation['zfaces'],
                  edgecolors='k')
    plt.colorbar()
    plt.title('Map of concentrations')
    plt.xlabel('mesh X coord')
    plt.ylabel('mesh Y coord')
    
    plt.savefig(options["map_file"], format=options["map_format"])               
            
    

if __name__ == '__main__':
    pass