import bpy
from typing import Set
from bpy.types import Operator, bpy_struct
from ..lib import pkginfo
from ..lib import plaidiator

if "_LOADED" in locals():
    import importlib

    for mod in (pkginfo, plaidiator):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()


class plaidiator_OT_AddPlaid(Operator):
    """Add a Plaidiator Stripe Set in the current node tree."""
    bl_idname = "plaidiator.add_plaid"
    bl_label = "Plaidiator Plaid"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context) -> bool:
        return bool(context.material)

    @classmethod
    def can_show(cls, context: bpy_struct) -> bool:
        return bool(context.space_data.tree_type == "ShaderNodeTree")

    def execute(self, context: bpy_struct) -> Set[str]:
        # Clear selection first so the transform operator doesn't drag anything else around
        for node in bpy.context.space_data.node_tree.nodes:
            node.select = False

        ng = plaidiator.place_plaidiator_ng(context)
        cursor = context.space_data.cursor_location

        ng.location[0] += cursor[0]
        ng.location[1] += cursor[1]

        # Put the nodes in "Move" mode like a normal Add does
        bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}


REGISTER_CLASSES = [plaidiator_OT_AddPlaid]
