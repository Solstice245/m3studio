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


desc_export_cull = 'This bone will not be exported to the M3 file if it\'s not used by any M3 data'


def register_props():
    bpy.types.Bone.bl_handle = bpy.props.StringProperty(options=set())
    bpy.types.Bone.m3_bind_scale = bpy.props.FloatVectorProperty(options=set(), size=3, subtype='XYZ', min=0.000001, default=(1,) * 3)
    bpy.types.Bone.m3_export_cull = bpy.props.BoolProperty(options=set(), default=True, description=desc_export_cull)
    bpy.types.EditBone.bl_handle = bpy.props.StringProperty(options=set())
    bpy.types.EditBone.m3_bind_scale = bpy.props.FloatVectorProperty(options=set(), size=3, subtype='XYZ', min=0.000001, default=(1,) * 3)
    bpy.types.EditBone.m3_export_cull = bpy.props.BoolProperty(options=set(), default=True, description=desc_export_cull)


class Panel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_BONE'
    bl_label = 'M3 Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'

    @classmethod
    def poll(cls, context):
        return context.bone

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.prop(context.bone, 'm3_bind_scale', text='Bind Scale')


classes = (
    Panel,
)
