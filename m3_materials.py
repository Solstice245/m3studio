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
    bpy.types.Object.m3_materialrefs = bpy.props.CollectionProperty(type=ReferenceProperties)
    bpy.types.Object.m3_materialrefs_index = bpy.props.IntProperty(options=set(), default=-1)
    bpy.types.Object.m3_materials_standard = bpy.props.CollectionProperty(type=StandardProperties)
    bpy.types.Object.m3_materials_standard_version = bpy.props.EnumProperty(options=set(), items=standard_versions, default='20')
    bpy.types.Object.m3_materials_displacement = bpy.props.CollectionProperty(type=DisplacementProperties)
    bpy.types.Object.m3_materials_composite = bpy.props.CollectionProperty(type=CompositeProperties)
    bpy.types.Object.m3_materials_terrain = bpy.props.CollectionProperty(type=TerrainProperties)
    bpy.types.Object.m3_materials_volume = bpy.props.CollectionProperty(type=VolumeProperties)
    bpy.types.Object.m3_materials_volumenoise = bpy.props.CollectionProperty(type=VolumeNoiseProperties)
    bpy.types.Object.m3_materials_creep = bpy.props.CollectionProperty(type=CreepProperties)
    bpy.types.Object.m3_materials_stb = bpy.props.CollectionProperty(type=SplatTerrainBakeProperties)
    bpy.types.Object.m3_materials_reflection = bpy.props.CollectionProperty(type=ReflectionProperties)
    bpy.types.Object.m3_materials_reflection_version = bpy.props.EnumProperty(options=set(), items=reflection_versions, default='2')
    bpy.types.Object.m3_materials_lensflare = bpy.props.CollectionProperty(type=LensFlareProperties)
    bpy.types.Object.m3_materials_lensflare_version = bpy.props.EnumProperty(options=set(), items=lensflare_versions, default='3')
    bpy.types.Object.m3_materials_buffer = bpy.props.CollectionProperty(type=BufferProperties)


standard_versions = (
    ('15', '15', 'Version 15'),
    ('16', '16', 'Version 16'),
    ('17', '17', 'Version 17'),
    ('18', '18', 'Version 18'),
    ('19', '19', 'Version 19'),
    ('20', '20', 'Version 20'),
)

reflection_versions = (
    ('1', '1', 'Version 1'),
    ('2', '2', 'Version 2'),
    ('3', '3', 'Version 3'),
)

lensflare_versions = (
    ('2', '2', 'Version 2'),
    ('3', '3', 'Version 3'),
)


def get_material_name(self):
    for matref in self.id_data.m3_materialrefs:
        if matref.mat_handle == self.bl_handle:
            return matref.name
    return 'Unknown Material'


class StandardProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Standard Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
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

    material_class: bpy.props.IntProperty(options=set())  # no UI, untested
    priority: bpy.props.IntProperty(options=set())
    blend_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_blend, default='OPAQUE')
    blend_mode_layer: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_layer_blend, default='ADD')
    blend_mode_emis1: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_layer_blend, default='ADD')
    blend_mode_emis2: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_layer_blend, default='ADD')
    spec_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.mat_spec, default='RGB')
    specularity: bpy.props.FloatProperty(options=set(), min=0.0, default=20.0)
    depth_blend_falloff: bpy.props.FloatProperty(options=set())
    alpha_test_threshold: bpy.props.IntProperty(options=set(), subtype='FACTOR', min=0, max=255)
    hdr_spec: bpy.props.FloatProperty(options=set(), min=0.0, default=1.0)
    hdr_emis: bpy.props.FloatProperty(options=set(), min=0.0, default=1.0)
    hdr_envi_const: bpy.props.FloatProperty(options=set(), min=0.0, default=1.0)
    hdr_envi_diff: bpy.props.FloatProperty(options=set(), min=0.0, default=0.0)
    hdr_envi_spec: bpy.props.FloatProperty(options=set(), min=0.0, default=0.0)
    parallax_height: bpy.props.FloatProperty(name='Parallax Height', default=0.0)
    parallax_height_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    motion_blur: bpy.props.FloatProperty(name='Motion Blur', min=0.0, default=0.0)  # no UI, not documented to function
    motion_blur_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)

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
    transparent_depth_effects: bpy.props.BoolProperty(options=set())
    transparent_local_lights: bpy.props.BoolProperty(options=set())
    disable_soft: bpy.props.BoolProperty(options=set())
    double_lambert: bpy.props.BoolProperty(options=set())
    hair_layer_sorting: bpy.props.BoolProperty(options=set())
    accept_splats: bpy.props.BoolProperty(options=set())
    decal_low_required: bpy.props.BoolProperty(options=set())
    emis_low_required: bpy.props.BoolProperty(options=set())
    spec_low_required: bpy.props.BoolProperty(options=set())
    accept_splats_only: bpy.props.BoolProperty(options=set())
    background_object: bpy.props.BoolProperty(options=set())
    unknown0x8000000: bpy.props.BoolProperty(options=set())
    depth_prepass_low_required: bpy.props.BoolProperty(options=set())
    no_highlighting: bpy.props.BoolProperty(options=set())
    clamp_output: bpy.props.BoolProperty(options=set())
    geometry_visible: bpy.props.BoolProperty(options=set(), default=True)


class DisplacementProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Displacement Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
    layer_norm: bpy.props.StringProperty(options=set())
    layer_strength: bpy.props.StringProperty(options=set())
    priority: bpy.props.IntProperty(options=set())
    strength_factor: bpy.props.FloatProperty(name='Distortion Factor', default=1.0)
    strength_factor_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)


class CompositeSectionProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Composite Material Section'

    material: bpy.props.PointerProperty(type=shared.M3MatRefPointerProp)
    alpha_factor: bpy.props.FloatProperty(name='Alpha Factor', default=1)
    alpha_factor_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)


class CompositeProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Composite Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
    sections: bpy.props.CollectionProperty(type=CompositeSectionProperties)
    sections_index: bpy.props.IntProperty(options=set(), default=-1)
    priority: bpy.props.IntProperty(options=set())


class TerrainProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Terrain Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
    layer_terrain: bpy.props.StringProperty(options=set())


class VolumeProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Volumetric Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
    layer_color: bpy.props.StringProperty(options=set())
    layer_unknown1: bpy.props.StringProperty(options=set())
    layer_unknown2: bpy.props.StringProperty(options=set())
    density: bpy.props.FloatProperty(name='Density')
    density_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)


class VolumeNoiseProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Volumetric Noise Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
    layer_color: bpy.props.StringProperty(options=set())
    layer_noise1: bpy.props.StringProperty(options=set())
    layer_noise2: bpy.props.StringProperty(options=set())
    density: bpy.props.FloatProperty(name='Density')
    density_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    near_plane: bpy.props.FloatProperty(name='Near Plane')
    near_plane_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    falloff: bpy.props.FloatProperty(name='Falloff')
    falloff_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    scroll_rate: bpy.props.FloatVectorProperty(name='Scroll Rate', size=3, subtype='XYZ')
    scroll_rate_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    translation: bpy.props.FloatVectorProperty(name='Translation', size=3, subtype='XYZ')
    translation_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    rotation: bpy.props.FloatVectorProperty(name='Rotations', size=3, subtype='XYZ')
    rotation_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    scale: bpy.props.FloatVectorProperty(name='Scale', size=3, subtype='XYZ')
    scale_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    alpha_threshold: bpy.props.IntProperty(options=set())
    draw_after_transparency: bpy.props.BoolProperty(options=set())


class CreepProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Creep Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
    layer_creep: bpy.props.StringProperty(options=set())


class SplatTerrainBakeProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Splat Terrain Bake Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
    layer_diff: bpy.props.StringProperty(options=set())
    layer_norm: bpy.props.StringProperty(options=set())
    layer_spec: bpy.props.StringProperty(options=set())


class ReflectionProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Reflection Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
    layer_norm: bpy.props.StringProperty(options=set())
    layer_strength: bpy.props.StringProperty(options=set())
    layer_blur: bpy.props.StringProperty(options=set())
    blur_angle: bpy.props.FloatProperty(name='Blur Angle')
    blur_angle_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    blur_distance: bpy.props.FloatProperty(name='Blur Distance', default=2)
    blur_distance_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    reflection_offset: bpy.props.FloatProperty(name='Reflection Offset')
    reflection_offset_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    reflection_strength: bpy.props.FloatProperty(name='Reflection Strength', default=1)
    reflection_strength_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    displacement_strength: bpy.props.FloatProperty(name='Displacement Strength', default=1)
    displacement_strength_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    use_layer_norm: bpy.props.BoolProperty(options=set())
    use_layer_strength: bpy.props.BoolProperty(options=set())
    blurring: bpy.props.BoolProperty(options=set())
    use_layer_blur: bpy.props.BoolProperty(options=set())
    render_transparent_pass: bpy.props.BoolProperty(options=set())


class LensFlareStarburstProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Lens Flare Material Starburst'

    name: bpy.props.StringProperty(options=set())
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

    def _get_identifier(self):
        return 'M3 Lens Flare Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
    layer_color: bpy.props.StringProperty(options=set())
    layer_unknown: bpy.props.StringProperty(options=set())
    starbursts: bpy.props.CollectionProperty(type=LensFlareStarburstProperties)
    starbursts_index: bpy.props.IntProperty(options=set(), default=-1)
    uv_cols: bpy.props.IntProperty(options=set(), min=1, default=1)
    uv_rows: bpy.props.IntProperty(options=set(), min=1, default=1)
    render_distance: bpy.props.FloatProperty(options=set(), min=0.0)
    intensity: bpy.props.FloatProperty(name='Intensity', min=0.0, default=1.0)
    intensity_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    intensity2: bpy.props.FloatProperty(name='Intensity 2', min=0.0, default=1.0)
    intensity2_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uniform_scale: bpy.props.FloatProperty(name='Uniform Scale', min=0.0, default=1.0)
    uniform_scale_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color: bpy.props.FloatVectorProperty(name='Color', subtype='COLOR', size=4, min=0.0, max=1.0, default=(1.0, 1.0, 1.0, 1.0))
    color_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)


def get_name(self):
    return self.get('name')


class BufferTexturePath(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(options=set(), get=get_name)


class BufferProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Buffer Material'

    name: bpy.props.StringProperty(options=set(), get=get_material_name)
    texture_paths: bpy.props.CollectionProperty(type=BufferTexturePath)
    texture_paths_index: bpy.props.IntProperty(options=set(), default=-1)


def m3_material_get(matref):
    mat = None
    if matref.mat_handle:
        mat_col = getattr(matref.id_data, matref.mat_type)
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


def draw_layer_pointer_prop(layout, material, layer_name, label='test'):
    col = layout.column(align=True)
    col.use_property_split = False
    split = col.split(factor=0.4, align=True)
    row = split.row(align=True)
    row.alignment = 'RIGHT'
    row.label(text=label)
    row = split.row(align=True)
    op = row.operator('m3.material_layer_search', text='', icon='VIEWZOOM')
    op.layer_name = layer_name
    layer = m3_material_layer_get(material.id_data, getattr(material, layer_name))
    if layer:
        row.prop(layer, 'name', text='', icon='NODE_COMPOSITING')
        op = row.operator('m3.material_layer_add', text='', icon='DUPLICATE')
        op.layer_name = layer_name
        op = row.operator('m3.material_layer_unlink', text='', icon='X')
        op.layer_name = layer_name
    else:
        op = row.operator('m3.material_layer_add', text='New', icon='ADD')
        op.layer_name = layer_name


def draw_standard_props(matref, layout):
    material = m3_material_get(matref)
    version = int(material.id_data.m3_materials_standard_version)

    draw_layer_pointer_prop(layout, material, 'layer_diff', 'Diffuse')
    draw_layer_pointer_prop(layout, material, 'layer_decal', 'Decal')
    draw_layer_pointer_prop(layout, material, 'layer_spec', 'Specular')

    if version >= 16:
        draw_layer_pointer_prop(layout, material, 'layer_gloss', 'Gloss')

    draw_layer_pointer_prop(layout, material, 'layer_emis1', 'Emissive 1')
    draw_layer_pointer_prop(layout, material, 'layer_emis2', 'Emissive 2')
    draw_layer_pointer_prop(layout, material, 'layer_envi', 'Environment')
    draw_layer_pointer_prop(layout, material, 'layer_envi_mask', 'Environment Mask')
    draw_layer_pointer_prop(layout, material, 'layer_alpha1', 'Alpha Mask 1')
    draw_layer_pointer_prop(layout, material, 'layer_alpha2', 'Alpha Mask 2')
    draw_layer_pointer_prop(layout, material, 'layer_norm', 'Normal')
    draw_layer_pointer_prop(layout, material, 'layer_height', 'Height')
    draw_layer_pointer_prop(layout, material, 'layer_light', 'Light')
    draw_layer_pointer_prop(layout, material, 'layer_ao', 'Ambient Occlusion')

    if version >= 19:
        draw_layer_pointer_prop(layout, material, 'layer_norm_blend1_mask', 'Normal Blend 1 Mask')
        draw_layer_pointer_prop(layout, material, 'layer_norm_blend2_mask', 'Normal Blend 2 Mask')
        draw_layer_pointer_prop(layout, material, 'layer_norm_blend1', 'Normal Blend 1')
        draw_layer_pointer_prop(layout, material, 'layer_norm_blend2', 'Normal Blend 2')

    layout.separator()
    col = layout.column(align=True)
    col.prop(material, 'blend_mode', text='Material Blend')
    col.prop(material, 'alpha_test_threshold', text='Alpha Test Threshold')
    if material.blend_mode != 'OPAQUE':
        col.prop(material, 'priority', text='Priority')
        col.prop(material, 'depth_blend_falloff', text='Depth Blend')
    col.separator()
    col.prop(material, 'blend_mode_layer', text='Layer Blend')
    col.prop(material, 'blend_mode_emis1', text='Emissive 1 Blend')
    col.prop(material, 'blend_mode_emis2', text='Emissive 2 Blend')
    col.separator()
    # col.prop(material, 'spec_mode', text='Specular Mode')  # * does this actually do anything?
    col.prop(material, 'specularity', text='Specularity')
    col.separator()
    col.prop(material, 'hdr_spec', text='Specular HDR')
    col.prop(material, 'hdr_emis', text='Emissive HDR')
    col.separator()

    if version >= 20:
        col.prop(material, 'hdr_envi_const', text='Environment HDR')
        col.prop(material, 'hdr_envi_diff', text='Diffuse')
        col.prop(material, 'hdr_envi_spec', text='Specular')
        col.separator()

    shared.draw_prop_anim(col, material, 'parallax_height', text='Parallax Height')

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
    col.prop(material, 'transparent_depth_effects', text='Transparent Depth')
    col.prop(material, 'transparent_local_lights', text='Transparent Local Lights')
    col.prop(material, 'disable_soft', text='Soft Lighting', invert_checkbox=True)
    col.prop(material, 'double_lambert', text='Double Lambert')
    # col.prop(material, 'hair_layer_sorting', text='Hair Layer Sorting')  # ? unsupported
    col.prop(material, 'accept_splats', text='Accept Splats')
    col.prop(material, 'accept_splats_only', text='Accept Splats Only')
    col.prop(material, 'background_object', text='Background Object')
    col.prop(material, 'no_highlighting', text='Highlightable', invert_checkbox=True)
    col.prop(material, 'clamp_output', text='Clamp Output')
    col.prop(material, 'geometry_visible', text='Geometry Visible')
    layout.separator()
    layout.label(text='Required on low end:')
    row = layout.row()
    row.use_property_split = False
    split = row.split(factor=1/3)
    col = split.column()
    col.alignment = 'LEFT'
    col.prop(material, 'depth_prepass_low_required', text='Depth Prepass')
    col = split.column()
    col.alignment = 'LEFT'
    col.prop(material, 'decal_low_required', text='Decal')
    # col = split.column()
    # col.alignment = 'LEFT'
    # col.prop(material, 'spec_low_required', text='Specular')  # ? unsupported
    col = split.column()
    col.alignment = 'LEFT'
    col.prop(material, 'emis_low_required', text='Emissive')


def draw_displacement_props(matref, layout):
    material = m3_material_get(matref)
    draw_layer_pointer_prop(layout, material, 'layer_norm', 'Normal')
    draw_layer_pointer_prop(layout, material, 'layer_strength', 'Strength')
    layout.separator()
    layout.prop(material, 'priority', text='Priority')
    shared.draw_prop_anim(layout, material, 'strength_factor', text='Strength Factor')


def draw_composite_props(matref, layout):
    material = m3_material_get(matref)
    layout.prop(material, 'priority', text='Priority')
    box = layout.box()
    box.use_property_split = False
    op = box.operator('m3.collection_add', text='Add Material Reference')
    op.collection = material.sections.path_from_id()
    for ii, item in enumerate(material.sections):
        row = box.row()
        shared.draw_prop_pointer_search(row, item.material, material.id_data, 'm3_materialrefs', icon='MATERIAL')
        shared.draw_prop_anim(row, item, 'alpha_factor', text='Alpha Factor')
        op = row.operator('m3.collection_remove', icon='X', text='')
        op.collection, op.index = (material.sections.path_from_id(), ii)


def draw_terrain_props(matref, layout):
    material = m3_material_get(matref)
    draw_layer_pointer_prop(layout, material, 'layer_terrain', 'Terrain')


def draw_volume_props(matref, layout):
    material = m3_material_get(matref)
    draw_layer_pointer_prop(layout, material, 'layer_color', 'Color')
    draw_layer_pointer_prop(layout, material, 'layer_unknown1', 'Unknown 1')
    draw_layer_pointer_prop(layout, material, 'layer_unknown2', 'Unknown 2')
    layout.separator()
    shared.draw_prop_anim(layout, material, 'density', text='Density')


def draw_volumenoise_props(matref, layout):
    material = m3_material_get(matref)
    draw_layer_pointer_prop(layout, material, 'layer_color', 'Color')
    draw_layer_pointer_prop(layout, material, 'layer_noise1', 'Noise 1')
    draw_layer_pointer_prop(layout, material, 'layer_noise2', 'Noise 2')
    layout.separator()
    shared.draw_prop_anim(layout, material, 'density', text='Density')
    shared.draw_prop_anim(layout, material, 'near_plane', text='Near Plane')
    shared.draw_prop_anim(layout, material, 'falloff', text='Falloff')
    shared.draw_prop_anim(layout, material, 'scroll_rate', text='Scroll Rate')
    layout.separator()
    shared.draw_prop_anim(layout, material, 'translation', text='Translation')
    shared.draw_prop_anim(layout, material, 'rotation', text='Rotation')
    shared.draw_prop_anim(layout, material, 'scale', text='Scale')
    layout.separator()
    layout.prop(material, 'alpha_threshold', text='Alpha Threshold')
    layout.prop(material, 'draw_after_transparency', text='Draw After Transparency')


def draw_creep_props(matref, layout):
    material = m3_material_get(matref)
    draw_layer_pointer_prop(layout, material, 'layer_creep', 'Creep')


def draw_stb_props(matref, layout):
    material = m3_material_get(matref)
    draw_layer_pointer_prop(layout, material, 'layer_diff', 'Diffuse')
    draw_layer_pointer_prop(layout, material, 'layer_spec', 'Specular')
    draw_layer_pointer_prop(layout, material, 'layer_norm', 'Normal')


def draw_reflection_props(matref, layout):
    material = m3_material_get(matref)
    version = int(material.id_data.m3_materials_reflection_version)

    draw_layer_pointer_prop(layout, material, 'layer_norm', 'Normal')
    draw_layer_pointer_prop(layout, material, 'layer_strength', 'Strength')

    if version >= 2:
        draw_layer_pointer_prop(layout, material, 'layer_blur', 'Blur')

    layout.separator()

    if version >= 2:
        shared.draw_prop_anim(layout, material, 'reflection_offset', text='Reflection Offset')

    shared.draw_prop_anim(layout, material, 'reflection_strength', text='Reflection Strength')
    shared.draw_prop_anim(layout, material, 'displacement_strength', text='Displacement Strength')

    if version >= 2:
        layout.separator()
        shared.draw_prop_anim(layout, material, 'blur_angle', text='Blur Angle')
        shared.draw_prop_anim(layout, material, 'blur_distance', text='Blur Distance')

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


def draw_lensflare_props(matref, layout):
    material = m3_material_get(matref)
    version = int(material.id_data.m3_materials_lensflare_version)

    draw_layer_pointer_prop(layout, material, 'layer_color', 'Color')
    draw_layer_pointer_prop(layout, material, 'layer_unknown', 'Unknown')
    layout.separator()
    col = layout.column(align=True)
    col.prop(material, 'uv_cols', text='UV Columns')
    col.prop(material, 'uv_rows', text='Rows')
    layout.separator()
    layout.prop(material, 'render_distance', text='Render Distance')
    layout.separator()
    shared.draw_prop_anim(layout, material, 'intensity', text='Intensity')

    if version >= 3:
        shared.draw_prop_anim(layout, material, 'intensity2', text='Intensity 2')
        layout.separator()
        shared.draw_prop_anim(layout, material, 'uniform_scale', text='Uniform Scale')
        layout.separator()
        shared.draw_prop_anim(layout, material, 'color', text='Tint Color')

    layout.separator()
    shared.draw_collection_list(layout.box(), material.starbursts, draw_lensflare_starburst_props, label='Starbursts:')


def draw_buffer_props(matref, layout):
    material = m3_material_get(matref)
    layout.label(text='"Buffer" material type is not supported. Convert to other materials.')
    layout.label(text='Listing texture paths used.')

    uilist_rows = 5 if len(material.texture_paths) else 3
    row = layout.row()
    row.template_list(
        'UI_UL_list', 'texture_paths', material,
        'texture_paths', material, 'texture_paths_index',
        rows=uilist_rows,
    )


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
    'm3_materials_buffer': {'name': 'Buffer', 'draw': draw_buffer_props},
}


class ReferenceProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Material Reference'

    mat_type: bpy.props.EnumProperty(options=set(), items=bl_enum.matref_type)
    mat_handle: bpy.props.StringProperty(options=set())


class MaterialList(bpy.types.UIList):
    bl_idname = 'UI_UL_M3_materials'

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, 'name', text='', emboss=False, icon_value=icon)
            split = row.row()
            split.alignment = 'RIGHT'
            split.label(text=mat_type_dict[item.mat_type]['name'])
            split.separator(factor=0.05)


class MaterialMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_materials'
    bl_label = 'Menu'

    def draw(self, context):
        layout = self.layout
        op = layout.operator('m3.material_duplicate', icon='DUPLICATE', text='Duplicate')
        op.dup_action_keyframes = False
        op = layout.operator('m3.material_duplicate', text='Duplicate With Animations')
        op.dup_action_keyframes = True


def draw_ops_add(layout):
    layout.operator('m3.material_add_popup', icon='ADD', text='')


def draw_ops_del(layout):
    layout.operator('m3.material_remove', icon='REMOVE', text='')


def draw_ops_mov(layout):
    op = layout.operator('m3.material_move', icon='TRIA_UP', text='')
    op.shift = -1
    op = layout.operator('m3.material_move', icon='TRIA_DOWN', text='')
    op.shift = 1


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_MATERIALS'
    bl_label = 'M3 Materials'

    def draw(self, context):
        self.layout.use_property_decorate = False
        matref = context.object.m3_materialrefs[context.object.m3_materialrefs_index] if context.object.m3_materialrefs_index > -1 else None
        shared.draw_collection_list(
            self.layout, context.object.m3_materialrefs, mat_type_dict[matref.mat_type]['draw'] if matref else lambda x, y: None,
            ops={'add': draw_ops_add, 'del': draw_ops_del}, ui_list_id=MaterialList.bl_idname, menu_id=MaterialMenu.bl_idname
        )


class M3MaterialLayerOpAdd(bpy.types.Operator):
    bl_idname = 'm3.material_layer_add'
    bl_label = 'New M3 Material Layer'
    bl_description = 'Create new M3 material layer'
    bl_options = {'UNDO'}

    layer_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        ob = context.object
        matref = ob.m3_materialrefs[ob.m3_materialrefs_index]
        mat = m3_material_get(matref)
        layer = m3_material_layer_get(ob, getattr(mat, self.layer_name))

        if layer:
            new_layer = shared.m3_item_duplicate(ob.m3_materiallayers, layer, True)
        else:
            new_layer = shared.m3_item_add(ob.m3_materiallayers)

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
        mat = m3_material_get(matref)
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
        mat = m3_material_get(matref)
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
        ob = context.object
        matref = shared.m3_item_add(ob.m3_materialrefs, item_name=mat_type_dict[self.mat_type]['name'])
        mat = shared.m3_item_add(getattr(ob, self.mat_type))
        matref.mat_type = self.mat_type
        matref.mat_handle = mat.bl_handle
        context.object.m3_materialrefs_index = len(context.object.m3_materialrefs) - 1

        return {'FINISHED'}


class M3MaterialOpRemove(bpy.types.Operator):
    bl_idname = 'm3.material_remove'
    bl_label = 'Remove M3 Material'
    bl_description = 'Removes the active item from the collection'
    bl_options = {'UNDO'}

    quiet: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        ob = context.object
        matrefs = ob.m3_materialrefs
        matref = matrefs[ob.m3_materialrefs_index]

        # check if material is in use
        user_strings = []

        for particle_system in ob.m3_particlesystems:
            if particle_system.material.value == matref.name:
                user_strings.append(f'The particle system {particle_system.name} is using this material')
        for ribbon in ob.m3_ribbons:
            if ribbon.material.value == matref.name:
                user_strings.append(f'The particle system {ribbon.name} is using this material')
        for projection in ob.m3_projections:
            if projection.material.value == matref.name:
                user_strings.append(f'The particle system {projection.name} is using this material')
        for child in ob.children_recursive:
            if child.type != 'MESH':
                continue
            for mesh_batch in child.m3_mesh_batches:
                if mesh_batch.material.value == matref.name:
                    user_strings.append(f'The mesh object {child.name} is using this material')
        for c_matref in matrefs:
            mat = m3_material_get(c_matref)
            if c_matref.mat_type == 'm3_materials_composite':
                for section in mat.sections:
                    if section.material.value == matref.name:
                        user_strings.append(f'The material {c_matref.name} is using this material')

        if user_strings:
            if not self.quiet:
                self.report({"ERROR"}, 'Deletion cancelled due to the following reason(s):\n' + '\n'.join(user_strings))
            return {'CANCELLED'}

        mat_col = getattr(ob, matref.mat_type)
        mat_ii = None
        for ii, item in enumerate(mat_col):
            if item.bl_handle == matref.mat_handle:
                mat_col.remove(ii)
                mat_ii = ii
                break

        ob.m3_materialrefs.remove(ob.m3_materialrefs_index)

        shared.remove_m3_action_keyframes(ob, matref.mat_type, mat_ii)
        for ii in range(mat_ii, len(matrefs)):
            shared.shift_m3_action_keyframes(ob, matref.mat_type, ii + 1)

        ob.m3_materialrefs_index -= 1 if (ob.m3_materialrefs_index == 0 and len(matrefs) == 0) or ob.m3_materialrefs_index == len(matrefs) else 0

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
            matrefs.move(ob.m3_materialrefs_index, ob.m3_materialrefs_index + self.shift)
            ob.m3_materialrefs_index += self.shift

        return {'FINISHED'}


class M3MaterialOpDuplicate(bpy.types.Operator):
    bl_idname = 'm3.material_duplicate'
    bl_label = 'Duplicate M3 Material'
    bl_description = 'Duplicates the active item in the list'
    bl_options = {'UNDO'}

    dup_action_keyframes: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        matrefs = context.object.m3_materialrefs
        matref = matrefs[context.object.m3_materialrefs_index]
        mat_col = getattr(context.object, matref.mat_type)
        mat = m3_material_get(matref)

        if context.object.m3_materialrefs_index == -1:
            return {'FINISHED'}

        new_mat = shared.m3_item_duplicate(mat_col, mat, self.dup_action_keyframes)
        new_matref = shared.m3_item_duplicate(matrefs, matref, False)
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
    BufferTexturePath,
    BufferProperties,
    ReferenceProperties,
    MaterialList,
    MaterialMenu,
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
