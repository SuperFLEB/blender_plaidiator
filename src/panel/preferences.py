from . import n_panel
from ..lib import pkginfo
from bpy.types import AddonPreferences, bpy_struct
from bpy.props import EnumProperty, BoolProperty

if "_LOADED" in locals():
    import importlib

    for mod in (pkginfo, n_panel):
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()


def get_location(self: "PlaidiatorPrefsPanel"):
    return self.get("value", 0)


def set_location(self: "PlaidiatorPrefsPanel", value: str):
    changed = self.get("value", 0) != value
    self["value"] = value
    if changed:
        n_panel.update_panel_category()


class PlaidiatorPrefsPanel(AddonPreferences):
    bl_idname = package_name

    n_panel_location: EnumProperty(
        name="N-Panel location",
        description="Where should the Plaidiator panel be located?",
        items=[
            ("Plaidiator", 'In a "Plaidiator" tab', "Put the panel in its own tab"),
            ("Node", 'In the "Node" tab', "Put the panel after other items in the Node tab"),
        ],
        get=get_location,
        set=set_location
    )

    new_stripe_copy: BoolProperty(
        name="Creating a new stripe copies the selected stripe",
        description="When adding a stripe, copy the selected stripe's color and position. If unchecked, the default stripe, a red stripe in the middle, is created.",
        default=True
    )

    def draw(self, context: bpy_struct) -> None:
        layout = self.layout
        layout.prop(self, "n_panel_location")
        fiddly_box = layout.box()
        fiddly_box.label(text="Fiddly little tweaks")
        fiddly_box.prop(self, "new_stripe_copy")


REGISTER_CLASSES = [PlaidiatorPrefsPanel]
