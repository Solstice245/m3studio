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
from . import enum


def register_props():
    bpy.types.Armature.m3_billboards = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Armature.m3_billboards_index = bpy.props.IntProperty(options=set(), default=-1)


def init_msgbus(arm, context):
    for billboard in arm.data.m3_billboards:
        shared.bone_update_event(billboard, context)


def draw_props(billboard, layout):
    layout.prop(billboard, 'billboard_type', text='Type')
    layout.prop(billboard, 'look', text='Look At Camera Center')


class Properties(shared.M3BoneUserPropertyGroup):
    billboard_type: bpy.props.EnumProperty(options=set(), items=enum.billboard_type, default='FULL')
    look: bpy.props.BoolProperty(options=set())


class Panel(bpy.types.Panel):
    bl_idname = 'DATA_PT_M3_BILLBOARDS'
    bl_label = 'M3 Billboards'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE'

    def draw(self, context):
        shared.draw_collection_list_active(context.object.data, self.layout, 'm3_billboards', draw_props)


classes = (
    Properties,
    Panel,
)