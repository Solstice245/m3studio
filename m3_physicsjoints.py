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
    bpy.types.Armature.m3_physicsjoints = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Armature.m3_physicsjoints_index = bpy.props.IntProperty(options=set(), default=-1)


def init_msgbus(arm, context):
    for joint in arm.data.m3_physicsjoints:
        shared.bone1_update_event(joint, context)
        shared.bone2_update_event(joint, context)


def bone1_update_callback(m3, bone):
    m3.bl_update = False
    m3.bone1 = bone.name
    m3.bl_update = True


def bone1_update_event(self, context):
    if not self.bl_update:
        return

    data = context.object.data
    bone = data.bones[self.bone1]
    if bone:
        bpy.msgbus.clear_by_owner(self.bone1)
        bpy.msgbus.subscribe_rna(
            key=bone.path_resolve('name', False),
            owner=self.bone1,
            args=(self, bone),
            notify=bone1_update_callback,
            options={'PERSISTENT'}
        )
    else:
        bpy.msgbus.clear_by_owner(self.bone1)


def bone2_update_callback(m3, bone):
    m3.bl_update = False
    m3.bone2 = bone.name
    m3.bl_update = True


def bone2_update_event(self, context):
    if not self.bl_update:
        return

    data = context.object.data
    bone = data.bones[self.bone2]
    if bone:
        bpy.msgbus.clear_by_owner(self.bone2)
        bpy.msgbus.subscribe_rna(
            key=bone.path_resolve('name', False),
            owner=self.bone2,
            args=(self, bone),
            notify=bone2_update_callback,
            options={'PERSISTENT'}
        )
    else:
        bpy.msgbus.clear_by_owner(self.bone2)


def draw_props(joint, layout):
    col = layout.column()
    col.prop_search(joint, 'bone1', bpy.context.object.pose, 'bones', text='Bone Joint Start')

    if not joint.bone1:
        row = col.row()
        row.label(text='')
        row.label(text='Invalid bone.', icon='ERROR')
        row.label(text='')
    else:
        col.prop(joint, 'location1', text='Location')
        col.prop(joint, 'rotation1', text='Rotation')

    col = layout.column()
    col.prop_search(joint, 'bone2', bpy.context.object.pose, 'bones', text='Bone Joint End')

    if not joint.bone2:
        row = col.row()
        row.label(text='')
        row.label(text='Invalid bone.', icon='ERROR')
        row.label(text='')
    else:
        col.prop(joint, 'location2', text='Location')
        col.prop(joint, 'rotation2', text='Rotation')

    col = layout.column(align=True)
    col.prop(joint, 'joint_type', text='Joint Type')

    if joint.joint_type == 'SPHERE':
        pass
    elif joint.joint_type == 'REVOLVE':
        col.prop(joint, 'limit_bool', text='Limit Rotation')
        sub = col.column(align=True)
        sub.active = joint.limit_bool
        sub.prop(joint, 'limit_min', text='Minimum')
        sub.prop(joint, 'limit_max', text='Maximum')
    elif joint.joint_type == 'CONE':
        col.prop(joint, 'limit_angle', text='Limit Angle')

    if joint.joint_type == 'WELD':
        col.prop(joint, 'angular_freq', text='Angular Frequency')
        col.prop(joint, 'damping_ratio', text='Damping Ratio')
    else:
        col.prop(joint, 'friction_bool', text='Friction')
        sub = col.column(align=True)
        sub.active = joint.friction_bool
        sub.prop(joint, 'friction', text='Amount')


class Properties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(options=set())
    bone1: bpy.props.StringProperty(options=set())
    bone2: bpy.props.StringProperty(options=set())
    location1: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    location2: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    rotation1: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', size=3)
    rotation2: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', size=3)
    joint_type: bpy.props.EnumProperty(options=set(), items=enum.physics_joint_type)
    limit_bool: bpy.props.BoolProperty(options=set())
    limit_min: bpy.props.FloatProperty(options=set())
    limit_max: bpy.props.FloatProperty(options=set())
    limit_angle: bpy.props.FloatProperty(options=set(), min=0)
    friction_bool: bpy.props.BoolProperty(options=set())
    friction: bpy.props.FloatProperty(options=set(), default=0.2, min=0, max=1)
    damping_ratio: bpy.props.FloatProperty(options=set(), default=0.7, min=0, max=1)
    angular_freq: bpy.props.FloatProperty(options=set(), min=0, default=5)


class Panel(bpy.types.Panel):
    bl_idname = 'DATA_PT_M3_PHYSICSJOINTS'
    bl_label = 'M3 Physics Joints'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE'

    def draw(self, context):
        shared.draw_collection_list_active(context.object.data, self.layout, 'm3_physicsjoints', draw_props)


classes = (
    Properties,
    Panel,
)