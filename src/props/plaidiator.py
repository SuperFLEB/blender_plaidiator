import bpy
from bpy.props import EnumProperty, CollectionProperty, FloatVectorProperty, FloatProperty, IntProperty
from bpy.types import PropertyGroup, ShaderNodeValToRGB, ShaderNodeGroup, Node, bpy_struct
from ..lib import stripe as stripe_lib

if "_LOADED" in locals():
    import importlib

    for mod in (stripe_lib,):
        importlib.reload(mod)
_LOADED = True


def _get_target_node(property: PropertyGroup) -> Node:
    node_group = property.id_data
    component_nodes = [node for node in node_group.nodes if hasattr(node, "plaidiator_component")]
    for node in component_nodes:
        if node.plaidiator_component == property:
            return node
        for prop in node.plaidiator_component.values():
            if prop == property or prop is property:
                return node
        for stripe in node.plaidiator_component.stripes:
            if stripe == property:
                return node


def rebuild_color_ramp_on_update(self: PropertyGroup, context: bpy_struct) -> None:
    if not hasattr(context.active_node, "plaidiator_id"):
        print("Plaidiator data changed, but current node had no plaidiator_id. Not applying updates.")
        return
    node = _get_target_node(self)
    stripe_lib.update_color_ramp(node)


class PlaidiatorGlobals(PropertyGroup):
    h_index: IntProperty(default=0)
    v_index: IntProperty(default=0)

    @classmethod
    def post_register(cls) -> None:
        bpy.types.WindowManager.plaidiator_globals = bpy.props.PointerProperty(
            type=cls,
        )


class Stripe(PropertyGroup):
    rgba: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(1.0, 0.0, 0.0, 1.0),
        size=4,
        min=0.0,
        max=1.0,
        update=rebuild_color_ramp_on_update,
    )
    center: FloatProperty(
        name="Position",
        default=0.5,
        min=0.0,
        max=1.0,
        update=rebuild_color_ramp_on_update,
    )
    width: FloatProperty(
        name="Width",
        default=0.1,
        min=0.0,
        max=1.0,
        update=rebuild_color_ramp_on_update,
    )


class PlaidiatorComponentProperties(PropertyGroup):
    background_rgba: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        update=rebuild_color_ramp_on_update
    )

    stripes: CollectionProperty(type=Stripe)

    @classmethod
    def post_register(cls) -> None:
        ShaderNodeValToRGB.plaidiator_component = bpy.props.PointerProperty(
            type=cls,
            name="Plaidiator Component Properties",
            description="Plaidiator addon ID and metadata for node groups"
        )


class PlaidiaitorID(PropertyGroup):
    type: EnumProperty(
        name="Type",
        description="Plaidiator node type",
        default="NONE",
        items=[
            ("NONE", "NONE", "Not a Plaidiator node"),
            ("PARENT_GROUP", "PARENT_GROUP", "Plaidiator Parent Nodegroup"),
            ("COLOR_RAMP_H", "COLOR_RAMP_H", "Color Ramp, Horizontal"),
            ("COLOR_RAMP_V", "COLOR_RAMP_V", "Color Ramp, Vertical"),
        ]
    )

    @classmethod
    def post_register(cls) -> None:
        for node_type in [ShaderNodeValToRGB, ShaderNodeGroup]:
            node_type.plaidiator_id = bpy.props.PointerProperty(
                type=cls,
                name="Plaidiator Type Information",
                description="Plaidiator Node Type Information"
            )


REGISTER_CLASSES = [Stripe, PlaidiatorComponentProperties, PlaidiaitorID, PlaidiatorGlobals]
