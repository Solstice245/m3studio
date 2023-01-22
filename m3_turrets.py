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
    bpy.types.Object.m3_turrets = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_turrets_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)
    bpy.types.Object.m3_turrets_part_version = bpy.props.EnumProperty(options=set(), items=turret_part_versions, default='4')


turret_part_versions = (
    ('1', '1', 'Version 1'),
    ('4', '4', 'Version 4'),
)


def update_collection_index(self, context):
    if self.m3_turrets_index in range(len(self.m3_turrets)):
        bl = self.m3_turrets[self.m3_turrets_index]
        shared.select_bones_handles(context.object, [part.bone for part in bl.parts])


def update_parts_collection_index(self, context):
    if self.parts_index in range(len(self.parts)):
        bl = self.parts[self.parts_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_part_props(part, layout):
    version = int(part.id_data.m3_turrets_part_version)

    shared.draw_prop_pointer(layout, part.id_data.pose.bones, part, 'bone', label='Bone', icon='BONE_DATA')
    col = layout.column()
    col.prop(part, 'group_id', text='Part Group')
    col.prop(part, 'main_part', text='Main Part')

    if version >= 4:
        col.prop(part, 'forward_x', text='Forward Vector X')
        col.prop(part, 'forward_y', text='Forward Vector Y')
        col.prop(part, 'forward_z', text='Forward Vector Z')
    else:
        col.prop(part, 'matrix', text='Matrix')

    col = layout.column()
    col.separator()
    col.prop(part, 'yaw_weight', text='Yaw Weight')
    col.prop(part, 'yaw_limited', text='Limit Yaw')
    sub = col.column()
    sub.active = part.yaw_limited
    sub.prop(part, 'yaw_min', text='Yaw Minimum')
    sub.prop(part, 'yaw_max', text='Yaw Maximum')
    col = layout.column()
    col.separator()
    col.prop(part, 'pitch_weight', text='Pitch Weight')
    col.prop(part, 'pitch_limited', text='Limit Pitch')
    sub = col.column()
    sub.active = part.pitch_limited
    sub.prop(part, 'pitch_min', text='Pitch Minimum')
    sub.prop(part, 'pitch_max', text='Pitch Maximum')
    col = layout.column(align=True)
    col.separator()
    col.prop(part, 'unknown132')
    col.prop(part, 'unknown136')


def draw_props(turret, layout):
    shared.draw_collection_list(layout.box(), turret.parts, draw_part_props, menu_id=PartMenu.bl_idname)


def turret_part_main_get(self):
    if self.get('main_part'):
        return self['main_part']
    else:
        return False


def turret_part_main_set(self, value):
    if value:
        for part in self.id_data.path_resolve(self.path_from_id().rsplit('[', 1)[0]):
            if part.group_id == self.group_id:
                part['main_part'] = False
    self['main_part'] = value


def turret_part_group_id_get(self):
    if self.get('group_id'):
        return self['group_id']
    else:
        return 1


def turret_part_group_id_set(self, value):
    if self.get('main_part'):
        if self.main_part:
            for part in self.id_data.path_resolve(self.path_from_id().rsplit('[', 1)[0]):
                if part.group_id == value:
                    part['main_part'] = False
    self['group_id'] = value


class PartProperties(shared.M3BoneUserPropertyGroup):
    forward_x: bpy.props.FloatVectorProperty(options=set(), size=4, default=(0, -1, 0, 0))
    forward_y: bpy.props.FloatVectorProperty(options=set(), size=4, default=(1, 0, 0, 0))
    forward_z: bpy.props.FloatVectorProperty(options=set(), size=4, default=(0, 0, 1, 0))
    main_part: bpy.props.BoolProperty(options=set(), get=turret_part_main_get, set=turret_part_main_set)
    group_id: bpy.props.IntProperty(options=set(), get=turret_part_group_id_get, set=turret_part_group_id_set, subtype='UNSIGNED', min=1, max=255)
    yaw_weight: bpy.props.FloatProperty(options=set(), min=0, max=1, default=1, subtype='FACTOR')
    yaw_limited: bpy.props.BoolProperty(options=set())
    yaw_min: bpy.props.FloatProperty(options=set(), subtype='ANGLE')
    yaw_max: bpy.props.FloatProperty(options=set(), subtype='ANGLE')
    pitch_weight: bpy.props.FloatProperty(options=set(), min=0, max=1, default=1, subtype='FACTOR')
    pitch_limited: bpy.props.BoolProperty(options=set())
    pitch_min: bpy.props.FloatProperty(options=set(), subtype='ANGLE')
    pitch_max: bpy.props.FloatProperty(options=set(), subtype='ANGLE')
    unknown132: bpy.props.FloatProperty(options=set())
    unknown136: bpy.props.FloatProperty(options=set())


class Properties(shared.M3PropertyGroup):
    parts: bpy.props.CollectionProperty(type=PartProperties)
    parts_index: bpy.props.IntProperty(options=set(), default=-1, update=update_parts_collection_index)


class PartMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_parts'
    bl_label = 'Menu'

    def draw(self, context):
        turret = context.object.m3_turrets[context.object.m3_turrets_index]
        shared.draw_menu_duplicate(self.layout, turret.parts, dup_keyframes_opt=False)


class TurretMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_turrets'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_turrets, dup_keyframes_opt=False)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_turrets'
    bl_label = 'M3 Turrets'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_turrets, draw_props, menu_id=TurretMenu.bl_idname)


classes = (
    PartProperties,
    Properties,
    PartMenu,
    TurretMenu,
    Panel,
)
