"""
A Blender addon that generates procedural clouds.
"""

import random
import bpy

bl_info = {
    "name": "Generate Clouds",
    "blender": (2, 80, 0),  # Minimum Blender version required
    "category": "Object",
    "author": "Rhylei Tremlett",
    "description": "Generates procedural clouds.",
    "version": (0, 0, 6),
    "location": "View3D > Add",  # "View3D > Add > Mesh",
    "doc_url": "https://github.com/KyrVorga/CGI605-Project",
    "tracker_url": "https://github.com/KyrVorga/CGI605-Project/issues",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/KyrVorga/CGI605-Project/wiki",
    "warning": "This addon is still under development.",
}


class GenerateCloud(bpy.types.Operator):
    bl_idname = "object.generate_cloud"
    bl_label = "Generate Cloud"
    bl_description = "Generates procedural clouds."
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def execute(self, context):
        """Generates a procedural cloud."""

        # ------------------- #SECTION - Cloud Anchor ------------------ #
        # Create an empty object to be used as the cloud anchor
        # The anchor is used as a reference point for the cloud and its volume
        # It allows the clouds to change shape as they move
        cloud_anchor = None

        # Check if there is already a cloud anchor
        if "Cloud Anchor" in bpy.data.objects:
            # If there is, set the cloud anchor to the existing object
            cloud_anchor = bpy.data.objects["Cloud Anchor"]
        else:
            # Create an emtpy object at the world origin
            bpy.ops.object.empty_add(
                type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            cloud_anchor = bpy.context.active_object
            cloud_anchor.name = "Cloud Anchor"

            # Make the cloud anchor hidden
            cloud_anchor.hide_viewport = True
            cloud_anchor.hide_render = True

        # Get the location of the cursor
        cursor_location = context.scene.cursor.location.copy()

        #!SECTION

        # ------------------- #SECTION - Collection ------------------ #
        # Create a cloud collection with a unique name using a random hex value
        collection_name = "Cloud Collection " + \
            str(hex(random.randint(0, 1000000)))
        cloud_collection = bpy.data.collections.new(collection_name)

        # Set the cloud collection to be the active collection
        bpy.context.scene.collection.children.link(cloud_collection)
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[
            collection_name]

        # ------------------- #SECTION - Cloud Mesh ------------------ #
        # Add a icospere at the cursor
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=1, enter_editmode=False, align='WORLD', location=cursor_location, scale=(1, 1, 1))

        # Set the name of the icosphere
        cloud_obj = bpy.context.active_object
        cloud_obj.name = "Cloud"

        # Set shading to smooth
        bpy.ops.object.shade_smooth()

        # Scale up the cloud to 5x its original size
        # Set each axis to bewtween 4 and 6
        cloud_obj.scale = (
            random.uniform(4, 6), random.uniform(4, 6), random.uniform(4, 6)
        )

        #!SECTION

        # ------------------- #SECTION - Displace Modifier ------------------ #
        # Add a displace modifier to the cloud
        cloud_obj.modifiers.new(name="Displace", type='DISPLACE')

        # Configure the displace modifier to use a cloud texture and set the object to the empty anchor point.
        # Check if the cloud texture already exists
        if "Cloud Texture" in bpy.data.textures:
            # If it does, set the texture to the cloud texture
            cloud_obj.modifiers["Displace"].texture = bpy.data.textures["Cloud Texture"]
        else:
            # Create a new texture for the cloud
            cloud_obj.modifiers["Displace"].texture = bpy.data.textures.new(
                name="Cloud Texture", type='CLOUDS')

        # Set the colour to RGB
        cloud_obj.modifiers["Displace"].texture.cloud_type = 'COLOR'

        # Set the noise depth to 0 and scale to 0.75
        cloud_obj.modifiers["Displace"].texture.noise_depth = 0
        cloud_obj.modifiers["Displace"].texture.noise_scale = 0.75

        # Set the displace strencth to 2.5
        cloud_obj.modifiers["Displace"].strength = 2.5

        # Set the displace texture to use the empty object as the anchor point
        cloud_obj.modifiers["Displace"].texture_coords = 'OBJECT'
        cloud_obj.modifiers["Displace"].texture_coords_object = cloud_anchor

        #!SECTION

        # ------------------- #SECTION - Subdivision Modifier ------------------ #
        # Add a subsurf modifier to the cloud
        cloud_obj.modifiers.new(name="Subdivision", type='SUBSURF')
        cloud_obj.modifiers["Subdivision"].levels = 2
        cloud_obj.modifiers["Subdivision"].render_levels = 2
        cloud_obj.modifiers["Subdivision"].subdivision_type = 'CATMULL_CLARK'

        #!SECTION

        # ------------------- #SECTION - Deform Modifier ------------------ #
        # Add a simple deform modifier to the cloud, set it to stretch negativley on the z axis
        cloud_obj.modifiers.new(name="Deform", type='SIMPLE_DEFORM')
        cloud_obj.modifiers["Deform"].deform_method = 'STRETCH'
        cloud_obj.modifiers["Deform"].deform_axis = 'Z'
        # Set the factor to random between -0.3 and -0.7
        cloud_obj.modifiers["Deform"].factor = random.uniform(-0.3, -0.7)

        #!SECTION

        # ------------------- #SECTION - Cloud Volume Setup ------------------ #
        # Create an emtpy volume object
        bpy.ops.object.volume_add(
            align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        volume_obj = bpy.context.active_object
        volume_obj.name = "Cloud Volume"

        # Add a mesh to volume modifier to the volume object
        volume_obj.modifiers.new(name="Mesh to Volume", type='MESH_TO_VOLUME')

        # Set the voxel count to 128
        volume_obj.modifiers["Mesh to Volume"].voxel_amount = 128

        # Set the mesh to volume modifier to use the cloud object
        volume_obj.modifiers["Mesh to Volume"].object = cloud_obj

        # Add a volume displace modifier to the volume object
        volume_obj.modifiers.new(
            name="Volume Displace", type='VOLUME_DISPLACE')

        # Set the displacement texture to use the cloud texture
        volume_obj.modifiers["Volume Displace"].texture = bpy.data.textures["Cloud Texture"]

        # Set the displacement strength to 1
        volume_obj.modifiers["Volume Displace"].strength = 1

        #!SECTION

        # ------------------- #SECTION - Cloud Movement Anchor ------------------ #
        # Create an empty object to be used as the movement anchor
        # The movement anchor allows the cloud to move easily
        bpy.ops.object.empty_add(
            type='PLAIN_AXES', align='WORLD', location=cursor_location, scale=(1, 1, 1))
        movement_anchor = bpy.context.active_object
        movement_anchor.name = "Movement Anchor"

        # Bind the location of the cloud objects to the movement anchor
        cloud_obj.constraints.new(type='COPY_LOCATION')
        cloud_obj.constraints["Copy Location"].target = movement_anchor
        cloud_obj.constraints["Copy Location"].use_x = True
        cloud_obj.constraints["Copy Location"].use_y = True
        cloud_obj.constraints["Copy Location"].use_z = True

        volume_obj.constraints.new(type='COPY_LOCATION')
        volume_obj.constraints["Copy Location"].target = movement_anchor
        volume_obj.constraints["Copy Location"].use_x = True
        volume_obj.constraints["Copy Location"].use_y = True
        volume_obj.constraints["Copy Location"].use_z = True

        # Set the original collection to be the active collection
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[
            "Collection"]

        return {'FINISHED'}

        #!SECTION


def draw_menu(self, context):
    """Draws the menu in the Add > Mesh menu."""
    self.layout.operator(GenerateCloud.bl_idname, icon="MOD_FLUIDSIM")


def register():
    """Registers the addon."""
    bpy.utils.register_class(GenerateCloud)
    bpy.types.VIEW3D_MT_add.append(draw_menu)


def unregister():
    """Unregisters the addon."""
    bpy.utils.unregister_class(GenerateCloud)
    bpy.types.VIEW3D_MT_add.remove(draw_menu)


if __name__ == "__main__":
    register()
