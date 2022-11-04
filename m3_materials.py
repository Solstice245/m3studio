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
    bpy.types.Object.m3_materials_reflection = bpy.props.CollectionProperty(type=ReflectionProperties)
    bpy.types.Object.m3_materials_lensflare = bpy.props.CollectionProperty(type=LensFlareProperties)
    bpy.types.Object.m3_material_ref = bpy.props.StringProperty(options=set())


def init_msgbus(ob, context):
    for matref in ob.m3_materialrefs:
        mat = m3_material_get(ob, matref)
        shared.m3_msgbus_sub(mat, matref, 'name', 'name')


class StandardProperties(shared.M3PropertyGroup):
    layer_diff: bpy.props.StringProperty(options=set())
    layer_decal: bpy.props.StringProperty(options=set())
    layer_spec: bpy.props.StringProperty(options=set())
    layer_gloss: bpy.props.StringProperty(options=set())
    layer_emis1: bpy.props.StringProperty(options=set())
    layer_emis2: bpy.props.StringProperty(options=set())
    layer_envi: bpy.props.StringProperty(options=set())
    layer_envi_mask: bpy.props.StringProperty(options=set())
    layer_alpha1: bpy.props.StringProperty(options=set())
    layer_alpha2: bpy.props.StringProperty(options=set())
    layer_norm: bpy.props.StringProperty(options=set())
    layer_height: bpy.props.StringProperty(options=set())
    layer_light: bpy.props.StringProperty(options=set())
    layer_ao: bpy.props.StringProperty(options=set())
    layer_norm_blend1_mask: bpy.props.StringProperty(options=set())
    layer_norm_blend2_mask: bpy.props.StringProperty(options=set())
    layer_norm_blend1: bpy.props.StringProperty(options=set())
    layer_norm_blend2: bpy.props.StringProperty(options=set())

    priority: bpy.props.IntProperty(options=set())
    blend_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_blend)
    layr_blend_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_layer_blend)
    emis_blend_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_layer_blend)
    emis_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_layer_blend)
    spec_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_spec)
    specularity: bpy.props.FloatProperty(options=set(), min=0, default=20)
    depth_blend_falloff: bpy.props.FloatProperty(options=set())
    cutout_threshold: bpy.props.IntProperty(options=set(), subtype='FACTOR', min=0, max=255)
    emis_multiply: bpy.props.FloatProperty(options=set(), min=0, default=1)
    spec_multiply: bpy.props.FloatProperty(options=set(), min=0, default=1)
    envi_const_multiply: bpy.props.FloatProperty(options=set(), min=0, default=1)
    envi_diff_multiply: bpy.props.FloatProperty(options=set(), min=0, default=0)
    envi_spec_multiply: bpy.props.FloatProperty(options=set(), min=0, default=0)

    vertex_color: bpy.props.BoolProperty(options=set())
    vertex_alpha: bpy.props.BoolProperty(options=set())
    unfogged: bpy.props.BoolProperty(options=set())
    two_sided: bpy.props.BoolProperty(options=set())
    unshaded: bpy.props.BoolProperty(options=set())
    no_shadows_cast: bpy.props.BoolProperty(options=set())
    no_hittest: bpy.props.BoolProperty(options=set())
    no_shadows_receive: bpy.props.BoolProperty(options=set())
    depth_prepass: bpy.props.BoolProperty(options=set())
    terrain_hdr: bpy.props.BoolProperty(options=set())
    unknown0x400: bpy.props.BoolProperty(options=set())
    simulate_roughness: bpy.props.BoolProperty(options=set())
    pixel_forward_lighting: bpy.props.BoolProperty(options=set())
    depth_fog: bpy.props.BoolProperty(options=set())
    transparent_shadows: bpy.props.BoolProperty(options=set())
    decal_lighting: bpy.props.BoolProperty(options=set())
    transparent_depth: bpy.props.BoolProperty(options=set())
    transparent_local_lights: bpy.props.BoolProperty(options=set())
    disable_soft: bpy.props.BoolProperty(options=set())
    double_lambert: bpy.props.BoolProperty(options=set())
    hair_layer_sorting: bpy.props.BoolProperty(options=set())
    accept_splats: bpy.props.BoolProperty(options=set())
    decal_required: bpy.props.BoolProperty(options=set())
    emis_required: bpy.props.BoolProperty(options=set())
    spec_required: bpy.props.BoolProperty(options=set())
    accept_splats_only: bpy.props.BoolProperty(options=set())
    background_object: bpy.props.BoolProperty(options=set())
    unknown0x8000000: bpy.props.BoolProperty(options=set())
    fill_required: bpy.props.BoolProperty(options=set())
    no_highlighting: bpy.props.BoolProperty(options=set())
    clamp_output: bpy.props.BoolProperty(options=set())
    geometry_visible: bpy.props.BoolProperty(options=set())


class DisplacementProperties(shared.M3PropertyGroup):
    layer_norm: bpy.props.StringProperty(options=set())
    layer_strength: bpy.props.StringProperty(options=set())
    priority: bpy.props.IntProperty(options=set())
    strength_factor: bpy.props.FloatProperty(name='Distortion Factor')


class CompositeSectionProperties(shared.M3PropertyGroup):
    name: bpy.props.StringProperty(options=set())
    matref: bpy.props.StringProperty(options=set())
    alpha_factor: bpy.props.FloatProperty(name='Alpha Factor', default=1)


class CompositeProperties(shared.M3PropertyGroup):
    sections: bpy.props.CollectionProperty(type=CompositeSectionProperties)
    sections_index: bpy.props.IntProperty(options=set(), default=-1)
    unknown: bpy.props.IntProperty(options=set(), min=0)


class TerrainProperties(shared.M3PropertyGroup):
    layer_terrain: bpy.props.StringProperty(options=set())


class VolumeProperties(shared.M3PropertyGroup):
    layer_color: bpy.props.StringProperty(options=set())
    layer_unknown1: bpy.props.StringProperty(options=set())
    layer_unknown2: bpy.props.StringProperty(options=set())
    density: bpy.props.FloatProperty(name='Density')


class VolumeNoiseProperties(shared.M3PropertyGroup):
    layer_color: bpy.props.StringProperty(options=set())
    layer_noise1: bpy.props.StringProperty(options=set())
    layer_noise2: bpy.props.StringProperty(options=set())
    density: bpy.props.FloatProperty(name='Density')
    near_plane: bpy.props.FloatProperty(name='Near Plane')
    falloff: bpy.props.FloatProperty(name='Falloff')
    scroll_rate: bpy.props.FloatVectorProperty(name='Scroll Rate', size=3, subtype='XYZ')
    translation: bpy.props.FloatVectorProperty(name='Translation', size=3, subtype='XYZ')
    rotation: bpy.props.FloatVectorProperty(name='Rotations', size=3, subtype='XYZ')
    scale: bpy.props.FloatVectorProperty(name='Scale', size=3, subtype='XYZ')
    alpha_threshold: bpy.props.IntProperty(options=set())
    draw_after_transparency: bpy.props.BoolProperty(options=set())


class CreepProperties(shared.M3PropertyGroup):
    layer_creep: bpy.props.StringProperty(options=set())


class SplatTerrainBakeProperties(shared.M3PropertyGroup):
    layer_diff: bpy.props.StringProperty(options=set())
    layer_norm: bpy.props.StringProperty(options=set())
    layer_spec: bpy.props.StringProperty(options=set())


class ReflectionProperties(shared.M3PropertyGroup):
    layer_norm: bpy.props.StringProperty(options=set())
    layer_strength: bpy.props.StringProperty(options=set())
    layer_blur: bpy.props.StringProperty(options=set())
    blur_angle: bpy.props.FloatProperty(name='Blur Angle')
    blur_distance: bpy.props.FloatProperty(name='Blur Distance', default=2)
    reflection_offset: bpy.props.FloatProperty(name='Reflection Offset')
    reflection_strength: bpy.props.FloatProperty(name='Reflection Strength', default=1)
    displacement_strength: bpy.props.FloatProperty(name='Displacement Strength', default=1)
    use_layer_norm: bpy.props.BoolProperty(options=set())
    use_layer_strength: bpy.props.BoolProperty(options=set())
    blurring: bpy.props.BoolProperty(options=set())
    use_layer_blur: bpy.props.BoolProperty(options=set())
    render_transparent_pass: bpy.props.BoolProperty(options=set())


class LensFlareStarburstProperties(shared.M3PropertyGroup):
    uv_index: bpy.props.IntProperty(options=set(), min=0)
    distance_factor: bpy.props.FloatProperty(options=set(), default=1)
    width: bpy.props.FloatProperty(options=set(), min=0, default=500)
    height: bpy.props.FloatProperty(options=set(), min=0, default=100)
    width_falloff: bpy.props.FloatProperty(options=set(), min=0, default=750)
    height_falloff: bpy.props.FloatProperty(options=set(), min=0, default=150)
    falloff_threshold: bpy.props.FloatProperty(options=set(), min=0)
    falloff_rate: bpy.props.FloatProperty(options=set(), min=0, default=1)
    color: bpy.props.FloatVectorProperty(options=set(), subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    face_source: bpy.props.BoolProperty(options=set())


class LensFlareProperties(shared.M3PropertyGroup):
    layer_color: bpy.props.StringProperty(options=set())
    layer_unknown: bpy.props.StringProperty(options=set())
    starbursts: bpy.props.CollectionProperty(type=LensFlareStarburstProperties)
    starbursts_index: bpy.props.IntProperty(options=set(), default=-1)
    uv_columns: bpy.props.IntProperty(options=set(), min=0)
    uv_rows: bpy.props.IntProperty(options=set(), min=0)
    render_distance: bpy.props.FloatProperty(options=set(), min=0)
    intensity: bpy.props.FloatProperty(name='Intensity', min=0)
    intensity2: bpy.props.FloatProperty(name='Intensity 2', min=0)
    uniform_scale: bpy.props.FloatProperty(name='Uniform Scale', min=0, default=1)
    color: bpy.props.FloatVectorProperty(name='Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))


def m3_material_get(ob, matref):
    mat = None
    if matref.mat_handle:
        mat_col = getattr(ob, matref.mat_type)
        for item in mat_col:
            if item.bl_handle == matref.mat_handle:
                mat = item
    return mat


def m3_material_layer_get(ob, handle):
    for layer in ob.m3_materiallayers:
        if layer.bl_handle == handle:
            return layer
    return None


def layer_enum(self, context):
    return [(layer.bl_handle, layer.name, '') for layer in context.object.m3_materiallayers]


def draw_layer_pointer_prop(ob, layout, material, layer_name, label='test'):
    col = layout.column(align=True)
    col.use_property_split = False
    split = col.split(factor=0.375, align=True)
    row = split.row(align=True)
    row.alignment = 'RIGHT'
    row.label(text=label)
    row = split.row(align=True)
    op = row.operator('m3.material_layer_search', text='', icon='VIEWZOOM')
    op.layer_name = layer_name
    layer = m3_material_layer_get(ob, getattr(material, layer_name))
    if layer:
        row.prop(layer, 'name', text='', icon='NODE_COMPOSITING')
        op = row.operator('m3.material_layer_add', text='', icon='DUPLICATE')
        op.layer_name = layer_name
        op = row.operator('m3.material_layer_unlink', text='', icon='X')
        op.layer_name = layer_name
    else:
        op = row.operator('m3.material_layer_add', text='New', icon='ADD')
        op.layer_name = layer_name


def draw_standard_props(context, material, layout):
    draw_layer_pointer_prop(context.object, layout, material, 'layer_diff', 'Diffuse')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_decal', 'Decal')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_spec', 'Specular')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_gloss', 'Gloss')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_emis1', 'Emissive 1')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_emis2', 'Emissive 2')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_envi', 'Environment')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_envi_mask', 'Environment Mask')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_alpha1', 'Alpha Mask 1')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_alpha2', 'Alpha Mask 2')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_norm', 'Normal')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_height', 'Height')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_light', 'Light')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_ao', 'Ambient Occlusion')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_norm_blend1_mask', 'Normal Blend 1 Mask')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_norm_blend2_mask', 'Normal Blend 2 Mask')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_norm_blend1', 'Normal Blend 1')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_norm_blend2', 'Normal Blend 2')
    layout.separator()
    col = layout.column()
    col.prop(material, 'blend_mode', text='Blend Mode')
    col.prop(material, 'layr_blend_mode', text='Layering Mode')
    col.prop(material, 'cutout_threshold', text='Cutout Threshold')
    col.prop(material, 'depth_blend_falloff', text='Depth Blend')
    col.prop(material, 'priority', text='Priority')
    col.separator()
    col.prop(material, 'emis_blend_mode', text='Emissive Mode')
    col.prop(material, 'emis_multiply', text='Multiplier')
    col.separator()
    col.prop(material, 'spec_mode', text='Specular Mode Mode')
    col.prop(material, 'specularity', text='Specularity')
    col.prop(material, 'spec_multiply', text='Multiply')
    col.separator()
    col = layout.column(align=True)
    col.prop(material, 'envi_const_multiply', text='Environment Multiply')
    col.prop(material, 'envi_diff_multiply', text='Diffuse')
    col.prop(material, 'envi_spec_multiply', text='Specular')
    col.separator()
    col = layout.column_flow(align=True, columns=2)
    col.use_property_split = False
    col.prop(material, 'vertex_color', text='Vertex Color')
    col.prop(material, 'vertex_alpha', text='Vertex Alpha')
    col.prop(material, 'unfogged', text='Fogged', invert_checkbox=True)
    col.prop(material, 'two_sided', text='Two Sided')
    col.prop(material, 'unshaded', text='Shaded', invert_checkbox=True)
    col.prop(material, 'no_shadows_cast', text='Cast Shadows', invert_checkbox=True)
    col.prop(material, 'no_shadows_receive', text='Recieve Shadows', invert_checkbox=True)
    col.prop(material, 'no_hittest', text='Hit Test', invert_checkbox=True)
    col.prop(material, 'depth_prepass', text='Depth Prepass')
    col.prop(material, 'terrain_hdr', text='Terrain HDR')
    col.prop(material, 'simulate_roughness', text='Simulate Roughness')
    col.prop(material, 'pixel_forward_lighting', text='Forward Lighting')
    col.prop(material, 'depth_fog', text='Depth Fog')
    col.prop(material, 'decal_lighting', text='Decal Lighting')
    col.prop(material, 'transparent_shadows', text='Transparent Shadows')
    col.prop(material, 'transparent_depth', text='Transparent Depth')
    col.prop(material, 'transparent_local_lights', text='Transparent Local Lights')
    col.prop(material, 'disable_soft', text='Soft Lighting', invert_checkbox=True)
    col.prop(material, 'double_lambert', text='Double Lambert')
    col.prop(material, 'hair_layer_sorting', text='Hair Layer Sorting')
    col.prop(material, 'accept_splats', text='Accept Splats')
    col.prop(material, 'accept_splats_only', text='Accept Splats Only')
    col.prop(material, 'background_object', text='Background Object')
    col.prop(material, 'no_highlighting', text='Highlightable', invert_checkbox=True)
    col.prop(material, 'clamp_output', text='Clamp Output')
    col.prop(material, 'geometry_visible', text='Geometry Visible')
    col.prop(material, 'fill_required', text='Fill Required')
    layout.separator()
    layout.label(text='Required on low end:')
    row = layout.row()
    row.use_property_split = False
    split = row.split(factor=1/3)
    col = split.column()
    col.alignment = 'LEFT'
    col.prop(material, 'decal_required', text='Decal')
    col = split.column()
    col.alignment = 'LEFT'
    col.prop(material, 'spec_required', text='Specular')
    col = split.column()
    col.alignment = 'LEFT'
    col.prop(material, 'emis_required', text='Emissive')


def draw_displacement_props(context, material, layout):
    draw_layer_pointer_prop(context.object, layout, material, 'layer_norm', 'Normal')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_strength', 'Strength')
    layout.separator()
    layout.prop(material, 'priority', text='Priority')
    layout.prop(material, 'strength_factor', text='Strength Multiplier')


def draw_composite_section_props(section, layout):
    matref = bpy.context.object.m3_materialrefs[bpy.context.object.m3_materialrefs_index]
    mat = m3_material_get(bpy.context.object, matref)
    section_matref_path = 'm3_materials_composite[{}].sections[{}].matref'.format(mat.bl_index, section.bl_index)
    shared.draw_pointer_prop(bpy.context.object, layout, 'm3_materialrefs', section_matref_path, 'Material', icon='MATERIAL')
    layout.prop(section, 'alpha_factor', text='Alpha Factor')


def draw_composite_props(context, material, layout):
    layout.prop(material, 'unknown', text='Unknown Number')
    box = layout.box()
    box.use_property_split = False
    op = box.operator('m3.collection_add', text='Add Material Reference')
    op.collection = 'm3_materials_composite[%d].sections' % (material.bl_index)
    for item in material.sections:
        ref_path = 'm3_materials_composite[%d].sections[%d].matref' % (material.bl_index, item.bl_index)
        row = box.row()
        shared.draw_pointer_prop(context.object, row, 'm3_materialrefs', ref_path, '', icon='MATERIAL')
        row.prop(item, 'alpha_factor', text='Alpha Factor')
        op = row.operator('m3.collection_remove', icon='X', text='')
        op.collection, op.index = ('m3_materials_composite[%d].sections' % material.bl_index, item.bl_index)


def draw_terrain_props(context, material, layout):
    draw_layer_pointer_prop(context.object, layout, material, 'layer_terrain', 'Terrain')


def draw_volume_props(context, material, layout):
    draw_layer_pointer_prop(context.object, layout, material, 'layer_color', 'Color')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_unknown1', 'Unknown 1')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_unknown2', 'Unknown 2')
    layout.separator()
    layout.prop(material, 'density', text='Density')


def draw_volumenoise_props(context, material, layout):
    draw_layer_pointer_prop(context.object, layout, material, 'layer_color', 'Color')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_noise1', 'Noise 1')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_noise2', 'Noise 2')
    layout.separator()
    layout.prop(material, 'density', text='Density')
    layout.prop(material, 'near_plane', text='Near Plane')
    layout.prop(material, 'falloff', text='Falloff')
    layout.prop(material, 'scroll_rate', text='Scroll Rate')
    layout.separator()
    layout.prop(material, 'translation', text='Translation')
    layout.prop(material, 'rotation', text='Rotation')
    layout.prop(material, 'scale', text='Scale')
    layout.separator()
    layout.prop(material, 'alpha_threshold', text='Alpha Threshold')
    layout.prop(material, 'draw_after_transparency', text='Draw After Transparency')


def draw_creep_props(context, material, layout):
    draw_layer_pointer_prop(context.object, layout, material, 'layer_creep', 'Creep')


def draw_stb_props(context, material, layout):
    draw_layer_pointer_prop(context.object, layout, material, 'layer_diff', 'Diffuse')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_spec', 'Specular')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_norm', 'Normal')


def draw_reflection_props(context, material, layout):
    draw_layer_pointer_prop(context.object, layout, material, 'layer_norm', 'Normal')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_strength', 'Strength')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_blur', 'Blur')
    layout.separator()
    layout.prop(material, 'reflection_offset', text='Reflection Offset')
    layout.prop(material, 'reflection_strength', text='Reflection Strength')
    layout.prop(material, 'displacement_strength', text='Displacement Strength')
    layout.separator()
    layout.prop(material, 'blur_angle', text='Blur Angle')
    layout.prop(material, 'blur_distance', text='Blur Distance')
    layout.separator()
    col = layout.column_flow(columns=2)
    col.use_property_split = False
    col.prop(material, 'use_layer_norm', text='Use Normal Layer')
    col.prop(material, 'use_layer_strength', text='Use Strength Layer')
    col.prop(material, 'blurring', text='Blurring')
    col.prop(material, 'use_layer_blur', text='Use Blur Layer')
    col = layout.column()
    col.use_property_split = False
    col.alignment = 'LEFT'
    col.prop(material, 'render_transparent_pass', text='Render On Trasparent Pass')


def draw_lensflare_starburst_props(starburst, layout):
    layout.prop(starburst, 'uv_index', text='UV Index')
    layout.separator()
    layout.prop(starburst, 'distance_factor', text='Distance Factor')
    layout.separator()
    layout.prop(starburst, 'width', text='Width')
    layout.prop(starburst, 'height', text='Height')
    layout.separator()
    layout.prop(starburst, 'width_falloff', text='Fallof Width')
    layout.prop(starburst, 'height_falloff', text='Fallof Height')
    layout.separator()
    layout.prop(starburst, 'falloff_threshold', text='Falloff Threshold')
    layout.prop(starburst, 'falloff_rate', text='Falloff Rate')
    layout.separator()
    layout.prop(starburst, 'color', text='Tint Color')
    layout.separator()
    layout.prop(starburst, 'face_source', text='Face Source')


def draw_lensflare_props(context, material, layout):
    draw_layer_pointer_prop(context.object, layout, material, 'layer_color', 'Color')
    draw_layer_pointer_prop(context.object, layout, material, 'layer_unknown', 'Unknown')
    layout.separator()
    col = layout.column(align=True)
    col.prop(material, 'uv_columns', text='UV Columns')
    col.prop(material, 'uv_rows', text='Rows')
    layout.separator()
    layout.prop(material, 'render_distance', text='Render Distance')
    layout.separator()
    layout.prop(material, 'intensity', text='Intensity')
    layout.prop(material, 'intensity2', text='Intensity 2')
    layout.separator()
    layout.prop(material, 'uniform_scale', text='Uniform Scale')
    layout.separator()
    layout.prop(material, 'color', text='Tint Color')
    layout.separator()
    shared.draw_collection_list(layout.box(), 'm3_materials_lensflare[{}].starbursts'.format(material.bl_index), draw_lensflare_starburst_props, label='Starbursts:')


mat_type_dict = {
    'm3_materials_standard': {'name': 'Standard', 'draw': draw_standard_props},
    'm3_materials_displacement': {'name': 'Displacement', 'draw': draw_displacement_props},
    'm3_materials_composite': {'name': 'Composite', 'draw': draw_composite_props},
    'm3_materials_terrain': {'name': 'Terrain', 'draw': draw_terrain_props},
    'm3_materials_volume': {'name': 'Volume', 'draw': draw_volume_props},
    'm3_materials_volumenoise': {'name': 'Volume Noise', 'draw': draw_volumenoise_props},
    'm3_materials_creep': {'name': 'Creep', 'draw': draw_creep_props},
    'm3_materials_stb': {'name': 'Splat Terrain Bake', 'draw': draw_stb_props},
    'm3_materials_reflection': {'name': 'Reflection', 'draw': draw_reflection_props},
    'm3_materials_lensflare': {'name': 'Lens Flare', 'draw': draw_lensflare_props},
}


def draw_props(context, matref, layout):
    mat = m3_material_get(context.object, matref)
    col = layout.column()
    col.alignment = 'RIGHT'
    col.label(text='Material Type: ' + mat_type_dict[matref.mat_type]['name'])
    mat_type_dict[matref.mat_type]['draw'](context, mat, layout)


class Properties(shared.M3PropertyGroup):
    mat_type: bpy.props.EnumProperty(options=set(), items=bl_enum.matref_type)
    mat_handle: bpy.props.StringProperty(options=set())


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_MATERIALS'
    bl_label = 'M3 Materials'

    def draw(self, context):
        layout = self.layout
        ob = context.object
        index = ob.m3_materialrefs_index
        rows = 5 if len(ob.m3_materialrefs) else 3

        row = layout.row()
        col = row.column()
        col.template_list('UI_UL_list', 'm3_materialrefs', ob, 'm3_materialrefs', ob, 'm3_materialrefs_index', rows=rows)
        col = row.column()
        sub = col.column(align=True)
        op = sub.operator('m3.material_add_popup', icon='ADD', text='')
        op = sub.operator('m3.material_remove', icon='REMOVE', text='')
        sub.separator()
        op = sub.operator('m3.material_duplicate', icon='DUPLICATE', text='')

        if len(ob.m3_materialrefs):
            sub.separator()
            op = sub.operator('m3.material_move', icon='TRIA_UP', text='')
            op.shift = -1
            op = sub.operator('m3.material_move', icon='TRIA_DOWN', text='')
            op.shift = 1

        if index < 0:
            return

        matref = ob.m3_materialrefs[index]

        col = layout.column()
        col.use_property_split = True
        col.separator()
        col.prop(matref, 'name', text='Name')
        col.separator()
        draw_props(context, matref, col)


class M3MaterialLayerOpAdd(bpy.types.Operator):
    bl_idname = 'm3.material_layer_add'
    bl_label = 'New M3 Material Layer'
    bl_description = 'Create new M3 material layer'
    bl_options = {'UNDO'}

    layer_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        ob = context.object
        matref = ob.m3_materialrefs[ob.m3_materialrefs_index]
        mat = m3_material_get(ob, matref)
        layer = m3_material_layer_get(ob, getattr(mat, self.layer_name))

        if layer:
            new_layer = shared.m3_item_duplicate('m3_materiallayers', layer)
        else:
            new_layer = shared.m3_item_add('m3_materiallayers')

        setattr(mat, self.layer_name, new_layer.bl_handle)

        return {'FINISHED'}


class M3MaterialLayerOpUnlink(bpy.types.Operator):
    bl_idname = 'm3.material_layer_unlink'
    bl_label = 'Unlink M3 Material Layer'
    bl_description = 'Unlinks the M3 material layer from this layer slot'
    bl_options = {'UNDO'}

    layer_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        ob = context.object
        matref = ob.m3_materialrefs[ob.m3_materialrefs_index]
        mat = m3_material_get(ob, matref)
        setattr(mat, self.layer_name, '')

        return {'FINISHED'}


class M3MaterialLayerOpSearch(bpy.types.Operator):
    bl_idname = 'm3.material_layer_search'
    bl_label = 'Search M3 Material Layer'
    bl_description = 'Search for and select M3 material layer'
    bl_options = {'UNDO'}
    bl_property = 'enum'

    enum: bpy.props.EnumProperty(items=layer_enum)
    layer_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        ob = context.object
        matref = ob.m3_materialrefs[ob.m3_materialrefs_index]
        mat = m3_material_get(ob, matref)
        setattr(mat, self.layer_name, self.enum)

        return {'FINISHED'}


class M3MaterialOpAddPopup(bpy.types.Operator):
    bl_idname = 'm3.material_add_popup'
    bl_label = 'New M3 Material'
    bl_description = 'Create new M3 material'
    bl_options = {'REGISTER', 'UNDO'}

    enum: bpy.props.EnumProperty(items=bl_enum.matref_type)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text='Material Type')
        col = layout.column_flow(columns=2, align=True)
        col.prop(self, 'enum', expand=True)
        layout.separator()

    def execute(self, context):
        bpy.ops.m3.material_add('INVOKE_DEFAULT', mat_type=self.enum)
        return {'FINISHED'}


class M3MaterialOpAdd(bpy.types.Operator):
    bl_idname = 'm3.material_add'
    bl_label = 'New M3 Material'
    bl_description = 'Adds a new item to the collection'
    bl_options = {'UNDO'}

    mat_type: bpy.props.StringProperty()

    def invoke(self, context, event):
        matref = shared.m3_item_add('m3_materialrefs', item_name=mat_type_dict[self.mat_type]['name'])
        mat = shared.m3_item_add(self.mat_type, item_name=matref.name)
        matref.mat_type = self.mat_type
        matref.mat_handle = mat.bl_handle

        shared.m3_msgbus_sub(mat, matref, 'name', 'name')

        context.object.m3_materialrefs_index = len(context.object.m3_materialrefs) - 1

        return {'FINISHED'}


class M3MaterialOpRemove(bpy.types.Operator):
    bl_idname = 'm3.material_remove'
    bl_label = 'Remove M3 Material'
    bl_description = 'Removes the active item from the collection'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        ob = context.object
        matrefs = ob.m3_materialrefs
        matref = matrefs[ob.m3_materialrefs_index]
        mat = m3_material_get(ob, matref)

        getattr(ob, matref.mat_type).remove(mat.bl_index)
        ob.m3_materialrefs.remove(ob.m3_materialrefs_index)

        shared.remove_m3_action_keyframes(ob, matref.mat_type, ob.m3_materialrefs_index)
        for ii in range(ob.m3_materialrefs_index, len(matrefs)):
            matrefs[ii].bl_index -= 1
            shared.shift_m3_action_keyframes(ob, matref.mat_type, ii + 1)

        ob.m3_materialrefs_index -= 1 if (ob.m3_materialrefs_index == 0 and len(matrefs) > 0) or ob.m3_materialrefs_index == len(matrefs) else 0

        return {'FINISHED'}


class M3MaterialOpMove(bpy.types.Operator):
    bl_idname = 'm3.material_move'
    bl_label = 'Move M3 Material'
    bl_description = 'Moves the active item up/down in the list'
    bl_options = {'UNDO'}

    shift: bpy.props.IntProperty()

    def invoke(self, context, event):
        ob = context.object
        matrefs = ob.m3_materialrefs

        if (ob.m3_materialrefs_index < len(matrefs) - self.shift and ob.m3_materialrefs_index >= -self.shift):
            matrefs[ob.m3_materialrefs_index].bl_index += self.shift
            matrefs[ob.m3_materialrefs_index + self.shift].bl_index -= self.shift
            matrefs.move(ob.m3_materialrefs_index, ob.m3_materialrefs_index + self.shift)
            ob.m3_materialrefs_index += self.shift

        return {'FINISHED'}


class M3MaterialOpDuplicate(bpy.types.Operator):
    bl_idname = 'm3.material_duplicate'
    bl_label = 'Duplicate M3 Material'
    bl_description = 'Duplicates the active item in the list'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        matrefs = context.object.m3_materialrefs
        matref = matrefs[context.object.m3_materialrefs_index]
        mat = m3_material_get(context.object, matref)

        if context.object.m3_materialrefs_index == -1:
            return {'FINISHED'}

        new_mat = shared.m3_item_duplicate(matref.mat_type, mat)
        new_matref = shared.m3_item_duplicate('m3_materialrefs', matref)
        new_matref.mat_handle = new_mat.bl_handle

        context.object.m3_materialrefs_index = len(matrefs) - 1

        return {'FINISHED'}


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
    ReflectionProperties,
    LensFlareStarburstProperties,
    LensFlareProperties,
    Properties,
    Panel,
    M3MaterialOpAddPopup,
    M3MaterialOpAdd,
    M3MaterialOpRemove,
    M3MaterialOpMove,
    M3MaterialOpDuplicate,
    M3MaterialLayerOpAdd,
    M3MaterialLayerOpUnlink,
    M3MaterialLayerOpSearch,
)
