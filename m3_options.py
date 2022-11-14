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


def update_bone_display_mode(self, context):
    for bone in context.object.data.bones:
        shared.set_bone_shape(context.object, bone)


desc_auto_bone_display_mode = 'Clicking on m3 list items changes the bone display mode, when applicable'
desc_auto_update_bone_selection = 'Clicking on m3 list items selects associated bones, when applicable'
desc_auto_update_timeline = 'Clicking on an m3 animation group sets the end points of the timeline to its beginning and ending frames'
desc_auto_update_action = 'Clicking on an m3 animation sets the action of the object'


class Properties(bpy.types.PropertyGroup):
    bone_display_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.options_bone_display, update=update_bone_display_mode)
    auto_update_bone_display_mode: bpy.props.BoolProperty(options=set(), default=True, description=desc_auto_bone_display_mode)
    auto_update_bone_selection: bpy.props.BoolProperty(options=set(), default=True, description=desc_auto_update_bone_selection)
    auto_update_timeline: bpy.props.BoolProperty(options=set(), default=True, description=desc_auto_update_timeline)
    auto_update_action: bpy.props.BoolProperty(options=set(), default=True, description=desc_auto_update_action)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_OBJECT_OPTIONS'
    bl_label = 'M3 Object Options'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        options = context.object.m3_options

        col = layout.column(align=True)
        col.prop(options, 'bone_display_mode', text='Bone Display')
        col.prop(options, 'auto_update_bone_display_mode', text='Auto Update Bone Display')
        col.prop(options, 'auto_update_bone_selection', text='Auto Update Bone Selection')
        col.separator()
        col.prop(options, 'auto_update_timeline', text='Auto Update Animation Timeline')
        col.prop(options, 'auto_update_action', text='Auto Update Animation Action')


classes = (
    Properties,
    Panel,
)
