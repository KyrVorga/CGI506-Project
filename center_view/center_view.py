"""
A Blender addon that centers the view on an active object.
"""

import bpy

bl_info = {
    "name": "Center View",
    "blender": (2, 80, 0),  # Minimum Blender version required
    "category": "3D View",
    "author": "Rhylei Tremlett",
    "description": "Centers the 3D View to Selected",
    "version": (0, 0, 1),
    "location": "View3D > Add",
    "doc_url": "https://github.com/KyrVorga/CGI605-Project",
    "tracker_url": "https://github.com/KyrVorga/CGI605-Project/issues",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/KyrVorga/CGI605-Project/wiki",
    "warning": "This addon is still under development.",
}


class CenterView(bpy.types.Operator):
    bl_idname = "view3d.view_center_selected"
    bl_label = "Center View to Selected"
    bl_description = "Creates a copy of your .blend file, timestamps it and moves it into /backups."
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def execute(self, context):
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


def draw_menu(self, context):
    self.layout.operator(CenterView.bl_idname)


addon_keymaps = []


def register():
    bpy.utils.register_class(CenterView)
    bpy.types.VIEW3D_MT_view_align.append(draw_menu)

    # Add the hotkey.
    keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    item = keymap.keymap_items.new(CenterView.bl_idname, type='V', value='PRESS')
    addon_keymaps.append((keymap, item))


def unregister():
    bpy.utils.unregister_class(CenterView)
    bpy.types.VIEW3D_MT_view_align.remove(draw_menu)

    # Remove the hotkey. 
    for keymap, item in addon_keymaps:
        keymap.keymap_items.remove(item)

    addon_keymaps.clear()


if __name__ == "__main__":
    register()
    # add startup code here and a startup conditional.
