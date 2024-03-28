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
from . import bl_enum
from . import shared


def register_props():
    bpy.types.Object.m3_hittest_tight = bpy.props.PointerProperty(type=Properties)
    bpy.types.Object.m3_hittests = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_hittests_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)


def update_collection_index(self, context):
    if self.m3_hittests_index in range(len(self.m3_hittests)):
        bl = self.m3_hittests[self.m3_hittests_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_props(hittest, layout):
    shared.draw_prop_pointer_search(layout, hittest.bone, hittest.id_data.data, 'bones', text='Bone', icon='BONE_DATA')
    shared.draw_volume_props(hittest, layout)


class Properties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Hit Test Volume'

    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.volume_shape)
    size: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3)
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    mesh_object: bpy.props.PointerProperty(type=bpy.types.Object)


class Menu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_hittests'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_hittests, dup_keyframes_opt=False)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_HITTESTS'
    bl_label = 'M3 Hit Test Volumes'

    def draw(self, context):
        layout = self.layout
        ob = context.object
        layout.use_property_split = True
        layout.label(text='Tight Hit Test:')
        draw_props(ob.m3_hittest_tight, layout)
        layout.label(text='Fuzzy Hit Tests:')
        shared.draw_collection_list(layout, ob.m3_hittests, draw_props, menu_id=Menu.bl_idname)


classes = (
    Properties,
    Menu,
    Panel,
)
