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
    norm_blend1_mask_layer: bpy.props.StringProperty(options=set())
    norm_blend2_mask_layer: bpy.props.StringProperty(options=set())
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
    matref: bpy.props.StringProperty(options=set())
    matref_handle: bpy.props.StringProperty(options=set())
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


def draw_layer_header(ob, layout, material, layer_name, label='test'):
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
    draw_layer_header(context.object, layout, material, 'diff_layer', 'Diffuse')
    draw_layer_header(context.object, layout, material, 'decal_layer', 'Decal')
    draw_layer_header(context.object, layout, material, 'spec_layer', 'Specular')
    draw_layer_header(context.object, layout, material, 'gloss_layer', 'Gloss')
    draw_layer_header(context.object, layout, material, 'emis1_layer', 'Emissive 1')
    draw_layer_header(context.object, layout, material, 'emis2_layer', 'Emissive 2')
    draw_layer_header(context.object, layout, material, 'evio_layer', 'Environment')
    draw_layer_header(context.object, layout, material, 'evio_mask_layer', 'Environment Mask')
    draw_layer_header(context.object, layout, material, 'alpha_mask1_layer', 'Alpha Mask 1')
    draw_layer_header(context.object, layout, material, 'alpha_mask2_layer', 'Alpha Mask 2')
    draw_layer_header(context.object, layout, material, 'norm_layer', 'Normal')
    draw_layer_header(context.object, layout, material, 'height_layer', 'Height')
    draw_layer_header(context.object, layout, material, 'lightmap_layer', 'Lightmap')
    draw_layer_header(context.object, layout, material, 'ao_layer', 'Ambient Occlusion')
    draw_layer_header(context.object, layout, material, 'norm_blend1_mask_layer', 'Normal Blend 1 Mask')
    draw_layer_header(context.object, layout, material, 'norm_blend2_mask_layer', 'Normal Blend 2 Mask')
    draw_layer_header(context.object, layout, material, 'norm_blend1_layer', 'Normal Blend 1')
    draw_layer_header(context.object, layout, material, 'norm_blend2_layer', 'Normal Blend 2')


def draw_props(context, matref, layout):
    mat = m3_material_get(context.object, matref)
    if matref.mat_type == 'm3_materials_standard':
        draw_standard_props(context, mat, layout)
    else:
        pass  # TODO


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
        op = sub.operator('m3.material_add', icon='ADD', text='')
        op = sub.operator('m3.material_remove', icon='REMOVE', text='')
        sub.separator()
        op = sub.operator('m3.material_duplicate', icon='DUPLICATE', text='')

        if len(ob.m3_animations):
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

    layer_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        ob = context.object
        layers = ob.m3_materiallayers
        matref = ob.m3_materialrefs[ob.m3_materialrefs_index]
        mat = m3_material_get(ob, matref)
        layer = m3_material_layer_get(ob, getattr(mat, self.layer_name))

        if layer:
            new_layer = shared.m3_item_duplicate(layers, layer)
        else:
            new_layer = shared.m3_item_new(layers)

        setattr(mat, self.layer_name, new_layer.bl_handle)

        return {'FINISHED'}


class M3MaterialLayerOpUnlink(bpy.types.Operator):
    bl_idname = 'm3.material_layer_unlink'
    bl_label = 'Unlink M3 Material Layer'
    bl_description = 'Unlinks the M3 material layer from this layer slot'

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
    bl_property = 'enum'

    enum: bpy.props.EnumProperty(items=layer_enum)
    layer_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        ob = context.object
        matref = ob.m3_materialrefs[ob.m3_materialrefs_index]
        mat = m3_material_get(ob, matref)
        setattr(mat, self.layer_name, self.enum)

        return {'FINISHED'}


class M3MaterialOpAdd(bpy.types.Operator):
    bl_idname = 'm3.material_add'
    bl_label = 'New M3 Material'
    bl_description = 'Adds a new item to the collection'

    def invoke(self, context, event):
        matref = shared.m3_item_new(context.object.m3_materialrefs)
        mat = shared.m3_item_new(context.object.m3_materials_standard)

        matref.mat_type = 'm3_materials_standard'
        matref.mat_handle = mat.bl_handle

        mat.name = matref.name

        context.object.m3_materialrefs_index = len(context.object.m3_materialrefs) - 1

        return {'FINISHED'}


class M3MaterialOpRemove(bpy.types.Operator):
    bl_idname = 'm3.material_remove'
    bl_label = 'Remove M3 Material'
    bl_description = 'Removes the active item from the collection'

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

    shift: bpy.props.IntProperty()

    def invoke(self, context, event):
        matrefs = context.object.m3_materialrefs

        if (self.index < len(collection) - self.shift and self.index >= -self.shift):
            matrefs[self.index].bl_index += self.shift
            matrefs[self.index + self.shift].bl_index -= self.shift
            matrefs.move(self.index, self.index + self.shift)
            context.object.m3_materialrefs_index += self.shift

        return {'FINISHED'}


class M3MaterialOpDuplicate(bpy.types.Operator):
    bl_idname = 'm3.material_duplicate'
    bl_label = 'Duplicate M3 Material'
    bl_description = 'Duplicates the active item in the list'

    def invoke(self, context, event):
        matrefs = context.object.m3_materialrefs
        matref = matrefs[context.object.m3_materialrefs_index]
        mat = m3_material_get(context.object, matref)

        if context.object.m3_materialrefs_index == -1:
            return {'FINISHED'}

        new_mat = shared.m3_item_duplicate(getattr(ob, matref.mat_type), mat)
        new_matref = shared.m3_item_duplicate(matrefs, matref)
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
    Properties,
    Panel,
    M3MaterialOpAdd,
    M3MaterialOpRemove,
    M3MaterialOpMove,
    M3MaterialOpDuplicate,
    M3MaterialLayerOpAdd,
    M3MaterialLayerOpUnlink,
    M3MaterialLayerOpSearch,
)
