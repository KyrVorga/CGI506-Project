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
    "version": (0, 0, 2),
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

    @staticmethod
    def execute(self, context):
        # Make sure the project has been named and saved at least once.
        if bpy.data.is_saved:
            # Pack all external data into the .blend
            bpy.ops.file.pack_all()
            bpy.ops.wm.save_mainfile()

            # Get the path to the blend file (inclusive).
            path_to_blend = bpy.data.filepath

            # Get the current date and format it into a folder compatible string.
            current_date = datetime.datetime.now()
            output_filename = current_date.strftime('%y_%m_%d-%H_%M_%S')

            # Get the current directory.
            current_directory = bpy.path.abspath("//")

            # Create the expected output path for the new blend file.
            copied_file_path = "{0}/{1}.blend".format(current_directory, output_filename)

            # Create the backup folder if it doesn't already exist.
            backup_folder_path = "{0}/backup".format(current_directory)

            if not os.path.exists(backup_folder_path):
                os.makedirs(backup_folder_path)

            # Use blender to save the .blend as a copy
            bpy.ops.wm.save_as_mainfile(filepath=copied_file_path, copy=True)

            # Move the above made copy into the backup folder
            shutil.move(src=copied_file_path, dst=backup_folder_path)

        return {'FINISHED'}


def draw_menu(self, context):
    self.layout.operator(Backup.bl_idname)


def register():
    bpy.utils.register_class(Backup)
    bpy.types.TOPBAR_MT_file.append(draw_menu)


def unregister():
    bpy.utils.unregister_class(Backup)
    bpy.types.TOPBAR_MT_file.remove(draw_menu)


if __name__ == "__main__":
    register()
