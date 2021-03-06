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
    bpy.types.Object.m3_ribbons = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_ribbons_index = bpy.props.IntProperty(options=set(), default=-1)


def draw_spline_props(spline, layout):
    col = layout.column(align=True)
    col.prop(spline, 'speed', text='Speed')
    col.prop(spline, 'yaw', text='Yaw')
    col.prop(spline, 'pitch', text='Pitch')
    col = layout.column(align=True)
    col.prop(spline, 'speed_var_shape', text='Speed Variation')
    sub = layout.column(align=True)
    sub.active = spline.speed_var_shape != 'NONE'
    sub.prop(spline, 'speed_var_freq', text='Frequency')
    sub.prop(spline, 'speed_var_amount', text='Amount')
    col = layout.column(align=True)
    col.prop(spline, 'yaw_var_shape', text='Yaw Variation')
    sub = layout.column(align=True)
    sub.active = spline.yaw_var_shape != 'NONE'
    sub.prop(spline, 'yaw_var_freq', text='Frequency')
    sub.prop(spline, 'yaw_var_amount', text='Amount')
    col = layout.column(align=True)
    col.prop(spline, 'pitch_var_shape', text='Pitch Variation')
    sub = layout.column(align=True)
    sub.active = spline.pitch_var_shape != 'NONE'
    sub.prop(spline, 'pitch_var_freq', text='Frequency')
    sub.prop(spline, 'pitch_var_amount', text='Amount')


def draw_props(ribbon, layout):
    col = layout.column(align=True)
    col.prop(ribbon, 'ribbon_type', text='Ribbon Type')

    if ribbon.ribbon_type == 'CYLINDER':
        col.prop(ribbon, 'edges', text='Edges')

    if ribbon.ribbon_type == 'STAR':
        col.prop(ribbon, 'edges', text='Edges')
        col.prop(ribbon, 'star_ratio', text='Cylinder/Planar Ratio')

    col = layout.column(align=True)
    col.prop(ribbon, 'material', text='Material')
    col = layout.column(align=True)
    col.prop(ribbon, 'lod_reduce', text='LOD Reduction')
    col.prop(ribbon, 'lod_cut', text='Cutoff')
    col = layout.column(align=True)
    col.prop(ribbon, 'divisions', text='Emission Rate')
    col.prop(ribbon, 'speed', text='Velocity')
    col.prop(ribbon, 'yaw', text='Yaw')
    col.prop(ribbon, 'pitch', text='Pitch')
    col.separator()

    shared.draw_collection_stack(layout, 'm3_ribbons[{}].splines'.format(ribbon.bl_index), 'Spline', draw_spline_props)

    col = layout.column(align=True)
    col.prop(ribbon, 'gravity', text='Gravity')
    col = layout.column(align=True)
    col.prop(ribbon, 'cull', text='Division Cull Type')

    if ribbon.cull == 'TIME':
        col.prop(ribbon, 'lifespan', text=' ')

    elif ribbon.cull == 'LENGTH':
        col.prop(ribbon, 'length', text='Length')
        row = col.row(align=True, heading='Lifespan')
        row.prop(ribbon, 'length_time', text='')
        sub = row.column(align=True)
        sub.active = ribbon.length_time
        sub.prop(ribbon, 'lifespan', text='')

    col = layout.column(align=True)
    col.prop(ribbon, 'twist', index=0, text='Twist Base')
    col.prop(ribbon, 'twist', index=1, text='Center')
    col.prop(ribbon, 'twist', index=2, text='Tip')
    col.prop(ribbon, 'twist_anim_mid', text='Animation Center')
    col.prop(ribbon, 'twist_anim_mid_time', text='Animation Center Time')
    col = layout.column(align=True)
    col.prop(ribbon, 'scale', index=0, text='Scale Base')
    col.prop(ribbon, 'scale', index=1, text='Center')
    col.prop(ribbon, 'scale', index=2, text='Tip')
    col.prop(ribbon, 'scale_anim_mid', text='Animation Center')
    col.prop(ribbon, 'scale_anim_mid_time', text='Animation Center Time')
    col = layout.column(align=True)
    col.prop(ribbon, 'color1', text='Color Base')
    col.prop(ribbon, 'color2', text='Center')
    col.prop(ribbon, 'color3', text='Tip')
    col.prop(ribbon, 'color_anim_mid', text='Color Animation Center')
    col.prop(ribbon, 'color_anim_mid_time', text='Color Animation Center Time')
    col.prop(ribbon, 'alpha_anim_mid', text='Alpha Animation Center')
    col.prop(ribbon, 'alpha_anim_mid_time', text='Alpha Animation Center Time')
    col = layout.column(align=True)
    col.prop(ribbon, 'stretch_limit', text='Stretch Limit')
    col.prop(ribbon, 'stretch_amount', text='Amount')
    col = layout.column(align=True)
    col.prop(ribbon, 'noise_amplitude', text='Noise Amplitude')
    col.prop(ribbon, 'noise_waves', text='Waves')
    col.prop(ribbon, 'noise_frequency', text='Frequency')
    col.prop(ribbon, 'noise_scale', text='Scale')
    col = layout.column(align=True)
    col.prop(ribbon, 'amplitude_var_shape', text='Amplitude Variation')
    sub = col.column(align=True)
    sub.active = ribbon.amplitude_var_shape != 'NONE'
    sub.prop(ribbon, 'amplitude_var_freq', text='Frequency')
    sub.prop(ribbon, 'amplitude_var_amount', text='Amount')
    col = layout.column(align=True)
    col.prop(ribbon, 'direction_var_shape', text='Direction Variation')
    sub = col.column(align=True)
    sub.active = ribbon.direction_var_shape != 'NONE'
    sub.prop(ribbon, 'direction_var_freq', text='Frequency')
    sub.prop(ribbon, 'direction_var_amount', text='Amount')
    col = layout.column(align=True)
    col.prop(ribbon, 'length_var_shape', text='Length Variation')
    sub = col.column(align=True)
    sub.active = ribbon.length_var_shape != 'NONE'
    sub.prop(ribbon, 'length_var_freq', text='Frequency')
    sub.prop(ribbon, 'length_var_amount', text='Amount')
    col = layout.column(align=True)
    col.prop(ribbon, 'scale_var_shape', text='Scale Variation')
    sub = col.column(align=True)
    sub.active = ribbon.scale_var_shape != 'NONE'
    sub.prop(ribbon, 'scale_var_freq', text='Frequency')
    sub.prop(ribbon, 'scale_var_amount', text='Amount')
    col = layout.column(align=True)
    col.prop(ribbon, 'alpha_var_shape', text='Alpha Variation')
    sub = col.column(align=True)
    sub.active = ribbon.alpha_var_shape != 'NONE'
    sub.prop(ribbon, 'alpha_var_freq', text='Frequency')
    sub.prop(ribbon, 'alpha_var_amount', text='Amount')
    col = layout.column_flow(align=True, columns=2)
    col.use_property_split = False
    col.prop(ribbon, 'collide_terrain', text='Collide Terrain')
    col.prop(ribbon, 'collide_objects', text='Collide Objects')
    col.prop(ribbon, 'edge_falloff', text='Edge Falloff')
    col.prop(ribbon, 'force_legacy', text='Force Legacy')
    col.prop(ribbon, 'inherit_parent_vel', text='Inherit Parent Velocity')
    col.prop(ribbon, 'scale_time_parent', text='Scale Time By Parent')
    col.prop(ribbon, 'local_time', text='Local Time')
    col.prop(ribbon, 'simulate_init', text='Simulate On Init')
    col.prop(ribbon, 'smooth_size', text='Smooth Size')
    col.prop(ribbon, 'bezier_smooth_size', text='Smooth Bezier Size')
    col.prop(ribbon, 'vertex_alpha', text='Vertex Alpha')


class SplineProperties(shared.M3BoneUserPropertyGroup):
    yaw: bpy.props.FloatProperty(name='Spline Yaw')
    yaw_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    yaw_var_amount: bpy.props.FloatProperty(name='Spline Yaw Variation Amount')
    yaw_var_freq: bpy.props.FloatProperty(name='Spline Yaw Variation Frequency')
    pitch: bpy.props.FloatProperty(name='Spline Pitch')
    pitch_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    pitch_var_amount: bpy.props.FloatProperty(name='Spline Pitch Variation Amount')
    pitch_var_freq: bpy.props.FloatProperty(name='Spline Pitch Variation Frequency')
    speed: bpy.props.FloatProperty(name='Spline Speed')
    speed_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    speed_var_amount: bpy.props.FloatProperty(name='Spline Speed Variation Amount')
    speed_var_freq: bpy.props.FloatProperty(name='Spline Speed Variation Frequency')


class Properties(shared.M3BoneUserPropertyGroup):
    material: bpy.props.StringProperty(options=set())
    splines: bpy.props.CollectionProperty(type=SplineProperties)
    ribbon_type: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_type)
    cull: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_cull)
    lod_cut: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    lod_reduce: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    active: bpy.props.BoolProperty(name='Active', default=True)  # TODO
    lifespan: bpy.props.FloatProperty(name='Lifespan', min=0, default=5)
    length: bpy.props.FloatProperty(name='Length', min=0)
    divisions: bpy.props.FloatProperty(options=set(), min=0, default=20)
    edges: bpy.props.IntProperty(options=set(), min=3, default=5)
    star_ratio: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    speed: bpy.props.FloatProperty(name='Speed')
    yaw: bpy.props.FloatProperty(name='Yaw')
    pitch: bpy.props.FloatProperty(name='Pitch')
    twist: bpy.props.FloatVectorProperty(name='Twist', subtype='XYZ', size=3)
    scale: bpy.props.FloatVectorProperty(name='Scale', subtype='XYZ', size=3, default=(1, 1, 1))
    color1: bpy.props.FloatVectorProperty(name='Base Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    color2: bpy.props.FloatVectorProperty(name='Center Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    color3: bpy.props.FloatVectorProperty(name='Tip Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 0))
    twist_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    scale_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    color_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    alpha_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    twist_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    scale_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    color_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    alpha_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    gravity: bpy.props.FloatProperty(options=set())
    stretch_amount: bpy.props.FloatProperty(options=set(), default=1)
    stretch_limit: bpy.props.FloatProperty(options=set(), default=1)
    noise_amplitude: bpy.props.FloatProperty(options=set())
    noise_waves: bpy.props.FloatProperty(options=set())
    noise_frequency: bpy.props.FloatProperty(options=set())
    noise_scale: bpy.props.FloatProperty(options=set())
    friction: bpy.props.FloatProperty(options=set(), min=0, max=1)  # TODO
    drag: bpy.props.FloatProperty(options=set())  # TODO
    mass: bpy.props.FloatProperty(options=set())  # TODO
    local_forces: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=16)  # TODO
    world_forces: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=16)  # TODO
    world_space: bpy.props.BoolProperty(options=set())
    amplitude_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    amplitude_var_amount: bpy.props.FloatProperty(name='Amplitude Variation Amount')
    amplitude_var_freq: bpy.props.FloatProperty(name='Amplitude Variation Frequency')
    direction_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    direction_var_amount: bpy.props.FloatProperty(name='Directional Variation Amount')
    direction_var_freq: bpy.props.FloatProperty(name='Directional Variation Frequency')
    length_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    length_var_amount: bpy.props.FloatProperty(name='Length Variation Amount')
    length_var_freq: bpy.props.FloatProperty(name='Length Variation Frequency')
    scale_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    scale_var_amount: bpy.props.FloatProperty(name='Scale Variation Amount')
    scale_var_freq: bpy.props.FloatProperty(name='Scale Variation Frequency')
    alpha_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    alpha_var_amount: bpy.props.FloatProperty(name='Alpha Variation Amount')
    alpha_var_freq: bpy.props.FloatProperty(name='Alpha Variation Frequency')
    parent_velocity: bpy.props.FloatProperty(name='Parent Velocity')  # TODO
    phase_shift: bpy.props.FloatProperty(name='Phase Shift')  # TODO
    collide_terrain: bpy.props.BoolProperty(options=set())
    collide_objects: bpy.props.BoolProperty(options=set())
    edge_falloff: bpy.props.BoolProperty(options=set())
    inherit_parent_vel: bpy.props.BoolProperty(options=set())
    smooth_size: bpy.props.BoolProperty(options=set())
    bezier_smooth_size: bpy.props.BoolProperty(options=set())
    vertex_alpha: bpy.props.BoolProperty(options=set())
    scale_time_parent: bpy.props.BoolProperty(options=set())
    force_legacy: bpy.props.BoolProperty(options=set())
    local_time: bpy.props.BoolProperty(options=set())
    simulate_init: bpy.props.BoolProperty(options=set())
    length_time: bpy.props.BoolProperty(options=set())


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_RIBBONS'
    bl_label = 'M3 Ribbons'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_ribbons', draw_props)


classes = (
    SplineProperties,
    Properties,
    Panel,
)
