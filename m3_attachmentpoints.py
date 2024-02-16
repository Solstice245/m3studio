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
from bpy.app.handlers import persistent
from . import shared
from . import bl_enum


def register_props():
    # prop_search can only operate on Blender collections
    bpy.types.Scene.m3_attachment_names = bpy.props.CollectionProperty(type=AttachmentNameProperties)
    bpy.types.Object.m3_attachmentpoints = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_attachmentpoints_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)


@persistent
def attachment_name_list_verify(self, context):
    for scene in bpy.data.scenes:
        scene.m3_attachment_names.clear()
        for name in bl_enum.attachment_names:
            scene.m3_attachment_names.add().name = name


@persistent
def attachmentpoint_names_fix(self, context):
    for ob in bpy.data.objects:
        for point in ob.m3_attachmentpoints:
            if not (point.name.startswith('Ref_') or point.name.startswith('Pos_')):
                point.name = 'Ref_' + point.name


class AttachmentNameProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(options=set())


def update_collection_index(self, context):
    if self.m3_attachmentpoints_index in range(len(self.m3_attachmentpoints)):
        bl = self.m3_attachmentpoints[self.m3_attachmentpoints_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_props(point, layout):
    layout.prop_search(point, 'name', bpy.context.scene, 'm3_attachment_names', text='Name')
    shared.draw_prop_pointer_search(layout, point.bone, point.id_data.data, 'bones', text='Bone', icon='BONE_DATA')
    shared.draw_collection_list(layout.box(), point.volumes, shared.draw_volume_props, menu_id=VolumeMenu.bl_idname, label='Volumes:')


class VolumeMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_attachmentvolumes'
    bl_label = 'Menu'

    def draw(self, context):
        point = context.object.m3_attachmentpoints[context.object.m3_attachmentpoints_index]
        shared.draw_menu_duplicate(self.layout, point.volumes, dup_keyframes_opt=False)


class PointMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_attachmentpoints'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_attachmentpoints, dup_keyframes_opt=False)


class Properties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Attachment Point'

    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)
    volumes: bpy.props.CollectionProperty(type=shared.M3VolumePropertyGroup)
    volumes_index: bpy.props.IntProperty(options=set(), default=-1)


class AttachmentList(bpy.types.UIList):
    bl_idname = 'UI_UL_M3_attachmentpoints'

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ATTACHMENTPOINTS'
    bl_label = 'M3 Attachment Points'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_attachmentpoints, draw_props, ui_list_id=AttachmentList.bl_idname, menu_id=PointMenu.bl_idname)


classes = (
    AttachmentNameProperties,
    Properties,
    VolumeMenu,
    PointMenu,
    AttachmentList,
    Panel,
)
