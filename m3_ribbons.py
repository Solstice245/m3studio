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
    bpy.types.Object.m3_ribbons = bpy.props.CollectionProperty(type=RibbonProperties)
    bpy.types.Object.m3_ribbons_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)
    bpy.types.Object.m3_ribbons_version = bpy.props.EnumProperty(options=set(), items=ribbon_version, default='9')
    bpy.types.Object.m3_ribbonsplines = bpy.props.CollectionProperty(type=SplineProperties)
    bpy.types.Object.m3_ribbonsplines_index = bpy.props.IntProperty(options=set(), default=-1, update=update_spline_collection_index)


# TODO UI stuff
ribbon_version = (
    # ('4', '4 (SC2 Beta)', 'Version 4. SC2 Beta only'),
    # ('5', '5 (SC2 Beta)', 'Version 5. SC2 Beta only'),
    ('6', '6', 'Version 6'),
    # ('7', '7', 'Version 7'), # * not documented to exist
    ('8', '8', 'Version 8'),
    ('9', '9', 'Version 9'),
)


def update_collection_index(self, context):
    if self.m3_ribbons_index in range(len(self.m3_ribbons)):
        bl = self.m3_ribbons[self.m3_ribbons_index]
        shared.select_bones_handles(context.object, [bl.bone])


def update_spline_collection_index(self, context):
    spline = self.m3_ribbonsplines[self.m3_ribbonsplines_index]
    if spline.points_index in range(len(spline.points)):
        bl = spline.points[spline.points_index]
        shared.select_bones_handles(context.object, [bl.bone])


def update_point_collection_index(self, context):
    if self.points_index in range(len(self.points)):
        bl = self.points[self.points_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_point_props(point, layout):
    layout.use_property_decorate = False
    shared.draw_prop_pointer_search(layout, point.bone, point.id_data.data, 'bones', text='Bone', icon='BONE_DATA')
    layout.separator()
    shared.draw_prop_items(shared.draw_prop_split(layout, text='Emission Offset'), point, 'emission_offset')
    layout.separator()
    shared.draw_prop_items(shared.draw_prop_split(layout, text='Emission Vector'), point, 'emission_vector')
    layout.separator()
    shared.draw_prop_anim(layout, point, 'velocity', text='Velocity')
    shared.draw_prop_anim(layout, point, 'velocity_base_fac', text='Base Factor')
    shared.draw_prop_anim(layout, point, 'velocity_end_fac', text='End Factor')
    layout.separator()
    row = shared.draw_prop_split(layout, text='Yaw/Pitch')
    shared.draw_op_anim_prop(row, point, 'yaw')
    row.separator(factor=0.325)
    shared.draw_op_anim_prop(row, point, 'pitch')
    layout.separator()
    shared.draw_var_props(layout, point, 'yaw', text='Yaw Variation')
    shared.draw_var_props(layout, point, 'pitch', text='Pitch')
    shared.draw_var_props(layout, point, 'velocity', text='Velocity')


def draw_spline_props(spline, layout):
    shared.draw_collection_list(layout.box(), spline.points, draw_point_props, menu_id=PointsMenu.bl_idname)


class SplinePointerProp(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(options=set(), get=shared.pointer_get_args('m3_ribbonsplines'), set=shared.pointer_set_args('m3_ribbonsplines', False))
    handle: bpy.props.StringProperty(options=set())


class PointProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Ribbon Spline Point'

    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)
    emission_offset: bpy.props.FloatVectorProperty(options=set(), size=3, subtype='XYZ')
    emission_vector: bpy.props.FloatVectorProperty(options=set(), size=3, subtype='XYZ')
    yaw: bpy.props.FloatProperty(name='Spline Yaw')
    yaw_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    yaw_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    yaw_var_amplitude: bpy.props.FloatProperty(name='Spline Yaw Variation Amount')
    yaw_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    yaw_var_frequency: bpy.props.FloatProperty(name='Spline Yaw Variation Frequency')
    yaw_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    pitch: bpy.props.FloatProperty(name='Spline Pitch')
    pitch_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    pitch_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    pitch_var_amplitude: bpy.props.FloatProperty(name='Spline Pitch Variation Amount')
    pitch_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    pitch_var_frequency: bpy.props.FloatProperty(name='Spline Pitch Variation Frequency')
    pitch_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    velocity: bpy.props.FloatProperty(name='Spline Velocity')
    velocity_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    velocity_base_fac: bpy.props.FloatProperty(name='Base Velocity Factor', default=1.0)
    velocity_base_fac_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    velocity_end_fac: bpy.props.FloatProperty(name='Base Velocity Factor', default=1.0)
    velocity_end_fac_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    velocity_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    velocity_var_amplitude: bpy.props.FloatProperty(name='Spline Velocity Variation Amount')
    velocity_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    velocity_var_frequency: bpy.props.FloatProperty(name='Spline Velocity Variation Frequency')
    velocity_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)


class SplineProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Ribbon Spline'

    points: bpy.props.CollectionProperty(type=PointProperties)
    points_index: bpy.props.IntProperty(options=set(), default=-1, update=update_point_collection_index)


class RibbonProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Ribbon'

    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)
    material: bpy.props.PointerProperty(type=shared.M3MatRefPointerProp)
    spline: bpy.props.PointerProperty(type=SplinePointerProp)
    ribbon_type: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_type)
    cull_method: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_cull)
    lod_cut: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    lod_reduce: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    active: bpy.props.BoolProperty(name='Active', default=True)
    active_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    lifespan: bpy.props.FloatProperty(name='Lifespan', min=0.0, default=1.0)
    lifespan_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    lifespan2: bpy.props.FloatProperty(name='Lifespan', min=0.0, default=1.0)
    lifespan2_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    lifespan_randomize: bpy.props.BoolProperty(options=set())
    divisions: bpy.props.FloatProperty(options=set(), min=0.0, default=20.0)
    sides: bpy.props.IntProperty(options=set(), min=3, default=5)
    star_ratio: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0.0, max=1.0, default=0.5)
    speed: bpy.props.FloatProperty(name='Speed', min=0.0)
    speed_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    speed_randomize: bpy.props.BoolProperty(options=set())
    length: bpy.props.FloatProperty(name='Length', min=0.0)
    length_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    yaw: bpy.props.FloatProperty(name='Yaw', unit='ROTATION')
    yaw_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    pitch: bpy.props.FloatProperty(name='Pitch', unit='ROTATION')
    pitch_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    spread_x: bpy.props.FloatProperty(name='Spread X', unit='ROTATION')
    spread_x_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    spread_y: bpy.props.FloatProperty(name='Spread X', unit='ROTATION')
    spread_y_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    twist: bpy.props.FloatVectorProperty(name='Twist', subtype='XYZ', size=3, unit='ROTATION')
    twist_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    scale: bpy.props.FloatVectorProperty(name='Scale', subtype='XYZ', size=3, default=(1, 1, 1))
    scale_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_base: bpy.props.FloatVectorProperty(name='Base Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    color_base_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_mid: bpy.props.FloatVectorProperty(name='Center Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    color_mid_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_tip: bpy.props.FloatVectorProperty(name='Tip Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 0))
    color_tip_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    twist_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=1)
    scale_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=1)
    color_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=1)
    alpha_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=1)
    twist_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    scale_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    color_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    alpha_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    scale_smoothing: bpy.props.EnumProperty(options=set(), items=bl_enum.anim_smoothing)
    color_smoothing: bpy.props.EnumProperty(options=set(), items=bl_enum.anim_smoothing)
    gravity: bpy.props.FloatProperty(options=set())
    noise_amplitude: bpy.props.FloatProperty(options=set())
    noise_frequency: bpy.props.FloatProperty(options=set())
    noise_cohesion: bpy.props.FloatProperty(options=set())
    noise_edge: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0.0, max=1.0, default=0.1)
    bounce: bpy.props.FloatProperty(options=set(), subtype='FACTOR', soft_min=0.0, soft_max=1.0)
    friction: bpy.props.FloatProperty(options=set(), subtype='FACTOR', soft_min=0.0, soft_max=1.0)
    drag: bpy.props.FloatProperty(options=set())
    mass: bpy.props.FloatProperty(options=set(), default=1.0)
    mass2: bpy.props.FloatProperty(options=set())
    mass_randomize: bpy.props.BoolProperty(options=set())
    local_forces: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=16)
    world_forces: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=16)
    world_space: bpy.props.BoolProperty(options=set())
    yaw_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    yaw_var_amplitude: bpy.props.FloatProperty(name='Yaw Variation Amount')
    yaw_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    yaw_var_frequency: bpy.props.FloatProperty(name='Yaw Variation Frequency')
    yaw_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    pitch_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    pitch_var_amplitude: bpy.props.FloatProperty(name='Pitch Variation Amount')
    pitch_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    pitch_var_frequency: bpy.props.FloatProperty(name='Pitch Variation Frequency')
    pitch_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    length_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    length_var_amplitude: bpy.props.FloatProperty(name='Length Variation Amount')
    length_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    length_var_frequency: bpy.props.FloatProperty(name='Length Variation Frequency')
    length_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    scale_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    scale_var_amplitude: bpy.props.FloatProperty(name='Scale Variation Amount')
    scale_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    scale_var_frequency: bpy.props.FloatProperty(name='Scale Variation Frequency')
    scale_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    alpha_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    alpha_var_amplitude: bpy.props.FloatProperty(name='Alpha Variation Amount')
    alpha_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    alpha_var_frequency: bpy.props.FloatProperty(name='Alpha Variation Frequency')
    alpha_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    parent_velocity: bpy.props.FloatProperty(name='Parent Velocity', subtype='FACTOR', soft_min=0.0, soft_max=1.0)
    parent_velocity_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    phase_shift: bpy.props.FloatProperty(name='Phase Shift')
    phase_shift_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    collide_terrain: bpy.props.BoolProperty(options=set())
    collide_objects: bpy.props.BoolProperty(options=set())
    edge_falloff: bpy.props.BoolProperty(options=set())
    inherit_parent_velocity: bpy.props.BoolProperty(options=set())
    scale_smooth: bpy.props.BoolProperty(options=set())
    scale_bezier: bpy.props.BoolProperty(options=set())
    vertex_alpha: bpy.props.BoolProperty(options=set())
    scale_time_parent: bpy.props.BoolProperty(options=set())
    force_cpu_sim: bpy.props.BoolProperty(options=set())
    local_time: bpy.props.BoolProperty(options=set())
    simulate_init: bpy.props.BoolProperty(options=set())
    length_time: bpy.props.BoolProperty(options=set())
    accurate_gpu_tangents: bpy.props.BoolProperty(options=set())


class PointsMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_ribbonsplinepoints'
    bl_label = 'Menu'

    def draw(self, context):
        spline = context.object.m3_ribbonsplines[context.object.m3_ribbonsplines_index]
        shared.draw_menu_duplicate(self.layout, spline.points, dup_keyframes_opt=True)


class SplineMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_ribbonsplines'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_ribbonsplines, dup_keyframes_opt=True)


class RibbonMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_ribbons'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_ribbons, dup_keyframes_opt=True)


class RibbonPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_RIBBONS'
    bl_label = 'M3 Ribbons'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_ribbons, None, menu_id=RibbonMenu.bl_idname)


class RibbonSubPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_parent_id = 'OBJECT_PT_M3_RIBBONS'

    @classmethod
    def poll(cls, context):
        return context.object.m3_ribbons_index in range(len(context.object.m3_ribbons))


class RibbonPanelEmitter(RibbonSubPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ribbons_emitter'
    bl_label = 'Emitter'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        ribbon = context.object.m3_ribbons[context.object.m3_ribbons_index]

        shared.draw_prop_pointer_search(layout, ribbon.bone, ribbon.id_data.data, 'bones', text='Bone', icon='BONE_DATA')
        shared.draw_prop_pointer_search(layout, ribbon.material, ribbon.id_data, 'm3_materialrefs', text='Material', icon='MATERIAL')
        shared.draw_prop_pointer_search(layout, ribbon.spline, ribbon.id_data, 'm3_ribbonsplines', text='Ribbon Spline', icon='LINKED')
        layout.separator()
        layout.prop(ribbon, 'lod_reduce', text='LOD Reduction')
        layout.prop(ribbon, 'lod_cut', text='Cutoff')
        layout.separator()
        col = layout.column(align=True)
        col.prop(ribbon, 'ribbon_type', text='Ribbon Type')
        if ribbon.ribbon_type == 'CYLINDER':
            col.prop(ribbon, 'sides', text='Edges')
        if ribbon.ribbon_type == 'STAR':
            col.prop(ribbon, 'sides', text='Edges')
            col.prop(ribbon, 'star_ratio', text='Cylinder/Planar Ratio')
        layout.separator()
        layout.prop(ribbon, 'divisions', text='Segments Per Second')
        layout.prop(ribbon, 'simulate_init', text='Pre Pump')
        layout.separator()
        shared.draw_prop_anim(layout, ribbon, 'active', text='Active')
        layout.separator()
        layout.prop(ribbon, 'force_cpu_sim', text='Force CPU Simulation')
        layout.prop(ribbon, 'accurate_gpu_tangents', text='Accurate GPU Tangents')
        layout.prop(ribbon, 'scale_time_parent', text='Scale Time By Parent')
        layout.prop(ribbon, 'local_time', text='Local Time')


class RibbonPanelInstance(RibbonSubPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ribbons_instance'
    bl_label = 'Instance'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        rib_ver = int(context.object.m3_ribbons_version)
        ribbon = context.object.m3_ribbons[context.object.m3_ribbons_index]

        layout.prop(ribbon, 'world_space', text='World Space')
        col = layout.column(align=True)
        col.prop(ribbon, 'cull_method', text='Instance Cull Type')
        if ribbon.cull_method == 'TIME':
            shared.draw_prop_anim(col, ribbon, 'lifespan', text=' ')
        elif ribbon.cull_method == 'LENGTH':
            shared.draw_prop_anim(col, ribbon, 'length', text='Length')
            row = col.row(align=True, heading='Lifespan')
            row.prop(ribbon, 'length_time', text='')
            sub = row.column(align=True)
            sub.active = ribbon.length_time
            shared.draw_prop_anim(sub, ribbon, 'lifespan', text='')
        layout.separator()
        shared.draw_prop_anim(layout, ribbon, 'speed', text='Velocity')
        row = shared.draw_prop_split(layout, text='Yaw/Pitch')
        shared.draw_op_anim_prop(row, ribbon, 'yaw')
        row.separator(factor=0.325)
        shared.draw_op_anim_prop(row, ribbon, 'pitch')
        layout.separator()
        row = shared.draw_prop_split(layout, text='Parent Velocity')
        row.prop(ribbon, 'inherit_parent_velocity', text='')
        sub = row.row()
        sub.active = ribbon.inherit_parent_velocity
        shared.draw_op_anim_prop(sub, ribbon, 'parent_velocity')
        layout.separator()
        col = layout.column(align=True)
        if rib_ver >= 8:
            col.prop(ribbon, 'color_smoothing', text='Color Smoothing')
        row = col.row(align=True)
        row.prop(ribbon, 'color_anim_mid', text='RGB/A Midpoint')
        row.prop(ribbon, 'alpha_anim_mid', text='')
        if ribbon.color_smoothing in ('LINEARHOLD', 'BEZIERHOLD') and rib_ver >= 8:
            row = col.row(align=True)
            row.prop(ribbon, 'color_anim_mid_time', text='RGB/A Hold Time')
            row.prop(ribbon, 'alpha_anim_mid_time', text='')
        col = layout.column(align=True)
        shared.draw_prop_anim(col, ribbon, 'color_base', text='Base')
        shared.draw_prop_anim(col, ribbon, 'color_mid', text='Center')
        shared.draw_prop_anim(col, ribbon, 'color_tip', text='Tip')
        row = layout.row()
        row.prop(ribbon, 'vertex_alpha', text='Vertex Alpha')
        row.prop(ribbon, 'edge_falloff', text='Edge Falloff')
        layout.separator()
        row = shared.draw_prop_split(layout, text='Scale Smoothing')
        sub = row.row(align=True)
        sub.ui_units_x = 1
        if rib_ver >= 8:
            sub.prop(ribbon, 'scale_smoothing', text='')
        row.separator(factor=0.325)
        sub = row.row(align=True)
        sub.ui_units_x = 1
        sub.prop(ribbon, 'scale_anim_mid', text='')
        if ribbon.scale_smoothing in ('LINEARHOLD', 'BEZIERHOLD') and rib_ver >= 8:
            sub.prop(ribbon, 'scale_anim_mid_time', text='')
        col = layout.column(align=True)
        shared.draw_prop_anim(col, ribbon, 'scale', index=0, text='Base')
        shared.draw_prop_anim(col, ribbon, 'scale', index=1, text='Center')
        shared.draw_prop_anim(col, ribbon, 'scale', index=2, text='Tip')
        layout.separator()
        row = layout.row(align=True)
        row.prop(ribbon, 'twist_anim_mid', text='Twist Midpoint')
        # row.prop(ribbon, 'twist_anim_mid_time', text='Animation Center Time')
        col = layout.column(align=True)
        shared.draw_prop_anim(col, ribbon, 'twist', index=0, text='Base')
        shared.draw_prop_anim(col, ribbon, 'twist', index=1, text='Center')
        shared.draw_prop_anim(col, ribbon, 'twist', index=2, text='Tip')


class RibbonPanelInstanceVariation(RibbonSubPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ribbons_instancevariation'
    bl_label = 'Instance Variation'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        ribbon = context.object.m3_ribbons[context.object.m3_ribbons_index]
        shared.draw_prop_anim(layout, ribbon, 'phase_shift', text='Phase Shift')
        layout.separator()
        shared.draw_var_props(layout, ribbon, 'yaw', text='Yaw')
        shared.draw_var_props(layout, ribbon, 'pitch', text='Pitch')
        shared.draw_var_props(layout, ribbon, 'length', text='Length')
        shared.draw_var_props(layout, ribbon, 'scale', text='Scale')
        shared.draw_var_props(layout, ribbon, 'alpha', text='Alpha')


class RibbonPanelPhysics(RibbonSubPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ribbons_physics'
    bl_label = 'Physics'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        rib_ver = int(context.object.m3_ribbons_version)
        ribbon = context.object.m3_ribbons[context.object.m3_ribbons_index]

        layout.prop(ribbon, 'mass', text='Mass')
        layout.prop(ribbon, 'gravity', text='Gravity')
        layout.prop(ribbon, 'drag', text='Drag')
        layout.separator()
        if rib_ver >= 8:
            row = layout.row()
            row.prop(ribbon, 'collide_terrain', text='Collide Terrain')
            row.prop(ribbon, 'collide_objects', text='Collide Objects')
            layout.prop(ribbon, 'friction', text='Friction')
            layout.prop(ribbon, 'bounce', text='Bounce')
            layout.separator()
        col = shared.draw_prop_split(layout, text='Local Force Channels', sep=2.05)
        col.prop(ribbon, 'local_forces', text='')
        col = shared.draw_prop_split(layout, text='World Force Channels', sep=2.05)
        col.prop(ribbon, 'world_forces', text='')


class RibbonPanelNoise(RibbonSubPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ribbons_noise'
    bl_label = 'Noise'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        ribbon = context.object.m3_ribbons[context.object.m3_ribbons_index]

        layout.prop(ribbon, 'noise_amplitude', text='Amplitude')
        layout.prop(ribbon, 'noise_frequency', text='Frequency')
        layout.prop(ribbon, 'noise_cohesion', text='Cohesion')
        layout.prop(ribbon, 'noise_edge', text='Edge')


class SplinePanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_RIBBONSPLINES'
    bl_label = 'M3 Ribbon Splines'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_ribbonsplines, draw_spline_props, menu_id=SplineMenu.bl_idname)


classes = (
    SplinePointerProp,
    PointProperties,
    SplineProperties,
    RibbonProperties,
    PointsMenu,
    SplineMenu,
    RibbonMenu,
    RibbonPanel,
    RibbonPanelEmitter,
    RibbonPanelInstance,
    RibbonPanelInstanceVariation,
    RibbonPanelPhysics,
    RibbonPanelNoise,
    SplinePanel,
)
