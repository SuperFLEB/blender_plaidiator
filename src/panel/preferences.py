from bpy.props import BoolProperty
from bpy.types import AddonPreferences, bpy_struct
from ..lib import pkginfo

if "_LOADED" in locals():
    import importlib

    for mod in (pkginfo,):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()


class PreferencesPanel(AddonPreferences):
    bl_idname = package_name
    preferences_checkbox_property: BoolProperty(
        name="Turn on checkbox in preferences panel",
        description="If this checkbox is checked, then it is checked",
        default=False
    )

    def draw(self, context: bpy_struct) -> None:
        layout = self.layout
        layout.prop(self, 'preferences_checkbox_property')


REGISTER_CLASSES = [PreferencesPanel]
