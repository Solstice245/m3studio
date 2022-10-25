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
from . import shared, bl_enum


def register_props():
    bpy.types.Object.m3_projections = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_projections_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)


def update_collection_index(self, context):
    ob = context.object
    bl = ob.m3_projections[ob.m3_projections_index]
    shared.select_bones_handles(ob, [bl.bone])
    shared.auto_update_bone_shapes(ob, 'PROJ')


def draw_props(projection, layout):
    col = layout.column()
    col.prop(projection, 'material', text='Material')
    col.prop(projection, 'projection_type', text='Type')
    col.prop(projection, 'layer', text='Layer')
    col = layout.column()
    col.prop(projection, 'active', text='Active')
    col = layout.column()
    col.prop(projection, 'field_of_view', text='Field of View')
    col.prop(projection, 'aspect_ratio', text='Aspect Ratio')
    col = layout.column()
    col.prop(projection, 'near', text='Near')
    col.prop(projection, 'far', text='Far')
    col = layout.column(align=True)
    col.prop(projection, 'depth', text='Depth')
    col.prop(projection, 'height', text='Height')
    col.prop(projection, 'width', text='Width')
    col = layout.column(align=True)
    col.prop(projection, 'alpha_initial', text='Alpha Initial')
    col.prop(projection, 'alpha_middle', text='Middle')
    col.prop(projection, 'alpha_final', text='Final')
    col = layout.column()
    col.prop(projection, 'lifetime_attack', text='Lifetime Attack')
    col.prop(projection, 'lifetime_attack_to', text='Attack To')
    col.prop(projection, 'lifetime_hold', text='Hold')
    col.prop(projection, 'lifetime_hold_to', text='Hold To')
    col.prop(projection, 'lifetime_decay', text='Decay')
    col = layout.column()
    col.prop(projection, 'attenuation_distance', text='Attenuation Distance')
    col = layout.column(align=True)
    col.prop(projection, 'lod_reduce', text='LOD Reduction')
    col.prop(projection, 'lod_cut', text='Cutoff')
    col = layout.column()
    col.prop(projection, 'static', text='Static')
    col.prop(projection, 'unknown_flag0', text='Unknown Flag 0')
    col.prop(projection, 'unknown_flag1', text='Unknown Flag 1')
    col.prop(projection, 'unknown_flag2', text='Unknown Flag 2')


class Properties(shared.M3BoneUserPropertyGroup):
    material: bpy.props.StringProperty(options=set())
    projection_type: bpy.props.EnumProperty(options=set(), items=bl_enum.projection_type)
    field_of_view: bpy.props.FloatProperty(name='Field Of View', default=45)
    aspect_ratio: bpy.props.FloatProperty(name='Aspect Ratio', default=1)
    near: bpy.props.FloatProperty(name='Near', default=0.5)
    far: bpy.props.FloatProperty(name='Far', default=10)
    depth: bpy.props.FloatProperty(default=0.5)
    height: bpy.props.FloatProperty(default=5)
    width: bpy.props.FloatProperty(default=5)
    alpha_initial: bpy.props.FloatProperty(options=set(), min=0, max=1, subtype='FACTOR')
    alpha_middle: bpy.props.FloatProperty(options=set(), min=0, max=1, default=1, subtype='FACTOR')
    alpha_final: bpy.props.FloatProperty(options=set(), min=0, max=1, subtype='FACTOR')
    lifetime_attack: bpy.props.FloatProperty(options=set(), min=0, default=1)
    lifetime_attack_to: bpy.props.FloatProperty(options=set(), min=0)
    lifetime_hold: bpy.props.FloatProperty(options=set(), min=0, default=1)
    lifetime_hold_to: bpy.props.FloatProperty(options=set(), min=0)
    lifetime_decay: bpy.props.FloatProperty(options=set(), min=0, default=1)
    attenuation_distance: bpy.props.FloatProperty(options=set(), min=0, default=1)
    layer: bpy.props.EnumProperty(options=set(), items=bl_enum.projection_layer)
    lod_cut: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    lod_reduce: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    active: bpy.props.BoolProperty(name='Active', default=True)
    static: bpy.props.BoolProperty(options=set())
    unknown_flag0: bpy.props.BoolProperty(options=set())
    unknown_flag1: bpy.props.BoolProperty(options=set())
    unknown_flag2: bpy.props.BoolProperty(options=set())


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_PROJECTIONS'
    bl_label = 'M3 Projections'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_projections', draw_props)


classes = (
    Properties,
    Panel,
)
