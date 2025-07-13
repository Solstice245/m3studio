#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

import mathutils

rot_fix_matrix = mathutils.Matrix(((0, 1, 0, 0),
                                  (-1, 0, 0, 0),
                                   (0, 0, 1, 0),
                                   (0, 0, 0, 1)))

rot_fix_matrix_transpose = rot_fix_matrix.transposed()


def io_anim_group(processor):
    processor.float('movement_speed')
    processor.integer('frequency')
    processor.bit('flags', 'not_looping')
    processor.bit('flags', 'always_global')
    processor.bit('flags', 'unknown0x4')
    processor.bit('flags', 'global_in_previewer')


def io_material_standard(processor):
    processor.bit('flags', 'vertex_color')
    processor.bit('flags', 'vertex_alpha')
    processor.bit('flags', 'unfogged')
    processor.bit('flags', 'two_sided')
    processor.bit('flags', 'unshaded')
    processor.bit('flags', 'no_shadows_cast')
    processor.bit('flags', 'no_hittest')
    processor.bit('flags', 'no_shadows_receive')
    processor.bit('flags', 'depth_prepass')
    processor.bit('flags', 'terrain_hdr')
    # processor.bit('flags', 'unknown0x400')
    processor.bit('flags', 'simulate_roughness')
    processor.bit('flags', 'pixel_forward_lighting')
    processor.bit('flags', 'depth_fog')
    processor.bit('flags', 'transparent_shadows')
    processor.bit('flags', 'decal_lighting')
    processor.bit('flags', 'transparent_depth_effects')
    processor.bit('flags', 'transparent_local_lights')
    processor.bit('flags', 'disable_soft')
    processor.bit('flags', 'double_lambert')
    processor.bit('flags', 'hair_layer_sorting')
    processor.bit('flags', 'accept_splats')
    processor.bit('flags', 'decal_low_required')
    processor.bit('flags', 'emis_low_required')
    processor.bit('flags', 'spec_low_required')
    processor.bit('flags', 'accept_splats_only')
    processor.bit('flags', 'background_object')
    # processor.bit('flags', 'unknown0x8000000')
    processor.bit('flags', 'depth_prepass_low_required')
    processor.bit('flags', 'no_highlighting')
    processor.bit('flags', 'clamp_output')
    processor.bit('flags', 'geometry_visible', since_version=17)
    processor.integer('material_class')
    processor.enum('blend_mode')
    processor.integer('priority')
    processor.float('specularity')
    processor.float('depth_blend_falloff')
    processor.integer('alpha_test_threshold')
    processor.float('hdr_spec')
    processor.float('hdr_emis')
    processor.float('hdr_envi_const', since_version=20)
    processor.float('hdr_envi_diff', since_version=20)
    processor.float('hdr_envi_spec', since_version=20)
    processor.enum('blend_mode_layer')
    processor.enum('blend_mode_emis1')
    processor.enum('blend_mode_emis2')
    processor.enum('spec_mode')
    processor.anim_float('parallax_height')
    processor.anim_float('motion_blur')


def io_material_displacement(processor):
    # processor.integer('unknown00') # ! unknown
    processor.anim_float('strength_factor')
    processor.integer('priority')


def io_material_composite(processor):
    processor.integer('priority')


def io_material_composite_section(processor):
    processor.anim_float('alpha_factor')


def io_material_terrain(processor):
    processor.integer('unknown633fd422', since_version=1)


def io_material_volume(processor):
    # processor.integer('unknown00')  # ! not documented
    # processor.integer('unknown01')  # ! not documented
    processor.anim_float('density')
    # processor.integer('unknown02')  # ! not documented
    # processor.integer('unknown03')  # ! not documented


def io_material_volume_noise(processor):
    # processor.integer('unknown50762f82')  # ! not documented
    processor.bit('flags', 'draw_after_transparency')
    processor.anim_float('density')
    processor.anim_float('near_plane')
    processor.anim_float('falloff')
    processor.anim_vec3('scroll_rate')
    processor.anim_vec3('translation')
    processor.anim_vec3('scale')
    processor.anim_vec3('rotation')
    processor.integer('alpha_threshold')
    # processor.integer('unknown1d13acfe')  # ! not documented


def io_material_stb(processor):
    pass


def io_material_creep(processor):
    processor.integer('unknownda1b4eb3')


def io_material_reflection(processor):
    processor.anim_float('reflection_strength')
    processor.anim_float('displacement_strength')
    processor.anim_float('reflection_offset', since_version=2)
    processor.anim_float('blur_angle', since_version=2)
    processor.anim_float('blur_distance', since_version=2)
    processor.bit('flags', 'use_layer_norm')
    processor.bit('flags', 'use_layer_strength')
    processor.bit('flags', 'render_in_transparent_pass')
    processor.bit('flags', 'blurring')
    processor.bit('flags', 'use_layer_blur')


def io_starburst(processor):
    processor.integer('uv_index')
    processor.float('distance_factor')
    processor.float('width')
    processor.float('height')
    processor.float('width_falloff')
    processor.float('height_falloff')
    # processor.integer('unk00')  # ! ignored
    # processor.integer('unk01')  # ! ignored
    processor.float('falloff_threshold')
    processor.float('falloff_rate')
    processor.color('color')
    processor.boolean('face_source')
    # processor.float('unk02')  # ! ignored
    # processor.float('unk03')  # ! ignored


def io_material_lens_flare(processor):
    processor.integer('uv_cols')
    processor.integer('uv_rows')
    processor.float('render_distance')
    processor.anim_float('intensity')
    processor.anim_color('color', since_version=3)
    processor.anim_float('intensity2', since_version=3)
    processor.anim_float('uniform_scale', since_version=3)


def io_material_buffer(processor):
    pass


def io_material_layer(processor):
    # processor.integer('id')  # ! unused
    processor.anim_color('color_value')
    processor.bit('flags', 'uv_wrap_x')
    processor.bit('flags', 'uv_wrap_y')
    processor.bit('flags', 'color_invert')
    processor.bit('flags', 'color_clamp')
    # processor.bit('flags', 'particle_uv_flipbook') # ! handle manually
    # processor.bit('flags', 'video') # ! handled manually
    # processor.bit('flags', 'color') # ! handled manually
    processor.bit('flags', 'fresnel_transform')
    processor.bit('flags', 'fresnel_normalize')
    processor.bit('flags', 'fresnel_local_transform')
    processor.bit('flags', 'fresnel_do_not_mirror')
    processor.enum('uv_source')
    processor.enum('color_channels')
    processor.anim_float('color_multiply')
    processor.anim_float('color_add')
    processor.integer('noise_type')
    processor.float('noise_amplitude', since_version=24)
    processor.float('noise_frequency', since_version=24)
    processor.integer('video_channel')
    processor.integer('video_frame_rate')
    processor.integer('video_frame_start')
    processor.integer('video_frame_end')
    processor.enum('video_mode')
    processor.boolean('video_sync_timing')
    processor.anim_uint32('video_play')
    processor.anim_boolean_flag('video_restart')
    processor.integer('uv_flipbook_rows')
    processor.integer('uv_flipbook_cols')
    processor.anim_uint16('uv_flipbook_frame')
    processor.anim_vec2('uv_offset')
    processor.anim_vec3('uv_angle')
    processor.anim_vec2('uv_tiling')
    processor.anim_float('uv_w_translation')
    processor.anim_float('uv_w_scale')
    processor.anim_float('color_brightness')
    processor.anim_vec3('uv_triplanar_offset', since_version=24)
    processor.anim_vec3('uv_triplanar_scale', since_version=24)
    processor.integer('uv_source_related')
    processor.enum('fresnel_type')
    processor.float('fresnel_exponent')
    processor.float('fresnel_min')
    processor.vec3('fresnel_translation', since_version=25)
    # processor.float('fresnel_max_offset') # ! handled manually
    # processor.vec3('fresnel_invert_mask', since_version=25) # ! handled manually
    processor.float('fresnel_yaw', since_version=25)
    processor.float('fresnel_pitch', since_version=25)
    # processor.integer('uv_density', till_version=25) # ! unused


def io_light(processor):
    processor.enum('shape')
    processor.bit('flags', 'shadows')
    # processor.bit('flags', 'spec') # ! ignored
    processor.bit('flags', 'ao')
    processor.bit('flags', 'light_opaque')
    processor.bit('flags', 'light_transparent')
    processor.bit('flags', 'team_color')
    processor.anim_vec3('color')
    processor.anim_float('intensity')
    # processor.anim_vec3('spec_color') # ! ignored
    # processor.anim_float('spec_intensity') # ! ignored
    processor.anim_float('attenuation_far')
    processor.anim_float('attenuation_near')
    processor.anim_float('hotspot')
    processor.anim_float('falloff')


def io_shadow_box(processor):
    processor.anim_float('length')
    processor.anim_float('width')
    processor.anim_float('height')


def io_camera(processor):
    processor.anim_float('field_of_view')
    processor.boolean('use_vertical_fov', since_version=3)
    processor.enum('depth_of_field_type', since_version=5)
    processor.anim_float('far_clip', since_version=3)
    processor.anim_float('near_clip', since_version=3)
    processor.anim_float('clip2', since_version=3)
    processor.anim_float('focal_depth', since_version=3)
    processor.anim_float('falloff_start', since_version=3)
    processor.anim_float('falloff_end', since_version=3)


def io_particle_system(processor):
    processor.anim_float('emit_speed')
    processor.anim_float('emit_speed_random')
    processor.boolean('emit_speed_randomize', till_version=14)
    processor.bit('additional_flags', 'emit_speed_randomize', since_version=17)
    processor.anim_float('emit_angle_x')
    processor.anim_float('emit_angle_y')
    processor.anim_float('emit_spread_x')
    processor.anim_float('emit_spread_y')
    processor.anim_float('lifespan')
    processor.anim_float('lifespan_random')
    processor.boolean('lifespan_randomize', till_version=14)
    processor.bit('additional_flags', 'lifespan_randomize', since_version=17)
    processor.float('distance_limit')
    processor.float('gravity')
    processor.float('size_anim_mid')
    processor.float('color_anim_mid')
    processor.float('alpha_anim_mid')
    processor.float('rotation_anim_mid')
    processor.float('size_hold', since_version=14)
    processor.float('color_hold', since_version=14)
    processor.float('alpha_hold', since_version=14)
    processor.float('rotation_hold', since_version=14)
    processor.enum('size_smoothing', since_version=14)
    processor.enum('color_smoothing', since_version=14)
    processor.enum('rotation_smoothing', since_version=14)
    processor.anim_vec3('size')
    processor.anim_vec3('rotation')
    processor.anim_color('color_init')
    processor.anim_color('color_mid')
    processor.anim_color('color_end')
    processor.float('drag')
    processor.float('mass')
    processor.float('mass2')
    processor.boolean('mass_randomize', till_version=14)
    processor.bit('additional_flags', 'mass_randomize', since_version=17)
    # processor.float('unknownFloat2c')
    processor.boolean('world_space', till_version=14)
    processor.bit('additional_flags', 'world_space', since_version=17)
    processor.integer('emit_max')
    processor.anim_float('emit_rate')
    processor.enum('emit_shape')
    processor.anim_vec3('emit_shape_size')
    processor.anim_vec3('emit_shape_size_cutout')
    processor.anim_float('emit_shape_radius')
    processor.anim_float('emit_shape_radius_cutout')
    processor.anim_float('spline_bounds_min')
    processor.anim_float('spline_bounds_max')
    processor.enum('emit_type')
    processor.boolean('size_randomize')
    processor.anim_vec3('size2')
    processor.boolean('rotation_randomize')
    processor.anim_vec3('rotation2')
    processor.boolean('color_randomize')
    processor.boolean('alpha_randomize')
    processor.anim_color('color2_init')
    processor.anim_color('color2_mid')
    processor.anim_color('color2_end')
    processor.anim_int16('emit_count')
    processor.integer('uv_flipbook_start_init_index')
    processor.integer('uv_flipbook_start_stop_index')
    processor.integer('uv_flipbook_end_init_index')
    processor.integer('uv_flipbook_end_stop_index')
    processor.float('uv_flipbook_start_lifespan_factor')
    processor.integer('uv_flipbook_cols')
    processor.integer('uv_flipbook_rows')
    # processor.float('uv_flipbook_col_fraction')  # ! handled by script
    # processor.float('uv_flipbook_row_fraction')  # ! handled by script
    processor.float('bounce')
    processor.float('friction')
    processor.integer('collide_emit_min')
    processor.integer('collide_emit_max')
    processor.float('collide_emit_chance')
    processor.float('collide_emit_energy')
    processor.integer('collide_events_cull')
    processor.enum('particle_type')
    processor.float('instance_tail')
    processor.bits_16('local_forces')
    processor.bits_16('world_forces')
    processor.float('noise_amplitude')
    processor.float('noise_frequency')
    processor.float('noise_cohesion')
    processor.float('noise_edge')
    processor.enum('yaw_var_shape')
    processor.anim_float('yaw_var_amplitude')
    processor.anim_float('yaw_var_frequency')
    processor.enum('pitch_var_shape')
    processor.anim_float('pitch_var_amplitude')
    processor.anim_float('pitch_var_frequency')
    processor.enum('speed_var_shape')
    processor.anim_float('speed_var_amplitude')
    processor.anim_float('speed_var_frequency')
    processor.enum('size_var_shape')
    processor.anim_float('size_var_amplitude')
    processor.anim_float('size_var_frequency')
    processor.enum('alpha_var_shape')
    processor.anim_float('alpha_var_amplitude')
    processor.anim_float('alpha_var_frequency')
    processor.enum('rotation_var_shape')
    processor.anim_float('rotation_var_amplitude')
    processor.anim_float('rotation_var_frequency')
    processor.enum('spread_x_var_shape')
    processor.anim_float('spread_x_var_amplitude')
    processor.anim_float('spread_x_var_frequency')
    processor.enum('spread_y_var_shape')
    processor.anim_float('spread_y_var_amplitude')
    processor.anim_float('spread_y_var_frequency')
    processor.anim_float('parent_velocity')
    # processor.bit('flags', 'sort_distance')  # ! handled by script
    processor.bit('flags', 'collide_terrain')
    processor.bit('flags', 'collide_objects')
    processor.bit('flags', 'collide_emit')
    processor.bit('flags', 'emit_shape_cutout')
    # processor.bit('flags', 'inherit_emit_params')
    processor.bit('flags', 'inherit_parent_velocity')
    # processor.bit('flags', 'sort_height')  # ! handled by script
    processor.bit('flags', 'sort_reverse')
    # the following 6 values get set based on smoothing types:
    # processor.bit('flags', 'old_rotation_smooth')  #! handled by script
    # processor.bit('flags', 'old_rotation_bezier')  #! handled by script
    # processor.bit('flags', 'old_size_smooth')  #! handled by script
    # processor.bit('flags', 'old_size_bezier')  #! handled by script
    # processor.bit('flags', 'old_color_smooth')  #! handled by script
    # processor.bit('flags', 'old_color_bezier')  #! handled by script
    # processor.bit('flags', 'lit_parts')  #! handled by script
    processor.bit('flags', 'random_uv_flipbook_start')
    processor.bit('flags', 'multiply_gravity')
    # processor.bit('flags', 'tail_clamp')  # ! handled by script
    # processor.bit('flags', 'use_trailing_particle')  # ! handled by script
    # processor.bit('flags', 'tail_fix')  # ! handled by script
    processor.bit('flags', 'vertex_alpha')
    # processor.bit('flags', 'model_particles')  # ! handled by script
    processor.bit('flags', 'swap_yz_on_model_particles')
    # processor.bit('flags', 'scale_time_parent')
    # processor.bit('flags', 'local_time')
    processor.bit('flags', 'simulate_init')
    # processor.bit('flags', 'copy')
    processor.bit('rotation_flags', 'relative', since_version=18)
    processor.bit('rotation_flags', 'always_set', since_version=18)
    processor.float('wind_multiplier')
    processor.enum('lod_reduce')
    processor.enum('lod_cut')
    processor.float('trail_chance')
    processor.anim_float('trail_rate')


def io_particle_copy(processor):
    processor.anim_float('emit_rate')
    processor.anim_int16('emit_count')


def io_ribbon(processor):
    processor.bit('additional_flags', 'world_space', since_version=8)
    processor.boolean('world_space', till_version=6)
    processor.anim_float('speed')
    # processor.anim_float('unknown75e0b576')
    # processor.integer('unknownd30655aa', till_version=6)
    processor.anim_float('yaw')
    processor.anim_float('pitch')
    # processor.anim_float('unknownee00ae0a')
    # processor.anim_float('unknown1686c0b7')
    processor.anim_float('lifespan')
    # processor.anim_float('unknown9eba8df8')
    # processor.integer('unknown26271cbe')
    # processor.integer('unknownda0542fa')
    # processor.integer('unknown76f48851')
    # processor.integer('unknown874bdc23', till_version=6)
    processor.float('gravity')
    processor.float('scale_anim_mid')
    processor.float('color_anim_mid')
    processor.float('alpha_anim_mid')
    processor.float('twist_anim_mid')
    processor.float('scale_anim_mid_time', since_version=8)
    processor.float('color_anim_mid_time', since_version=8)
    processor.float('alpha_anim_mid_time', since_version=8)
    processor.float('twist_anim_mid_time', since_version=8)
    processor.anim_vec3('scale')
    processor.anim_vec3('twist')
    processor.anim_color('color_base')
    processor.anim_color('color_mid')
    processor.anim_color('color_tip')
    processor.float('drag')
    processor.float('mass')
    processor.float('mass2')
    # processor.float('unknownc7004d01')
    # processor.integer('unknown20683e1b', till_version=6)
    processor.bits_16('local_forces')
    processor.bits_16('world_forces')
    # processor.integer('unknownfb168d8c', since_version=9)
    processor.float('noise_amplitude')
    processor.float('noise_frequency')
    processor.float('noise_cohesion')
    processor.float('noise_edge')
    processor.enum('ribbon_type')
    processor.enum('cull_method')
    processor.float('divisions')
    processor.float('sides')
    processor.float('star_ratio')
    processor.anim_float('length')
    # processor.integer('unknown3fbae7d6', till_version=6)
    processor.anim_uint32('active')
    processor.bit('flags', 'collide_terrain')
    processor.bit('flags', 'collide_objects')
    processor.bit('flags', 'edge_falloff')
    processor.bit('flags', 'inherit_parent_velocity')
    processor.bit('flags', 'scale_smooth')
    processor.bit('flags', 'scale_bezier')
    processor.bit('flags', 'vertex_alpha')
    processor.bit('flags', 'scale_time_parent')
    processor.bit('flags', 'force_cpu_sim')
    processor.bit('flags', 'local_time')
    processor.bit('flags', 'simulate_init')
    processor.bit('flags', 'length_time')
    processor.bit('flags', 'accurate_gpu_tangents')
    processor.enum('scale_smoothing', since_version=8)
    processor.enum('color_smoothing', since_version=8)
    processor.float('friction')
    processor.float('bounce')
    processor.enum('lod_reduce')
    processor.enum('lod_cut')
    processor.enum('yaw_var_shape')
    processor.anim_float('yaw_var_amplitude')
    processor.anim_float('yaw_var_frequency')
    processor.enum('pitch_var_shape')
    processor.anim_float('pitch_var_amplitude')
    processor.anim_float('pitch_var_frequency')
    processor.enum('length_var_shape')
    processor.anim_float('length_var_amplitude')
    processor.anim_float('length_var_frequency')
    processor.enum('scale_var_shape')
    processor.anim_float('scale_var_amplitude')
    processor.anim_float('scale_var_frequency')
    processor.enum('alpha_var_shape')
    processor.anim_float('alpha_var_amplitude')
    processor.anim_float('alpha_var_frequency')
    processor.anim_float('parent_velocity')
    processor.anim_float('phase_shift')


def io_projection(processor):
    processor.enum('projection_type')
    processor.anim_vec3('offset')
    processor.anim_float('pitch')
    processor.anim_float('yaw')
    processor.anim_float('roll')
    processor.anim_float('field_of_view')
    processor.anim_float('aspect_ratio')
    processor.anim_float('near')
    processor.anim_float('far')
    processor.anim_float('box_offset_z_bottom')
    processor.anim_float('box_offset_z_top')
    processor.anim_float('box_offset_x_left')
    processor.anim_float('box_offset_x_right')
    processor.anim_float('box_offset_y_front')
    processor.anim_float('box_offset_y_back')
    processor.float('falloff')
    processor.float('alpha_init')
    processor.float('alpha_mid')
    processor.float('alpha_end')
    processor.float('lifetime_attack')
    processor.float('lifetime_attack_to')
    processor.float('lifetime_hold')
    processor.float('lifetime_hold_to')
    processor.float('lifetime_decay')
    processor.float('lifetime_decay_to')
    processor.float('attenuation_distance')
    processor.anim_uint32('active')
    processor.enum('layer')
    processor.enum('lod_reduce')
    processor.enum('lod_cut')
    processor.bit('flags', 'static')
    processor.bit('flags', 'unknown_flag0x2')
    processor.bit('flags', 'unknown_flag0x4')
    processor.bit('flags', 'unknown_flag0x8')


def io_force(processor):
    processor.enum('force_type')
    processor.enum('shape')
    # processor.integer('unknown_for0)  # ! uknown
    processor.bit('flags', 'falloff')
    processor.bit('flags', 'height_gradient')
    processor.bit('flags', 'unbounded')
    processor.bit('flags', 'unknown0x08')
    processor.bit('flags', 'unknown0x10')
    processor.bits_32('channels')
    processor.anim_float('strength')
    processor.anim_float('width')
    processor.anim_float('height')
    processor.anim_float('length')


def io_warp(processor):
    processor.anim_float('radius')
    processor.anim_float('strength')
    # processor.anim_float('unknown9306aac0')
    # processor.anim_float('unknown50c7f2b4')
    # processor.anim_float('unknown8d9c977c')
    # processor.anim_float('unknownca6025a2')


def io_ribbon_spline(processor):
    processor.vec3('emission_offset')
    processor.vec3('emission_vector')
    processor.anim_float('velocity')
    processor.anim_float('velocity_base_fac')
    processor.anim_float('velocity_end_fac')
    processor.enum('velocity_var_shape')
    processor.anim_float('velocity_var_amplitude')
    processor.anim_float('velocity_var_frequency')
    processor.anim_float('yaw')
    processor.enum('yaw_var_shape')
    processor.anim_float('yaw_var_amplitude')
    processor.anim_float('yaw_var_frequency')
    processor.anim_float('pitch')
    processor.enum('pitch_var_shape')
    processor.anim_float('pitch_var_amplitude')
    processor.anim_float('pitch_var_frequency')
    # processor.integer('unknowneee1a711')  # ! unknown
    # processor.anim_float('unknown01')  # ! unknown
    # processor.anim_float('unknown02')  # ! unknown
    # processor.float('unknown02')  # ! unknown
    # processor.float('unknown03')  # ! unknown


def io_rigid_body(processor):
    processor.integer('simulation_type', since_version=3)
    processor.enum('physical_material', since_version=3)
    processor.float('mass', since_version=3)
    processor.float('friction', since_version=3)
    processor.float('bounce', since_version=3)
    processor.float('damping_linear', since_version=3)
    processor.float('damping_angular', since_version=3)
    processor.float('gravity_factor', since_version=3)
    processor.bit('flags', 'collidable')
    processor.bit('flags', 'walkable')
    processor.bit('flags', 'stackable')
    processor.bit('flags', 'simulate_collision')
    processor.bit('flags', 'ignore_local_bodies')
    processor.bit('flags', 'always_exists')
    processor.bit('flags', 'no_simulation')
    processor.bits_16('local_forces')
    processor.bits_16('world_forces')
    processor.integer('priority')


def io_rigid_body_joint(processor):
    processor.enum('joint_type')
    processor.boolean('limit_bool')
    processor.float('limit_min')
    processor.float('limit_max')
    processor.float('limit_angle')
    processor.boolean('friction_bool')
    processor.float('friction')
    processor.float('damping_ratio')
    processor.float('angular_frequency')
    # processor.integer('break_threshold')  # ! ignored
    # processor.integer('shape_collision_value')  # ! ignored


def io_cloth(processor):
    processor.float('density')
    processor.float('tracking')
    processor.float('stiffness_stretching')
    processor.float('stiffness_horizontal')
    processor.float('stiffness_blending')
    processor.float('damping')
    processor.float('friction')
    processor.float('gravity')
    processor.float('explosion_scale')
    processor.float('wind_scale')
    processor.float('stiffness_shear')
    processor.float('drag_factor')
    processor.float('lift_factor')
    processor.float('stiffness_spheres')
    processor.boolean('skin_collision', since_version=4)
    processor.float('skin_offset', since_version=4)
    processor.float('skin_exponent', since_version=4)
    processor.float('skin_stiffness', since_version=4)
    processor.vec3('local_wind', since_version=4)


def io_ik(processor):
    processor.float('search_up')
    processor.float('search_down')
    processor.float('search_speed')
    processor.float('goal_threshold')


def io_turret_part(processor):
    # processor.vec4('forward_x', since_version=4)  # ! handled manually
    # processor.vec4('forward_y', since_version=4)  # ! handled manually
    # processor.vec4('forward_z', since_version=4)  # ! handled manually
    # processor.vec4('up_x', since_version=4)  # ! handled manually
    # processor.vec4('up_y', since_version=4)  # ! handled manually
    # processor.vec4('up_z', since_version=4)  # ! handled manually
    # processor.bit('flags', 'main_part')  # ! handled manually
    # processor.integer('group_id')  # ! handled manually
    processor.bit('yaw_flags', 'yaw_limited')
    processor.float('yaw_min')
    processor.float('yaw_max')
    processor.float('yaw_weight', since_version=4)
    processor.bit('pitch_flags', 'pitch_limited')
    processor.float('pitch_min')
    processor.float('pitch_max')
    processor.float('pitch_weight', since_version=4)
    # processor.integer('unknown132')  # seem to havve no perceptible effect
    # processor.integer('unknown136')  # seem to havve no perceptible effect


def io_tmd(processor):
    processor.float('unknownd3f6c7b8')
    processor.float('unknown74229b33')
    processor.anim_float('unknownd4f91286')
    processor.anim_float('unknown77f047c2')
    processor.integer('unknownbc1e64c1')
    processor.integer('unknown6cd3476c')
    processor.integer('unknownccd5a5af')


def io_billboard(processor):
    processor.enum('billboard_type')
    processor.boolean('camera_look_at')


material_type_io_method = {
    1: io_material_standard,
    2: io_material_displacement,
    3: io_material_composite,
    4: io_material_terrain,
    5: io_material_volume,
    7: io_material_creep,
    8: io_material_volume_noise,
    9: io_material_stb,
    10: io_material_reflection,
    11: io_material_lens_flare,
    12: io_material_buffer,
}
