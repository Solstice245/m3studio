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
    bpy.types.Object.m3_physicsjoints = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_physicsjoints_index = bpy.props.IntProperty(options=set(), default=-1)


def init_msgbus(ob, context):
    for joint in ob.m3_physicsjoints:
        shared.bone1_update_event(joint, context)
        shared.bone2_update_event(joint, context)


def draw_props(joint, layout):
    col = layout.column()
    shared.draw_bone_prop(joint, bpy.context.object.pose, col, 'bone1', 'Bone Joint Start')

    if joint.bone1:
        col.prop(joint, 'location1', text='Location')
        col.prop(joint, 'rotation1', text='Rotation')

    col = layout.column()
    shared.draw_bone_prop(joint, bpy.context.object.pose, col, 'bone2', 'Bone Joint End')

    if joint.bone2:
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


class Properties(shared.M3PropertyGroup):
    bone1: bpy.props.StringProperty(options=set(), update=shared.bone1_update_event)
    bone2: bpy.props.StringProperty(options=set(), update=shared.bone2_update_event)
    location1: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    location2: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    rotation1: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', size=3)
    rotation2: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', size=3)
    joint_type: bpy.props.EnumProperty(options=set(), items=bl_enum.physics_joint_type)
    limit_bool: bpy.props.BoolProperty(options=set())
    limit_min: bpy.props.FloatProperty(options=set())
    limit_max: bpy.props.FloatProperty(options=set())
    limit_angle: bpy.props.FloatProperty(options=set(), min=0)
    friction_bool: bpy.props.BoolProperty(options=set())
    friction: bpy.props.FloatProperty(options=set(), default=0.2, min=0, max=1)
    damping_ratio: bpy.props.FloatProperty(options=set(), default=0.7, min=0, max=1)
    angular_freq: bpy.props.FloatProperty(options=set(), min=0, default=5)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_PHYSICSJOINTS'
    bl_label = 'M3 Physics Joints'

    def draw(self, context):
        shared.draw_collection_list_active(context.object, self.layout, 'm3_physicsjoints', draw_props)


classes = (
    Properties,
    Panel,
)
