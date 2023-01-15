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
    bpy.types.Object.m3_warps = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_warps_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)


def update_collection_index(self, context):
    if self.m3_warps_index in range(len(self.m3_warps)):
        bl = self.m3_warps[self.m3_warps_index]
        shared.select_bones_handles(context.object, [bl.bone])
        shared.auto_update_bone_display_mode(context.object, 'WRP_')


def draw_props(warp, layout):
    shared.draw_pointer_prop(layout, warp.id_data.data.bones, warp, 'bone', label='Bone', icon='BONE_DATA')
    col = layout.column(align=True)
    col.prop(warp, 'radius', text='Radius')
    col.prop(warp, 'strength', text='Strength')


class Properties(shared.M3BoneUserPropertyGroup):
    radius: bpy.props.FloatProperty(name='M3 Warp Radius', min=0, default=1)
    strength: bpy.props.FloatProperty(name='M3 Warp Strength', min=0, default=1)


class Menu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_warps'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_warps, dup_keyframes_opt=True)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_WARPS'
    bl_label = 'M3 Vertex Warpers'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_warps, draw_props, menu_id=Menu.bl_idname)


classes = (
    Properties,
    Menu,
    Panel,
)
