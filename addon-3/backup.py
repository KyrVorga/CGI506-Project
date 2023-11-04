"""
A Blender addon that creates versioned backups of your .blend file.
"""

import bpy
import shutil
import datetime
import os

bl_info = {
    "name": "Backup",
    "blender": (2, 80, 0),  # Minimum Blender version required
    "category": "Object",
    "author": "Rhylei Tremlett",
    "description": "Creates a copy of your .blend file, timestamps it and moves it into /backups.",
    "version": (0, 0, 3),
    "location": "File > External",
    "doc_url": "https://github.com/KyrVorga/CGI605-Project",
    "tracker_url": "https://github.com/KyrVorga/CGI605-Project/issues",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/KyrVorga/CGI605-Project/wiki",
    "warning": "This addon is still under development.",
}


class Backup(bpy.types.Operator):
    bl_idname = "object.backup"
    bl_label = "Backup"
    bl_description = "Creates a copy of your .blend file, timestamps it and moves it into /backups."
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @staticmethod
    def execute(self, context):
        """Creates a copy of the .blend file, timestamps it and moves it into the selected folder."""
        # Make sure the project has been named and saved at least once.
        if bpy.data.is_saved:
            # Pack all external data into the .blend
            bpy.ops.wm.save_mainfile()

            # Get the current blend file name.
            blend_file_name = bpy.path.basename(
                bpy.context.blend_data.filepath)

            # Get the current date and format it into a folder compatible string.
            current_date = datetime.datetime.now()
            output_filename = blend_file_name.replace(
                ".blend", "") + "_" + current_date.strftime("%Y-%m-%d_%H-%M-%S") + ".blend"

            # Get the current directory.
            current_directory = bpy.path.abspath("//")

            # Create the expected output path for the new blend file.
            copied_file_path = "{0}/{1}".format(
                current_directory, output_filename)

            # Remove the user made filename from the path.
            backup_folder_path = os.path.dirname(self.filepath)

            # Use blender to save the .blend as a copy
            bpy.ops.wm.save_as_mainfile(filepath=copied_file_path, copy=True)

            # Move the above made copy into the backup folder
            shutil.move(src=copied_file_path, dst=backup_folder_path)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """Checks if the operator can run."""
        return context.object is not None

    def invoke(self, context, event):
        """Opens the file browser."""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def draw_menu(self, context):
    """Draws the menu item."""
    self.layout.operator(Backup.bl_idname)


def register():
    """Registers the operator."""
    bpy.utils.register_class(Backup)
    bpy.types.TOPBAR_MT_file.append(draw_menu)


def unregister():
    """Unregisters the operator."""
    bpy.utils.unregister_class(Backup)
    bpy.types.TOPBAR_MT_file.remove(draw_menu)


if __name__ == "__main__":
    register()
