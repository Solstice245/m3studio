# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from . import shared
from . import bl_enum


def register_props():
    bpy.types.Object.m3_materialrefs = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_materialrefs_index = bpy.props.IntProperty(options=set(), default=-1)
    bpy.types.Object.m3_materials_standard = bpy.props.CollectionProperty(type=StandardProperties)
    bpy.types.Object.m3_materials_displacement = bpy.props.CollectionProperty(type=DisplacementProperties)
    bpy.types.Object.m3_materials_composite = bpy.props.CollectionProperty(type=CompositeProperties)
    bpy.types.Object.m3_materials_terrain = bpy.props.CollectionProperty(type=TerrainProperties)
    bpy.types.Object.m3_materials_volume = bpy.props.CollectionProperty(type=VolumeProperties)
    bpy.types.Object.m3_materials_volumenoise = bpy.props.CollectionProperty(type=VolumeNoiseProperties)
    bpy.types.Object.m3_materials_creep = bpy.props.CollectionProperty(type=CreepProperties)
    bpy.types.Object.m3_materials_stb = bpy.props.CollectionProperty(type=SplatTerrainBakeProperties)


class StandardProperties(shared.M3PropertyGroup):
    diff_layer: bpy.props.StringProperty(options=set())
    decal_layer: bpy.props.StringProperty(options=set())
    spec_layer: bpy.props.StringProperty(options=set())
    gloss_layer: bpy.props.StringProperty(options=set())
    emis1_layer: bpy.props.StringProperty(options=set())
    emis2_layer: bpy.props.StringProperty(options=set())
    evio_layer: bpy.props.StringProperty(options=set())
    evio_mask_layer: bpy.props.StringProperty(options=set())
    alpha_mask1_layer: bpy.props.StringProperty(options=set())
    alpha_mask2_layer: bpy.props.StringProperty(options=set())
    norm_layer: bpy.props.StringProperty(options=set())
    height_layer: bpy.props.StringProperty(options=set())
    lightmap_layer: bpy.props.StringProperty(options=set())
    ao_layer: bpy.props.StringProperty(options=set())
    norm_blend_mask1_layer: bpy.props.StringProperty(options=set())
    norm_blend_mask2_layer: bpy.props.StringProperty(options=set())
    norm_blend1_layer: bpy.props.StringProperty(options=set())
    norm_blend2_layer: bpy.props.StringProperty(options=set())

    priority: bpy.props.IntProperty(options=set())
    blend_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_blend)
    layer_blend_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_layer_blend)
    emiss_blend_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_layer_blend)
    spec_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_spec)
    specularity: bpy.props.FloatProperty(options=set(), min=0, default=20)
    depth_blend_falloff: bpy.props.FloatProperty(options=set())
    cutout_threshold: bpy.props.IntProperty(options=set(), subtype='FACTOR', min=0, max=255)

    flag_use_vertex_color: bpy.props.BoolProperty(options=set())
    flag_use_vertex_alpha: bpy.props.BoolProperty(options=set())
    flag_unfogged: bpy.props.BoolProperty(options=set())
    flag_two_sided: bpy.props.BoolProperty(options=set())
    flag_unshaded: bpy.props.BoolProperty(options=set())
    flag_no_shadows_cast: bpy.props.BoolProperty(options=set())
    flag_no_hittest: bpy.props.BoolProperty(options=set())
    flag_no_shadows_recieved: bpy.props.BoolProperty(options=set())
    flag_depth_prepass: bpy.props.BoolProperty(options=set())
    flag_terrain_hdr: bpy.props.BoolProperty(options=set())
    flag_simulate_roughness: bpy.props.BoolProperty(options=set())
    flag_pixel_forward_lighting: bpy.props.BoolProperty(options=set())
    flag_depth_fog: bpy.props.BoolProperty(options=set())
    flag_transparent_shadows: bpy.props.BoolProperty(options=set())
    flag_decal_lighting: bpy.props.BoolProperty(options=set())
    flag_transparent_depth: bpy.props.BoolProperty(options=set())
    flag_transparent_local_lights: bpy.props.BoolProperty(options=set())
    flag_disable_soft: bpy.props.BoolProperty(options=set())
    flag_double_lambert: bpy.props.BoolProperty(options=set())
    flag_hair_layer_sorting: bpy.props.BoolProperty(options=set())
    flag_accept_splats: bpy.props.BoolProperty(options=set())
    flag_decal_required: bpy.props.BoolProperty(options=set())
    flag_emissive_required: bpy.props.BoolProperty(options=set())
    flag_specular_required: bpy.props.BoolProperty(options=set())
    flag_accept_splats_only: bpy.props.BoolProperty(options=set())
    flag_background_object: bpy.props.BoolProperty(options=set())
    flag_fill_required: bpy.props.BoolProperty(options=set())
    flag_exclude_from_highlighting: bpy.props.BoolProperty(options=set())
    flag_clamp_output: bpy.props.BoolProperty(options=set())
    flag_geometry_visible: bpy.props.BoolProperty(options=set())


class DisplacementProperties(shared.M3PropertyGroup):
    norm_layer: bpy.props.StringProperty(options=set())
    strength_layer: bpy.props.StringProperty(options=set())

    priority: bpy.props.IntProperty(options=set())
    strength_factor: bpy.props.FloatProperty(name='Distortion Factor')


class CompositeSectionProperties(shared.M3PropertyGroup):
    name: bpy.props.StringProperty(options=set())
    material_reference: bpy.props.StringProperty(options=set())
    alpha_factor: bpy.props.FloatProperty(name='Alpha Factor')


class CompositeProperties(shared.M3PropertyGroup):
    sections: bpy.props.CollectionProperty(type=CompositeSectionProperties)


class TerrainProperties(shared.M3PropertyGroup):
    terrain_layer: bpy.props.StringProperty(options=set())


class VolumeProperties(shared.M3PropertyGroup):
    color_layer: bpy.props.StringProperty(options=set())
    unknown_layer1: bpy.props.StringProperty(options=set())
    unknown_layer2: bpy.props.StringProperty(options=set())
    density: bpy.props.FloatProperty(name='Density')


class VolumeNoiseProperties(shared.M3PropertyGroup):
    color_layer: bpy.props.StringProperty(options=set())
    noise1_layer: bpy.props.StringProperty(options=set())
    noise2_layer: bpy.props.StringProperty(options=set())
    density: bpy.props.FloatProperty(name='Density')
    near_plane: bpy.props.FloatProperty(name='Near Plane')
    falloff: bpy.props.FloatProperty(name='Falloff')
    scroll_rate: bpy.props.FloatVectorProperty(name='Scroll Rate', size=3, subtype='XYZ')
    translation: bpy.props.FloatVectorProperty(name='Translation', size=3, subtype='XYZ')
    rotation: bpy.props.FloatVectorProperty(name='Rotations', size=3, subtype='XYZ')
    scale: bpy.props.FloatVectorProperty(name='Scale', size=3, subtype='XYZ')
    alpha_threshold: bpy.props.IntProperty(options=set())
    flag_draw_after_transparency: bpy.props.BoolProperty(options=set())


class CreepProperties(shared.M3PropertyGroup):
    creep_layer: bpy.props.StringProperty(options=set())


class SplatTerrainBakeProperties(shared.M3PropertyGroup):
    diff_layer: bpy.props.StringProperty(options=set())
    norm_layer: bpy.props.StringProperty(options=set())
    spec_layer: bpy.props.StringProperty(options=set())


def draw_props(material, context):
    pass


class Properties(shared.M3PropertyGroup):
    material_type: bpy.props.IntProperty(options=set(), default=-1)
    material_index: bpy.props.IntProperty(options=set(), default=-1)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_MATERIALS'
    bl_label = 'M3 Materials'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_materialrefs', draw_props)


classes = (
    StandardProperties,
    DisplacementProperties,
    CompositeSectionProperties,
    CompositeProperties,
    TerrainProperties,
    VolumeProperties,
    VolumeNoiseProperties,
    CreepProperties,
    SplatTerrainBakeProperties,
    Properties,
    Panel,
)
