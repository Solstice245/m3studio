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
    if self.m3_shadowboxes_index in range(len(self.m3_shadowboxes)):
        bl = self.m3_shadowboxes[self.m3_shadowboxes_index]
        shared.select_bones_handles(self, [bl.bone])


def draw_props(shbx, layout):
    shared.draw_prop_pointer_search(layout, shbx.bone, shbx.id_data.data, 'bones', text='Bone', icon='BONE_DATA')
    col = layout.column(align=True)
    shared.draw_prop_anim(col, shbx, 'length', text='Length')
    shared.draw_prop_anim(col, shbx, 'width', text='Width')
    shared.draw_prop_anim(col, shbx, 'height', text='Height')


class Properties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Shadow Box'

    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)
    length: bpy.props.FloatProperty(name='M3 Shadow Box Length', min=0, default=1)
    length_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    width: bpy.props.FloatProperty(name='M3 Shadow Box Width', min=0, default=1)
    width_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    height: bpy.props.FloatProperty(name='M3 Shadow Box Height', min=0, default=1)
    height_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)


class Menu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_shadowboxes'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_shadowboxes, dup_keyframes_opt=True)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_shadowboxes'
    bl_label = 'M3 Shadow Boxes'

    def draw(self, context):
        model_version = int(context.object.m3_model_version)

        if model_version >= 21:
            shared.draw_collection_list(self.layout, context.object.m3_shadowboxes, draw_props, menu_id=Menu.bl_idname)
        else:
            self.layout.label(icon='ERROR', text='M3 model version must be at least 21.')


classes = (
    Properties,
    Menu,
    Panel,
)
