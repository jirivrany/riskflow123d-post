'''
Created on 20 Nov 2013

@author: albert
'''
import matplotlib.pyplot as plt
import numpy as np
import toptriangle
import section
from ruzne import value_set

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

def get_surface_triangle_from_node_coords(elem, nodes, filter_out):
    '''
    get the node x,y coordinates from node structure
    node has 4 points in 3D - we need 3 of it, composing largest triangle
    '''
    index = [0, 1, 2, 3]
    index.remove(filter_out)
    node_coords = [tuple(nodes[node_id][:2]) for node_id in elem[2]]
    return [node_coords[i] for i in index]
    

def get_surface_triangles_from_bcd(bcd_name, slist):
    """
    Read a Flow .bcd file 
    search for surface elements
    returns list of surface elements with points on plane side
    """
    elements = {}
    readmode = 0
    typ = 0
    where  = 0
    height_limit = 10
    
    with open(bcd_name, "r") as mshfile:
        for line in mshfile:
            line = line.strip()
            if line.startswith('$'):
                if line == '$BoundaryConditions':
                    readmode = 1
                else:
                    readmode = 0
            elif readmode:
                columns = line.split()
                if len(columns) > 5:
                    #first column is type of condition
                    element_id = int(columns[4])
                    if element_id in slist:
                        elements[element_id] = int(columns[5])
                         
    return elements                     

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

def get_triangles_surface(mesh_elements, nodes, dict_concentrations, sim_time, bcd_file):
    '''
    transform the mesh coordinates to the list 
    of tuples (concentration, triangle)
    only 3D elements are valid
    '''
    elements = get_surface_triangles_from_bcd(bcd_file, mesh_elements)
            
    triangles = [ (conc_at_time(elid, sim_time, dict_concentrations), 
                   get_surface_triangle_from_node_coords(elem, nodes, elements[elid])) 
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
    lab_x = options['xlabel'] if value_set(options, 'xlabel') else 'mesh X coord'
    lab_y = options['ylabel'] if value_set(options, 'ylabel') else 'mesh Y coord'
    lab_tit = options['title'] if value_set(options, 'title') else 'Map of concentrations'
    
    
    plt.figure()
    plt.gca().set_aspect('equal')
    plt.tripcolor(triangulation['x_np'],
                  triangulation['y_np'],
                  triangulation['triangles'],
                  facecolors=triangulation['zfaces'],
                  edgecolors='k')
    plt.colorbar()
    plt.title(lab_tit)
    plt.xlabel(lab_x)
    plt.ylabel(lab_y)
    
    plt.savefig(options["map_file"], format=options["map_format"])               
            
def test_surface_nodes():
    bcd_name = '/home/albert/data/risk_flow/riskflow/test_postproc/master/mm.bcd'
    surface = '/home/albert/data/risk_flow/riskflow/test_postproc/master/surface.txt'
    with open(surface) as surf:
        slist = [int(x) for x in surf.readlines()]
        
    elems = get_surface_triangles_from_bcd(bcd_name, slist)
    print elems    

if __name__ == '__main__':
    test_surface_nodes()