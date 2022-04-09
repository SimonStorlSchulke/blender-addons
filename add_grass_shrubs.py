# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import bmesh
import math
import mathutils
import random

bl_info = {
    "name" : "Grass Shrub Generator",
    "description" : "Creates a Collection of customizable grass shrubs for use in particle systems.",
    "author" : "Simon Storl-Schulke ",
    "version" : (1, 0, 0),
    "blender" : (3, 10, 0),
    "location": "View3D > Add > Mesh",
    "doc_url": "https://github.com/SimonStorlSchulke/blender-addons",
    "tracker_url": "https://github.com/SimonStorlSchulke/blender-addons/issues",
    "category" : "Add Mesh",
}


def map_range(v, from_min, from_max, to_min, to_max):
    """Maps a value v from an old scale (from_min, from_max)to a new scale (to_min, to_max)"""
    return to_min + (v - from_min) * (to_max - to_min) / (from_max - from_min)


class GRASSSHRUBGENERATOR_OT_add_grass_shrubs(bpy.types.Operator):
    bl_idname = "grassshrubgenerator.add_gras_shrubs"
    bl_label = "Grass Shrubs"
    bl_description = "Add a collection of random Grass Shrubs for use in particle systems"
    bl_options = {"REGISTER", "UNDO"}

    AMMOUNT: bpy.props.IntProperty(name="Shrubs Ammount", default=1, min=1, max=25)
    BLADES: bpy.props.IntProperty(name="Blades", default=8, min=1, max=50)
    SPREAD: bpy.props.FloatProperty(name="Spread", default=0.1, min=0)
    WIDTH_EXPONENT: bpy.props.FloatProperty(name="Width Exponent", default=0.8, min=0)
    RANDOM_BLADE_ROT: bpy.props.FloatProperty(name="Random Blade Rotation", default=25)

    WIDTH_BASE: bpy.props.FloatProperty(name="Base Width", default=0.01, min=0)
    WIDTH_TIP: bpy.props.FloatProperty(name="Tip Width", default=0, min=0)

    HEIGHT_MIN: bpy.props.FloatProperty(name="Meight Min", default=0.05, min=0)
    HEIGHT_MAX: bpy.props.FloatProperty(name="Height Max", default=0.15, min=0)
    RESOLUTION: bpy.props.IntProperty(name="resolution", default = 10)

    ROT_BASE_MIN: bpy.props.FloatProperty(name="Rotation Base Min", default=3, min=0)
    ROT_BASE_MAX: bpy.props.FloatProperty(name="Rotation Base Max", default=25, min=0)
    ROT_TIP_MIN: bpy.props.FloatProperty(name="Rotation Tip Min", default=30, min=0)
    ROT_TIP_MAX: bpy.props.FloatProperty(name="Rotation Tip Max", default=90, min=0)
    ROT_FALLOFF: bpy.props.FloatProperty(name="Rotation Falloff", default=5, min=0.01)

    SEED: bpy.props.IntProperty(name="Seed")

    def generate_shrub(self) -> bpy.types.Object:

        grass_mesh = bpy.data.meshes.new("grass_shrub_mesh")
        grass_object = bpy.data.objects.new("grass shrub", grass_mesh)

        bm = bmesh.new()
        bm.from_mesh(grass_mesh)
        uv_layer = bm.loops.layers.uv.new()

        for i in range(self.BLADES):
            blade_height = random.uniform(self.HEIGHT_MIN, self.HEIGHT_MAX)
            blade_res = int(self.RESOLUTION * 10 * blade_height)
            c_blade = []

            c_rot_base = random.uniform(self.ROT_BASE_MIN, self.ROT_BASE_MAX)
            c_rot_tip = random.uniform(self.ROT_TIP_MIN, self.ROT_TIP_MAX)

            last_vert_1 = None
            last_vert_2 = None

            for i in range(blade_res):
                progress = i / (blade_res-1)
                gradient = math.pow(progress, self.WIDTH_EXPONENT)

                pos_x = map_range(gradient, 0, 1, self.WIDTH_BASE, self.WIDTH_TIP)
                pos_y = progress * blade_height
                
                vert_1: bmesh.types.BMVert = bm.verts.new((-pos_x, 0, pos_y))
                vert_2: bmesh.types.BMVert = bm.verts.new((pos_x, 0, pos_y))

                # Rotate blade verts more the further at the top they are
                rot_angle = map_range(math.pow(progress, self.ROT_FALLOFF), 0, 1, c_rot_base, c_rot_tip)
                rot_matrix = mathutils.Matrix.Rotation(math.radians(rot_angle), 4, 'X')
                bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=rot_matrix, verts=[vert_1, vert_2])
                
                # Don't generate Polygon at first iteration (only 2 verts exist then)
                if i != 0:
                    face = bm.faces.new((last_vert_1,last_vert_2,vert_2,vert_1))
                    face.smooth = True

                    # Generate UVs per face deoending on current vertex index
                    for i_vert, vert in enumerate(face.loops):
                        vert[uv_layer].uv = ((i_vert==0 or i_vert==3), (i-(i_vert<2)) / blade_res)

                c_blade.append(vert_1)
                c_blade.append(vert_2)
                last_vert_1 = vert_1
                last_vert_2 = vert_2

            # random offset per blade
            offset: mathutils.Vector = mathutils.Vector((random.uniform(-1,1), random.uniform(-1,1), 0))
            offset = offset.normalized() * random.uniform(0, self.SPREAD)

            # alignrotation to offset + random
            blade_rotation: mathutils.Quaternion = offset.normalized().to_track_quat("-Y", "Z")
            random_z_angle = random.uniform(-self.RANDOM_BLADE_ROT, self.RANDOM_BLADE_ROT)
            blade_rotation.rotate(mathutils.Euler((0, 0, -math.radians(random_z_angle))))

            bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix = blade_rotation.to_matrix(), verts=c_blade)
            bmesh.ops.translate(bm, vec=offset, verts=c_blade)

        bm.to_mesh(grass_mesh)
        bm.free()
        return grass_object

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        random.seed(self.SEED)
        grass_collection: bpy.types.Collection
        if "Grass Shrubs" in bpy.data.collections:
            grass_collection = bpy.data.collections["Grass Shrubs"]
        else:
            grass_collection = bpy.data.collections.new("Grass Shrubs")
         
        try:
            bpy.context.scene.collection.children.link(grass_collection)
        except:
            ... # collction already linked

        for i in range(self.AMMOUNT):
            c_shrub: bpy.types.Object = self.generate_shrub()
            grass_collection.objects.link(c_shrub)
            c_shrub.location.x = (i-(self.AMMOUNT-1)/2) * self.SPREAD * 3

        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(GRASSSHRUBGENERATOR_OT_add_grass_shrubs.bl_idname, icon='OUTLINER_OB_HAIR')

def register():
    bpy.utils.register_class(GRASSSHRUBGENERATOR_OT_add_grass_shrubs)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(GRASSSHRUBGENERATOR_OT_add_grass_shrubs)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)