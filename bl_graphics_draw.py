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

import math
import bpy
import mathutils
import gpu
from gpu_extras.batch import batch_for_shader
from . import shared
from . import bl_graphics_data as blgd
from .io_shared import rot_fix_matrix_transpose

POLYLINE_SHADER_ID = '3D_POLYLINE_UNIFORM_COLOR' if (4, 0, 0) > bpy.app.version else 'POLYLINE_UNIFORM_COLOR'

def get_pb_from_handle(ob, bone_handle, handle_bone_dict):

    bone_from_handle = handle_bone_dict.get(bone_handle, False)
    if bone_from_handle is False:
        bone_from_handle = shared.m3_pointer_get(ob.pose.bones, bone_handle)
        handle_bone_dict[bone_handle] = bone_from_handle
    if bone_from_handle and ob.data.bones.get(bone_from_handle.name).hide:
        return None
    return bone_from_handle


def get_pb_world_matrix(ob, pb_matrix_dict, pb, apply_bind_matrix=False):
    try:
        return pb_matrix_dict[pb]
    except KeyError:
        if apply_bind_matrix:
            bs = pb.m3_bind_scale
            pb_matrix_dict[pb] = ob.matrix_world @ pb.matrix @ mathutils.Matrix.LocRotScale(None, None, (1 / bs[0], 1 / bs[1], 1 / bs[2]))
        else:
            pb_matrix_dict[pb] = ob.matrix_world @ pb.matrix
    return pb_matrix_dict[pb]


def get_transformed_coords(coords, matrix):
    new_coords = []
    for co in coords:
        new_coords.append(matrix @ co)
    return new_coords


uni_polyline_shader = gpu.shader.from_builtin(POLYLINE_SHADER_ID)


def batch_uni_polyline(coords, indices, color, line_width=0.35):
    region = bpy.context.region
    uni_polyline_shader.uniform_float("lineWidth", line_width)
    uni_polyline_shader.uniform_float("viewportSize", (region.width, region.height))
    uni_polyline_shader.uniform_float('color', [*color] + [1])
    batch = batch_for_shader(uni_polyline_shader, 'LINES', {'pos': coords}, indices=indices)
    batch.draw(uni_polyline_shader)


# TODO cache batches rather than generating new ones on every execution?
# TODO cache pose bone world matrices outside of draw func?

# TODO options to filter generation of helper types
# TODO optionally pass over items which are not to be exported
def draw():
    space_3d = bpy.context.space_data

    if not space_3d.overlay.show_overlays:
        return

    if space_3d.shading.type == 'SOLID':
        if space_3d.overlay.show_xray_bone:
            gpu.state.depth_mask_set(False)
        else:
            gpu.state.depth_test_set('LESS_EQUAL')
            gpu.state.depth_mask_set(True)
    elif space_3d.shading.type == 'WIREFRAME':
        gpu.state.depth_mask_set(False)
    else:
        return

    ob = bpy.context.object

    if not ob:
        return

    if ob.type == 'ARMATURE' and ob.mode == 'POSE':
        selected_pbs = bpy.context.selected_pose_bones_from_active_object
        pb_select = {pose_bone: pose_bone in selected_pbs for pose_bone in ob.pose.bones}

        pb_to_world_matrix = {}
        pb_to_world_bind_matrix = {}
        pb_handles = {}

        opts = ob.m3_options

        if ob.m3_bounds.opt_display:
            bnds = ob.m3_bounds
            coords, indices = blgd.cube
            coords = []
            coords.append(mathutils.Vector((bnds.right, bnds.front, bnds.bottom)))
            coords.append(mathutils.Vector((bnds.left, bnds.front, bnds.bottom)))
            coords.append(mathutils.Vector((bnds.right, bnds.back, bnds.bottom)))
            coords.append(mathutils.Vector((bnds.left, bnds.back, bnds.bottom)))
            coords.append(mathutils.Vector((bnds.right, bnds.front, bnds.top)))
            coords.append(mathutils.Vector((bnds.left, bnds.front, bnds.top)))
            coords.append(mathutils.Vector((bnds.right, bnds.back, bnds.top)))
            coords.append(mathutils.Vector((bnds.left, bnds.back, bnds.top)))
            coords = get_transformed_coords(coords, ob.matrix_world)
            batch_uni_polyline(coords, indices, (1, 1, 1))

        for item in ob.m3_attachmentpoints:
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb:
                if opts.draw_attach_points or (pb_select[pb] and opts.draw_selected):
                    pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)
                    col = blgd.att_point_color_normal if not pb_select[pb] else blgd.att_point_color_select
                    coords, indices = blgd.point
                    coords = get_transformed_coords(coords, pb_matrix)
                    batch_uni_polyline(coords, indices, col)

            attach = item
            for ii, item in enumerate(item.volumes):
                pb = get_pb_from_handle(ob, attach.bone, pb_handles)
                if pb:
                    if opts.draw_attach_volumes or (pb_select[pb] and opts.draw_selected):
                        col = blgd.att_point_color_normal if not pb_select[pb] or ii != attach.volumes_index else blgd.att_point_color_select
                        pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)
                        item_matrix = mathutils.Matrix.LocRotScale((-item.location.y, item.location.x, item.location.z), item.rotation, item.scale.yxz)
                        if item.shape == 'CUBE':
                            volume_matrix = mathutils.Matrix.LocRotScale(None, None, (item.size[1], item.size[0], item.size[2]))
                            coords, indices = blgd.cube
                        elif item.shape == 'SPHERE':
                            volume_matrix = mathutils.Matrix.Scale(item.size[0], 4)
                            coords, indices = blgd.sphere
                        elif item.shape == 'CAPSULE':
                            volume_matrix = mathutils.Matrix.Scale(1.0, 4)
                            coords, indices = blgd.init_capsule(item.size[0], item.size[1])
                        elif item.shape == 'CYLINDER':
                            volume_matrix = mathutils.Matrix.LocRotScale(None, None, (item.size[0], item.size[0], item.size[1]))
                            coords, indices = blgd.cylinder
                        elif item.shape == 'MESH':
                            # TODO cache coords and indices per object that is used as volume shape
                            if not item.mesh_object:
                                continue
                            volume_matrix = rot_fix_matrix_transpose
                            coords = [vert.co for vert in item.mesh_object.data.vertices]
                            indices = [edge.vertices for edge in item.mesh_object.data.edges]

                        final_matrix = pb_matrix @ item_matrix @ volume_matrix
                        coords = get_transformed_coords(coords, final_matrix)
                        batch_uni_polyline(coords, indices, col)

        for item in [item for item in ob.m3_hittests] + [ob.m3_hittest_tight]:
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb:
                if not opts.draw_hittests and not (pb_select[pb] and opts.draw_selected):
                    continue

                pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)
                swizzle_rot = mathutils.Euler((item.rotation.y, item.rotation.x, item.rotation.z))
                item_matrix = mathutils.Matrix.LocRotScale((-item.location.y, item.location.x, item.location.z), swizzle_rot, item.scale.yxz)
                col = blgd.hittest_color_normal if not pb_select[pb] else blgd.hittest_color_select
                if item.shape == 'CUBE':
                    volume_matrix = mathutils.Matrix.LocRotScale(None, None, (item.size[1], item.size[0], item.size[2]))
                    coords, indices = blgd.cube
                elif item.shape == 'SPHERE':
                    volume_matrix = mathutils.Matrix.Scale(item.size[0], 4)
                    coords, indices = blgd.sphere
                elif item.shape == 'CAPSULE':
                    volume_matrix = mathutils.Matrix.Scale(1.0, 4)
                    coords, indices = blgd.init_capsule(item.size[0], item.size[1])
                elif item.shape == 'CYLINDER':
                    volume_matrix = mathutils.Matrix.LocRotScale(None, None, (item.size[0], item.size[0], item.size[1]))
                    coords, indices = blgd.cylinder
                elif item.shape == 'MESH':
                    if not item.mesh_object:
                        continue
                    volume_matrix = rot_fix_matrix_transpose
                    coords = [vert.co for vert in item.mesh_object.data.vertices]
                    indices = [edge.vertices for edge in item.mesh_object.data.edges]

                final_matrix = pb_matrix @ item_matrix @ volume_matrix
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for item in ob.m3_lights:
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb:
                if not opts.draw_lights and not (pb_select[pb] and opts.draw_selected):
                    continue

                col = blgd.light_color_normal if not pb_select[pb] else blgd.light_color_select
                pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)
                if item.shape == 'POINT':
                    volume_matrix = mathutils.Matrix.Scale(item.attenuation_far, 4)
                    coords, indices = blgd.sphere
                elif item.shape == 'SPOT':
                    volume_matrix = mathutils.Matrix.LocRotScale(None, None, (item.attenuation_far, item.attenuation_far, item.falloff))
                    coords, indices = blgd.cone

                final_matrix = pb_matrix @ volume_matrix
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        handle_to_par_data = {}

        for item in ob.m3_particlesystems:
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb:
                pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)

                if not opts.draw_particles and not (pb_select[pb] and opts.draw_selected):
                    continue

                if item.emit_shape == 'MESH':
                    continue

                col = blgd.particle_color_normal if not pb_select[pb] else blgd.particle_color_select

                size = item.emit_shape_size
                size_cutout = item.emit_shape_size_cutout
                radius = item.emit_shape_radius
                radius_cutout = item.emit_shape_radius_cutout

                coords = None
                indices = None
                par_matrix = None
                par_cutout_matrix = None

                # TODO implement helpers for emission properties such as angle and spread?

                if item.emit_shape == 'POINT':
                    coords, indices = blgd.point
                elif item.emit_shape == 'PLANE':
                    coords, indices = blgd.plane
                    par_matrix = mathutils.Matrix.LocRotScale(None, None, (size[1], size[0], size[2]))
                    if item.emit_shape_cutout:
                        par_cutout_matrix = mathutils.Matrix.LocRotScale(None, None, size_cutout)
                elif item.emit_shape == 'SPHERE':
                    coords, indices = blgd.sphere
                    par_matrix = mathutils.Matrix.Scale(radius, 4)
                    if item.emit_shape_cutout:
                        par_cutout_matrix = mathutils.Matrix.Scale(radius_cutout, 4)
                elif item.emit_shape == 'CUBE':
                    coords, indices = blgd.cube
                    par_matrix = mathutils.Matrix.LocRotScale(None, None, (size[1], size[0], size[2]))
                    if item.emit_shape_cutout:
                        par_cutout_matrix = mathutils.Matrix.LocRotScale(None, None, (size_cutout[1], size_cutout[0], size_cutout[2]))
                elif item.emit_shape == 'CYLINDER':
                    coords, indices = blgd.cylinder
                    par_matrix = mathutils.Matrix.LocRotScale(None, None, (radius, radius, size[1]))
                    if item.emit_shape_cutout:
                        par_cutout_matrix = mathutils.Matrix.LocRotScale(None, None, (radius_cutout, radius_cutout, size_cutout[2]))
                elif item.emit_shape == 'DISC':
                    coords, indices = blgd.disc
                    par_matrix = mathutils.Matrix.Scale(radius, 4)
                    if item.emit_shape_cutout:
                        par_cutout_matrix = mathutils.Matrix.Scale(radius_cutout, 4)
                elif item.emit_shape == 'SPLINE':
                    # TODO dashed line back to emitter bone
                    coords = []
                    indices = []
                    for ii, point in enumerate(item.emit_shape_spline):
                        coords.append(mathutils.Vector(point.location))
                        indices.append((ii, ii + 1))
                    par_matrix = rot_fix_matrix_transpose
                    del indices[-1]

                handle_to_par_data[item.bl_handle] = (coords, indices, par_matrix, par_cutout_matrix)

                if par_matrix:
                    final_matrix = pb_matrix @ par_matrix
                else:
                    final_matrix = pb_matrix

                par_coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(par_coords, indices, col)

                if par_cutout_matrix:
                    final_matrix = pb_matrix @ par_matrix
                    par_cutout_coords = get_transformed_coords(coords, final_matrix)
                    batch_uni_polyline(par_cutout_coords, indices, col)

        for item in ob.m3_particlecopies:
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb and len(item.systems):
                if not opts.draw_particles and not (pb_select[pb] and opts.draw_selected):
                    continue

                pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)

                col = blgd.particle_color_normal if not pb_select[pb] else blgd.particle_color_select
                for system in item.systems:
                    system_data = handle_to_par_data.get(system.handle)
                    if not system_data:
                        continue
                    coords, indices, par_matrix, par_cutout_matrix = system_data
                    if coords and indices:
                        if par_matrix:
                            final_matrix = pb_matrix @ par_matrix
                        else:
                            final_matrix = pb_matrix
                        par_coords = get_transformed_coords(coords, final_matrix)
                        batch_uni_polyline(par_coords, indices, col)

                        if par_cutout_matrix:
                            final_cutout_matrix = pb_matrix @ par_cutout_matrix
                            par_cutout_coords = get_transformed_coords(coords, final_cutout_matrix)
                            batch_uni_polyline(par_cutout_coords, indices, col)

        # TODO RIB_

        for item in ob.m3_projections:
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb:
                if not opts.draw_projections and not (pb_select[pb] and opts.draw_selected):
                    continue

                pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)
                col = blgd.projector_color_normal if not pb_select[pb] else blgd.projector_color_select
                vec_min = mathutils.Vector((item.box_offset_y_front, item.box_offset_x_left, item.box_offset_z_top))
                vec_max = mathutils.Vector((item.box_offset_y_back, item.box_offset_x_right, item.box_offset_z_bottom))
                proj_matrix = mathutils.Matrix.LocRotScale(vec_max + vec_min, None, vec_max - vec_min)
                coords, indices = blgd.cube
                final_matrix = pb_matrix @ proj_matrix
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for item in ob.m3_forces:
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb:
                if not opts.draw_forces and not (pb_select[pb] and opts.draw_selected):
                    continue

                pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)
                col = blgd.force_color_normal if not pb_select[pb] else blgd.force_color_select

                if item.shape == 'CUBE':
                    volume_matrix = mathutils.Matrix.LocRotScale(None, None, (item.width, item.length, item.height))
                    coords, indices = blgd.cube
                elif item.shape == 'CYLINDER':
                    volume_matrix = mathutils.Matrix.LocRotScale(None, None, (item.width, item.length, item.height))
                    coords, indices = blgd.cylinder
                elif item.shape == 'SPHERE':
                    volume_matrix = mathutils.Matrix.Scale(item.width, 4)
                    coords, indices = blgd.sphere
                elif item.shape == 'HEMISPHERE':
                    volume_matrix = mathutils.Matrix.Scale(item.width, 4)
                    coords, indices = blgd.hemisphere
                elif item.shape == 'CONEDOME':
                    volume_matrix = mathutils.Matrix.Scale(1.0, 4)
                    coords, indices = blgd.init_cone_dome(item.width, item.height)

                final_matrix = pb_matrix @ volume_matrix
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for item in ob.m3_cameras:
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb:
                if not opts.draw_cameras and not (pb_select[pb] and opts.draw_selected):
                    continue

                pb_matrix = get_pb_world_matrix(ob, pb_to_world_matrix, pb)
                col = blgd.camera_color_normal if not pb_select[pb] else blgd.camera_color_select
                final_matrix = pb_matrix @ mathutils.Matrix.LocRotScale(None, None, (item.field_of_view, item.field_of_view, item.focal_depth))
                coords, indices = blgd.camera
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        handle_to_physics_shape_data = {}

        for rigid_body in ob.m3_rigidbodies:
            pb = get_pb_from_handle(ob, rigid_body.bone, pb_handles)
            physics_shape = shared.m3_pointer_get(ob.m3_physicsshapes, rigid_body.physics_shape)
            if pb and physics_shape:
                if not opts.draw_rigidbodies and not (pb_select[pb] and opts.draw_selected):
                    continue

                pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)

                physics_shape_data = handle_to_physics_shape_data.get(physics_shape.bl_handle)

                if not physics_shape_data:
                    handle_to_physics_shape_data[physics_shape.bl_handle] = {}
                    for ii, item in enumerate(physics_shape.volumes):
                        col = blgd.physics_color_normal if not pb_select[pb] or ii != physics_shape.volumes_index else blgd.physics_color_select
                        item_loc = mathutils.Vector((-item.location.y, item.location.x, item.location.z))
                        item_rot = mathutils.Euler((-item.rotation.y, item.rotation.x, item.rotation.z))
                        item_matrix = mathutils.Matrix.LocRotScale(item_loc, item_rot, item.scale.yxz)
                        if item.shape == 'CUBE':
                            volume_matrix = mathutils.Matrix.LocRotScale(None, None, (item.size[1], item.size[0], item.size[2]))
                            coords, indices = blgd.cube
                        elif item.shape == 'SPHERE':
                            volume_matrix = mathutils.Matrix.Scale(item.size[0], 4)
                            coords, indices = blgd.sphere
                        elif item.shape == 'CAPSULE':
                            volume_matrix = mathutils.Matrix.Scale(1, 4)
                            coords, indices = blgd.init_capsule(item.size[0], item.size[1])
                        elif item.shape == 'CYLINDER':
                            volume_matrix = mathutils.Matrix.LocRotScale(None, None, (item.size[0], item.size[0], item.size[1]))
                            coords, indices = blgd.cylinder
                        elif item.shape == 'MESH' or item.shape == 'CONVEXHULL':
                            # TODO display actual convex hull of mesh if it is not convex when shape is CONVEXHULL
                            if not item.mesh_object:
                                continue
                            volume_matrix = rot_fix_matrix_transpose
                            coords = [vert.co for vert in item.mesh_object.data.vertices]
                            indices = [edge.vertices for edge in item.mesh_object.data.edges]

                        handle_to_physics_shape_data[physics_shape.bl_handle][ii] = (coords, indices, item_matrix, volume_matrix)

                        final_matrix = pb_matrix @ item_matrix @ volume_matrix
                        coords = get_transformed_coords(coords, final_matrix)
                        batch_uni_polyline(coords, indices, col)
                else:
                    for ii, item in physics_shape_data.items():
                        if not item:
                            continue
                        col = blgd.physics_color_normal if not pb_select[pb] or ii != shape.volumes_index else blgd.physics_color_select
                        final_matrix = pb_matrix @ item[2] @ item[3]
                        coords = get_transformed_coords(item[0], final_matrix)
                        batch_uni_polyline(coords, item[1], col)

        # TODO PHYJ

        for constraint_set in ob.m3_clothconstraintsets:
            # TODO only procede if the constraint set is used
            for item in constraint_set.constraints:
                pb = get_pb_from_handle(ob, item.bone, pb_handles)
                if pb:
                    if not opts.draw_clothconstraints and not (pb_select[pb] and opts.draw_selected):
                        continue

                    pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)
                    item_loc = mathutils.Vector((-item.location.x, item.location.y, -item.location.z))
                    item_rot = mathutils.Euler((-item.rotation.x, item.rotation.y, -item.rotation.z))
                    item_matrix = mathutils.Matrix.LocRotScale(item_loc, item_rot, item.scale.yxz)
                    col = blgd.cloth_color_normal if not pb_select[pb] else blgd.cloth_color_select
                    final_matrix = pb_matrix @ item_matrix
                    coords, indices = blgd.init_capsule(item.radius, item.height)
                    coords = get_transformed_coords(coords, final_matrix)
                    batch_uni_polyline(coords, indices, col)

        for ii, item in enumerate(ob.m3_ikjoints):
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb:
                if not opts.draw_ikjoints and not (pb_select[pb] and opts.draw_selected):
                    continue

                bone_parent = bone
                for jj in range(0, item.joint_length):
                    if bone_parent.parent:
                        bone_parent = bone_parent.parent if bone_parent else bone_parent
                if bone_parent is not bone:
                    pbp = ob.pose.bones.get(bone_parent.name)
                    pb_world_m = get_pb_world_matrix(ob, pb_to_world_matrix, pb)
                    pbp_world_m = get_pb_world_matrix(ob, pb_to_world_matrix, pbp)
                    col = blgd.ik_color_normal if ii != ob.m3_ikjoints_index else blgd_ik_color_select
                    coords, indices = ((pb_world_m.translation, pbp_world_m.translation), (0, 1))
                    batch_uni_polyline(coords, indices, col)

        for item in ob.m3_shadowboxes:
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb:
                if not opts.draw_shadowboxes and not (pb_select[pb] and opts.draw_selected):
                    continue

                col = blgd.shbx_color_normal if not pb_select[pb] else blgd.shbx_color_select
                pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)
                volume_matrix = mathutils.Matrix.LocRotScale(None, None, (item.width, item.length, item.height))
                final_matrix = pb_matrix @ volume_matrix
                coords, indices = blgd.cube
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for item in ob.m3_warps:
            pb = get_pb_from_handle(ob, item.bone, pb_handles)
            if pb:
                if not opts.draw_warps and not (pb_select[pb] and opts.draw_selected):
                    continue

                col = blgd.warp_color_normal if not pb_select[pb] else blgd.warp_color_select
                pb_matrix = get_pb_world_matrix(ob, pb_to_world_bind_matrix, pb, apply_bind_matrix=True)
                final_matrix = pb_matrix @ mathutils.Matrix.Scale(item.radius, 4)
                coords, indices = blgd.sphere
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for turret in ob.m3_turrets:
            for item in turret.parts:
                pb = get_pb_from_handle(ob, item.bone, pb_handles)
                if pb:
                    if not opts.draw_turrets and not (pb_select[pb] and opts.draw_selected):
                        continue

                    yaw_rot = mathutils.Euler(item.forward)
                    yaw_rot[1] -= 1.570796132
                    yaw_rot[2] -= 1.570796132

                    pitch_rot = mathutils.Euler(item.forward)
                    pitch_rot[0] -= 1.570796132
                    pitch_rot[1] += 1.570796132
                    pitch_rot[2] += 1.570796132

                    if item.yaw_weight:
                        col = blgd.turret_yaw_color_normal if not pb_select[pb] else blgd.turret_yaw_color_select
                        final_matrix = mathutils.Matrix.LocRotScale(get_pb_world_matrix(ob, pb_to_world_matrix, pb).translation, yaw_rot, (0.5, 0.5, 0.5))
                        if item.yaw_limited:
                            yaw_limit_arc = -item.yaw_min + item.yaw_max
                            yaw_limit_arc_med = (item.yaw_min + item.yaw_max) / 2
                            coords, indices = blgd.get_arc_wire_data(yaw_limit_arc)
                            final_matrix @= mathutils.Euler((0.0, 0.0, yaw_limit_arc_med)).to_matrix().to_4x4()
                        else:
                            coords, indices = blgd.arc360

                        coords = get_transformed_coords(coords, final_matrix)
                        batch_uni_polyline(coords, indices, col, line_width=1.0)

                    if item.pitch_weight:
                        col = blgd.turret_pitch_color_normal if not pb_select[pb] else blgd.turret_pitch_color_select
                        final_matrix = mathutils.Matrix.LocRotScale(get_pb_world_matrix(ob, pb_to_world_matrix, pb).translation, pitch_rot, (0.5, 0.5, 0.5))
                        if item.pitch_limited:
                            pitch_limit_arc = -item.pitch_min + item.pitch_max
                            pitch_limit_arc_med = (item.pitch_min + item.pitch_max) / 2
                            coords, indices = blgd.get_arc_wire_data(pitch_limit_arc)
                            final_matrix @= mathutils.Euler((0.0, 0.0, pitch_limit_arc_med)).to_matrix().to_4x4()
                        else:
                            coords, indices = blgd.arc180

                        coords = get_transformed_coords(coords, final_matrix)
                        batch_uni_polyline(coords, indices, col, line_width=1.0)
