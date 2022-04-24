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
    bpy.types.Object.m3_lights = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_lights_index = bpy.props.IntProperty(options=set(), default=-1, update=update_bone_shapes_option)


def init_msgbus(ob, context):
    for light in ob.m3_lights:
        shared.bone_update_event(light, context)


def update_bone_shapes_option(self, context):
    if context.object.m3_options.auto_update_bone_shapes:
        if context.object.m3_options.bone_shapes != 'LITE':
            context.object.m3_options.bone_shapes = 'LITE'


def draw_props(light, layout):
    col = layout.column(align=True)
    col.prop(light, 'shape', text='Shape')
    col.prop(light, 'attenuation_near', text='Attenuation Near')
    col.prop(light, 'attenuation_far', text='Far')
    if light.shape == 'SPOT':
        col.prop(light, 'hotspot', text='Hotspot')
        col.prop(light, 'falloff', text='Falloff')
    col = layout.column(align=True)
    col.prop(light, 'intensity', text='Intensity')
    col.prop(light, 'color', text='Color')
    col = layout.column_flow(columns=2)
    col.use_property_split = False
    col.prop(light, 'shadows', text='Casts Shadows (Spot)')
    col.prop(light, 'unknownFlag0x04', text='Unknown Flag 0x04')
    col.prop(light, 'active', text='Turn On')
    col.prop(light, 'transparent_objects', text='Apply To Transparent Objects')


class Properties(shared.M3BoneUserPropertyGroup):
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.light_shape, update=shared.bone_shape_update_event)
    unknownAt1: bpy.props.IntProperty(options=set())
    unknownAt8: bpy.props.IntProperty(options=set())
    unknownAt12: bpy.props.IntProperty(options=set(), default=-1)
    color: bpy.props.FloatVectorProperty(name='M3 Light Color', subtype='COLOR', size=3, min=0, max=1, default=(1, 1, 1))
    intensity: bpy.props.FloatProperty(name='M3 Light Intensity')
    attenuation_far: bpy.props.FloatProperty(name='M3 Light Attenuation Far', default=3, update=shared.bone_shape_update_event)
    attenuation_near: bpy.props.FloatProperty(name='M3 Light Attenuation Near', default=2)
    falloff: bpy.props.FloatProperty(name='M3 Light Falloff', default=3, update=shared.bone_shape_update_event)
    hotspot: bpy.props.FloatProperty(name='M3 Light Hotspot', default=2)
    unknown148: bpy.props.FloatProperty(options=set())
    shadows: bpy.props.BoolProperty(options=set())
    unknownFlag0x04: bpy.props.BoolProperty(options=set())
    active: bpy.props.BoolProperty(options=set(), default=True)
    transparent_objects: bpy.props.BoolProperty(options=set())


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_LIGHTS'
    bl_label = 'M3 Lights'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_lights', draw_props)


classes = (
    Properties,
    Panel,
)
