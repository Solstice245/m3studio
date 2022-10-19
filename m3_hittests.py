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
    bpy.types.Object.m3_hittest_tight = bpy.props.PointerProperty(type=shared.M3VolumePropertyGroup)
    bpy.types.Object.m3_hittests = bpy.props.CollectionProperty(type=shared.M3VolumePropertyGroup)
    bpy.types.Object.m3_hittests_index = bpy.props.IntProperty(options=set(), default=-1, update=update_bone_shapes_option)


def update_bone_shapes_option(self, context):
    if context.object.m3_options.auto_update_bone_shapes:
        if context.object.m3_options.bone_shapes != 'FTHT':
            context.object.m3_options.bone_shapes = 'FTHT'


def draw_props(hittest, layout):
    sub = layout.column(align=True)
    sub.prop(hittest, 'shape', text='Shape Type')
    if hittest.shape == 'CUBE':
        sub.prop(hittest, 'size', text='Size')
    elif hittest.shape == 'SPHERE':
        sub.prop(hittest, 'size', index=0, text='Size R')
    elif hittest.shape == 'CAPSULE':
        sub.prop(hittest, 'size', index=0, text='Size R')
        sub.prop(hittest, 'size', index=1, text='H')

    col = layout.column()
    col.prop(hittest, 'location', text='Location')
    col.prop(hittest, 'rotation', text='Rotation')
    col.prop(hittest, 'scale', text='Scale')


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_HITTESTS'
    bl_label = 'M3 Hit Test Volumes'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.label(text='Tight Hit Test:')
        shared.draw_pointer_prop(bpy.context.object, layout, 'data.bones', 'm3_hittest_tight.bone', 'Bone', 'BONE_DATA')
        draw_props(context.object.m3_hittest_tight, layout)
        layout.label(text='Fuzzy Hit Tests:')
        shared.draw_collection_list(layout, 'm3_hittests', draw_props)


classes = (
    Panel,
)
