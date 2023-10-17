# from backup import backup
# from center_view import center_view
# from create_weather import create_weather
# import bpy
#
# if __name__ == "__main__":
#     # backup.register()
#     # center_view.register()
#     # create_weather.register()
#
#     minimal_layout = bpy.data.libraries.new(name="Minimal", internal=False)
#
#     # Link the layout to the startup file
#     bpy.context.screen.layout_library = minimal_layout

import bpy
import os
import shutil
import atexit
from bpy.app.handlers import persistent


@persistent
def add_sphere(dummy):
    for i in range(4):
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=1, location=((i - 1) * 3, 0, 3))


@persistent
def run_when_new_blend_file_open(dummy):
    """
    Workspaces
    Modeling: For modification of geometry by modeling tools.
    Sculpting: For modification of meshes by sculpting tools.
    UV Editing: For mapping of image texture coordinates to 3D surfaces.
    Texture Paint: For coloring image textures in the 3D Viewport.
    Shading: For specifying material properties for rendering.
    Animation: For making properties of objects dependent on time.
    Rendering: For viewing and analyzing rendering results.
    Compositing: For combining and post-processing of images and rendering information.
    Geometry Nodes: For procedural modeling using Geometry Nodes.
    Scripting: For interacting with Blender’s Python API and writing scripts.
    """
    try:
        # get the default workspace
        default = bpy.data.workspaces.get("Layout")

        if "Minimal" not in bpy.data.workspaces:
            bpy.ops.workspace.duplicate({"workspace": default})
            bpy.data.workspaces["Layout.001"].name = "Minimal"

        # May be already done, but explicitly make this workspace the active one
        bpy.context.window.workspace = bpy.data.workspaces["Minimal"]

        # Find the 3D viewport screen area.
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                # area.screen_full_area()
                area.show_fullscreen = True
                break

    except:
        print("An exception occurred.")


def clear_blender_cache():
    """
    Locates the Blender temp/cache files and clears them.
    """
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


def register():
    bpy.app.handlers.load_post.append(add_sphere)
    bpy.app.handlers.load_post.append(run_when_new_blend_file_open)

    atexit.register(bpy.app.handlers.load_post.remove, clear_blender_cache)


def unregister():
    pass


if __name__ == "__main__":
    register()
