import bpy
import os
from bpy.types import ShaderNode, ShaderNodeGroup, NodeTree, bpy_prop_collection, bpy_struct
from . import node_group as node_group_lib

if "_LOADED" in locals():
    import importlib

    for mod in (node_group_lib,):
        importlib.reload(mod)
_LOADED = True


def _next_name(collection: bpy_prop_collection, prefix: str, separator: str = " ", start: int = 1) -> str:
    if prefix not in collection:
        return prefix
    counter = start
    while (name := f"{prefix}{separator}{counter}") in collection:
        counter += 1
    return name


def import_ng(node_group_name: str) -> NodeTree:
    internal_file = os.path.join(os.path.dirname(__file__), "..", "plaidiator_internal.blend")

    if node_group_name in bpy.data.node_groups:
        return bpy.data.node_groups[node_group_name]

    print(f"Import {node_group_name} from {internal_file}...")

    with bpy.data.libraries.load(internal_file) as (src, dest):
        if node_group_name in src.node_groups:
            print(f"Import {node_group_name} found")
            dest.node_groups = [node_group_name]
        else:
            print("Import failed. Not found.")

    return bpy.data.node_groups[node_group_name]


def place_plaidiator_ng(context: bpy_struct) -> ShaderNodeGroup:
    node_tree = context.space_data.node_tree
    if not node_tree:
        return []
    node_group = import_ng("PlaidiatorNG")
    ng_node = node_tree.nodes.new(type="ShaderNodeGroup")
    ng_node.plaidiator_id.type = "PARENT_GROUP"

    ng_copy = node_group.copy()
    ng_copy.name = _next_name(bpy.data.node_groups, "Untitled Plaid", " ", 2)
    ng_node.node_tree = ng_copy

    return ng_node


