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
    bpy.types.Object.m3_materiallayers = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_materiallayers_index = bpy.props.IntProperty(options=set(), default=-1)


def draw_props(layer, layout):
    layout.prop(layer, 'unknownbd3f7b5d', text='Unknown (id: bd3f7b5d)')
    col = layout.column(align=True)
    col.prop(layer, 'color_type', text='Layer Type')
    if layer.color_type == 'BITMAP':
        col.prop(layer, 'color_bitmap', text='Image Path')
        col.prop(layer, 'color_channels', text='Color Channels')
    else:
        col.prop(layer, 'color_value', text='Color Value')
    col = layout.column()
    col.prop(layer, 'color_add', text='Add')
    col.prop(layer, 'color_multiply', text='Multiply')
    col.prop(layer, 'color_brightness', text='Brightness')
    row = layout.row()
    row.prop(layer, 'color_invert', text='Invert')
    row.prop(layer, 'color_clamp', text='Clamp')
    layout.separator()
    layout.prop(layer, 'uv_source', text='UV Source')
    row = layout.row(heading='Wrap')
    row.prop(layer, 'uv_wrap', index=0, text='X')
    row.prop(layer, 'uv_wrap', index=1, text='Y')
    layout.prop(layer, 'uv_offset', text='Offset')
    layout.prop(layer, 'uv_angle', text='Angle')
    layout.prop(layer, 'uv_tiling', text='Tiling')
    col = layout.column()
    sub = col.column(align=True)
    sub.prop(layer, 'uv_flipbook_rows', text='Flipbook Rows')
    sub.prop(layer, 'uv_flipbook_columns', text='Columns')
    col.prop(layer, 'uv_flipbook_frame', text='Frame')
    if 'TRIPLANAR' in layer.uv_source:
        layout.prop(layer, 'uv_triplanar_offset', text='Triplanar Offset')
        layout.prop(layer, 'uv_triplanar_scale', text='Triplanar Scale')
    layout.separator()
    col = layout.column()
    col.prop(layer, 'noise_amplitude', text='Volume Noise Amplitide')
    col.prop(layer, 'noise_frequency', text='Frequency')
    layout.separator()
    layout.prop(layer, 'fresnel_type', text='Fresel Mode')
    if layer.fresnel_type != 'DISABLED':
        layout.prop(layer, 'fresnel_exponent', text='Exponent')
        col = layout.column(align=True)
        col.prop(layer, 'fresnel_min', text='Minimum')
        col.prop(layer, 'fresnel_max', text='Maximum')
        layout.prop(layer, 'fresnel_mask', text='Mask')
        col = layout.column(align=True)
        col.prop(layer, 'fresnel_yaw', text='Yaw')
        col.prop(layer, 'fresnel_pitch', text='Pitch')
        row = layout.row()
        row.prop(layer, 'fresnel_local_transform', text='Local Transform')
        row.prop(layer, 'fresnel_do_not_mirror', text='Don\'t Mirror')
    layout.separator()
    layout.prop(layer, 'video_channel', text='RTT Channel')
    if layer.video_channel != 'NONE':
        layout.prop(layer, 'video_mode', text='Video Mode')
        col = layout.column()
        col.prop(layer, 'video_frame_rate', text='Frame Rate')
        col.prop(layer, 'video_frame_start', text='Frame Start')
        col.prop(layer, 'video_frame_end', text='Frame End')
        layout.prop(layer, 'video_sync_timing', text='Sync Timing')
        layout.prop(layer, 'video_play', text='Play')
        layout.prop(layer, 'video_restart', text='Restart')


class Properties(shared.M3PropertyGroup):
    unknownbd3f7b5d: bpy.props.IntProperty(name='unknownbd3f7b5d', default=-1, options=set())
    color_type: bpy.props.EnumProperty(items=bl_enum.material_layer_type, options=set())
    color_bitmap: bpy.props.StringProperty(default='', options=set())
    color_channels: bpy.props.EnumProperty(items=bl_enum.material_layer_channel, options=set(), default='RGB')
    color_value: bpy.props.FloatVectorProperty(name='Color', default=(1.0, 1.0, 1.0, 1.0), min=0.0, max=1.0, size=4, subtype='COLOR', options={'ANIMATABLE'})
    color_invert: bpy.props.BoolProperty(options=set(), default=False)
    color_clamp: bpy.props.BoolProperty(options=set(), default=False)
    color_add: bpy.props.FloatProperty(name='Color Add', options={'ANIMATABLE'}, description='Adds (or subtracts) value from the color values')
    color_multiply: bpy.props.FloatProperty(name='Color Multiplier', options={'ANIMATABLE'}, default=1.0)
    color_brightness: bpy.props.FloatProperty(name='Brightness', options={'ANIMATABLE'}, default=1.0)
    uv_source: bpy.props.EnumProperty(items=bl_enum.uv_source, options=set())
    uv_wrap: bpy.props.BoolVectorProperty(options=set(), size=2, default=(True, True))
    uv_offset: bpy.props.FloatVectorProperty(name='UV Offset', default=(0.0, 0.0), size=2, subtype='XYZ', options={'ANIMATABLE'})
    uv_angle: bpy.props.FloatVectorProperty(name='UV Angle', default=(0.0, 0.0, 0.0), size=3, subtype='XYZ', options={'ANIMATABLE'})
    uv_tiling: bpy.props.FloatVectorProperty(name='UV Tiling', default=(1.0, 1.0), size=2, subtype='XYZ', options={'ANIMATABLE'})
    uv_flipbook_rows: bpy.props.IntProperty(name='Flipbook Rows', default=0, options=set())
    uv_flipbook_columns: bpy.props.IntProperty(name='Flipbook Columns', default=0, options=set())
    uv_flipbook_frame: bpy.props.IntProperty(name='Flipbook Frame', default=0, options={'ANIMATABLE'})
    uv_triplanar_offset: bpy.props.FloatVectorProperty(name='Tri Planer Offset', default=(0.0, 0.0, 0.0), size=3, subtype='XYZ', options={'ANIMATABLE'})
    uv_triplanar_scale: bpy.props.FloatVectorProperty(name='Tri Planer Scale', default=(1.0, 1.0, 1.0), size=3, subtype='XYZ', options={'ANIMATABLE'})
    fresnel_type: bpy.props.EnumProperty(items=bl_enum.fresnel_type, options=set())
    fresnel_exponent: bpy.props.FloatProperty(default=4.0, options=set())
    fresnel_min: bpy.props.FloatProperty(default=0.0, options=set())
    fresnel_max: bpy.props.FloatProperty(default=1.0, options=set())
    fresnel_mask: bpy.props.FloatVectorProperty(size=3, options=set(), subtype='XYZ', min=0, max=1)
    fresnel_yaw: bpy.props.FloatProperty(subtype='ANGLE', options=set())
    fresnel_pitch: bpy.props.FloatProperty(subtype='ANGLE', options=set())
    fresnel_local_transform: bpy.props.BoolProperty(options=set(), default=False)
    fresnel_do_not_mirror: bpy.props.BoolProperty(options=set(), default=False)
    video_channel: bpy.props.EnumProperty(items=bl_enum.rtt_channel, options=set())
    video_frame_rate: bpy.props.IntProperty(options=set(), default=24)
    video_frame_start: bpy.props.IntProperty(options=set(), default=0)
    video_frame_end: bpy.props.IntProperty(options=set(), default=-1)
    video_mode: bpy.props.EnumProperty(items=bl_enum.video_mode, options=set())
    video_sync_timing: bpy.props.BoolProperty(options=set())
    video_play: bpy.props.BoolProperty(name='Video Play', options={'ANIMATABLE'}, default=True)
    video_restart: bpy.props.BoolProperty(name='Video Restart', options={'ANIMATABLE'}, default=True)
    noise_amplitude: bpy.props.FloatProperty(options=set(), default=0.8)
    noise_frequency: bpy.props.FloatProperty(options=set(), default=0.5)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_MATERIALLAYERS'
    bl_label = 'M3 Material Layers'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_materiallayers', draw_props)


classes = (
    Properties,
    Panel,
)
