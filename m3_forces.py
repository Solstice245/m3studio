#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
    bpy.types.Armature.m3_forces = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Armature.m3_forces_index = bpy.props.IntProperty(options=set(), default=-1)


def init_msgbus(arm, context):
    for force in arm.data.m3_forces:
        shared.bone_update_event(force, context)


def draw_props(force, layout):
    col = layout.column()
    col.prop(force, 'force_type', text='Type')
    col = layout.column(align=True)
    col.prop(force, 'shape', text='Shape')
    col.prop(force, 'size', text='Size')
    col = layout.column()
    col.use_property_split = False
    col.prop(force, 'channels', text='Force Channels')
    col = layout.column(align=True)
    col.prop(force, 'strength', text='Strength')
    col = layout.column_flow(align=True)
    col.prop(force, 'falloff', text='Falloff')
    col.prop(force, 'height_gradient', text='Height Gradient')
    col.prop(force, 'unbounced', text='Unbounced')


class Properties(shared.M3BoneUserPropertyGroup):
    force_type: bpy.props.EnumProperty(options=set(), items=bl_enum.force_type)
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.force_shape)
    size: bpy.props.FloatVectorProperty(name='M3 Force Size', subtype='XYZ', size=3, min=0.001, default=tuple(3 * [1]))
    channels: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=32)
    strength: bpy.props.FloatProperty(name='M3 Force Strength', default=1)
    falloff: bpy.props.BoolProperty(options=set())
    height_gradient: bpy.props.BoolProperty(options=set())
    unbounced: bpy.props.BoolProperty(options=set())


class Panel(bpy.types.Panel):
    bl_idname = 'DATA_PT_M3_FORCES'
    bl_label = 'M3 Forces'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE'

    def draw(self, context):
        shared.draw_collection_list_active(context.object.data, self.layout, 'm3_forces', draw_props)


classes = (
    Properties,
    Panel,
)
