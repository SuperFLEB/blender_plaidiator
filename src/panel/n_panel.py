import bpy
from enum import Enum
from bpy.types import Panel, UIList, UILayout, Node, bpy_struct
from bpy.utils import register_class, unregister_class
from ..operator import stripe as stripe_op
from ..lib import pkginfo, stripe as stripe_lib, node_group as node_group_lib
from ..props import plaidiator as plaidiator_props

if "_LOADED" in locals():
    import importlib

    for mod in (pkginfo, stripe_lib, node_group_lib, stripe_op, plaidiator_props):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()
last_seen_node = None


class Components(Enum):
    H = "h"
    V = "v"


class NODE_UL_stripe_list(UIList):
    def draw_item(self, context: bpy_struct, layout: UILayout, _1, item: plaidiator_props.Stripe, _2, _3, _4, _5):
        stripe = item
        layout = layout.column()
        layout.row().prop(data=stripe, property="rgba", text="Color")
        measures_layout = layout.row()
        measures_layout.prop(data=stripe, property="center", text="Center")
        measures_layout.prop(data=stripe, property="width", text="Width")


class NODE_PT_plaidiator_detail(Panel):
    bl_idname = 'NODE_PT_plaidiator_detail'
    bl_category = 'Plaidiator'
    bl_label = 'Plaidiator'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context: bpy_struct):
        return context.area.ui_type == "ShaderNodeTree"

    def draw_vector_warning(self, context: bpy_struct, layout: UILayout, node: Node) -> None:
        try:
            vector_socket = node_group_lib.compat_get_socket(node, "Vector", "INPUT")
        except KeyError:
            return
        for link in node.id_data.links:
            if link.to_socket == vector_socket:
                return
        box = layout.box()
        box.label(text="Vector socket not attached.", icon="ERROR")

    def draw_component(self, context: bpy_struct, layout: UILayout, node: Node, component: Components) -> None:
        p_globals = context.window_manager.plaidiator_globals
        hv = component.value
        title = {
            "h": "Horizontal Stripes",
            "v": "Vertical Stripes"
        }.get(hv, "Unknown Component")

        box = layout.box()
        box.label(text=title)
        box.prop(data=node.plaidiator_component, property="background_rgba", text="Background")

        list_row = box.row()
        list_column = list_row.column()
        list_column.template_list("NODE_UL_stripe_list", f"StripesList_{hv}", node.plaidiator_component, "stripes",
                                  p_globals, f"{hv}_index")
        ops_column = list_row.column()

        ops_column.context_pointer_set(name="target_node", data=node)
        ops_column.context_pointer_set(name="target_component", data=node.plaidiator_component)

        add_op = ops_column.operator(stripe_op.PLAIDIATOR_OT_InsertStripe.bl_idname, icon='ADD', text="")
        remove_op = ops_column.operator(stripe_op.PLAIDIATOR_OT_DeleteStripe.bl_idname, icon='REMOVE', text="")

        ops_column.separator()

        up_op = ops_column.operator(stripe_op.PLAIDIATOR_OT_MoveStripeUp.bl_idname, icon='TRIA_UP', text="")
        down_op = ops_column.operator(stripe_op.PLAIDIATOR_OT_MoveStripeDown.bl_idname, icon='TRIA_DOWN', text="")

        add_op.stripe_index = remove_op.stripe_index = up_op.stripe_index = down_op.stripe_index = p_globals.get(f"{hv}_index")
        add_op.hv = remove_op.hv = up_op.hv = down_op.hv = hv

    def draw(self, context: bpy_struct) -> None:
        global last_seen_node
        layout = self.layout
        node = context.active_node
        p_globals = context.window_manager.plaidiator_globals

        # Reset plaidiator_globals when the active node changes
        if node != last_seen_node:
            last_seen_node = node
            p_globals.h_index = 0
            p_globals.v_index = 0

        if not node or not hasattr(node, "plaidiator_id"):
            layout.label(text="Not a Plaidiator node")
            return

        if node.plaidiator_id.type == "PARENT_GROUP":
            self.draw_vector_warning(context, layout, node)

            if h_nodes := [n for n in node.node_tree.nodes if
                           hasattr(n, "plaidiator_id") and n.plaidiator_id.type == "COLOR_RAMP_H"]:
                self.draw_component(context, layout, h_nodes[0], Components.H)
            if v_nodes := [n for n in node.node_tree.nodes if
                           hasattr(n, "plaidiator_id") and n.plaidiator_id.type == "COLOR_RAMP_V"]:
                self.draw_component(context, layout, v_nodes[0], Components.V)
            return

        if node.plaidiator_id.type in {"COLOR_RAMP_H", "COLOR_RAMP_V"}:
            hv = {
                "COLOR_RAMP_H": Components.H,
                "COLOR_RAMP_V": Components.V,
            }[node.plaidiator_id.type]
            self.draw_component(context, layout, node, hv)
            return

        layout.label(text="Unknown node type")


def set_panel_category_from_prefs() -> None:
    """Set the panel's category (tab) from the n_panel_location preference"""
    try:
        location = bpy.context.preferences.addons[package_name].preferences.n_panel_location
        NODE_PT_plaidiator_detail.bl_category = location
    except AttributeError:
        # This means the preferences aren't set up, so just pass and use the default
        pass


def update_panel_category() -> None:
    """Set the panel's category (tab) from the n_panel_location preference and unregister/reregister the panel"""
    unregister_class(NODE_PT_plaidiator_detail)
    set_panel_category_from_prefs()
    register_class(NODE_PT_plaidiator_detail)



REGISTER_CLASSES = [NODE_PT_plaidiator_detail, NODE_UL_stripe_list]
