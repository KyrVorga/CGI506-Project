import bpy
import os
import shutil
import atexit
from bpy.app.handlers import persistent


class CenterView(bpy.types.Operator):
    bl_idname = "view3d.center_view"
    bl_label = "Center View to selected object"
    bl_description = "Centers the viewport on the active object and resets zoom."
    bl_options = {'REGISTER', 'UNDO'}

    # Stores hotkeys.
    addon_keymaps = []

    @staticmethod
    def execute(self, context):
        """Centers the viewport on the active object and resets zoom."""
        # Store the current cursor location.
        cursor_location = context.scene.cursor.location.copy()

        # Center the cursor on the active item.
        bpy.ops.view3d.snap_cursor_to_selected()

        # Center the view on the cursor.
        bpy.ops.view3d.view_center_cursor()

        # Zoom into active item.
        bpy.ops.view3d.view_selected()

        # Reset the cursor location.
        context.scene.cursor.location = cursor_location

        return {'FINISHED'}


@persistent
def on_start(dummy):
    """Creates a new minimal workspace and sets it as the active one."""
    try:
        # get the default workspace
        default = bpy.data.workspaces.get("Layout")

        if "Minimal" not in bpy.data.workspaces:
            bpy.ops.workspace.duplicate({"workspace": default})
            bpy.data.workspaces["Layout.001"].name = "Minimal"

        # May be already done, but explicitly make this workspace the active one
        bpy.context.window.workspace = bpy.data.workspaces["Minimal"]

    except:
        print("An exception occurred.")


def clear_blender_cache():
    """Locates the Blender temp/cache files and clears them."""
    # Get the path to the Blender temp/cache directory
    cache_dir = os.path.join(os.path.expanduser(
        "~"), ".config", "blender", "cache")

    # Check if the directory exists
    if os.path.exists(cache_dir):
        # Clear the directory
        shutil.rmtree(cache_dir)
        os.makedirs(cache_dir)
        print("Blender cache cleared successfully.")
    else:
        print("Blender cache directory not found.")


def register_center_view_hotkey():
    """Registers the hotkey for the CenterView operator."""
    # Add the hotkey.
    keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(
        name='3D View', space_type='VIEW_3D')
    item = keymap.keymap_items.new(
        CenterView.bl_idname, type='V', value='PRESS')

    # Add the hotkey to the list.
    CenterView.addon_keymaps.append((keymap, item))


def remove_center_view_hotkey():
    """Removes the hotkey for the CenterView operator."""
    # Remove the hotkey.
    for keymap, item in CenterView.addon_keymaps:
        keymap.keymap_items.remove(item)

    # Clear the keymap list.
    CenterView.addon_keymaps.clear()


def register():
    """Registers operators and hotkeys."""
    # Register the operator
    bpy.utils.register_class(CenterView)

    # Add the hotkey.
    register_center_view_hotkey()

    # Register on_start to run when Blender finishes loading.
    bpy.app.handlers.load_post.append(on_start)

    # Register functions to run when Blender exits.
    atexit.register(bpy.app.handlers.load_post.remove,
                    clear_blender_cache, remove_center_view_hotkey)


def unregister():
    """Unregisters operators and hotkeys."""
    # Unregister the operator
    bpy.utils.unregister_class(CenterView)

    # Remove the hotkey.
    remove_center_view_hotkey()


if __name__ == "__main__":
    register()
