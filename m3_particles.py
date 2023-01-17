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
    bpy.types.Object.m3_particle_systems = bpy.props.CollectionProperty(type=SystemProperties)
    bpy.types.Object.m3_particle_systems_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)
    bpy.types.Object.m3_particle_systems_version = bpy.props.EnumProperty(options=set(), items=particle_system_versions, default='24')
    bpy.types.Object.m3_particle_copies = bpy.props.CollectionProperty(type=CopyProperties)
    bpy.types.Object.m3_particle_copies_index = bpy.props.IntProperty(options=set(), default=-1, update=update_copy_collection_index)


# TODO UI stuff
particle_system_versions = (
    ('10', '10', 'Version 10'),
    ('11', '11', 'Version 11'),
    ('12', '12', 'Version 12'),
    ('17', '17', 'Version 17'),
    ('18', '18', 'Version 18'),
    ('19', '19', 'Version 19'),
    ('21', '21', 'Version 21'),
    ('22', '22', 'Version 22'),
    ('23', '23', 'Version 23'),
    ('24', '24', 'Version 24'),
)


def update_collection_index(self, context):
    if self.m3_particle_systems_index in range(len(self.m3_particle_systems)):
        bl = self.m3_particle_systems[self.m3_particle_systems_index]
        shared.select_bones_handles(context.object, [bl.bone])


def update_copy_collection_index(self, context):
    if self.m3_particle_copies_index in range(len(self.m3_particle_copies)):
        bl = self.m3_particle_copies[self.m3_particle_copies_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_copy_props(copy, layout):
    shared.draw_pointer_prop(layout, copy.id_data.data.bones, copy, 'bone', label='Bone', icon='BONE_DATA')
    col = layout.column(align=True)
    col.prop(copy, 'emit_rate', text='Emission Rate')
    col.prop(copy, 'emit_count', text='Emission Amount')
    layout.separator()
    shared.draw_handle_list(layout.box(), copy.id_data.m3_particle_systems, copy, 'systems', label='Particle System')


def draw_props(particle, layout):
    col = layout.column()
    shared.draw_pointer_prop(col, particle.id_data.data.bones, particle, 'bone', label='Bone', icon='BONE_DATA')
    shared.draw_pointer_prop(col, particle.id_data.m3_materialrefs, particle, 'material', label='Material', icon='MATERIAL')
    col.prop(particle, 'particle_type', text='Type')

    if particle.particle_type == 'RECT_BILLBOARD':
        col.prop(particle, 'length_width_ratio', text='Length/Width Ratio')

    col.prop(particle, 'distance_limit', text='Distance Limit')
    col = layout.column(align=True)
    col.prop(particle, 'lod_reduce', text='LOD Reduction')
    col.prop(particle, 'lod_cut', text='Cutoff')
    col.separator()
    col.prop(particle, 'emit_max', text='Emission Max')
    col.prop(particle, 'emit_rate', text='Rate')
    col.prop(particle, 'emit_count', text='Count')
    col.separator()
    col = layout.column(align=True)
    col.prop(particle, 'emit_type', text='Emission Type')
    col.prop(particle, 'emit_shape', text='Emission Area Shape')

    if particle.emit_shape != 'POINT':
        size_xy = particle.emit_shape in ['PLANE', 'CUBE']
        size_z = particle.emit_shape in ['CUBE', 'CYLINDER']
        size_r = particle.emit_shape in ['SPHERE', 'CYLINDER', 'DISC']
        if size_xy or size_z or size_r:
            if size_xy:
                col.prop(particle, 'emit_shape_size', index=0, text='X')
                col.prop(particle, 'emit_shape_size', index=1, text='Y')
            if size_z:
                col.prop(particle, 'emit_shape_size', index=2, text='Z')
            if size_r:
                col.prop(particle, 'emit_shape_radius', text='R')
            col.prop(particle, 'emit_shape_cutout', index=0, text='Emission Area Cutout')
            col = col.column(align=True)
            col.active = particle.emit_shape_cutout
            if size_xy:
                col.prop(particle, 'emit_shape_size_cutout', index=0, text='X')
                col.prop(particle, 'emit_shape_size_cutout', index=1, text='Y')
            if size_z:
                col.prop(particle, 'emit_shape_size_cutout', index=2, text='Z')
            if size_r:
                col.prop(particle, 'emit_shape_radius_cutout', text='R')
        elif particle.emit_shape == 'SPLINE':
            box = col.box()
            box.use_property_split = False
            op = box.operator('m3.collection_add', text='Add Spline Point')
            op.collection = particle.emit_shape_spline.path_from_id()
            for ii, item in enumerate(particle.emit_shape_spline):
                row = box.row(align=True)
                row.prop(item, 'location', index=0, text='X')
                row.prop(item, 'location', index=1, text='Y')
                row.prop(item, 'location', index=2, text='Z')
                row.separator()
                op = row.operator('m3.collection_remove', icon='X', text='')
                op.collection, op.index = (particle.emit_shape_spline.path_from_id(), ii)
        elif particle.emit_shape == 'MESH':
            box = col.box()
            box.use_property_split = False
            op = box.operator('m3.collection_add', text='Add Mesh Object')
            op.collection = particle.emit_shape_meshes.path_from_id()
            for ii, item in enumerate(particle.emit_shape_meshes):
                row = box.row()
                row.prop(item, 'bl_object', text='')
                op = row.operator('m3.collection_remove', icon='X', text='')
                op.collection, op.index = (particle.emit_shape_meshes.path_from_id(), ii)

    col = layout.column(align=True)
    col.prop(particle, 'emit_speed', text='Emission Speed')
    row = col.row(align=True, heading='Randomize')
    row.prop(particle, 'emit_speed_randomize', text='')
    sub = row.column(align=True)
    sub.active = particle.emit_speed_randomize
    sub.prop(particle, 'emit_speed_random', text='')
    col.separator()
    col.prop(particle, 'emit_angle_x', text='Emission Angle X')
    col.prop(particle, 'emit_angle_y', text='Y')
    col.separator()
    col.prop(particle, 'emit_spread_x', text='Emission Spread X')
    col.prop(particle, 'emit_spread_y', text='Y')
    col.separator()
    col.prop(particle, 'lifespan', text='Lifespan')
    row = col.row(align=True, heading='Randomize')
    row.prop(particle, 'lifespan_randomize', text='')
    sub = row.column(align=True)
    sub.active = particle.lifespan_randomize
    sub.prop(particle, 'lifespan_random', text='')
    col.separator()
    col.prop(particle, 'mass', text='Mass')
    row = col.row(align=True, heading='Randomize')
    row.prop(particle, 'mass_randomize', text='')
    sub = row.column(align=True)
    sub.active = particle.mass_randomize
    sub.prop(particle, 'mass2', text='')
    col.separator()
    col.prop(particle, 'gravity', text='Gravity')
    col.prop(particle, 'drag', text='Drag')
    col.prop(particle, 'friction', text='Friction')
    col.prop(particle, 'bounce', text='Bounce')
    col.prop(particle, 'wind_multiplier', text='Wind Multiplier')
    col = layout.column()
    col.separator()
    sub = col.column(align=True)
    sub.prop(particle, 'color_init', text='Color Initial')
    sub.prop(particle, 'color_mid', text='Middle')
    sub.prop(particle, 'color_end', text='Final')
    row = col.row(align=True, heading='Randomize')
    row.prop(particle, 'color_randomize', text='')
    sub = col.column(align=True)
    sub.active = particle.color_randomize
    sub.prop(particle, 'color2_init', text='Color Random Initial')
    sub.prop(particle, 'color2_mid', text='Middle')
    sub.prop(particle, 'color2_end', text='Final')
    sub = col.column()
    sub.separator()
    sub2 = sub.column(align=True)
    sub2.prop(particle, 'color_smoothing', text='Color Smooth Type')
    sub2.prop(particle, 'color_anim_mid', text='Color Middle')
    sub2.prop(particle, 'alpha_anim_mid', text='Alpha Middle')

    if particle.color_smoothing == 'LINEARHOLD' or particle.color_smoothing == 'BEZIERHOLD':
        sub2.prop(particle, 'color_hold', text='Color Hold Time')
        sub2.prop(particle, 'alpha_hold', text='Alpha Hold Time')

    col = layout.column(align=True)
    col.prop(particle, 'rotation', index=0, text='Rotation Initial')
    col.prop(particle, 'rotation', index=1, text='Middle')
    col.prop(particle, 'rotation', index=2, text='Final')
    row = col.row(align=True, heading='Randomize')
    row.prop(particle, 'rotation_randomize', text='')
    sub = col.column(align=True)
    sub.active = particle.rotation_randomize
    sub.prop(particle, 'rotation2', index=0, text='Rotation Random Initial')
    sub.prop(particle, 'rotation2', index=1, text='Middle')
    sub.prop(particle, 'rotation2', index=2, text='Final')
    sub = col.column(align=True)
    sub.separator()
    sub2 = sub.column(align=True)
    sub2.prop(particle, 'rotation_smoothing', text='Rotation Smooth Type')
    sub2.prop(particle, 'rotation_anim_mid', text='Rotation Middle')

    if particle.rotation_smoothing == 'LINEARHOLD' or particle.rotation_smoothing == 'BEZIERHOLD':
        sub2.prop(particle, 'rotation_hold', text='Rotation Hold Time')

    col = layout.column(align=True)
    col.prop(particle, 'size', index=0, text='Size Initial')
    col.prop(particle, 'size', index=1, text='Middle')
    col.prop(particle, 'size', index=2, text='Final')
    row = col.row(align=True, heading='Randomize')
    row.prop(particle, 'size_randomize', text='')
    sub = col.column(align=True)
    sub.active = particle.size_randomize
    sub.prop(particle, 'size2', index=0, text='Size Random Initial')
    sub.prop(particle, 'size2', index=1, text='Middle')
    sub.prop(particle, 'size2', index=2, text='Final')
    sub = col.column()
    sub.separator()
    sub2 = sub.column(align=True)
    sub2.prop(particle, 'size_smoothing', text='Size Smooth Type')
    sub2.prop(particle, 'size_anim_mid', text='Size Middle')

    if particle.size_smoothing == 'LINEARHOLD' or particle.size_smoothing == 'BEZIERHOLD':
        sub2.prop(particle, 'size_hold', text='Size Hold Time')

    col = layout.column(align=True)
    col.prop(particle, 'noise_amplitude', text='Noise Amplitude')
    col.prop(particle, 'noise_frequency', text='Frequency')
    col.prop(particle, 'noise_cohesion', text='Cohesion')
    col.prop(particle, 'noise_edge', text='Edge')
    col = layout.column()
    sub = col.column(align=True)
    sub.prop(particle, 'uv_flipbook_cols', text='Flipbook Columns')
    sub.prop(particle, 'uv_flipbook_rows', text='Rows')
    sub = col.column(align=True)
    sub.prop(particle, 'uv_flipbook_col_fraction', text='Column Width')
    sub.prop(particle, 'uv_flipbook_row_fraction', text='Row Height')
    col = layout.column()
    sub = col.column(align=True)
    sub.prop(particle, 'uv_flipbook_start_init_index', text='Phase 1 Start')
    sub.prop(particle, 'uv_flipbook_start_stop_index', text='End')
    sub = col.column(align=True)
    sub.prop(particle, 'uv_flipbook_end_init_index', text='Phase 2 Start')
    sub.prop(particle, 'uv_flipbook_end_stop_index', text='End')
    sub = col.column(align=True)
    sub.prop(particle, 'uv_flipbook_start_lifespan_factor', text='Phase 1 Length')
    col = layout.column(align=True)
    col.separator()
    shared.draw_pointer_prop(col, particle.id_data.m3_particle_systems, particle, 'trail_particle', label='Trailing Particle', icon='LINKED')
    col.prop(particle, 'trail_chance', text='Chance')
    col.prop(particle, 'trail_rate', text='Rate')
    col = layout.column()
    col.use_property_split = False
    col.prop(particle, 'local_forces', text='Local Force Channels')
    col.prop(particle, 'world_forces', text='World Force Channels')
    col = layout.column_flow(align=True, columns=2)
    col.use_property_split = False
    col.prop(particle, 'trailing', text='Trailing Enabled')
    col.prop(particle, 'sort', text='Sort')
    col.prop(particle, 'collide_terrain', text='Collide Terrain')
    col.prop(particle, 'collide_objects', text='Collide Objects')
    col.prop(particle, 'spawn_on_bounce', text='Spawn On Bounce')
    col.prop(particle, 'inherit_emit_shape', text='Inherit Emission Area')
    col.prop(particle, 'inherit_emit_params', text='Inherit Emission Parameters')
    col.prop(particle, 'inherit_parent_velocity', text='Inherit Parent Velocity')
    col.prop(particle, 'sort_z_height', text='Sort By Z-Height')
    col.prop(particle, 'old_rotation_smooth', text='Smooth Rotation (Old)')
    col.prop(particle, 'old_rotation_smooth_bezier', text='Smooth Rotation Bezier (Old)')
    col.prop(particle, 'old_size_smooth', text='Smooth Size (Old)')
    col.prop(particle, 'old_size_smooth_bezier', text='Smooth Size Bezier (Old)')
    col.prop(particle, 'old_color_smooth', text='Smooth Color (Old)')
    col.prop(particle, 'old_color_smooth_bezier', text='Smooth Color Bezier (Old)')
    col.prop(particle, 'reverse_iteration', text='Reverse Iteration')
    col.prop(particle, 'lit_parts', text='Lit Parts')
    col.prop(particle, 'random_uv_flipbook_start', text='uv Start')
    col.prop(particle, 'multiply_gravity', text='Multiply By Gravity')
    col.prop(particle, 'clamp_trailing_particles', text='Clamp Trailing Parts')
    col.prop(particle, 'spawn_trailing_particles', text='Spawn Trailing Parts')
    col.prop(particle, 'fix_length_trailing_particles', text='Fix Length Trailing Parts')
    col.prop(particle, 'vertex_alpha', text='Use Vertex Alpha')
    col.prop(particle, 'model_parts', text='Model Parts')
    col.prop(particle, 'swap_yz_on_model_parts', text='Swap Y-Z On Model Parts')
    col.prop(particle, 'scale_time_parent', text='Scale Time By Parent')
    col.prop(particle, 'local_time', text='Use Local Time')
    col.prop(particle, 'simulate_init', text='Simulate On Init')
    col.prop(particle, 'copy', text='Copy')
    col.prop(particle, 'relative', text='Relative Rotation')
    col.prop(particle, 'always_set', text='Always Set')


class SplinePointProperties(shared.M3PropertyGroup):
    location: bpy.props.FloatVectorProperty(name='Location', subtype='XYZ', size=3)


class CopyProperties(shared.M3BoneUserPropertyGroup):
    systems: bpy.props.CollectionProperty(type=shared.M3PropertyGroup)
    emit_rate: bpy.props.FloatProperty(name='Particle Copy Emission Rate', min=0)
    emit_count: bpy.props.IntProperty(name='Particle Copy Emission Count', min=0)


class SystemProperties(shared.M3BoneUserPropertyGroup):
    material: bpy.props.StringProperty(options=set())
    particle_type: bpy.props.EnumProperty(options=set(), items=bl_enum.particle_type)
    length_width_ratio: bpy.props.FloatProperty(default=1)
    distance_limit: bpy.props.FloatProperty(options=set(), min=0)
    lod_cut: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    lod_reduce: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    emit_type: bpy.props.EnumProperty(options=set(), items=bl_enum.particle_emit_type)
    emit_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.particle_shape)
    emit_shape_cutout: bpy.props.BoolProperty(options=set())
    emit_shape_size: bpy.props.FloatVectorProperty(name='Emission Area Size', subtype='XYZ', size=3, default=(1, 1, 1))
    emit_shape_size_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_shape_size_cutout: bpy.props.FloatVectorProperty(name='Emission Area Size Cutout', subtype='XYZ', size=3)
    emit_shape_size_cutout_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_shape_radius: bpy.props.FloatProperty(name='Emission Radius', default=1)
    emit_shape_radius_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_shape_radius_cutout: bpy.props.FloatProperty(name='Emission Radius Cutout')
    emit_shape_radius_cutout_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_shape_meshes: bpy.props.CollectionProperty(type=shared.M3ObjectPropertyGroup)
    emit_shape_spline: bpy.props.CollectionProperty(type=SplinePointProperties)
    emit_max: bpy.props.IntProperty(options=set(), min=0)
    emit_rate: bpy.props.FloatProperty(name='Emission Rate', min=0)
    emit_rate_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_count: bpy.props.IntProperty(name='Emission Amount', min=0)
    emit_count_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_speed: bpy.props.FloatProperty(name='Emission Speed')
    emit_speed_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_speed_random: bpy.props.FloatProperty(name='Emission Speed Random', default=1)
    emit_speed_random_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_speed_randomize: bpy.props.BoolProperty(options=set())
    emit_angle_x: bpy.props.FloatProperty(name='Emission Angle X')
    emit_angle_x_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_angle_y: bpy.props.FloatProperty(name='Emission Angle Y')
    emit_angle_y_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_spread_x: bpy.props.FloatProperty(name='Emission Spread X')
    emit_spread_x_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    emit_spread_y: bpy.props.FloatProperty(name='Emission Spread Y')
    emit_spread_y_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    lifespan: bpy.props.FloatProperty(name='Lifespan', default=0.5, min=0)
    lifespan_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    lifespan_random: bpy.props.FloatProperty(name='Lifespan Random', default=1, min=0)
    lifespan_random_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    lifespan_randomize: bpy.props.BoolProperty(options=set())
    gravity: bpy.props.FloatProperty(options=set())
    mass: bpy.props.FloatProperty(options=set())
    mass2: bpy.props.FloatProperty(options=set(), default=1)
    mass_randomize: bpy.props.BoolProperty(options=set())
    friction: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1)
    bounce: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1)
    drag: bpy.props.FloatProperty(options=set(), min=0)
    wind_multiplier: bpy.props.FloatProperty(options=set())
    color_init: bpy.props.FloatVectorProperty(name='Initial Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    color_init_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_mid: bpy.props.FloatVectorProperty(name='Middle Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    color_mid_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_end: bpy.props.FloatVectorProperty(name='Final Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 0))
    color_end_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color2_init: bpy.props.FloatVectorProperty(name='Initial Color Random', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    color2_init_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color2_mid: bpy.props.FloatVectorProperty(name='Middle Color Random', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    color2_mid_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color2_end: bpy.props.FloatVectorProperty(name='Final Color Random', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 0))
    color2_end_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_randomize: bpy.props.BoolProperty(options=set())
    rotation: bpy.props.FloatVectorProperty(name='Rotation', subtype='XYZ', size=3)
    rotation_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    rotation2: bpy.props.FloatVectorProperty(name='Rotation Random', subtype='XYZ', size=3)
    rotation2_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    rotation_randomize: bpy.props.BoolProperty(options=set())
    size: bpy.props.FloatVectorProperty(name='Size', subtype='XYZ', size=3, default=(1, 1, 1))
    size_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    size2: bpy.props.FloatVectorProperty(name='Size Random', subtype='XYZ', size=3, default=(1, 1, 1))
    size2_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    size_randomize: bpy.props.BoolProperty(options=set())
    color_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    alpha_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    rotation_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    size_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    color_hold: bpy.props.FloatProperty(options=set(), min=0)
    alpha_hold: bpy.props.FloatProperty(options=set(), min=0)
    rotation_hold: bpy.props.FloatProperty(options=set(), min=0)
    size_hold: bpy.props.FloatProperty(options=set(), min=0)
    color_smoothing: bpy.props.EnumProperty(options=set(), items=bl_enum.anim_smoothing)
    rotation_smoothing: bpy.props.EnumProperty(options=set(), items=bl_enum.anim_smoothing)
    size_smoothing: bpy.props.EnumProperty(options=set(), items=bl_enum.anim_smoothing)
    noise_amplitude: bpy.props.FloatProperty(options=set())
    noise_frequency: bpy.props.FloatProperty(options=set())
    noise_cohesion: bpy.props.FloatProperty(options=set())
    noise_edge: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=0.5)
    trail_particle: bpy.props.StringProperty(options=set())
    trail_chance: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1)
    trail_rate: bpy.props.FloatProperty(name='Particle Trail Rate', default=10)
    trail_rate_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    uv_flipbook_cols: bpy.props.IntProperty(options=set(), min=0)
    uv_flipbook_rows: bpy.props.IntProperty(options=set(), min=0)
    uv_flipbook_col_fraction: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1)
    uv_flipbook_row_fraction: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1)
    uv_flipbook_start_init_index: bpy.props.IntProperty(options=set(), min=0, max=255)
    uv_flipbook_start_stop_index: bpy.props.IntProperty(options=set(), min=0, max=255)
    uv_flipbook_end_init_index: bpy.props.IntProperty(options=set(), min=0, max=255)
    uv_flipbook_end_stop_index: bpy.props.IntProperty(options=set(), min=0, max=255)
    uv_flipbook_start_lifespan_factor: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    local_forces: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=16)
    world_forces: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=16)
    trailing: bpy.props.BoolProperty(options=set())
    sort: bpy.props.BoolProperty(options=set())
    collide_terrain: bpy.props.BoolProperty(options=set())
    collide_objects: bpy.props.BoolProperty(options=set())
    spawn_on_bounce: bpy.props.BoolProperty(options=set())
    inherit_emit_shape: bpy.props.BoolProperty(options=set())
    inherit_emit_params: bpy.props.BoolProperty(options=set())
    inherit_parent_velocity: bpy.props.BoolProperty(options=set())
    sort_z_height: bpy.props.BoolProperty(options=set())
    reverse_iteration: bpy.props.BoolProperty(options=set())
    old_color_smooth: bpy.props.BoolProperty(options=set())
    old_color_smooth_bezier: bpy.props.BoolProperty(options=set())
    old_rotation_smooth: bpy.props.BoolProperty(options=set())
    old_rotation_smooth_bezier: bpy.props.BoolProperty(options=set())
    old_size_smooth: bpy.props.BoolProperty(options=set())
    old_size_smooth_bezier: bpy.props.BoolProperty(options=set())
    lit_parts: bpy.props.BoolProperty(options=set())
    random_uv_flipbook_start: bpy.props.BoolProperty(options=set())
    multiply_gravity: bpy.props.BoolProperty(options=set())
    clamp_trailing_particles: bpy.props.BoolProperty(options=set())
    spawn_trailing_particles: bpy.props.BoolProperty(options=set())
    fix_length_trailing_particles: bpy.props.BoolProperty(options=set())
    vertex_alpha: bpy.props.BoolProperty(options=set())
    model_parts: bpy.props.BoolProperty(options=set())
    swap_yz_on_model_parts: bpy.props.BoolProperty(options=set())
    scale_time_parent: bpy.props.BoolProperty(options=set())
    local_time: bpy.props.BoolProperty(options=set())
    simulate_init: bpy.props.BoolProperty(options=set())
    copy: bpy.props.BoolProperty(options=set())
    relative: bpy.props.BoolProperty(options=set())
    always_set: bpy.props.BoolProperty(options=set())


class SystemMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_particle_systems'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_particle_systems, dup_keyframes_opt=True)


class CopyMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_particle_copies'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_particle_copies, dup_keyframes_opt=True)


class CopyPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_m3_particle_copies'
    bl_label = 'M3 Particle Copies'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_particle_copies, draw_copy_props, menu_id=CopyMenu.bl_idname)


class SystemPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_m3_particle_systems'
    bl_label = 'M3 Particle Systems'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_particle_systems, draw_props, menu_id=SystemMenu.bl_idname)


classes = (
    SplinePointProperties,
    CopyProperties,
    SystemProperties,
    SystemMenu,
    CopyMenu,
    SystemPanel,
    CopyPanel,
)
