"""
A Blender addon to apply a rain emitter to all selected meshes.
"""

import bpy

bl_info = {
    "name": "Apply Rain",
    "blender": (2, 80, 0),  # Minimum Blender version required
    "category": "Object",
    "author": "Rhylei Tremlett",
    "description": "Applies a rain emitter to all selected meshes.",
    "version": (0, 0, 5),
    "location": "View3D > Add",  # "View3D > Add > Mesh",
    "doc_url": "https://github.com/KyrVorga/CGI605-Project",
    "tracker_url": "https://github.com/KyrVorga/CGI605-Project/issues",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/KyrVorga/CGI605-Project/wiki",
    "warning": "This addon is still under development.",
}


class ApplyRain(bpy.types.Operator):
    """
    This operator applies a rain emitter to all selected mesh objects.
    It creates a raindrop object and a glass material for the rain drops.
    It also adds a particle system to each selected mesh object and configures it to emit rain particles.
    Finally, it adds a Dynamic Paint modifier to each selected mesh object to simulate raindrops on the surface.
    """
    bl_idname = "object.apply_rain"
    bl_label = "Apply Rain"
    bl_description = "Applies a rain emitter to all selected objects."
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def execute(self, context):
        """Applies a rain emitter to all selected mesh objects."""
        # Get all selected mesh objects from the outliner.
        selected_objects = [
            obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        # ------------------- #SECTION - Raindrop Mesh ------------------ #
        # Check if the raindrop already exists. If not, create it.
        raindrop_obj = bpy.data.objects.get("Raindrop")
        if raindrop_obj is None:
            # Create the raindrop object.
            bpy.ops.mesh.primitive_ico_sphere_add(
                radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 1), scale=(1, 1, 1))
            raindrop_obj = bpy.context.active_object
            raindrop_obj.name = "Raindrop"

            # Add a Decimate modifier to the raindrop object.
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = 0.25
            bpy.ops.object.shade_smooth()
            # raindrop_obj.hide_viewport = True

            #!SECTION

        # ------------------- #SECTION - Rain Material------------------ #
        # Create glass material for Rain Drops.
        mat = bpy.data.materials.get("Rain")
        if mat is None:
            # Create material.
            mat = bpy.data.materials.new(name="Rain")

            mat.use_nodes = True
            nodes = mat.node_tree.nodes

            # Clear existing nodes
            for node in nodes:
                nodes.remove(node)

            # Create a Glass BSDF node
            glass_node = nodes.new(type="ShaderNodeBsdfGlass")
            glass_node.location = (0, 0)

            # Create a Material Output node
            output_node = nodes.new(type="ShaderNodeOutputMaterial")
            output_node.location = (400, 0)

            # Connect the Glass BSDF node to the Material Output node
            material_output = output_node.inputs['Surface']
            glass_output = glass_node.outputs['BSDF']
            mat.node_tree.links.new(material_output, glass_output)

            mat.use_screen_refraction = True

            #!SECTION

        # ------------------- #SECTION - Apply Material------------------ #
        # Assign rain material to raindrop object.
        if raindrop_obj.data.materials:
            # Assign to 1st material slot.
            raindrop_obj.data.materials[0] = mat
        else:
            # No slots.
            raindrop_obj.data.materials.append(mat)

            #!SECTION

        # ------------------- #SECTION - Particle System ------------------ #
        # Add a rain emmitter to every selected mesh object.
        for obj in selected_objects:
            # Set the active object to the current object.
            bpy.context.view_layer.objects.active = obj

            # Add a particle system to the emitter object
            rain_system = add_particle_system(obj)

            # Change the render type of particles to 'OBJECT'
            rain_system.settings.render_type = 'OBJECT'

            # Configure the rain particle system
            rain_system.settings.instance_object = bpy.data.objects["Raindrop"]
            rain_system.settings.particle_size = 0.01
            rain_system.settings.size_random = 1
            rain_system.settings.count = 10000
            rain_system.settings.emit_from = 'VOLUME'

            # Set the emitter to not be visible in viewport and render
            obj.show_instancer_for_viewport = False
            obj.show_instancer_for_render = False

            #!SECTION

            # ------------------- #SECTION - Dynamic Paint ------------------ #
            # Setup the dynamic paint modifier
            dynamic_paint_modifier = obj.modifiers.new(
                name="Dynamic Paint", type='DYNAMIC_PAINT')
            dynamic_paint_modifier.ui_type = 'BRUSH'

            # Set the brush type to 'PAINT'
            bpy.ops.dpaint.type_toggle(type='BRUSH')

            # Get the active object
            active_obj = bpy.context.active_object

            # Modify the brush settings to use the emitter particle system as the paint source
            obj.modifiers["Dynamic Paint"].brush_settings.paint_source = "PARTICLE_SYSTEM"
            obj.modifiers["Dynamic Paint"].brush_settings.particle_system = \
                active_obj.particle_systems["Rain Particle System"]
            obj.modifiers["Dynamic Paint"].brush_settings.solid_radius = 0.05

            #!SECTION

        return {'FINISHED'}


class RevertRain(bpy.types.Operator):
    bl_idname = "object.revert_rain"
    bl_label = "Revert Rain"
    bl_description = "Reverts the effects of Apply Rain operator on meshes."
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def execute(self, context):
        """Reverts the effects of Apply Rain operator on meshes."""
        # Get all selected mesh objects from the outliner.
        selected_objects = [
            obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        # Add a Dynamic Canvas to every selected mesh object.
        for obj in selected_objects:
            # Set the active object to the current object.
            bpy.context.view_layer.objects.active = obj

            # Delete the particle system
            bpy.ops.object.particle_system_remove()

            # Remove dynamic paint from object
            bpy.ops.object.modifier_remove(modifier="Dynamic Paint")

        return {'FINISHED'}


def add_particle_system(emitter_obj):
    """Adds a particle system to the emitter object and returns it."""
    # Add a particle system to the emitter object
    bpy.ops.object.particle_system_add()
    # Get the last added particle system
    particle_system = emitter_obj.particle_systems[-1]
    particle_system.name = "Rain Particle System"
    return particle_system


def draw_menu(self, context):
    """Draws the menu for the Apply Rain operator."""
    self.layout.operator(ApplyRain.bl_idname, icon="MOD_FLUIDSIM")
    self.layout.operator(RevertRain.bl_idname, icon="MOD_FLUIDSIM")


def register():
    """Registers the Apply Rain operator."""
    bpy.utils.register_class(ApplyRain)
    bpy.utils.register_class(RevertRain)

    bpy.types.VIEW3D_MT_add.append(draw_menu)


def unregister():
    """Unregisters the Apply Rain operator."""
    bpy.utils.unregister_class(ApplyRain)
    bpy.utils.unregister_class(RevertRain)
    bpy.types.VIEW3D_MT_add.remove(draw_menu)


if __name__ == "__main__":
    register()
