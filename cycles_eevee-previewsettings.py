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
    "version": (1, 1, 0),
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



def draw_material_settings(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    mat = context.material

    layout.prop(mat, "use_backface_culling")
    layout.prop(mat, "blend_method")
    layout.prop(mat, "shadow_method")

    row = layout.row()
    row.active = ((mat.blend_method == 'CLIP') or (mat.shadow_method == 'CLIP'))
    row.prop(mat, "alpha_threshold")

    if mat.blend_method not in {'OPAQUE', 'CLIP', 'HASHED'}:
        layout.prop(mat, "show_transparent_back")

    layout.prop(mat, "use_screen_refraction")
    layout.prop(mat, "refraction_depth")
    layout.prop(mat, "use_sss_translucency")
    layout.prop(mat, "pass_index")


class materialSettingsPanel(bpy.types.Panel):

    bl_label = "Material Preview Settings"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        mat = context.material
        return mat and context.engine == "CYCLES"

class EEVEE_MATERIAL_PT_viewport_settings(materialSettingsPanel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_parent_id = "MATERIAL_PT_viewport"

    def draw(self, context):
        draw_material_settings(self, context)

class EEVEE_MATERIAL_PT_viewport_settings_Node_Editor(materialSettingsPanel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Options"
    #bl_parent_id = "MATERIAL_PT_viewport" - throws an Error (parent not found) because somehow the Viewport Display Panel is only defined for the Properties space type(?)

    def draw(self, context):
        draw_material_settings(self, context)


def register():
    bpy.utils.register_class(PREVIEWSETTINGS_PT_panel)
    bpy.utils.register_class(EEVEE_MATERIAL_PT_viewport_settings)
    bpy.utils.register_class(EEVEE_MATERIAL_PT_viewport_settings_Node_Editor)

    
def unregister():
    bpy.utils.unregister_class(PREVIEWSETTINGS_PT_panel)
    bpy.utils.unregister_class(EEVEE_MATERIAL_PT_viewport_settings)
    bpy.utils.unregister_class(EEVEE_MATERIAL_PT_viewport_settings_Node_Editor)

if __name__ == "__main__":
    register()
