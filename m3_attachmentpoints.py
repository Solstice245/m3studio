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
    bpy.types.Object.m3_attachmentpoints_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)


def update_collection_index(self, context):
    if self.m3_attachmentpoints_index in range(len(self.m3_attachmentpoints)):
        bl = self.m3_attachmentpoints[self.m3_attachmentpoints_index]
        shared.select_bones_handles(context.object, [bl.bone])
        shared.auto_update_bone_display_mode(context.object, 'ATT_')


def draw_props(point, layout):
    shared.draw_pointer_prop(layout, point.id_data.data.bones, point, 'bone', label='Bone', icon='BONE_DATA')
    shared.draw_collection_list(layout.box(), point.volumes, shared.draw_volume_props, menu_id=VolumeMenu.bl_idname, label='Volumes:')


class VolumeMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_attachmentvolumes'
    bl_label = 'Menu'

    def draw(self, context):
        point = context.object.m3_attachmentpoints[context.object.m3_attachmentpoints_index]
        shared.draw_menu_duplicate(self.layout, point.volumes, dup_keyframes_opt=False)


class PointMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_attachmentpoints'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_attachmentpoints, dup_keyframes_opt=False)


class Properties(shared.M3BoneUserPropertyGroup):
    volumes: bpy.props.CollectionProperty(type=shared.M3VolumePropertyGroup)
    volumes_index: bpy.props.IntProperty(options=set(), default=-1)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ATTACHMENTPOINTS'
    bl_label = 'M3 Attachment Points'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_attachmentpoints, draw_props, menu_id=PointMenu.bl_idname)


classes = (
    Properties,
    VolumeMenu,
    PointMenu,
    Panel,
)
