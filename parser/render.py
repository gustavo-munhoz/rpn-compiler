from graphviz import Digraph
from parser.ast_node import ASTNode
from semantics.annotated_ast import AnnotatedASTNode


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


def render_annotated_ast(root: AnnotatedASTNode) -> Digraph:
    """
    Cria uma representação visual de uma árvore de nós já anotados
    pelo analisador semântico, mostrando o label, tipo e sinal.
    """
    dot = Digraph()

    def add_nodes_edges(node: AnnotatedASTNode):
        label_parts = [
            node.label,
            f"type: {node.eval_type.name}",
            f"sign: {node.sign.name}"
        ]

        if node.needs_cast_to_float:
            label_parts.append("CAST TO FLOAT")

        formatted_label = "{ " + " | ".join(label_parts) + " }"

        dot.node(str(id(node)), label=formatted_label, shape="record")

        for child in node.children:
            add_nodes_edges(child)
            dot.edge(str(id(node)), str(id(child)))

    add_nodes_edges(root)
    return dot
