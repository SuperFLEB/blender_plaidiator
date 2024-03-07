from typing import Callable
import bpy
from .lib import addon
from .operator import plaidiator, stripe
from .props import plaidiator as plaidiator_props
from .panel import n_panel, preferences as preferences_panel

if "_LOADED" in locals():
    import importlib

    for mod in (addon, preferences_panel, n_panel, plaidiator, plaidiator_props,):
        importlib.reload(mod)
_LOADED = True

package_name = __package__

bl_info = {
    "name": "Plaidiator",
    "description": "Create plaids and tartans easily with this addon",
    "author": "FLEB (a.k.a. SuperFLEB)",
    "version": (0, 1, 1),
    "blender": (3, 6, 0),
    "location": "View3D > Object",
    "warning": "",  # used for warning icon and text in addons panel
    "doc_url": "https://github.com/SuperFLEB/blender_plaidiator",
    "tracker_url": "https://github.com/SuperFLEB/blender_plaidiator/issues",
    "support": "COMMUNITY",
    "category": "Material",
}

# This can be used to register menus (MT) or header items (HT)
menus: list[tuple[str, Callable]] = [
    ("NODE_MT_add", addon.menuitem(plaidiator.plaidiator_OT_AddPlaid, 'EXEC_DEFAULT'))
]

# Registerable modules have a REGISTER_CLASSES list that lists all registerable classes in the module
registerable_modules = [
    n_panel,
    plaidiator,
    stripe,
    plaidiator_props,
]


def register() -> None:
    # Register prefs separately so we can set the n-panel's "bl_category" before the n-panel gets registered
    addon.register_classes([preferences_panel])
    n_panel.set_panel_category_from_prefs()

    addon.warn_unregisterable(registerable_modules)
    addon.register_classes(registerable_modules)
    addon.register_functions(registerable_modules)
    addon.register_menus(menus)


def unregister() -> None:
    try:
        del bpy.types.WindowManager.plaidiator_globals
    except AttributeError:
        pass
    addon.unregister_menus(menus)
    addon.unregister_functions(registerable_modules)
    addon.unregister_classes(registerable_modules)
    addon.unregister_classes([preferences_panel])


if __name__ == "__main__":
    register()
