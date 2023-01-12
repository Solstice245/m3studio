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
    shared.select_bones_handles(ob, bl.bone)


def draw_props(joint, layout):
    shared.draw_pointer_prop(layout, joint.id_data.data.bones, joint, 'bone', label='Target Bone', icon='BONE_DATA')
    col = layout.column(align=True)
    col.prop(joint, 'joint_length', text='Joint Length')
    col.separator()
    col.prop(joint, 'search_up', text='Search Up')
    col.prop(joint, 'search_down', text='Search Down')
    col.prop(joint, 'search_speed', text='Search Speed')
    col.separator()
    col.prop(joint, 'goal_threshold', text='Goal Position Threshold')


class Properties(shared.M3PropertyGroup):
    bone: bpy.props.StringProperty(options=set())
    joint_length: bpy.props.IntProperty(options=set(), min=1)
    search_up: bpy.props.FloatProperty(options=set(), default=1)
    search_down: bpy.props.FloatProperty(options=set(), default=-2)
    search_speed: bpy.props.FloatProperty(options=set(), min=0, default=0.2)
    goal_threshold: bpy.props.FloatProperty(options=set(), min=0, default=0.05)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_IKJOINTS'
    bl_label = 'M3 Inverse Kinematics'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_ikjoints, draw_props)


classes = (
    Properties,
    Panel,
)
