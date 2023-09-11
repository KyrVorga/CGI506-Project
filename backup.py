import bpy
import shutil
import datetime
import os

bl_info = {
    "name": "Zip Backup",
    "blender": (2, 80, 0),  # Minimum Blender version required
    "category": "Object",
    "author": "Rhylei Tremlett",
    "description": "Creates a zip containing your .blend file, and optionally moves it.",
    "version": (0, 0, 1),
    # "location": "View3D > Add",  # "View3D > Add > Mesh",
    "doc_url": "https://github.com/KyrVorga/CGI605-Project",
    "tracker_url": "https://github.com/KyrVorga/CGI605-Project/issues",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/KyrVorga/CGI605-Project/wiki",
    "warning": "This addon is still under development.",
}


if __name__ == "__main__":
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