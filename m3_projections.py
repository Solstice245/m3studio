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
    if self.m3_projections_index in range(len(self.m3_projections)):
        bl = self.m3_projections[self.m3_projections_index]
        shared.select_bones_handles(context.object, [bl.bone])
        shared.auto_update_bone_display_mode(context.object, 'PROJ')


def draw_props(projection, layout):
    col = layout.column()
    shared.draw_pointer_prop(col, projection.id_data.data.bones, projection, 'bone', label='Bone', icon='BONE_DATA')
    shared.draw_pointer_prop(col, projection.id_data.m3_materialrefs, projection, 'material', label='Material', icon='MATERIAL')
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
    col.prop(projection, 'box_offset_z_bottom', text='Bottom')
    col.prop(projection, 'box_offset_z_top', text='Top')
    col.prop(projection, 'box_offset_x_left', text='Left')
    col.prop(projection, 'box_offset_x_right', text='Right')
    col.prop(projection, 'box_offset_y_front', text='Front')
    col.prop(projection, 'box_offset_y_back', text='Back')
    col = layout.column(align=True)
    col.prop(projection, 'alpha_init', text='Alpha Initial')
    col.prop(projection, 'alpha_mid', text='Middle')
    col.prop(projection, 'alpha_end', text='Final')
    col = layout.column()
    col.prop(projection, 'lifetime_attack', text='Lifetime Attack')
    col.prop(projection, 'lifetime_attack_to', text='Attack To')
    col.prop(projection, 'lifetime_hold', text='Hold')
    col.prop(projection, 'lifetime_hold_to', text='Hold To')
    col.prop(projection, 'lifetime_decay', text='Decay')
    col.prop(projection, 'lifetime_decay_to', text='Decay To')
    col = layout.column()
    col.prop(projection, 'attenuation_distance', text='Attenuation Distance')
    col = layout.column(align=True)
    col.prop(projection, 'lod_reduce', text='LOD Reduction')
    col.prop(projection, 'lod_cut', text='Cutoff')
    col = layout.column()
    col.prop(projection, 'static', text='Static')
    col.prop(projection, 'unknown_flag0x2', text='Unknown Flag 0')
    col.prop(projection, 'unknown_flag0x4', text='Unknown Flag 1')
    col.prop(projection, 'unknown_flag0x8', text='Unknown Flag 2')


class Properties(shared.M3BoneUserPropertyGroup):
    material: bpy.props.StringProperty(options=set())
    projection_type: bpy.props.EnumProperty(options=set(), items=bl_enum.projection_type)
    field_of_view: bpy.props.FloatProperty(name='M3 Splat Field Of View', default=45)
    aspect_ratio: bpy.props.FloatProperty(name='M3 Splat Aspect Ratio', default=1)
    near: bpy.props.FloatProperty(name='M3 Splat Near', default=0.5)
    far: bpy.props.FloatProperty(name='M3 Splat Far', default=10)
    box_offset_z_bottom: bpy.props.FloatProperty(name='M3 Splat Bottom', default=-0.25)
    box_offset_z_top: bpy.props.FloatProperty(name='M3 Splat Top', default=0.25)
    box_offset_x_left: bpy.props.FloatProperty(name='M3 Splat Left', default=-2)
    box_offset_x_right: bpy.props.FloatProperty(name='M3 Splat Right', default=2)
    box_offset_y_front: bpy.props.FloatProperty(name='M3 Splat Front', default=2)
    box_offset_y_back: bpy.props.FloatProperty(name='M3 Splat Back', default=-2)
    alpha_init: bpy.props.FloatProperty(options=set(), min=0, max=1, subtype='FACTOR')
    alpha_mid: bpy.props.FloatProperty(options=set(), min=0, max=1, default=1, subtype='FACTOR')
    alpha_end: bpy.props.FloatProperty(options=set(), min=0, max=1, subtype='FACTOR')
    lifetime_attack: bpy.props.FloatProperty(options=set(), min=0, default=1)
    lifetime_attack_to: bpy.props.FloatProperty(options=set(), min=0)
    lifetime_hold: bpy.props.FloatProperty(options=set(), min=0, default=1)
    lifetime_hold_to: bpy.props.FloatProperty(options=set(), min=0)
    lifetime_decay: bpy.props.FloatProperty(options=set(), min=0, default=1)
    lifetime_decay_to: bpy.props.FloatProperty(options=set(), min=0)
    attenuation_distance: bpy.props.FloatProperty(options=set(), min=0, default=1)
    layer: bpy.props.EnumProperty(options=set(), items=bl_enum.projection_layer)
    lod_cut: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    lod_reduce: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    active: bpy.props.BoolProperty(name='Active', default=True)
    static: bpy.props.BoolProperty(options=set())
    unknown_flag0x2: bpy.props.BoolProperty(options=set())
    unknown_flag0x4: bpy.props.BoolProperty(options=set())
    unknown_flag0x8: bpy.props.BoolProperty(options=set())


class Menu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_projections'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_projections, dup_keyframes_opt=True)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_PROJECTIONS'
    bl_label = 'M3 Projections'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_projections, draw_props, menu_id=Menu.bl_idname)


classes = (
    Properties,
    Menu,
    Panel,
)
