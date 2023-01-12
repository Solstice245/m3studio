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
    bpy.types.Object.m3_cameras = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_cameras_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)
    bpy.types.Object.m3_cameras_version = bpy.props.EnumProperty(options=set(), items=camera_versions, default='5')


camera_versions = (
    ('2', '2', 'Version 2'),
    # version 2 is largely undocumented
    ('3', '3', 'Version 3'),
    ('5', '5', 'Version 5'),
)


def update_collection_index(self, context):
    ob = context.object
    bl = ob.m3_cameras[ob.m3_cameras_index]
    shared.select_bones_handles(ob, [bl.bone])
    shared.auto_update_bone_display_mode(ob, 'CAM_')


def draw_props(camera, layout):
    version = int(camera.id_data.m3_cameras_version)

    shared.draw_pointer_prop(layout, camera.id_data.data.bones, camera, 'bone', label='Bone', icon='BONE_DATA')
    col = layout.column(align=True)
    col.prop(camera, 'field_of_view', text='Field Of View')
    col.prop(camera, 'far_clip', text='Far Clip')
    col.prop(camera, 'near_clip', text='Near Clip')
    col.prop(camera, 'clip2', text='Clip 2')
    col.prop(camera, 'focal_depth', text='Focal Depth')
    col.prop(camera, 'falloff_start', text='Falloff Start')
    col.prop(camera, 'falloff_end', text='Fallof End')
    if version >= 5:
        col.prop(camera, 'depth_of_field_type', text='Depth Of Field Type')
    col.prop(camera, 'depth_of_field', text='Depth Of Field')
    col.prop(camera, 'use_vertical_fov', text='Vertical FOV')


class Properties(shared.M3BoneUserPropertyGroup):
    field_of_view: bpy.props.FloatProperty(name='M3 Camera Field Of View', default=0.5)
    far_clip: bpy.props.FloatProperty(name='M3 Camera Far Clip', default=10)
    near_clip: bpy.props.FloatProperty(name='M3 Camera Near Clip', default=0.1)
    clip2: bpy.props.FloatProperty(name='M3 Camera Clip 2', default=10)
    focal_depth: bpy.props.FloatProperty(name='M3 Camera Focal Depth', default=2)
    falloff_start: bpy.props.FloatProperty(name='M3 Camera Falloff Start', default=1)
    falloff_end: bpy.props.FloatProperty(name='M3 Camera Falloff End', default=2)
    depth_of_field: bpy.props.FloatProperty(name='M3 Camera Depth Of Field', default=0.5)
    depth_of_field_type: bpy.props.EnumProperty(options=set(), items=bl_enum.camera_dof)
    use_vertical_fov: bpy.props.BoolProperty(options=set())


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_CAMERAS'
    bl_label = 'M3 Cameras'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_cameras, draw_props)


classes = (
    Properties,
    Panel,
)
