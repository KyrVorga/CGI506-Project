"""
A Blender addon to create dynamic weather effects and procedural clouds.
"""

import bpy

bl_info = {
    "name": "Create Weather",
    "blender": (2, 80, 0),  # Minimum Blender version required
    "category": "Object",
    "author": "Rhylei Tremlett",
    "description": "A small system to generate procedural weather.",
    "version": (0, 0, 3),
    "location": "View3D > Add",  # "View3D > Add > Mesh",
    "doc_url": "https://github.com/KyrVorga/CGI605-Project",
    "tracker_url": "https://github.com/KyrVorga/CGI605-Project/issues",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/KyrVorga/CGI605-Project/wiki",
    "warning": "This addon is still under development.",
}


class CreateWeather(bpy.types.Operator):
    bl_idname = "object.create_weather"
    bl_label = "Create Weather"
    bl_description = "Creates a procedural weather simulation"
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def execute(self, context):
        # Create a new plane for the surface
        bpy.ops.mesh.primitive_plane_add(
            size=2, enter_editmode=False, align='WORLD', location=(0, 0, -1), scale=(1, 1, 1))
        surface_obj = bpy.context.active_object
        surface_obj.name = "Water Surface"
        bpy.ops.object.shade_smooth()

        # apply subsurface division to water surface
        bpy.ops.object.modifier_add(type='SUBSURF')
        surface_obj.modifiers["Subdivision"].levels = 6
        surface_obj.modifiers["Subdivision"].render_levels = 6
        surface_obj.modifiers["Subdivision"].subdivision_type = 'SIMPLE'

        # apply dynamic brush canvas to water surface
        bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
        surface_obj.modifiers["Dynamic Paint"].ui_type = 'CANVAS'
        bpy.ops.dpaint.type_toggle(type='CANVAS')
        surface_obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].surface_type = 'WAVE'
        surface_obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].brush_radius_scale = 0.35
        surface_obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].brush_influence_scale = 0.5
        surface_obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].wave_timescale = 3
        surface_obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].wave_speed = 0.67
        surface_obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces[
            "Surface"].brush_influence_scale = 0.25089

        # Create the raindrop object
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 1), scale=(1, 1, 1))
        raindrop_obj = bpy.context.active_object
        raindrop_obj.name = "Raindrop"

        # Add a Decimate modifier to the raindrop object
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].ratio = 0.25
        bpy.ops.object.shade_smooth()

        # Create a new plane for the rain Emitter
        bpy.ops.mesh.primitive_plane_add(
            size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        emitter_obj = bpy.context.active_object
        emitter_obj.name = "Rain Emitter"

        # Add a particle system to the emitter object
        rain_system = add_particle_system(emitter_obj)

        # Change the render type of particles to 'OBJECT'
        rain_system.settings.render_type = 'OBJECT'

        rain_system.settings.instance_object = bpy.data.objects["Raindrop"]
        rain_system.settings.particle_size = 0.01
        rain_system.settings.size_random = 1
        rain_system.settings.count = 1000

        dynamic_paint_modifier = emitter_obj.modifiers.new(
            name="Dynamic Paint", type='DYNAMIC_PAINT')
        dynamic_paint_modifier.ui_type = 'BRUSH'
        bpy.ops.dpaint.type_toggle(type='BRUSH')

        emitter_obj.modifiers["Dynamic Paint"].brush_settings.paint_source = "PARTICLE_SYSTEM"
        emitter_obj.modifiers["Dynamic Paint"].brush_settings.particle_system = \
            bpy.data.objects["Rain Emitter"].particle_systems["Rain Particle System"]
        emitter_obj.modifiers["Dynamic Paint"].brush_settings.solid_radius = 0.05

        # Create glass material for Rain Drops
        mat = bpy.data.materials.get("Rain")
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name="Rain")

        # Assign rain material to raindrop object
        if raindrop_obj.data.materials:
            # assign to 1st material slot
            raindrop_obj.data.materials[0] = mat
        else:
            # no slots
            raindrop_obj.data.materials.append(mat)

        # Assign rain material  to surface object
        if surface_obj.data.materials:
            # assign to 1st material slot
            surface_obj.data.materials[0] = mat
        else:
            # no slots
            surface_obj.data.materials.append(mat)

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

        return {'FINISHED'}


def add_particle_system(emitter_obj):
    # Add a particle system to the emitter object
    bpy.ops.object.particle_system_add()
    # Get the last added particle system
    particle_system = emitter_obj.particle_systems[-1]
    particle_system.name = "Rain Particle System"
    return particle_system


def configure_dynamic_paint(emitter_obj, particle_system):
    # Add Dynamic Paint modifier to the emitter object
    dynamic_paint_modifier = emitter_obj.modifiers.new(
        name="Dynamic Paint", type='DYNAMIC_PAINT')
    dynamic_paint_modifier.ui_type = 'BRUSH'
    dynamic_paint_modifier.brush_settings.particle_system = particle_system
    dynamic_paint_modifier.type_toggle(type='BRUSH')


def draw_menu(self, context):
    self.layout.operator(CreateWeather.bl_idname, icon="MOD_FLUIDSIM")


def register():
    bpy.utils.register_class(CreateWeather)
    bpy.types.VIEW3D_MT_add.append(draw_menu)


def unregister():
    bpy.utils.unregister_class(CreateWeather)
    bpy.types.VIEW3D_MT_add.remove(draw_menu)


if __name__ == "__main__":
    register()
