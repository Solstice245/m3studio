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
    bpy.types.Object.m3_forces = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_forces_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)
    bpy.types.Object.m3_forces_version = bpy.props.EnumProperty(options=set(), items=force_version, default='2')


force_version = (
    ('1', '1', 'Version 1'),
    ('2', '2', 'Version 2'),
)


def update_collection_index(self, context):
    if self.m3_forces_index in range(len(self.m3_forces)):
        bl = self.m3_forces[self.m3_forces_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_props(force, layout):
    layout.use_property_decorate = False
    shared.draw_prop_pointer_search(layout, force.bone, force.id_data.data, 'bones', text='Bone', icon='BONE_DATA')
    layout.prop(force, 'force_type', text='Type')
    col = layout.column(align=True)
    col.prop(force, 'shape', text='Shape')
    if force.shape in ('SPHERE', 'HEMISPHERE'):
        shared.draw_prop_anim(col, force, 'width', text='Radius')
    elif force.shape == 'CYLINDER':
        shared.draw_prop_anim(col, force, 'width', text='Radius')
        shared.draw_prop_anim(col, force, 'height', text='Height')
    elif force.shape == 'CUBE':
        shared.draw_prop_anim(col, force, 'width', text='Width')
        shared.draw_prop_anim(col, force, 'height', text='Height')
        shared.draw_prop_anim(col, force, 'length', text='Length')
    elif force.shape == 'CONEDOME':
        shared.draw_prop_anim(col, force, 'width', text='Radius')
        shared.draw_prop_anim(col, force, 'height', text='Angle Factor')
    layout.separator()
    shared.draw_prop_anim(layout, force, 'strength', text='Strength')
    layout.separator()
    row = shared.draw_prop_split(layout, text='Force Channels')
    row.prop(force, 'channels', text='')
    layout.separator()
    col = layout.column_flow(align=True, columns=2)
    col.use_property_split = False
    col.prop(force, 'falloff', text='Falloff')
    col.prop(force, 'height_gradient', text='Height Gradient')
    col.prop(force, 'unbounded', text='Unbounded')
    col.prop(force, 'unknown0x08', text='Unknown (0x8)')
    col.prop(force, 'unknown0x10', text='Unknown (0x10)')


class Properties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Force'

    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)
    force_type: bpy.props.EnumProperty(options=set(), items=bl_enum.force_type)
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.force_shape)
    width: bpy.props.FloatProperty(name='M3 Force Width', min=0.001, default=1.0)
    width_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    height: bpy.props.FloatProperty(name='M3 Force Height', min=0.001, default=1.0)
    height_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    length: bpy.props.FloatProperty(name='M3 Force Length', min=0.001, default=1.0)
    length_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    channels: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=32)
    strength: bpy.props.FloatProperty(name='M3 Force Strength', default=1)
    strength_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    falloff: bpy.props.BoolProperty(options=set())
    height_gradient: bpy.props.BoolProperty(options=set())
    unbounded: bpy.props.BoolProperty(options=set())
    unknown0x08: bpy.props.BoolProperty(options=set(), default=True)
    unknown0x10: bpy.props.BoolProperty(options=set(), default=True)


class Menu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_forces'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_forces, dup_keyframes_opt=True)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_FORCES'
    bl_label = 'M3 Forces'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_forces, draw_props, menu_id=Menu.bl_idname)


classes = (
    Properties,
    Menu,
    Panel,
)
