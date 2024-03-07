from typing import Set
from bpy.types import Operator, bpy_struct
from bpy.props import IntProperty, StringProperty
from ..lib import stripe as stripe_lib

if "_LOADED" in locals():
    import importlib

    for mod in (stripe_lib,):
        importlib.reload(mod)
_LOADED = True


def update_selection(context: bpy_struct, hv: str, index: int) -> None:
    p_globals = context.window_manager.plaidiator_globals
    index_key = f"{hv}_index"
    if hasattr(p_globals, index_key):
        setattr(p_globals, index_key, index)


def update_node(context: bpy_struct) -> None:
    stripe_lib.update_color_ramp(context.target_node)


class PLAIDIATOR_OT_MoveStripeUp(Operator):
    """Move the given stripe up"""
    bl_idname = "plaidiator.move_stripe_up"
    bl_label = "Move Stripe Up"
    bl_options = {'REGISTER', 'UNDO'}

    stripe_index: IntProperty()
    hv: StringProperty()

    def execute(self, context) -> Set[str]:
        if self.stripe_index == 0:
            return {'FINISHED'}
        new_index = self.stripe_index - 1
        context.target_component.stripes.move(self.stripe_index, new_index)
        update_selection(context, self.hv, new_index)
        update_node(context)
        return {'FINISHED'}


class PLAIDIATOR_OT_MoveStripeDown(Operator):
    """Move the given stripe down"""
    bl_idname = "plaidiator.move_stripe_down"
    bl_label = "Move Stripe Down"
    bl_options = {'REGISTER', 'UNDO'}

    stripe_index: IntProperty()
    hv: StringProperty()

    def execute(self, context) -> Set[str]:
        if self.stripe_index >= len(context.target_component.stripes):
            return {'FINISHED'}
        new_index = self.stripe_index + 1
        context.target_component.stripes.move(self.stripe_index, new_index)
        update_selection(context, self.hv, new_index)
        update_node(context)
        return {'FINISHED'}


class PLAIDIATOR_OT_InsertStripe(Operator):
    """Insert a new stripe"""
    bl_idname = "plaidiator.insert_stripe"
    bl_label = "Insert New Stripe"
    bl_options = {'REGISTER', 'UNDO'}

    hv: StringProperty()

    def execute(self, context) -> Set[str]:
        context.target_component.stripes.add()
        context.target_component.stripes.move(len(context.target_component.stripes) - 1, 0)
        update_selection(context, self.hv, 0)
        update_node(context)
        return {'FINISHED'}


class PLAIDIATOR_OT_DeleteStripe(Operator):
    """Delete the current stripe"""
    bl_idname = "plaidiator.delete_stripe"
    bl_label = "Delete Stripe"
    bl_options = {'REGISTER', 'UNDO'}

    stripe_index: IntProperty()
    hv: StringProperty()

    def execute(self, context) -> Set[str]:
        context.target_component.stripes.remove(self.stripe_index)
        update_node(context)
        return {'FINISHED'}


REGISTER_CLASSES = [PLAIDIATOR_OT_MoveStripeUp, PLAIDIATOR_OT_MoveStripeDown, PLAIDIATOR_OT_InsertStripe,
                    PLAIDIATOR_OT_DeleteStripe]
