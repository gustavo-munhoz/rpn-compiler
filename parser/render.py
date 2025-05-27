from graphviz import Digraph
from parser.ast_node import ASTNode


def render_ast(root: ASTNode, fmt="png") -> Digraph:
    g = Digraph(format=fmt)
    counter = {"id": 0}

    def add(node: ASTNode):
        counter["id"] += 1
        my_id = f"n{counter['id']}"
        g.node(my_id, node.label)
        for child in node.children:
            child_id = add(child)
            g.edge(my_id, child_id)
        return my_id

    add(root)
    return g
