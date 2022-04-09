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

bl_info = {
    "name": "Add Lightblocker",
    "author": "Simon Storl-Schulke",
    "description": "Adds a simple Light Blocker with material setup for the selected Light.",
    "version": (1, 0),
    "blender": (3, 10, 0),
    "location": "View3D > Light Context Menu > Add Lightblocker",
    "warning": "",
    "doc_url": "https://github.com/SimonStorlSchulke/blender-addons",
    "tracker_url": "https://github.com/SimonStorlSchulke/blender-addons/issues",
    "category": "Lighting",
}

import bpy

def main(context):
    light = bpy.context.object
    
    # create Plane facing the Light
    bpy.ops.mesh.primitive_plane_add()
    blocker = bpy.context.object
    bpy.ops.object.constraint_add(type='TRACK_TO')
    blocker.constraints["Track To"].track_axis = 'TRACK_Z'
    blocker.constraints["Track To"].up_axis = 'UP_Y'
    blocker.constraints["Track To"].target = light
    blocker.name = "Lightblocker"
    
    if "Lightblocker Addon" not in bpy.data.node_groups:
        create_group()
    create_material(context)


def create_material(context):
    mat = bpy.data.materials.new("Lightblocker")
    mat.use_nodes = True
    mat.shadow_method = "CLIP"
    mat.blend_method = "CLIP"
    mat.diffuse_color[3] = 0.2

    tree = mat.node_tree

    tree.nodes.remove(tree.nodes["Principled BSDF"])
    tree.nodes["Material Output"].location = (500, 0)

    # Setup Nodes
    n_group = tree.nodes.new(type="ShaderNodeGroup")
    n_group.node_tree = bpy.data.node_groups["Lightblocker Addon"]
    n_group.location = (300, 0)

    n_ramp = tree.nodes.new("ShaderNodeValToRGB")
    n_ramp.color_ramp.elements[0].position = 0.4
    n_ramp.color_ramp.elements[1].position = 0.6
    n_ramp.location = (0, 0)


    n_noise = tree.nodes.new("ShaderNodeTexNoise")
    n_noise.noise_dimensions = "2D"
    n_noise.location = (-200, 0)

    # Create Links
    tree.links.new(n_noise.outputs[0], n_ramp.inputs[0])
    tree.links.new(n_ramp.outputs[0], n_group.inputs[0])
    tree.links.new(n_group.outputs[0], tree.nodes["Material Output"].inputs[0])
    
    bpy.context.object.data.materials.append(mat)


def create_group():    
    group = bpy.data.node_groups.new("Lightblocker Addon", "ShaderNodeTree")
    n_inputs = group.nodes.new('NodeGroupInput')
    group.inputs.new('NodeSocketFloat','Transparency')

    n_outputs = group.nodes.new('NodeGroupOutput')
    group.outputs.new('NodeSocketShader','Shader')

    # Create Nodes
    n_lightpath = group.nodes.new('ShaderNodeLightPath')
    n_add = group.nodes.new('ShaderNodeMath')
    n_invert = group.nodes.new('ShaderNodeMath')
    n_invert.operation = "SUBTRACT"
    n_invert.inputs[0].default_value = 1
    n_diffuse = group.nodes.new('ShaderNodeBsdfDiffuse')
    n_transparent = group.nodes.new('ShaderNodeBsdfTransparent')
    n_mix = group.nodes.new('ShaderNodeMixShader')

    # Node Layout
    n_outputs.location = (400,0)
    n_mix.location = (200,0)
    n_diffuse.location = (0,-20)
    n_transparent.location = (0,-150)
    n_add.location = (0,150)
    n_invert.location = (-200,0)
    n_lightpath.location = (-400,0)
    n_inputs.location = (-400,100)

    # Node Links
    group.links.new(n_inputs.outputs[0], n_add.inputs[0])
    group.links.new(n_lightpath.outputs[1], n_invert.inputs[1])
    group.links.new(n_invert.outputs[0], n_add.inputs[1])
    group.links.new(n_diffuse.outputs[0], n_mix.inputs[1])
    group.links.new(n_transparent.outputs[0], n_mix.inputs[2])
    group.links.new(n_add.outputs[0], n_mix.inputs[0])
    group.links.new(n_mix.outputs[0], n_outputs.inputs[0])

    
class OT_add_lightblocker(bpy.types.Operator):
    """Add a simple Light Blocker for the selected Light"""
    bl_idname = "light.addlighblocker"
    bl_label = "Add Light Blocker"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'LIGHT'
    
    def execute(self, context):
        main(context)
        return {'FINISHED'}

def add_contextmenu_entry(self, context):
    if context.object is not None and context.object.type == 'LIGHT':
        layout = self.layout
        layout.operator("light.addlighblocker", text="Add Lightblocker")


def register():
    bpy.utils.register_class(OT_add_lightblocker)
    bpy.types.VIEW3D_MT_object_context_menu.append(add_contextmenu_entry)

def unregister():
    bpy.utils.unregister_class(OT_add_lightblocker)
    bpy.types.VIEW3D_MT_object_context_menu.remove(add_contextmenu_entry)


if __name__ == "__main__":
    register()
