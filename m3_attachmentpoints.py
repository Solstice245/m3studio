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
    bpy.types.Object.m3_attachmentpoints = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_attachmentpoints_index = bpy.props.IntProperty(options=set(), default=-1)


def init_msgbus(ob, context):
    for point in ob.m3_attachmentpoints:
        shared.bone_update_event(point, context)
        for volume in point.volumes:
            shared.bone_update_event(volume, context)


def draw_volume_props(volume, layout):
    sub = layout.column(align=True)
    sub.prop(volume, 'shape', text='Shape Type')
    if volume.shape == 'CUBE':
        sub.prop(volume, 'size', text='Size')
    elif volume.shape == 'SPHERE':
        sub.prop(volume, 'size', index=0, text='Size R')
    elif volume.shape == 'CAPSULE':
        sub.prop(volume, 'size', index=0, text='Size R')
        sub.prop(volume, 'size', index=1, text='H')
    if volume.shape in ['CUBE', 'SPHERE', 'CAPSULE']:
        col = layout.column()
        col.prop(volume, 'location', text='Location')
        col.prop(volume, 'rotation', text='Rotation')
        col.prop(volume, 'scale', text='Scale')


def draw_props(point, layout):
    shared.draw_subcollection_list(point, layout, 'm3_attachmentpoints', 'volumes', 'Volume', draw_volume_props)


class Properties(shared.M3BoneUserPropertyGroup):
    volumes: bpy.props.CollectionProperty(type=shared.M3VolumePropertyGroup)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ATTACHMENTPOINTS'
    bl_label = 'M3 Attachment Points'

    def draw(self, context):
        shared.draw_collection_list_active(context.object, self.layout, 'm3_attachmentpoints', draw_props)


classes = (
    Properties,
    Panel,
)
