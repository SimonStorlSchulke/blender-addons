# Blender Previewsettings Add-on
# Contributor(s): Simon Storl-Schulke (github.com/SimonStorlSchulke)
#
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
    "name": "Previewsettings",
    "description": "When using Cycles, displays the most relevant Eevee settings for the Material Preview in the Viewport Shading Menu",
    "author": "Simon Storl-Schulke",
    "version": (1, 0, 0),
    "blender": (3, 2, 2),
    "location": "View3D → Header → Material Preview Shading Foldout-Menu",
    "category": "Interface" }
    

import bpy

class PREVIEWSETTINGS_PT_panel(bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_shading"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Preview Rendersettings"

    @classmethod
    def poll(cls, context):
        view = context.space_data
        if view.type == 'VIEW_3D':
            return view.shading.type == "MATERIAL" and context.scene.render.engine == "CYCLES"
        else:
            return context.scene.display.shading.type == "MATERIAL" and context.scene.render.engine == "CYCLES"


    def draw(self, context):

        layout: bpy.types.UILayout = self.layout
        props: bpy.types.SceneEEVEE = context.scene.eevee
        
        layout.prop(props, "taa_samples")
        layout.prop(props, "use_bloom")
        layout.prop(props, "bloom_intensity", text="Bloom Intensity")
        layout.prop(props, "bloom_radius", text="Bloom Radius")
        layout.prop(props, "use_gtao")
        layout.prop(props, "gtao_distance", text="AO Distance")
        layout.prop(props, "gtao_factor", text="AO Factor")
        layout.prop(props, "use_ssr")
        layout.prop(props, "use_ssr_refraction")
        layout.prop(props, "volumetric_start", text="Volumetric Start")
        layout.prop(props, "volumetric_end", text="Volumetric End")
        layout.prop(props, "volumetric_tile_size", text="Tile Size")
        layout.prop(props, "use_volumetric_lights")
        layout.prop(props, "use_volumetric_shadows")

def register():
    bpy.utils.register_class(PREVIEWSETTINGS_PT_panel)
    
def unregister():
    bpy.utils.unregister_class(PREVIEWSETTINGS_PT_panel)
