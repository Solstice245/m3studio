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
    bpy.types.Object.m3_shadowboxes = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_shadowboxes_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)


def update_collection_index(self, context):
    ob = context.object
    bl = ob.m3_shadowboxes[ob.m3_shadowboxes_index]
    shared.select_bones_handles(ob, [bl.bone])
    shared.auto_update_bone_display_mode(ob, 'SHBX')


def draw_props(shbx, layout):
    shared.draw_pointer_prop(layout, shbx.id_data.data.bones, shbx, 'bone', bone_search=True, label='Bone', icon='BONE_DATA')
    col = layout.column(align=True)
    col.prop(shbx, 'length', text='Length')
    col.prop(shbx, 'width', text='Width')
    col.prop(shbx, 'height', text='Height')


class Properties(shared.M3BoneUserPropertyGroup):
    length: bpy.props.FloatProperty(name='M3 Shadow Box Length', min=0, default=1, update=shared.bone_shape_update_event)
    width: bpy.props.FloatProperty(name='M3 Shadow Box Width', min=0, default=1, update=shared.bone_shape_update_event)
    height: bpy.props.FloatProperty(name='M3 Shadow Box Height', min=0, default=1, update=shared.bone_shape_update_event)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_shadowboxes'
    bl_label = 'M3 Shadow Boxes'

    def draw(self, context):
        model_version = int(context.object.m3_model_version)

        if model_version >= 21:
            shared.draw_collection_list(self.layout, context.object.m3_shadowboxes, draw_props)
        else:
            self.layout.label(icon='ERROR', text='M3 model version must be at least 21.')


classes = (
    Properties,
    Panel,
)
