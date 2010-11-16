import ast
import pydot
import pprint

tree = list()

class TraceParse( ast.NodeVisitor ):
    def visit(self, node, tree = None):
        self.generic_visit(node, tree)

    def generic_visit(self, node, tree):
        ''' 
        print node
        for field, value in ast.iter_fields( node  ):
            print 'field =', repr(field), ': value =', repr(value)
        print ''
        '''

        if node not in tree:
            tree.append(node)
        for child in ast.iter_child_nodes(node):
            tree.append(list())
            self.generic_visit(child, tree[-1])

'''
tree = {}

class TraceParse( ast.NodeVisitor ):
    def visit(self, node, tree = None):
        self.generic_visit(node, tree)

    def generic_visit(self, node, tree):
        if node not in tree:
            tree[node] = dict()
        for child in ast.iter_child_nodes(node):
            tree[node][child] = dict()
            self.generic_visit(child, tree[node])
'''

def generate_edges( tree, edges = None ): 
    if edges == None:
        edges = []
    for subtree in tree[1:]:
        from_node = str(tree[0])
        to_node = str(subtree[0])

        from_node_str = from_node[6:].split()[0] + ' ' + from_node.split()[-1][:-1]
        to_node_str  = to_node[6:].split()[0] + ' ' + to_node.split()[-1][:-1]

        edges.append( (from_node_str, to_node_str) )
        if subtree[1:]:
            generate_edges(subtree, edges)
    return edges

with open('recolumn.py') as f:
    source = f.read()

source_ast = ast.parse(source)
TraceParse().visit( source_ast, tree)

'''
pp = pprint.PrettyPrinter(depth = 4)
pp.pprint(tree)
'''

edges = generate_edges(tree)
dot_file = pydot.graph_from_edges(edges, directed = True)

dot_file.write("big_tree.dot",  format = 'raw')

