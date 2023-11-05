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
    "version": (0, 0, 4),
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
        """Applies a wave dynamic canvas to all selected mesh objects."""
        # Get all selected mesh objects from the outliner.
        selected_objects = [
            obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        # Add a Dynamic Canvas to every selected mesh object.
        for obj in selected_objects:
            # Set the active object to the current object.
            bpy.context.view_layer.objects.active = obj

            # Apply dynamic brush canvas to water surface
            bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
            obj.modifiers["Dynamic Paint"].ui_type = 'CANVAS'
            bpy.ops.dpaint.type_toggle(type='CANVAS')

            # Set canvas settings
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].surface_type = 'WAVE'
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].brush_radius_scale = 0.35
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].brush_influence_scale = 0.5
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].wave_timescale = 3
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].wave_speed = 0.67
            obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces[
                "Surface"].brush_influence_scale = 0.25089

        return {'FINISHED'}


class RevertWaves(bpy.types.Operator):
    bl_idname = "object.revert_waves"
    bl_label = "Revert Waves"
    bl_description = "Reverts the effects of Apply Waves operator on meshes."
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def execute(self, context):
        """Removes the wave dynamic canvas on all selected mesh objects."""
        # Get all selected mesh objects from the outliner.
        selected_objects = [
            obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        # Add a Dynamic Canvas to every selected mesh object.
        for obj in selected_objects:
            # Set the active object to the current object.
            bpy.context.view_layer.objects.active = obj

            # remove dynamic brush canvas from water surface
            bpy.ops.object.modifier_remove(modifier="Dynamic Paint")

        return {'FINISHED'}


def draw_menu(self, context):
    """Draws the menu for the Apply Waves operator."""
    self.layout.operator(ApplyWaves.bl_idname, icon="MOD_FLUIDSIM")
    self.layout.operator(RevertWaves.bl_idname, icon="MOD_FLUIDSIM")


def register():
    """Registers the Apply Waves operator."""
    bpy.utils.register_class(ApplyWaves)
    bpy.utils.register_class(RevertWaves)
    bpy.types.VIEW3D_MT_add.append(draw_menu)


def unregister():
    """Unregisters the Apply Waves operator."""
    bpy.utils.unregister_class(ApplyWaves)
    bpy.utils.unregister_class(RevertWaves)
    bpy.types.VIEW3D_MT_add.remove(draw_menu)


if __name__ == "__main__":
    register()
