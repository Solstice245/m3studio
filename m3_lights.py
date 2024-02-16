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
    bpy.types.Object.m3_lights_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)


def update_collection_index(self, context):
    if self.m3_lights_index in range(len(self.m3_lights)):
        bl = self.m3_lights[self.m3_lights_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_props(light, layout):
    layout.use_property_decorate = False
    shared.draw_prop_pointer_search(layout, light.bone, light.id_data.data, 'bones', text='Bone', icon='BONE_DATA')
    col = layout.column(align=True)
    col.prop(light, 'shape', text='Shape')
    shared.draw_prop_anim(col, light, 'attenuation_near', text='Attenuation Near')
    shared.draw_prop_anim(col, light, 'attenuation_far', text='Far')
    if light.shape == 'SPOT':
        shared.draw_prop_anim(col, light, 'hotspot', text='Hotspot')
        shared.draw_prop_anim(col, light, 'falloff', text='Falloff')
    layout.separator()
    shared.draw_prop_anim(layout, light, 'intensity', text='Intensity')
    shared.draw_prop_anim(layout, light, 'color', text='Color')
    layout.separator()
    col = layout.column_flow(columns=2)
    col.use_property_split = False
    col.prop(light, 'light_opaque', text='Lights Opaque')
    col.prop(light, 'light_transparent', text='Lights Transparent')
    col.prop(light, 'team_color', text='Team Colored')
    if light.shape == 'SPOT':
        col.prop(light, 'shadows', text='Casts Shadows')
    col.prop(light, 'ao', text='Ambient Occlusion')


class Properties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Light'

    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.light_shape, default='POINT')
    color: bpy.props.FloatVectorProperty(name='M3 Light Color', subtype='COLOR', size=3, min=0, max=1, default=(1, 1, 1))
    color_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    intensity: bpy.props.FloatProperty(name='M3 Light Intensity')
    intensity_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    attenuation_far: bpy.props.FloatProperty(name='M3 Light Attenuation Far', default=3)
    attenuation_far_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    attenuation_near: bpy.props.FloatProperty(name='M3 Light Attenuation Near', default=2)
    attenuation_near_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    falloff: bpy.props.FloatProperty(name='M3 Light Falloff', default=3)
    falloff_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    hotspot: bpy.props.FloatProperty(name='M3 Light Hotspot', default=2)
    hotspot_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    ao: bpy.props.BoolProperty(options=set(), description='NOTE: This feature is (probably) exclusive to campaign mode')
    light_opaque: bpy.props.BoolProperty(options=set(), default=True)
    light_transparent: bpy.props.BoolProperty(options=set())
    shadows: bpy.props.BoolProperty(options=set())
    team_color: bpy.props.BoolProperty(options=set())


class Menu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_lights'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_lights, dup_keyframes_opt=True)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_LIGHTS'
    bl_label = 'M3 Lights'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_lights, draw_props, menu_id=Menu.bl_idname)


classes = (
    Properties,
    Menu,
    Panel,
)
