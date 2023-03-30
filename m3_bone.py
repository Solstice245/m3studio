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


desc_export_cull = 'This bone will not be exported to the M3 file if it\'s not used by any M3 data'
desc_batching = 'If a mesh material reference is bound to this bone, this property determines if the material will be rendered onto the mesh'


def register_props():
    bpy.types.Object.m3_bone_id_lockers = bpy.props.CollectionProperty(type=M3BoneHandlePropertyGroup)  # establishes which bones own their IDs
    bpy.types.Bone.bl_handle = bpy.props.StringProperty(options=set())
    bpy.types.EditBone.bl_handle = bpy.props.StringProperty(options=set())
    bpy.types.PoseBone.bl_handle = bpy.props.StringProperty(options=set(), get=get_bone_handle, set=set_bone_handle)
    bpy.types.PoseBone.m3_export_cull = bpy.props.BoolProperty(options=set(), default=True, description=desc_export_cull)
    bpy.types.PoseBone.m3_bind_scale = bpy.props.FloatVectorProperty(options=set(), size=3, subtype='XYZ', default=(1,) * 3)  # setter to prevent == 0?
    bpy.types.PoseBone.m3_location_hex_id = bpy.props.StringProperty(options=set(), maxlen=8, get=get_bone_loc_id, set=set_bone_loc_id, default='')
    bpy.types.PoseBone.m3_rotation_hex_id = bpy.props.StringProperty(options=set(), maxlen=8, get=get_bone_rot_id, set=set_bone_rot_id, default='')
    bpy.types.PoseBone.m3_scale_hex_id = bpy.props.StringProperty(options=set(), maxlen=8, get=get_bone_scl_id, set=set_bone_scl_id, default='')
    bpy.types.PoseBone.m3_batching_hex_id = bpy.props.StringProperty(options=set(), maxlen=8, get=get_bone_bat_id, set=set_bone_bat_id, default='')
    bpy.types.PoseBone.m3_batching = bpy.props.BoolProperty(name='M3 Bone Render', default=True, description=desc_batching)


def get_bone_handle(self):
    bone = self.id_data.data.bones.get(self.name)
    return bone.get('bl_handle', '')


def set_bone_handle(self, value):
    bone = self.id_data.data.bones.get(self.name)
    bone['bl_handle'] = value


bone_anim_props = ['m3_location_hex_id', 'm3_rotation_hex_id', 'm3_scale_hex_id', 'm3_batching_hex_id']


def get_bone_loc_id(self):
    return self['m3_location_hex_id']


def set_bone_loc_id(self, value):
    set_bone_hex_id(self, value, 'm3_location_hex_id')


def get_bone_rot_id(self):
    return self['m3_rotation_hex_id']


def set_bone_rot_id(self, value):
    set_bone_hex_id(self, value, 'm3_rotation_hex_id')


def get_bone_scl_id(self):
    return self['m3_scale_hex_id']


def set_bone_scl_id(self, value):
    set_bone_hex_id(self, value, 'm3_scale_hex_id')


def get_bone_bat_id(self):
    return self['m3_batching_hex_id']


def set_bone_bat_id(self, value):
    set_bone_hex_id(self, value, 'm3_batching_hex_id')


def set_bone_hex_id(self, value, prop):
    shared.m3_data_handles_verify(self.id_data.pose.bones)

    if self.bl_handle in (locker.bone for locker in self.id_data.m3_bone_id_lockers):
        try:
            self[prop] = hex(int(value, 16))[2:]
        except ValueError:
            self[prop] = shared.m3_anim_id_gen()
    else:
        locker = self.id_data.m3_bone_id_lockers.add()
        locker.bone = self.bl_handle
        for all_prop in bone_anim_props:
            self[all_prop] = shared.m3_anim_id_gen()


class M3BoneHandlePropertyGroup(bpy.types.PropertyGroup):
    bone: bpy.props.StringProperty(options=set())


class M3EditBoneAnimHeaders(bpy.types.Operator):
    bl_idname = 'm3.edit_bone_anim_headers'
    bl_label = 'Edit M3 Animation Headers'
    bl_description = 'Opens a window for editing M3 bone animation header properties'
    bl_options = {'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        # use set function of the anim id prop to get locker before it first becomes visible to user
        bpy.context.active_pose_bone.m3_location_hex_id = bpy.context.active_pose_bone.m3_location_hex_id
        return context.window_manager.invoke_props_dialog(self, width=180)

    def draw(self, context):
        pb = bpy.context.active_pose_bone
        main = self.layout.row(align=True)
        split = main.split(factor=0.5)
        row = split.row()
        col = row.column()
        col.alignment = 'RIGHT'
        col.label(text='Location ID')
        col.label(text='Rotation ID')
        col.label(text='Scaling ID')
        col.label(text='Batching ID')
        row = split.row()
        col = row.column()
        col.prop(pb, 'm3_location_hex_id', text='')
        col.prop(pb, 'm3_rotation_hex_id', text='')
        col.prop(pb, 'm3_scale_hex_id', text='')
        col.prop(pb, 'm3_batching_hex_id', text='')


class ToolPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_m3_pose_bone"
    bl_label = "M3 Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    @classmethod
    def poll(cls, context):
        return context.active_pose_bone

    def draw(self, context):
        self.layout.prop(context.active_pose_bone, 'm3_batching', text='Batching')
        col = self.layout.column(align=True)
        col.label(text='Bind Scale:')
        col.prop(context.active_pose_bone, 'm3_bind_scale', index=0, text='X')
        col.prop(context.active_pose_bone, 'm3_bind_scale', index=1, text='Y')
        col.prop(context.active_pose_bone, 'm3_bind_scale', index=2, text='Z')
        col = self.layout.column()
        col.operator('m3.edit_bone_anim_headers', icon='PREFERENCES')


class Panel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_BONE'
    bl_label = 'M3 Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'

    @classmethod
    def poll(cls, context):
        return context.active_pose_bone

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.prop(context.active_pose_bone, 'm3_batching', text='Batching')
        self.layout.prop(context.active_pose_bone, 'm3_bind_scale', text='Bind Scale')
        self.layout.operator('m3.edit_bone_anim_headers', icon='PREFERENCES')


classes = (
    M3BoneHandlePropertyGroup,
    M3EditBoneAnimHeaders,
    ToolPanel,
    Panel,
)
