#!/usr/bin/env python
"""Based on Mesh Class by Carl Osterwisch <osterwischc@asme.org>, January 2005
    Mesh -- A class for storing nodes and elements.

"""

class Mesh(object):
    """This is a class for storing nodes and elements.

    Members:
    nodes -- A dict of the form { nodenode_id: [ xcoord, ycoord, zcoord] }
    elements -- A dict of the form { elemnode_id: (type, [tags], [nodenode_ids]) }
    mtr_index == A dict with index of materials - { element tag nr. 1 : [elmnode_id]}
    elm_index == A dict with index of elements - { nodenode_id : [elmnodeids] }
    
    Methods:
    read(file) -- Parse a Gmsh version 1.0 or 2.0 mesh file
    write(file) -- Output a Gmsh version 2.0 mesh file
    """

    def __init__(self):
        self.read_finished = False
        self.read_tick = 0
        self.nodes = {}
        self.elements = {}
        self.mtr_index = {}
        self.elm_index = {}

    def read(self, fname):
        """Read a Gmsh .msh file.
        
        Reads Gmsh format 1.0 and 2.0 mesh files, storing the nodes and
        elements in the appropriate dicts.
        """

        readmode = 0
        mshfile = open(fname,"r")
        for line in mshfile:
            line = line.strip()
            if line.startswith('$'):
                if line == '$NOD' or line == '$Nodes':
                    readmode = 1
                elif line == '$ELM':
                    readmode = 2
                elif line == '$Elements':
                    readmode = 3
                else:
                    readmode = 0
            elif readmode:
                columns = line.split()
                if readmode == 1 and len(columns) == 4:
                    # Version 1.0 or 2.0 Nodes
                    try:
                        self.nodes[int(columns[0])] = map(float, columns[1:])
                    except ValueError:
                        print 'Node format error: '+line
                        readmode = 0
                elif readmode > 1 and len(columns) > 5:
                    # Version 1.0 or 2.0 Elements 
                    try:
                        columns = map(int, columns)
                    except ValueError:
                        print 'Element format error: '+line
                        readmode = 0
                    else:
                        (node_id, type) = columns[0:2]
                        if readmode == 2:
                            # Version 1.0 Elements
                            tags = columns[2:4]
                            nodes = columns[5:]
                        else:
                            # Version 2.0 Elements
                            ntags = columns[2]
                            tags = columns[3:3+ntags]
                            nodes = columns[3+ntags:]
                        self.elements[node_id] = (type, tags, nodes)
                        
                        #create elm index
                        for no in nodes:
                            if self.elm_index.has_key(no):
                                self.elm_index[no].append(node_id)
                            else:
                                self.elm_index[no] = [node_id,]
                        
                        #create mtr index
                        if self.mtr_index.has_key(tags[0]):
                            self.mtr_index[tags[0]].append(node_id)
                        else:
                            self.mtr_index[tags[0]] = [node_id,]    
       

    def write(self, fname):
        
        fp = open(fname,"w")
        """Dump the mesh out to a Gmsh 2.0 msh fp."""
        print >>fp, '$MeshFormat\n2.0 0 8\n$EndMeshFormat'
        print >>fp, '$Nodes\n%d'%len(self.nodes)
        for (node_id, coord) in self.nodes.items():
            print >>fp, node_id, ' '.join(map(str, coord))
        print >>fp, '$EndNodes'
        print >>fp, '$Elements\n%d'%len(self.elements)
        for (node_id, elem) in self.elements.items():
            (type, tags, nodes) = elem
            print >>fp, node_id, type, len(tags),
            print >>fp, ' '.join(map(str, tags)),
            print >>fp, ' '.join(map(str, nodes))
        print >>fp, '$EndElements'

if __name__ == '__main__':
    fileName = '../../data/test1.msh '
    p = Mesh()
    p.read(fileName)
    
    print '  %d Nodes' %len(p.nodes)
    print '  %d Elements'%len(p.elements)
    print p.elements[2]
    print p.elements[2][1][1]
    
    outName = '../../data/out.msh'
    p.write(outName)

