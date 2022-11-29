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
    processor.bit('flags', 'global_in_previewer')


def io_material_standard(processor):
    processor.bit('additional_flags', 'depth_blend_falloff')
    processor.bit('additional_flags', 'vertex_color')
    processor.bit('additional_flags', 'vertex_alpha')
    # processor.bit('additional_flags', 'unknown0x200')
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
    processor.bit('flags', 'geometry_visible')
    processor.enum('blend_mode')
    processor.integer('priority')
    processor.float('specularity')
    processor.float('depth_blend_falloff')
    processor.integer('cutout_threshold')
    processor.float('spec_multiply')
    processor.float('emis_multiply')
    processor.float('envi_const_multiply', since_version=20)
    processor.float('envi_diff_multiply', since_version=20)
    processor.float('envi_spec_multiply', since_version=20)
    # processor.integer('unknown2481ae8a')
    processor.enum('layr_blend_mode')
    processor.enum('emis_blend_mode')
    processor.enum('emis_mode')
    processor.enum('spec_mode')
    processor.anim_float('parallax_height')
    processor.anim_uint32('unknown_animation_ref')


def io_material_displacement(processor):
    processor.integer('unknown0')
    processor.anim_float('strength_factor')
    processor.integer('priority')


def io_material_composite(processor):
    processor.integer('unknown')


def io_material_composite_section(processor):
    processor.anim_float('alpha_factor')


def io_material_terrain(processor):
    processor.integer('unknown633fd422', since_version=1)


def io_material_volume(processor):
    processor.integer('unknown0')
    processor.integer('unknown1')
    processor.anim_float('volume_density')
    processor.integer('unknown2')
    processor.integer('unknown3')


def io_material_volume_noise(processor):
    processor.integer('unknown50762f82')
    processor.bit('flags', 'draw_after_transparency')
    processor.anim_float('volume_density')
    processor.anim_float('near_plane')
    processor.anim_float('falloff')
    processor.anim_vec3('scroll_rate')
    processor.anim_vec3('translation')
    processor.anim_vec3('scale')
    processor.anim_vec3('rotation')
    processor.integer('alpha_treshold')
    processor.integer('unknown1d13acfe')


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
    processor.integer('face_source')
    # processor.float('unk02')  # ! ignored
    # processor.float('unk03')  # ! ignored


def io_material_lens_flare(processor):
    processor.integer('unknown7f492c0a', till_version=2)
    processor.integer('uv_cols', since_version=3)
    processor.integer('uv_rows', since_version=3)
    processor.float('render_distance', since_version=3)
    processor.anim_float('intensity', since_version=3)
    processor.anim_color('color', since_version=3)
    processor.anim_float('intensity2', since_version=3)
    processor.anim_float('uniform_scale', since_version=3)


def io_material_buffer(processor):
    pass


def io_material_layer(processor):
    # processor.integer('unknown00')  # ! unknown
    processor.anim_color('color_value')
    processor.bit('flags', 'uv_wrap_x')
    processor.bit('flags', 'uv_wrap_y')
    processor.bit('flags', 'color_invert')
    processor.bit('flags', 'color_clamp')
    # processor.bit('flags', 'particle_uv_flipbook') # ! handle manually
    # processor.bit('flags', 'video') # ! handled manually
    # processor.bit('flags', 'color') # ! handled manually
    processor.bit('flags', 'ignored_fresnel_flag1')
    processor.bit('flags', 'ignored_fresnel_flag2')
    processor.bit('flags', 'fresnel_local_transform')
    processor.bit('flags', 'fresnel_do_not_mirror')
    processor.enum('uv_source')
    processor.enum('color_channels')
    processor.anim_float('color_multiply')
    processor.anim_float('color_add')
    # processor.integer('unknown3b61017a')  # ! unknown
    processor.float('noise_amplitude', since_version=24)
    processor.float('noise_frequency', since_version=24)
    processor.enum('video_channel')
    processor.integer('video_frame_rate')
    processor.integer('video_frame_start')
    processor.integer('video_frame_end')
    processor.enum('video_mode')
    processor.boolean('video_sync_timing')
    processor.anim_boolean_based_on_SDU3('video_play')
    processor.anim_boolean_based_on_SDFG('video_restart')
    processor.integer('uv_flipbook_rows')
    processor.integer('uv_flipbook_cols')
    processor.anim_uint16('uv_flipbook_frame')
    processor.anim_vec2('uv_offset')
    processor.anim_vec3('uv_angle')
    processor.anim_vec2('uv_tiling')
    # processor.anim_uint32('unknowna4ec0796')  # ! unknown
    # processor.anim_float('unknowna44bf452')  # ! unknown
    processor.anim_float('color_brightness')
    processor.anim_vec3('uv_triplanar_offset', since_version=24)
    processor.anim_vec3('uv_triplanar_scale', since_version=24)
    processor.integer('uv_source_related')
    processor.enum('fresnel_type')
    processor.float('fresnel_exponent')
    processor.float('fresnel_min')
    # processor.float('fresnel_max_offset') # ! handled manually
    # processor.float('unknown15') # ! unknown
    # processor.integer('unknown16', since_version=25) # ! unknown
    # processor.integer('unknown17', since_version=25) # ! unknown
    # processor.float('fresnel_inverted_mask_x', since_version=25) # ! handled manually
    # processor.float('fresnel_inverted_mask_y', since_version=25) # ! handled manually
    # processor.float('fresnel_inverted_mask_z', since_version=25) # ! handled manually
    processor.float('fresnel_yaw', since_version=25)
    processor.float('fresnel_pitch', since_version=25)
    # processor.integer('unknowned0e748d', since_version=25, till_version=25) # ! unknown


def io_light(processor):
    processor.enum('shape')
    processor.bit('flags', 'shadows')
    # processor.bit('flags', 'spec') # ! ignored
    # processor.bit('flags', 'ao') # ! ignored
    processor.bit('flags', 'light_opaque')
    processor.bit('flags', 'light_transparent')
    processor.bit('flags', 'team_color')
    processor.anim_vec3('color')
    processor.anim_float('intensity')
    # processor.anim_vec3('spec_color') # ! ignored
    # processor.anim_float('spec_intensity') # ! ignored
    processor.anim_float('attenuation_far')
    processor.float('unknownAt148')
    processor.anim_float('attenuation_near')
    processor.anim_float('hotspot')
    processor.anim_float('falloff')


def io_shadow_box(processor):
    processor.anim_float('length')
    processor.anim_float('width')
    processor.anim_float('height')


def io_camera(processor):
    processor.anim_float('field_of_view')
    processor.integer('use_vertical_fov', since_version=3)
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
    processor.boolean('emit_speed_randomize', till_version=12)
    processor.bit('additional_flags', 'emit_speed_randomize', since_version=17)
    processor.anim_float('emit_angle_x')
    processor.anim_float('emit_angle_y')
    processor.anim_float('emit_spread_x')
    processor.anim_float('emit_spread_y')
    processor.anim_float('lifespan')
    processor.anim_float('lifespan_random')
    processor.boolean('lifespan_randomize', till_version=12)
    processor.bit('additional_flags', 'lifespan_randomize', since_version=17)
    processor.float('distance_limit')
    processor.float('gravity')
    processor.float('size_anim_mid')
    processor.float('color_anim_mid')
    processor.float('alpha_anim_mid')
    processor.float('rotation_anim_mid')
    processor.float('size_hold', since_version=17)
    processor.float('color_hold', since_version=17)
    processor.float('alpha_hold', since_version=17)
    processor.float('rotation_hold', since_version=17)
    processor.enum('size_smoothing', since_version=17)
    processor.enum('color_smoothing', since_version=17)
    processor.enum('rotation_smoothing', since_version=17)
    processor.anim_vec3('size')
    processor.anim_vec3('rotation')
    processor.anim_color('color_init')
    processor.anim_color('color_mid')
    processor.anim_color('color_end')
    processor.float('drag')
    processor.float('mass')
    processor.float('mass2')
    processor.boolean('mass_randomize', till_version=12)
    processor.bit('additional_flags', 'mass_randomize', since_version=17)
    # processor.float('unknownFloat2c')
    processor.boolean('trailing', till_version=12)
    processor.bit('additional_flags', 'trailing', since_version=17)
    processor.integer('emit_max')
    processor.anim_float('emit_rate')
    processor.enum('emit_shape')
    processor.anim_vec3('emit_shape_size')
    processor.anim_vec3('emit_shape_size_cutout')
    processor.anim_float('emit_shape_radius')
    processor.anim_float('emit_shape_radius_cutout')
    processor.enum('emit_type')
    processor.boolean('size_randomize')
    processor.anim_vec3('size2')
    processor.boolean('rotation_randomize')
    processor.anim_vec3('rotation2')
    processor.boolean('color_randomize')
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
    processor.float('uv_flipbook_col_fraction')
    processor.float('uv_flipbook_row_fraction')
    processor.float('bounce')
    processor.float('friction')
    processor.enum('particle_type')
    processor.float('length_width_ratio')
    processor.bits_16('local_forces')
    processor.bits_16('world_forces')
    processor.float('noise_amplitude')
    processor.float('noise_frequency')
    processor.float('noise_cohesion')
    processor.float('noise_edge')
    processor.bit('flags', 'sort')
    processor.bit('flags', 'collide_terrain')
    processor.bit('flags', 'collide_objects')
    processor.bit('flags', 'spawn_on_bounce')
    processor.bit('flags', 'emit_shape_cutout')
    processor.bit('flags', 'inherit_emit_params')
    processor.bit('flags', 'inherit_parent_velocity')
    processor.bit('flags', 'sort_z_height')
    processor.bit('flags', 'reverse_iteration')
    # the following 6 values get set based on smoothing types:
    # processor.bit('flags', 'smooth_rotation')
    # processor.bit('flags', 'smooth_rotation_bezier')
    # processor.bit('flags', 'smooth_zize')
    # processor.bit('flags', 'smooth_size_bezier')
    # processor.bit('flags', 'smooth_color')
    # processor.bit('flags', 'smooth_color_bezier')
    processor.bit('flags', 'lit_parts')
    processor.bit('flags', 'random_uv_flipbook_start')
    processor.bit('flags', 'multiply_gravity')
    processor.bit('flags', 'clamp_trailing_particles')
    processor.bit('flags', 'spawn_trailing_particles')
    processor.bit('flags', 'fix_length_trailing_particles')
    processor.bit('flags', 'vertex_alpha')
    processor.bit('flags', 'model_parts')
    processor.bit('flags', 'swap_yz_on_model_parts')
    processor.bit('flags', 'scale_time_parent')
    processor.bit('flags', 'local_time')
    processor.bit('flags', 'simulate_init')
    processor.bit('flags', 'copy')
    processor.bit('rotation_flags', 'relative', since_version=18)
    processor.bit('rotation_flags', 'always_set', since_version=18)
    processor.float('wind_multiplier')
    processor.enum('lod_reduce')
    processor.enum('lod_cut')
    processor.float('trail_chance')
    processor.anim_float('trail_rate')


def io_particle_copy(processor):
    processor.anim_float('emit_rate')
    processor.anim_float('emit_amount')


def io_ribbon(processor):
    processor.bit('additional_flags', 'world_space', since_version=8)
    processor.anim_float('length')
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
    processor.integer('world_space', till_version=6)
    processor.bits_16('local_forces')
    processor.bits_16('world_forces')
    # processor.integer('unknownfb168d8c', since_version=9)
    processor.float('noise_amplitude')
    processor.float('noise_waves')
    processor.float('noise_frequency')
    processor.float('noise_scale')
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
    processor.bit('flags', 'scale_smooth_bezier')
    processor.bit('flags', 'vertex_alpha')
    processor.bit('flags', 'scale_time_parent')
    processor.bit('flags', 'force_cpu_sim')
    processor.bit('flags', 'local_time')
    processor.bit('flags', 'simulate_init')
    processor.bit('flags', 'length_time')
    processor.bit('flags', 'accurate_gpu_tangents')
    processor.enum('scale_smoothing')
    processor.enum('color_smoothing')
    processor.float('friction', since_version=8)
    processor.float('bounce', since_version=8)
    processor.enum('lod_reduce')
    processor.enum('lod_cut')
    # TODO processor.enum('yaw_var_shape')
    # TODO processor.anim_float('yaw_var_amplitude')
    # TODO processor.anim_float('yaw_var_frequency')
    # TODO processor.enum('pitch_var_shape')
    # TODO processor.anim_float('pitch_var_amplitude')
    # TODO processor.anim_float('pitch_var_frequency')
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
    processor.float('alpha_over_time_init')
    processor.float('alpha_over_time_mid')
    processor.float('alpha_over_time_end')
    processor.float('lifetime_attack')
    processor.float('lifetime_attack_to')
    processor.float('lifetime_hold')
    processor.float('lifetime_hold_to')
    processor.float('lifetime_decay')
    processor.float('lifetime_decay_to')
    processor.float('attenuation_plane_distance')
    processor.anim_uint32('active')
    processor.enum('layer')
    processor.enum('lod_reduce')
    processor.enum('lod_cut')
    processor.bit('flags', 'static')
    processor.bit('flags', 'unknown_flag0x2')
    processor.bit('flags', 'unknown_flag0x4')
    processor.bit('flags', 'unknown_flag0x8')


def io_force(processor):
    processor.enum('type')
    processor.enum('shape')
    processor.bit('flags', 'falloff')
    processor.bit('flags', 'height_gradient')
    processor.bit('flags', 'unbounded')
    processor.bits_32('channels')
    processor.anim_float('strength')
    processor.anim_float('width')
    processor.anim_float('height')
    processor.anim_float('length')


def io_warp(processor):
    processor.anim_float('radius')
    processor.anim_float('compression_strength')


def io_ribbon_spline(processor):
    processor.float('tan1')
    processor.float('tan2')
    processor.float('tan3')
    processor.anim_float('length')
    processor.enum('length_var_shape')
    processor.anim_float('length_var_amplitude')
    processor.anim_float('length_var_frequency')
    processor.anim_float('yaw')
    processor.enum('yaw_var_shape')
    processor.anim_float('yaw_var_amplitude')
    processor.anim_float('yaw_var_frequency')
    processor.anim_float('pitch')
    processor.enum('pitch_var_shape')
    processor.anim_float('pitch_var_amplitude')
    processor.anim_float('pitch_var_frequency')
    processor.integer('unknown1')
    processor.integer('unknowneee1a711')
    processor.anim_float('unknown3')
    processor.anim_float('unknown4')


def io_rigid_body(processor):
    processor.integer('simulation_type', since_version=3)
    processor.enum('physical_material', since_version=3)
    processor.float('mass', since_version=3)
    processor.float('friction', since_version=3)
    processor.float('restitution', since_version=3)
    processor.float('damping_linear', since_version=3)
    processor.float('damping_angular', since_version=3)
    processor.float('gravity_factor', since_version=3)
    processor.bit('flags', 'collidable')
    processor.bit('flags', 'walkable')
    processor.bit('flags', 'stackable')
    processor.bit('flags', 'simulate_on_collision')
    processor.bit('flags', 'ignore_local_bodies')
    processor.bit('flags', 'always_exists')
    processor.bit('flags', 'no_simulation')
    processor.bits_16('local_forces')
    processor.bits_16('world_forces')
    processor.integer('priority')


def io_rigid_body_joint(processor):
    processor.enum('joint_type')
    processor.integer('limit_bool')
    processor.float('limit_min')
    processor.float('limit_max')
    processor.float('limit_angle')
    processor.integer('friction_bool')
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
    processor.float('shear_stiffness')
    processor.float('drag_factor')
    processor.float('lift_factor')
    processor.float('sphere_attachment_stiffness')
    processor.integer('skin_collision', since_version=4)
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
    processor.vec4('forward_x', since_version=4)
    processor.vec4('forward_y', since_version=4)
    processor.vec4('forward_z', since_version=4)
    processor.vec4('up_x', since_version=4)
    processor.vec4('up_y', since_version=4)
    processor.vec4('up_z', since_version=4)
    processor.bit('flags', 'main_part')
    processor.integer('group_id')
    processor.bit('yaw_flags', 'yaw_limited')
    processor.float('yaw_min')
    processor.float('yaw_max')
    processor.float('yaw_weight', since_version=4)
    processor.bit('pitch_flags', 'pitch_limited')
    processor.float('pitch_min')
    processor.float('pitch_max')
    processor.float('pitch_weight', since_version=4)
    processor.integer('unknownAt132')
    processor.integer('unknownAt136')
    processor.integer('unknownAt140', since_version=4)
    processor.integer('unknownAt144', since_version=4)
    processor.integer('unknownAt148', since_version=4)


def io_billboard(processor):
    processor.enum('billboard_type')
    processor.integer('camera_look_at')


material_type_to_model_reference = {
    1: 'materials_standard',
    2: 'materials_displacement',
    3: 'materials_composite',
    4: 'materials_terrain',
    5: 'materials_volume',
    7: 'materials_creep',
    8: 'materials_volumenoise',
    9: 'materials_stb',
    10: 'materials_reflection',
    11: 'materials_lensflare',
    12: 'materials_buffer',
}

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

material_type_to_layers = {
    1: ['diff', 'decal', 'spec', 'gloss', 'emis1', 'emis2', 'envi', 'envi_mask', 'alpha1', 'alpha2', 'norm',
        'height', 'light', 'ao', 'norm_blend1_mask', 'norm_blend2_mask', 'norm_blend1', 'norm_blend2'],
    2: ['normal', 'strength'],
    3: [],
    4: ['terrain'],
    5: ['color', 'unknown1', 'unknown2'],
    7: ['creep'],
    8: ['color', 'noise1', 'noise2'],
    9: ['diff', 'spec', 'normal'],
    10: ['norm', 'strength', 'blur'],
    11: ['color', 'unknown'],
    12: []
}

material_collections = [
    'None', 'm3_materials_standard', 'm3_materials_displacement', 'm3_materials_composite', 'm3_materials_terrain', 'm3_materials_volume', 'None',
    'm3_materials_creep', 'm3_materials_volume_noise', 'm3_materials_stb', 'm3_materials_reflection', 'm3_materials_lens_flare', 'm3_materials_buffer',
]
