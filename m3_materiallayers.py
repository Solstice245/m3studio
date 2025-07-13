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
from .shared import material_type_to_layers, material_collections


def register_props():
    bpy.types.Object.m3_materiallayers = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_materiallayers_index = bpy.props.IntProperty(options=set(), default=-1)
    bpy.types.Object.m3_materiallayers_version = bpy.props.EnumProperty(options=set(), items=layer_versions, default='26')


layer_versions = (
    # ('20', '20 (SC2 Beta)', 'Version 20. SC2 Beta only'),
    # ('21', '21 (SC2 Beta)', 'Version 21. SC2 Beta only'),
    ('22', '22', 'Version 22'),
    ('23', '23', 'Version 23'),
    ('24', '24', 'Version 24'),
    ('25', '25', 'Version 25'),
    ('26', '26', 'Version 26'),
)


def draw_props(layer, layout):
    layout.use_property_decorate = False
    version = int(layer.id_data.m3_materiallayers_version)
    is_bitmap = layer.color_type == 'BITMAP'

    col = layout.column(align=True)
    col.prop(layer, 'color_type', text='Layer Type')
    if is_bitmap:
        col.prop(layer, 'color_bitmap', text='Image Path')
    else:
        col.prop(layer, 'color_value', text='Color Value')
    col.prop(layer, 'color_channels', text='Color Channels')
    col = layout.column()
    shared.draw_prop_anim(col, layer, 'color_add', text='Add')
    shared.draw_prop_anim(col, layer, 'color_multiply', text='Multiply')
    shared.draw_prop_anim(col, layer, 'color_brightness', text='Brightness')
    row = layout.row()
    row.prop(layer, 'color_invert', text='Invert')
    row.prop(layer, 'color_clamp', text='Clamp')

    if is_bitmap:
        layout.separator()
        col = layout.column(align=True)
        col.prop(layer, 'uv_source', text='UV Source')
        col.prop(layer, 'uv_source_related', text='Hint')
        row = layout.row(heading='Wrap')
        row.prop(layer, 'uv_wrap_x', text='U')
        row.prop(layer, 'uv_wrap_y', text='V')
        row = shared.draw_prop_split(layout, text='Offset')
        shared.draw_op_anim_header(row, layer, 'uv_offset')
        shared.draw_prop_items(row, layer, 'uv_offset')
        row = shared.draw_prop_split(layout, text='Angle')
        shared.draw_op_anim_header(row, layer, 'uv_angle')
        shared.draw_prop_items(row, layer, 'uv_angle')
        row = shared.draw_prop_split(layout, text='Tiling')
        shared.draw_op_anim_header(row, layer, 'uv_tiling')
        shared.draw_prop_items(row, layer, 'uv_tiling')

        if version >= 23 and 'TRIPLANAR' in layer.uv_source:
            layout.separator()
            layout.prop(layer, 'uv_triplanar_offset', text='Triplanar Offset')
            layout.prop(layer, 'uv_triplanar_scale', text='Triplanar Scale')

        layout.separator()
        col = layout.column(align=True)
        layout.prop(layer, 'noise_type', text='Noise Type')
        if version >= 24 and layer.noise_type != 0:
            row = col.row(align=True)
            row.prop(layer, 'noise_amplitude', text='Amplitude/Frequency')
            row.prop(layer, 'noise_frequency', text='')

    if layer.color_bitmap.endswith('.ogv'):
        layout.separator()
        layout.prop(layer, 'video_mode', text='Video Mode')
        col = layout.column()
        col.prop(layer, 'video_frame_rate', text='Frame Rate')
        col.prop(layer, 'video_frame_start', text='Frame Start')
        col.prop(layer, 'video_frame_end', text='Frame End')
        shared.draw_prop_anim(layout, layer, 'video_play', text='Play')
        shared.draw_prop_anim(layout, layer, 'video_restart', text='Restart')
        layout.prop(layer, 'video_sync_timing', text='Sync Timing')
    else:
        layout.separator()
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(layer, 'uv_flipbook_rows', text='Flipbook Rows/Columns')
        row.prop(layer, 'uv_flipbook_cols', text='')
        shared.draw_prop_anim(col, layer, 'uv_flipbook_frame', text='Frame')

    layout.separator()
    layout.prop(layer, 'fresnel_type', text='Fresel Mode')
    if layer.fresnel_type != 'DISABLED':
        layout.prop(layer, 'fresnel_exponent', text='Exponent')
        row = shared.draw_prop_split(layout, text='Min/Max')
        row.prop(layer, 'fresnel_min', text='')
        row.prop(layer, 'fresnel_max', text='')

        if version >= 25:
            shared.draw_prop_items(shared.draw_prop_split(layout, text='Translation'), layer, 'fresnel_translation')
            shared.draw_prop_items(shared.draw_prop_split(layout, text='Mask'), layer, 'fresnel_mask')
            row = shared.draw_prop_split(layout, text='Rotation')
            row.prop(layer, 'fresnel_yaw', text='')
            row.prop(layer, 'fresnel_pitch', text='')

        row = layout.row()
        row.prop(layer, 'fresnel_transform', text='Transform')
        row.prop(layer, 'fresnel_normalize', text='Normalize')
        row = layout.row()
        row.prop(layer, 'fresnel_local_transform', text='Local Transform')
        row.prop(layer, 'fresnel_do_not_mirror', text='Don\'t Mirror')

    layout.separator()
    layout.prop(layer, 'video_channel', text='RTT Channel')


class Properties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Material Layer'

    name: bpy.props.StringProperty(options=set(), )
    color_type: bpy.props.EnumProperty(items=bl_enum.material_layer_type, options=set())
    color_bitmap: bpy.props.StringProperty(default='', options=set())
    color_channels: bpy.props.EnumProperty(items=bl_enum.material_layer_channel, options=set(), default='RGB')
    color_value: bpy.props.FloatVectorProperty(name='Color', default=(1.0, 1.0, 1.0, 1.0), min=0.0, max=1.0, size=4, subtype='COLOR', options={'ANIMATABLE'})
    color_value_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_invert: bpy.props.BoolProperty(options=set(), default=False)
    color_clamp: bpy.props.BoolProperty(options=set(), default=False)
    color_add: bpy.props.FloatProperty(name='Color Add', options={'ANIMATABLE'}, description='Adds (or subtracts) value from the color values')
    color_add_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_multiply: bpy.props.FloatProperty(name='Color Multiplier', options={'ANIMATABLE'}, default=1.0)
    color_multiply_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_brightness: bpy.props.FloatProperty(name='Brightness', options={'ANIMATABLE'}, default=1.0)
    color_brightness_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uv_source: bpy.props.EnumProperty(items=bl_enum.uv_source, options=set())
    uv_wrap_x: bpy.props.BoolProperty(options=set(), default=True)
    uv_wrap_y: bpy.props.BoolProperty(options=set(), default=True)
    uv_offset: bpy.props.FloatVectorProperty(name='UV Offset', default=(0.0, 0.0), size=2, subtype='XYZ', options={'ANIMATABLE'})
    uv_offset_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uv_angle: bpy.props.FloatVectorProperty(name='UV Angle', default=(0.0, 0.0, 0.0), size=3, subtype='EULER', unit='ROTATION', options={'ANIMATABLE'})
    uv_angle_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uv_tiling: bpy.props.FloatVectorProperty(name='UV Tiling', default=(1.0, 1.0), size=2, subtype='XYZ', options={'ANIMATABLE'})
    uv_tiling_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uv_w_translation: bpy.props.FloatProperty(name='W Translation', default=0.0, options={'ANIMATABLE'})  # no UI, not documented to work
    uv_w_translation_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uv_w_scale: bpy.props.FloatProperty(name='W Scale', default=1.0, options={'ANIMATABLE'})  # no UI, not documented to work
    uv_w_scale_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uv_flipbook_rows: bpy.props.IntProperty(name='Flipbook Rows', default=0, options=set())
    uv_flipbook_cols: bpy.props.IntProperty(name='Flipbook Columns', default=0, options=set())
    uv_flipbook_frame: bpy.props.IntProperty(name='Flipbook Frame', default=0, options={'ANIMATABLE'})
    uv_flipbook_frame_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uv_triplanar_offset: bpy.props.FloatVectorProperty(name='Tri Planer Offset', default=(0.0, 0.0, 0.0), size=3, subtype='XYZ', options={'ANIMATABLE'})
    uv_triplanar_offset_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uv_triplanar_scale: bpy.props.FloatVectorProperty(name='Tri Planer Scale', default=(1.0, 1.0, 1.0), size=3, subtype='XYZ', options={'ANIMATABLE'})
    uv_triplanar_scale_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uv_source_related: bpy.props.IntProperty(options=set(), default=-1, min=-1)
    fresnel_type: bpy.props.EnumProperty(items=bl_enum.fresnel_type, options=set())
    fresnel_exponent: bpy.props.FloatProperty(default=4.0, options=set())
    fresnel_min: bpy.props.FloatProperty(default=0.0, options=set())
    fresnel_max: bpy.props.FloatProperty(default=1.0, options=set())
    fresnel_translation: bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), size=3, subtype='XYZ', options=set())
    fresnel_mask: bpy.props.FloatVectorProperty(size=3, options=set(), subtype='XYZ', min=0, max=1)
    fresnel_yaw: bpy.props.FloatProperty(subtype='ANGLE', options=set())
    fresnel_pitch: bpy.props.FloatProperty(subtype='ANGLE', options=set())
    fresnel_transform: bpy.props.BoolProperty(options=set())
    fresnel_normalize: bpy.props.BoolProperty(options=set())
    fresnel_local_transform: bpy.props.BoolProperty(options=set(), default=False)
    fresnel_do_not_mirror: bpy.props.BoolProperty(options=set(), default=False)
    video_channel: bpy.props.IntProperty(options=set(), min=-1, max=6, default=-1)
    video_frame_rate: bpy.props.IntProperty(options=set(), min=0, default=24)
    video_frame_start: bpy.props.IntProperty(options=set(), min=0, default=0)
    video_frame_end: bpy.props.IntProperty(options=set(), min=-1, default=-1)
    video_mode: bpy.props.EnumProperty(items=bl_enum.video_mode, options=set())
    video_sync_timing: bpy.props.BoolProperty(options=set())
    video_play: bpy.props.BoolProperty(name='Video Play', options={'ANIMATABLE'}, default=False)
    video_play_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    video_restart: bpy.props.BoolProperty(name='Video Restart', options={'ANIMATABLE'}, default=False)
    video_restart_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    noise_type: bpy.props.IntProperty(options=set(), min=0)
    noise_amplitude: bpy.props.FloatProperty(options=set(), default=0.8)
    noise_frequency: bpy.props.FloatProperty(options=set(), default=0.5)


class Menu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_materiallayers'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_materiallayers, dup_keyframes_opt=True)


def draw_ops_del(layout):
    layout.operator('m3.materiallayer_del', icon='REMOVE', text='')


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_MATERIALLAYERS'
    bl_label = 'M3 Material Layers'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_materiallayers, draw_props, ops={'del': draw_ops_del}, menu_id=Menu.bl_idname)


class M3MaterialLayerOpRemove(bpy.types.Operator):
    bl_idname = 'm3.materiallayer_del'
    bl_label = 'Remove Collection Item'
    bl_description = 'Removes the active item from the collection'

    def invoke(self, context, event):
        ob = context.object
        layers = ob.m3_materiallayers
        layer = layers[ob.m3_materiallayers_index]

        # check if layer is in use
        user_strings = []
        for matref in ob.m3_materialrefs:
            mat = shared.m3_pointer_get(getattr(ob, matref.mat_type), matref.mat_handle)
            for layer_name in material_type_to_layers[material_collections.index(matref.mat_type)]:
                if getattr(mat, 'layer_' + layer_name) == layer.bl_handle:
                    user_strings.append(f'The material {matref.name} is using this material layer')

        if user_strings:
            self.report({"ERROR"}, 'Deletion cancelled due to the following reason(s):\n' + '\n'.join(user_strings))
            return {'CANCELLED'}

        ob.m3_materiallayers.remove(ob.m3_materiallayers_index)

        shared.remove_m3_action_keyframes(ob, 'm3_materiallayers', ob.m3_materiallayers_index)
        for ii in range(ob.m3_materiallayers_index, len(ob.m3_materiallayers)):
            shared.shift_m3_action_keyframes(ob, 'm3_materiallayers', ii + 1)

        ob.m3_materiallayers_index -= 1 if (ob.m3_materiallayers_index == 0 and len(layers) == 0) or ob.m3_materiallayers_index == len(layers) else 0

        return {'FINISHED'}


classes = (
    M3MaterialLayerOpRemove,
    Properties,
    Menu,
    Panel,
)
