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
    "name" : "Hardify",
    "author" : "Simon Storl-Schulke",
    "description" : "Shade Object smooth and turn on Autosmooth + Optional Weighted Normals Modifier",
    "version" : (1, 0, 0),
    "blender" : (3, 10, 0),
    "location" : "Object Mode > Select Mesh Object > Object Context menu (Rightclick or W)",
    "warning" : "",
    "doc_url": "https://github.com/SimonStorlSchulke/blender-addons",
    "tracker_url": "https://github.com/SimonStorlSchulke/blender-addons/issues",
    "category" : "Mesh"
}

import bpy
import math

class OT_hardify(bpy.types.Operator):
    bl_idname = "object.hardify"
    bl_label = "Hardify Object"
    bl_description = "Shade Object smooth and turn on Autosmooth + Optional Weighted Normals Modifier"
    bl_options = {"REGISTER", "UNDO"}

    autosmooth_angle: bpy.props.FloatProperty(
        name = "Autosmooth Angle",
        description = "Autosmooth Angle",
        default = 30,
    )

    use_weighted_normal: bpy.props.BoolProperty(
        name = "Use Weighted Normals",
        description = "Use Weighted Normals",
        default = False,
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.object and context.object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(self.autosmooth_angle)

        if self.use_weighted_normal:

            for modifier in bpy.context.object.modifiers:
                if modifier.type == "WEIGHTED_NORMAL":
                    return {"FINISHED"}

            bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')

        return {"FINISHED"}


def add_contextmenu_entry(self, context):
    if context.object is not None and context.object.type == 'MESH':
        layout = self.layout
        layout.operator(OT_hardify.bl_idname, text="Hardify", icon="MOD_NORMALEDIT")


def register():
    bpy.utils.register_class(OT_hardify)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(add_contextmenu_entry)
    
def unregister():
    bpy.utils.unregister_class(OT_hardify)
    bpy.types.VIEW3D_MT_object_context_menu.remove(add_contextmenu_entry)
