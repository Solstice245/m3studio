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
    bpy.types.Object.m3_ikchains = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_ikchains_index = bpy.props.IntProperty(options=set(), default=-1)


def init_msgbus(ob, context):
    for chain in ob.m3_ikchains:
        shared.bone1_update_event(chain, context)
        shared.bone2_update_event(chain, context)


def draw_props(chain, layout):
    col = layout.column(align=True)

    shared.draw_bone_prop(chain, bpy.context.object.pose, col, 'bone1', 'Bone Chain Start')
    shared.draw_bone_prop(chain, bpy.context.object.pose, col, 'bone2', 'Bone Chain End')

    col = layout.column(align=True)
    col.prop(chain, 'max_search_up', text='Max Search Up')
    col.prop(chain, 'max_search_down', text='Max Search Down')
    col.prop(chain, 'max_search_speed', text='Max Search Speed')
    col = layout.column()
    col.prop(chain, 'goal_threshold', text='Goal Position Threshold')


class Properties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(options=set())
    bone1: bpy.props.StringProperty(options=set(), update=shared.bone1_update_event)
    bone2: bpy.props.StringProperty(options=set(), update=shared.bone2_update_event)
    max_search_up: bpy.props.FloatProperty(options=set())
    max_search_down: bpy.props.FloatProperty(options=set())
    max_search_speed: bpy.props.FloatProperty(options=set(), min=0)
    goal_threshold: bpy.props.FloatProperty(options=set(), min=0)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_IKCHAINS'
    bl_label = 'M3 Inverse Kinematics'

    def draw(self, context):
        shared.draw_collection_list_active(context.object, self.layout, 'm3_ikchains', draw_props)


classes = (
    Properties,
    Panel,
)
