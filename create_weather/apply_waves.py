"""
A Blender addon to apply dynamic canvas to a meshes to interact with rain and create waves/ripples.
"""

import bpy

bl_info = {
    "name": "Apply Waves",
    "blender": (2, 80, 0),  # Minimum Blender version required
    "category": "Object",
    "author": "Rhylei Tremlett",
    "description": "Applies dynamic canvas to meshes to interact with rain and create waves/ripples.",
    "version": (0, 0, 3),
    "location": "View3D > Add",  # "View3D > Add > Mesh",
    "doc_url": "https://github.com/KyrVorga/CGI605-Project",
    "tracker_url": "https://github.com/KyrVorga/CGI605-Project/issues",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/KyrVorga/CGI605-Project/wiki",
    "warning": "This addon is still under development.",
}


class ApplyWaves(bpy.types.Operator):
    bl_idname = "object.apply_waves"
    bl_label = "Apply Waves"
    bl_description = "Creates a dynamic canvas to produces waves/ripples."
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def execute(self, context):
        # Get all selected mesh objects from the outliner.
        selected_objects = [
            obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        # Add a Dynamic Canvas to every selected mesh object.
        for obj in selected_objects:
            # Set the active object to the current object.
            bpy.context.view_layer.objects.active = obj

            # apply dynamic brush canvas to water surface
            bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
            obj.modifiers["Dynamic Paint"].ui_type = 'CANVAS'
            bpy.ops.dpaint.type_toggle(type='CANVAS')
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].surface_type = 'WAVE'
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].brush_radius_scale = 0.35
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].brush_influence_scale = 0.5
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].wave_timescale = 3
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].wave_speed = 0.67
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces[
                "Surface"].brush_influence_scale = 0.25089

        return {'FINISHED'}


def draw_menu(self, context):
    self.layout.operator(ApplyWaves.bl_idname, icon="MOD_FLUIDSIM")


def register():
    bpy.utils.register_class(ApplyWaves)
    bpy.types.VIEW3D_MT_add.append(draw_menu)


def unregister():
    bpy.utils.unregister_class(ApplyWaves)
    bpy.types.VIEW3D_MT_add.remove(draw_menu)


if __name__ == "__main__":
    register()
