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
    bpy.types.Object.m3_animations = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_animations_index = bpy.props.IntProperty(options=set(), default=-1)


def draw_transform_collection_props(transform_collection, layout):
    layout.prop(transform_collection, 'concurrent', text='Concurrent')
    layout.prop(transform_collection, 'priority', text='Priority')


def draw_props(anim, layout):
    col = layout.column(align=True)
    col.prop(anim, 'frame_start', text='Frame Start')
    col.prop(anim, 'frame_end', text='End')
    row = layout.row(heading='Simulate Physics')
    row.prop(anim, 'simulate', text='')
    col = row.column()
    col.active = anim.simulate
    col.prop(anim, 'simulate_frame', text='On Frame')
    col = layout.column()
    col.prop(anim, 'frequency', text='Frequency')
    col.prop(anim, 'movement_speed', text='Movement Speed')
    col.prop(anim, 'not_looping', text='Does Not Loop')
    col.prop(anim, 'always_global', text='Always Global')
    col.prop(anim, 'global_in_previewer', text='Global In Previewer')

    shared.draw_collection_stack(
        layout=layout, collection_path='m3_animations[{}].transform_collection'.format(anim.bl_index), label='Animation Group',
        draw_func=draw_transform_collection_props, use_name=True, can_duplicate=False,
    )


class DataPathProperties(bpy.types.PropertyGroup):
    val: bpy.props.StringProperty(options=set())


class TransformCollectionProperties(shared.M3PropertyGroup):
    priority: bpy.props.IntProperty(options=set(), min=0)
    concurrent: bpy.props.BoolProperty(options=set())
    data_paths: bpy.props.CollectionProperty(type=DataPathProperties)


class Properties(shared.M3PropertyGroup):
    frame_start: bpy.props.IntProperty(options=set(), min=0)
    frame_end: bpy.props.IntProperty(options=set(), min=0, default=60)
    simulate: bpy.props.BoolProperty(options=set())
    simulate_frame: bpy.props.IntProperty(options=set())
    movement_speed: bpy.props.FloatProperty(options=set())
    frequency: bpy.props.IntProperty(options=set(), min=0)
    not_looping: bpy.props.BoolProperty(options=set())
    always_global: bpy.props.BoolProperty(options=set())
    global_in_previewer: bpy.props.BoolProperty(options=set())
    transform_collection: bpy.props.CollectionProperty(type=TransformCollectionProperties)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ANIMATIONS'
    bl_label = 'M3 Animations'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_animations', draw_props)


classes = (
    DataPathProperties,
    TransformCollectionProperties,
    Properties,
    Panel,
)
