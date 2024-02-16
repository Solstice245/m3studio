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
from . import bl_enum, shared


def register_props():
    bpy.types.Object.m3_billboards = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_billboards_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)


def update_collection_index(self, context):
    if self.m3_billboards_index in range(len(self.m3_billboards)):
        bl = self.m3_billboards[self.m3_billboards_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_props(billboard, layout):
    layout.prop(billboard, 'billboard_type', text='Type')
    layout.prop(billboard, 'camera_look_at', text='Look At Camera Center')
    layout.prop(billboard, 'up', text='Upward Vector')
    layout.prop(billboard, 'forward', text='Forward Vector')


class Properties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Billboard'

    bone: bpy.props.PointerProperty(type=shared.M3BonePointerPropExclusive)
    billboard_type: bpy.props.EnumProperty(options=set(), items=bl_enum.billboard_type, default='FULL')
    camera_look_at: bpy.props.BoolProperty(options=set())
    up: bpy.props.FloatVectorProperty(options=set(), size=3, subtype='EULER', unit='ROTATION')
    forward: bpy.props.FloatVectorProperty(options=set(), size=3, subtype='EULER', unit='ROTATION')


class Menu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_billboards'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_billboards, dup_keyframes_opt=False)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_BILLBOARDS'
    bl_label = 'M3 Billboards'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_billboards, draw_props, ui_list_id='UI_UL_M3_bone_user', menu_id=Menu.bl_idname)


classes = (
    Properties,
    Menu,
    Panel,
)
