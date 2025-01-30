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
    bpy.types.Object.m3_tmd = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_tmd_index = bpy.props.IntProperty(options=set(), default=-1)


def draw_props(tmd, layout):
    layout.prop(tmd, 'unknownd3f6c7b8', text='Unknown 0')
    layout.prop(tmd, 'unknown74229b33', text='Unknown 1')
    layout.prop(tmd, 'unknownd4f91286', text='Unknown 2')
    layout.prop(tmd, 'unknown77f047c2', text='Unknown 3')
    layout.prop(tmd, 'unknownbc1e64c1', text='Unknown 4')
    layout.prop(tmd, 'unknown6cd3476c', text='Unknown 5')
    layout.prop(tmd, 'unknownccd5a5af', text='Unknown 6')


class VecProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Vector'

    vector: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)


class Properties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 TMD'

    vectors: bpy.props.CollectionProperty(type=VecProperties)
    unknownd3f6c7b8: bpy.props.FloatProperty(options=set())
    unknown74229b33: bpy.props.FloatProperty(options=set())
    unknownd4f91286: bpy.props.FloatProperty()
    unknownd4f91286_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    unknown77f047c2: bpy.props.FloatProperty()
    unknown77f047c2_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    unknownbc1e64c1: bpy.props.IntProperty(options=set(), default=1)
    unknown6cd3476c: bpy.props.IntProperty(options=set(), default=0)
    unknownccd5a5af: bpy.props.IntProperty(options=set(), default=0)


class Menu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_M3_tmd'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_tmd, dup_keyframes_opt=False)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_TMD'
    bl_label = 'M3 TMD Data'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_tmd, draw_props, menu_id=Menu.bl_idname)


classes = (
    VecProperties,
    Properties,
    # Menu,
    # Panel,
)
