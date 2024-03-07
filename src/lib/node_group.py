import bpy
from bpy.types import NodeTree, NodeSocket, Node

"""
Compatibility functions for working with Node Group socket changes between Blender 3.x and 4.x
"""

def compat_create_socket(node_group: NodeTree, type: str, name: str, in_out: str = "INPUT") -> NodeSocket:
    if hasattr(node_group, "inputs"):
        return node_group.outputs.new(type, name) if in_out == "OUTPUT" else node_group.inputs.new(type, name)
    return node_group.interface.new_socket(name=name, in_out=in_out, socket_type=type)


def compat_get_socket(ng_node: Node, index: int | str, in_out: str="INPUT") -> NodeSocket:
    if hasattr(ng_node, "inputs"):
        return ng_node.inputs[index] if in_out == "INPUT" else ng_node.outputs[index]
    if isinstance(index, str):
        items = {i.name: i for i in ng_node.interface.items_tree if i.in_out == in_out}
        return items[index]
    return compat_get_sockets(ng_node, in_out)[index]


def compat_get_sockets(node_group, in_out="INPUT") -> list[NodeSocket]:
    if hasattr(node_group, "inputs"):
        return [s for s in (node_group.inputs if in_out == "INPUT" else node_group.outputs)]
    return [s for s in node_group.interface.items_tree if s.in_out == in_out]

