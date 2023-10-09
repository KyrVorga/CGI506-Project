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
from bpy.app.handlers import persistent


@persistent
def add_sphere(dummy):
    for i in range(3):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=((i - 1) * 3, 0, 3))


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
        # print(" to 'Scripting' workspaces ")
        #
        # bpy.ops.workspace.append_activate(
        #     idname='Layout',
        #     filepath=bpy.utils.user_resource('CONFIG', path='startup.blend')
        # )
        #
        # bpy.context.window.workspace = bpy.data.workspaces['Minimal']

        # get the default workspace
        default = bpy.data.workspaces.get("Layout")

        if "Minimal" not in bpy.data.workspaces:
            bpy.ops.workspace.duplicate({"workspace": default})
            bpy.data.workspaces["Layout.001"].name = "Minimal"
            # May be already done, but explicitly make this workspace the active one
            bpy.context.window.workspace = bpy.data.workspaces["Minimal"]
            # bpy.ops.screen.toggle_header_menus()

    except:
        print("An exception occurred.")


def register():
    bpy.app.handlers.load_post.append(add_sphere)
    bpy.app.handlers.load_post.append(run_when_new_blend_file_open)


def unregister():
    pass


if __name__ == "__main__":
    register()
