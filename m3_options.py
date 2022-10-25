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
    bpy.types.Object.m3_options = bpy.props.PointerProperty(type=Properties)


def update_bone_shapes(self, context):
    for bone in context.object.data.bones:
        shared.set_bone_shape(context.object, bone)


class Properties(bpy.types.PropertyGroup):
    bone_shapes: bpy.props.EnumProperty(options=set(), items=bl_enum.options_bone_display, update=update_bone_shapes)
    auto_update_bone_shapes: bpy.props.BoolProperty(options=set(), default=True, description='Clicking on m3 list items changes the bone display mode')
    auto_select_bones: bpy.props.BoolProperty(options=set(), default=True, description='Clicking on m3 list items selects associated bones')


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_OBJECT_OPTIONS'
    bl_label = 'M3 Object Options'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        options = context.object.m3_options

        col = layout.column(align=True)
        col.prop(options, 'bone_shapes', text='Bone Display')
        col.prop(options, 'auto_update_bone_shapes', text='Auto Update Bone Display')


classes = (
    Properties,
    Panel,
)
