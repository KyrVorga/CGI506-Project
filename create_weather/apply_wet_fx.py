"""
A Blender addon set up meshes to interact with rain and create wet effects.
"""

import bpy

bl_info = {
    "name": "Apply Wet FX",
    "blender": (2, 80, 0),  # Minimum Blender version required
    "category": "Object",
    "author": "Rhylei Tremlett",
    "description": "Sets up meshes to interact with rain and create wet effects.",
    "version": (0, 0, 28),
    "location": "View3D > Add",  # "View3D > Add > Mesh",
    "doc_url": "https://github.com/KyrVorga/CGI605-Project",
    "tracker_url": "https://github.com/KyrVorga/CGI605-Project/issues",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/KyrVorga/CGI605-Project/wiki",
    "warning": "This addon is still under development.",
}

# Program Logic:
# check if any objects are selected
# for each selected object check that it is a mesh
# check for exising material, if none, create one.
# check for existing dynamic canvas
# create a dynamic canvas for each selected object or add to existing canvas
# create a wetmap for each selected object
# if it has a material, duplicate it and begin modifying the material
# if it does not have a material, create a material and modify it

# Part two:
# in the material, check if there are components connected to base color, specular, roughness and normals
# create an attribute node and set it to the wetmap
# create 4 mix shaders and one invert node
# connect them all up, and if there are existing textures, intercept them with the mix shaders.


class ApplyWetFX(bpy.types.Operator):
    bl_idname = "object.apply_wet_fx"
    bl_label = "Apply Wet FX"
    bl_description = "Sets up meshes to interact with rain and create wet effects."
    bl_options = {'REGISTER', 'UNDO'}

    # The origin
    original_materials = {}

    @staticmethod
    def execute(self, context):
        """Applies a wet FX to all selected mesh objects."""

        # ---------------------------------------------------------------------------- #
        #                           #SECTION - Object Setup                            #
        # ---------------------------------------------------------------------------- #
        # Get all selected mesh objects from the outliner.
        selected_objects = [
            obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        # Add a Dynamic Canvas to every selected mesh object.
        for obj in selected_objects:

            # Set the active object to the current object.
            bpy.context.view_layer.objects.active = obj

            # ---------------------------- #SECTION - Material ---------------------------- #
            # Check for existing material, if none, create one.
            if obj.active_material is None:
                # Create material.
                mat = bpy.data.materials.new(name="Wet")
                obj.active_material = mat

            # If there is an existing material, duplicate it.
            else:
                self.original_materials[obj.name] = obj.active_material

                mat = obj.active_material.copy()
                obj.active_material = mat

            #!SECTION

            # ---------------------------- #SECTION - Dynamic Canvas ---------------------------- #
            # Check for existing dynamic canvas.
            if obj.modifiers.get("Dynamic Paint") is not None:
                # Check if there is a canvas surface with name "Wet Layer"
                if obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces.get("Wet Layer") is None:
                    # If it doesn't exist, add a new canvas surface.
                    bpy.ops.dpaint.surface_slot_add()

                else:
                    # If it exists, return finished.
                    return {'FINISHED'}

            else:
                # Apply dynamic canvas.
                bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
                bpy.context.object.modifiers["Dynamic Paint"].ui_type = 'CANVAS'
                bpy.ops.dpaint.type_toggle(type='CANVAS')

            # Most recent canvas surface is the one we want to modify.
            bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces[-1].name = "Wet Layer"
            wet_layer = bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Wet Layer"]
            wet_layer.surface_type = 'PAINT'

            wet_layer.brush_radius_scale = 0.7
            wet_layer.brush_influence_scale = 0.9

            wet_layer.use_drying = False

            wet_layer.use_spread = True
            wet_layer.spread_speed = 0.1

            bpy.ops.dpaint.output_toggle(output='B')

            #!SECTION

            # ---------------------------- #SECTION - Collision ---------------------------- #

            # Add a collision modifier and set it to kill particles
            bpy.ops.object.modifier_add(type='COLLISION')
            obj.collision.use_particle_kill = True

            #!SECTION
            #!SECTION

            # ---------------------------------------------------------------------------- #
            #                          #SECTION - Material Nodes                           #
            # ---------------------------------------------------------------------------- #
            # Start setting up the node network.
            bpy.context.object.active_material.use_nodes = True

            # Create a wet_fx frame
            wet_fx_frame = mat.node_tree.nodes.new(type="NodeFrame")

            # Create an atrribute node and set it to the wetmap
            wetmap_node = mat.node_tree.nodes.new(type="ShaderNodeAttribute")
            wetmap_node.attribute_name = "dp_wetmap"

            # Move the node into the frame
            wetmap_node.parent = wet_fx_frame

            wetmap_node.location = (-1600, 0)

            # --------------------------- #SECTION - Base Color --------------------------- #

            # Create a color mix node
            base_color_mix_node = mat.node_tree.nodes.new(
                type="ShaderNodeMixRGB")
            base_color_mix_node.blend_type = 'DARKEN'

            # Add the attribute node to the mix node factor
            mat.node_tree.links.new(
                base_color_mix_node.inputs[0], wetmap_node.outputs[0])

            # Set the secondary mix colour to black
            base_color_mix_node.inputs[2].default_value = (0, 0, 0.02, 1)

            # Check if there is anything connected to the base color
            if mat.node_tree.nodes.get("Principled BSDF").inputs[0].links:
                # If there is, connect it to the mix node
                mat.node_tree.links.new(
                    base_color_mix_node.inputs[1], mat.node_tree.nodes.get("Principled BSDF").inputs[0].links[0].from_socket)

                # Disconnect the existing link
                mat.node_tree.links.remove(
                    mat.node_tree.nodes.get("Principled BSDF").inputs[0].links[0])

            # Link the mix node output to the base color input
            mat.node_tree.links.new(
                mat.node_tree.nodes.get("Principled BSDF").inputs[0], base_color_mix_node.outputs[0])

            # Move the node into the frame
            base_color_mix_node.parent = wet_fx_frame

            base_color_mix_node.location = (-1200, 0)

            #!SECTION

            # --------------------------- #SECTION - Specular --------------------------- #

            # Create a color mix node
            specular_mix_node = mat.node_tree.nodes.new(
                type="ShaderNodeMixRGB")
            specular_mix_node.blend_type = 'MIX'

            # run the attribute node through the primary input
            mat.node_tree.links.new(
                specular_mix_node.inputs[1], wetmap_node.outputs[0])

            # Set the secondary mix colour to white
            specular_mix_node.inputs[2].default_value = (1, 1, 1, 1)

            # Set the factor to 0.5
            specular_mix_node.inputs[0].default_value = 0.5

            # Check if there is anything connected to the specular
            if mat.node_tree.nodes.get("Principled BSDF").inputs[7].links:
                # If there is, connect it to the mix node
                mat.node_tree.links.new(
                    specular_mix_node.inputs[0], mat.node_tree.nodes.get("Principled BSDF").inputs[7].links[0].from_socket)

                # Disconnect the existing link
                mat.node_tree.links.remove(
                    mat.node_tree.nodes.get("Principled BSDF").inputs[7].links[0])

            # Link the mix node output to the specular input
            mat.node_tree.links.new(
                mat.node_tree.nodes.get("Principled BSDF").inputs[7], specular_mix_node.outputs[0])

            # Move the node into the frame
            specular_mix_node.parent = wet_fx_frame

            specular_mix_node.location = (-1200, -200)

            #!SECTION

            # --------------------------- #SECTION - Roughness --------------------------- #

            # Create a color mix node
            roughness_mix_node = mat.node_tree.nodes.new(
                type="ShaderNodeMixRGB")
            roughness_mix_node.blend_type = 'MIX'

            # Set the secondary mix colour to grey, value 0.2
            roughness_mix_node.inputs[2].default_value = (0.2, 0.2, 0.2, 1)

            # run the attribute node through the factor
            mat.node_tree.links.new(
                roughness_mix_node.inputs[0], wetmap_node.outputs[0])

            # Check if there is anything connected to the roughness
            if mat.node_tree.nodes.get("Principled BSDF").inputs[9].links:
                # If there is, connect it to the mix node
                mat.node_tree.links.new(
                    roughness_mix_node.inputs[1], mat.node_tree.nodes.get("Principled BSDF").inputs[9].links[0].from_socket)

                # Disconnect the existing link
                mat.node_tree.links.remove(
                    mat.node_tree.nodes.get("Principled BSDF").inputs[9].links[0])

            # Link the mix node output to the roughness input
            mat.node_tree.links.new(
                mat.node_tree.nodes.get("Principled BSDF").inputs[9], roughness_mix_node.outputs[0])

            # Move the node into the frame
            roughness_mix_node.parent = wet_fx_frame

            roughness_mix_node.location = (-1200, -400)

            #!SECTION

            # --------------------------- #SECTION - Normals --------------------------- #

            # Create a color mix node
            normal_mix_node = mat.node_tree.nodes.new(
                type="ShaderNodeMixRGB")
            normal_mix_node.blend_type = 'MIX'

            # run the attribute node through the factor
            mat.node_tree.links.new(
                normal_mix_node.inputs[0], wetmap_node.outputs[0])

            # Set the secondary mix colour to grey, value 0.25
            normal_mix_node.inputs[2].default_value = (0.25, 0.25, 0.25, 1)

            # Check if there is anything connected to the normals
            if mat.node_tree.nodes.get("Principled BSDF").inputs[22].links:
                # If there is, connect it to the mix node
                mat.node_tree.links.new(
                    normal_mix_node.inputs[1], mat.node_tree.nodes.get("Principled BSDF").inputs[22].links[0].from_socket)

                # Disconnect the existing link
                mat.node_tree.links.remove(
                    mat.node_tree.nodes.get("Principled BSDF").inputs[22].links[0])

            # Link the mix node output to the normals input
            mat.node_tree.links.new(
                mat.node_tree.nodes.get("Principled BSDF").inputs[22], normal_mix_node.outputs[0])

            # Move the node into the frame
            normal_mix_node.parent = wet_fx_frame

            normal_mix_node.location = (-1200, -600)

            #!SECTION

            #!SECTION

        return {'FINISHED'}


class RevertWetFX(bpy.types.Operator):
    bl_idname = "object.revert_wet_fx"
    bl_label = "Revert Wet FX"
    bl_description = "Reverts the effects of the Apply Wet FX operator."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Reverts the effects of the Apply Wet FX operator."""
        # Get all selected mesh objects from the outliner.
        selected_objects = [
            obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        # For each object in the selection, revert the effects of the operator
        for obj in selected_objects:
            # ------------------------- #SECTION - Revert material ------------------------ #

            # If the mesh has a material
            if obj.active_material is not None:
                # Delete the wet material
                bpy.data.materials.remove(obj.active_material)

                # If the original material exists
                if obj.name in ApplyWetFX.original_materials:

                    # Restore the original material
                    obj.data.materials[0] = ApplyWetFX.original_materials[obj.name]

                    # Remove the original material from the list
                    ApplyWetFX.original_materials.pop(obj.name)

                    # Set the original material to the active material
                    obj.active_material = obj.data.materials[0]

            #!SECTION

            # -------------------------- #SECTION - Remove wetmap ------------------------- #
            # Check if there is a wetmap
            if obj.data.vertex_colors.get("dp_wetmap") is not None:
                # If it exists, remove it.
                bpy.ops.dpaint.output_toggle(output='B')

            #!SECTION

            # ------------------------- #SECTION - Revert canvas ------------------------ #
            # Check if there is a dynamic canvas
            if obj.modifiers.get("Dynamic Paint") is not None:
                # Check if there is a canvas surface with name "Wet Layer"
                if obj.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces.get("Wet Layer") is not None:
                    # If it exists, delete it.
                    bpy.ops.dpaint.surface_slot_remove()

                # Delete the dynamic canvas
                bpy.ops.object.modifier_remove(modifier="Dynamic Paint")

            #!SECTION

            # ------------------------ #SECTION - Remove collision ------------------------ #
            # Check if there is a collision modifier
            if obj.modifiers.get("Collision") is not None:
                # If it exists, delete it.
                bpy.ops.object.modifier_remove(modifier="Collision")

            #!SECTION

        return {'FINISHED'}


def draw_menu(self, context):
    """Draw the menu item in the add menu."""
    self.layout.operator(ApplyWetFX.bl_idname, icon="MOD_FLUIDSIM")
    self.layout.operator(RevertWetFX.bl_idname, icon="MOD_FLUIDSIM")


def register():
    """Registers the Apply Wet FX operator."""
    bpy.utils.register_class(ApplyWetFX)
    bpy.utils.register_class(RevertWetFX)
    bpy.types.VIEW3D_MT_add.append(draw_menu)


def unregister():
    """Unregisters the Apply Wet FX operator."""
    bpy.utils.unregister_class(ApplyWetFX)
    bpy.utils.unregister_class(RevertWetFX)
    bpy.types.VIEW3D_MT_add.remove(draw_menu)


if __name__ == "__main__":
    register()
