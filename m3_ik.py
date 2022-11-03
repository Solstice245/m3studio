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


def register_props():
    bpy.types.Object.m3_ikjoints = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_ikjoints_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)


def update_collection_index(self, context):
    ob = context.object
    bl = ob.m3_ikjoints[ob.m3_ikjoints_index]
    shared.select_bones_handles(ob, [bl.bone1, bl.bone2])


def draw_props(joint, layout):
    col = layout.column(align=True)

    shared.draw_pointer_prop(bpy.context.object, col, 'data.bones', 'm3_ikjoints[{}].bone1'.format(joint.bl_index), 'Bone Joint Start', 'BONE_DATA')
    shared.draw_pointer_prop(bpy.context.object, col, 'data.bones', 'm3_ikjoints[{}].bone2'.format(joint.bl_index), 'Bone Joint End', 'BONE_DATA')

    col = layout.column(align=True)
    col.prop(joint, 'search_up', text='Search Up')
    col.prop(joint, 'search_down', text='Search Down')
    col.prop(joint, 'search_speed', text='Search Speed')
    col = layout.column()
    col.prop(joint, 'goal_threshold', text='Goal Position Threshold')


class Properties(shared.M3PropertyGroup):
    bone1: bpy.props.StringProperty(options=set())
    bone2: bpy.props.StringProperty(options=set())
    search_up: bpy.props.FloatProperty(options=set())
    search_down: bpy.props.FloatProperty(options=set())
    search_speed: bpy.props.FloatProperty(options=set(), min=0)
    goal_threshold: bpy.props.FloatProperty(options=set(), min=0)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_IKJOINTS'
    bl_label = 'M3 Inverse Kinematics'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_ikjoints', draw_props)


classes = (
    Properties,
    Panel,
)
