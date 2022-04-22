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
    bpy.types.Object.m3_tighthittest = bpy.props.PointerProperty(type=shared.M3VolumePropertyGroup)
    bpy.types.Object.m3_hittests = bpy.props.CollectionProperty(type=shared.M3VolumePropertyGroup)
    bpy.types.Object.m3_hittests_index = bpy.props.IntProperty(options=set(), default=-1)


def init_msgbus(ob, context):
    shared.bone_update_event(ob.m3_tighthittest)
    for hittest in ob.m3_hittests:
        shared.bone_update_event(hittest, context)


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
        shared.draw_bone_prop(context.object.m3_tighthittest, context.object, layout)
        draw_props(context.object.m3_tighthittest, layout)
        layout.label(text='Fuzzy Hit Tests:')
        shared.draw_collection_list(layout, 'm3_hittests', draw_props)


classes = (
    Panel,
)
