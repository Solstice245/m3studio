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
import mathutils
import gpu
from gpu_extras.batch import batch_for_shader
from . import shared
from . import bl_graphics_data as blgd
from .io_shared import rot_fix_matrix_transpose


def get_bone_from_handle(ob, bone_handle, handle_bone_dict):
    bone_from_handle = handle_bone_dict.get(bone_handle, False)
    if bone_from_handle is False:
        bone_from_handle = shared.m3_pointer_get(ob.data.bones, bone_handle)
        handle_bone_dict[bone_handle] = bone_from_handle
    if bone_from_handle and bone_from_handle.hide:
        return None
    return bone_from_handle


def get_pb_world_matrix(ob, pose_bone, pb_matrix_dict):
    pb_world_matrix = pb_matrix_dict.get(pose_bone)
    if not pb_world_matrix:
        pb_world_matrix = ob.matrix_world @ pose_bone.matrix
        pb_matrix_dict[pose_bone] = pb_world_matrix
    return pb_world_matrix


def get_transformed_coords(coords, matrix):
    new_coords = []
    for co in coords:
        new_coords.append(matrix @ co)
    return new_coords


uni_polyline_shader = gpu.shader.from_builtin('3D_POLYLINE_UNIFORM_COLOR')


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
# TODO RIB_, PHYJ, PATU
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
        handle_to_bone = {}
        bone_to_inv_bind_scale_matrix = {}

        for bone in ob.data.bones:
            bs = bone.m3_bind_scale
            bone_to_inv_bind_scale_matrix[bone] = mathutils.Matrix.LocRotScale(None, None, (1 / bs[0], 1 / bs[1], 1 / bs[2]))

        for item in ob.m3_attachmentpoints:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                pb_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                col = blgd.att_point_color_normal if not pb_select[pb] else blgd.att_point_color_select
                coords, indices = blgd.point
                coords = get_transformed_coords(coords, pb_matrix @ bone_to_inv_bind_scale_matrix[bone])
                batch_uni_polyline(coords, indices, col)

            for ii, vol in enumerate(item.volumes):
                attach = item
                item = vol
                vol_bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
                if vol_bone:
                    vol_pb = ob.pose.bones.get(bone.name)
                    vol_pb_matrix = get_pb_world_matrix(ob, vol_pb, pb_to_world_matrix)
                    col = blgd.att_point_color_normal if not pb_select[pb] or ii != attach.volumes_index else blgd.att_point_color_select
                    vol_post_matrix = mathutils.Matrix.LocRotScale(item.location, item.rotation, item.scale)
                    vol_final_matrix = vol_pb_matrix.copy()
                    if item.shape == 'CUBE':
                        vol_final_matrix @= mathutils.Matrix.LocRotScale(None, None, (item.size[1], item.size[0], item.size[2]))
                        coords, indices = blgd.cube
                    elif item.shape == 'SPHERE':
                        vol_final_matrix @= mathutils.Matrix.Scale(item.size[0], 4)
                        coords, indices = blgd.sphere
                    elif item.shape == 'CAPSULE':
                        coords, indices = blgd.init_capsule(item.size[0], item.size[1])
                    elif item.shape == 'CYLINDER':
                        vol_final_matrix @= mathutils.Matrix.LocRotScale(None, None, (item.size[0], item.size[0], item.size[2]))
                        coords, indices = blgd.cylinder
                    elif item.shape == 'MESH':
                        # TODO cache coords and indices per object that is used as volume shape
                        if not item.mesh_object:
                            continue
                        vol_final_matrix @= rot_fix_matrix_transpose
                        coords = [vert.co for vert in item.mesh_object.data.vertices]
                        indices = [edge.vertices for edge in item.mesh_object.data.edges]

                    vol_final_matrix @= bone_to_inv_bind_scale_matrix[vol_bone] @ vol_post_matrix

                    coords = get_transformed_coords(coords, vol_final_matrix)
                    batch_uni_polyline(coords, indices, col)

        for item in [item for item in ob.m3_hittests] + [ob.m3_hittest_tight]:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                pb_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                col = blgd.hittest_color_normal if not pb_select[pb] else blgd.hittest_color_select
                final_matrix = pb_matrix.copy()
                if item.shape == 'CUBE':
                    final_matrix @= mathutils.Matrix.LocRotScale(None, None, (item.size[1], item.size[0], item.size[2]))
                    coords, indices = blgd.cube
                elif item.shape == 'SPHERE':
                    final_matrix @= mathutils.Matrix.Scale(item.size[0], 4)
                    coords, indices = blgd.sphere
                elif item.shape == 'CAPSULE':
                    coords, indices = blgd.init_capsule(item.size[0], item.size[1])
                elif item.shape == 'CYLINDER':
                    final_matrix @= mathutils.Matrix.LocRotScale(None, None, (item.size[0], item.size[0], item.size[2]))
                    coords, indices = blgd.cylinder
                elif item.shape == 'MESH':
                    if not item.mesh_object:
                        continue
                    final_matrix @= rot_fix_matrix_transpose
                    coords = [vert.co for vert in item.mesh_object.data.vertices]
                    indices = [edge.vertices for edge in item.mesh_object.data.edges]

                final_matrix @= bone_to_inv_bind_scale_matrix[bone] @ mathutils.Matrix.LocRotScale(item.location, item.rotation, item.scale)
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for item in ob.m3_lights:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                col = blgd.light_color_normal if not pb_select[pb] else blgd.light_color_select
                final_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                if item.shape == 'POINT':
                    final_matrix @= mathutils.Matrix.Scale(item.attenuation_far, 4)
                    coords, indices = blgd.sphere
                elif item.shape == 'SPOT':
                    final_matrix @= mathutils.Matrix.LocRotScale(None, None, (item.attenuation_far, item.attenuation_far, item.falloff))
                    coords, indices = blgd.cone

                final_matrix @= bone_to_inv_bind_scale_matrix[bone]
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        handle_to_par_data = {}

        for item in ob.m3_particle_systems:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                pb_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)

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
                    par_matrix = mathutils.Matrix.LocRotScale(None, None, (radius, radius, size[2]))
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
                    del indices[-1]

                handle_to_par_data[item.bl_handle] = [coords, indices, par_matrix, par_cutout_matrix]

                if par_matrix:
                    final_matrix = pb_matrix @ bone_to_inv_bind_scale_matrix[bone] @ par_matrix
                else:
                    final_matrix = pb_matrix @ bone_to_inv_bind_scale_matrix[bone]

                par_coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(par_coords, indices, col)

                if par_cutout_matrix:
                    final_matrix = pb_matrix @ bone_to_inv_bind_scale_matrix[bone] @ par_matrix
                    par_cutout_coords = get_transformed_coords(coords, final_matrix)
                    batch_uni_polyline(par_cutout_coords, indices, col)

        for item in ob.m3_particle_copies:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone and len(item.systems):
                pb = ob.pose.bones.get(bone.name)
                pb_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                inv_bind_scale = bone_to_inv_bind_scale_matrix[bone]

                col = blgd.particle_color_normal if not pb_select[pb] else blgd.particle_color_select
                for system in item.systems:
                    system_data = handle_to_par_data.get(system)
                    if not system_data:
                        continue
                    coords, indices, par_matrix, par_cutout_matrix = system_data
                    if coords and indices:
                        if par_matrix:
                            final_matrix = pb_matrix @ inv_bind_scale @ par_matrix
                        else:
                            final_matrix = pb_matrix @ inv_bind_scale
                        par_coords = get_transformed_coords(coords, final_matrix)
                        batch_uni_polyline(par_coords, indices, col)

                        if par_cutout_matrix:
                            final_cutout_matrix = pb_matrix @ inv_bind_scale @ par_cutout_matrix
                            par_cutout_coords = get_transformed_coords(coords, final_cutout_matrix)
                            batch_uni_polyline(par_cutout_coords, indices, col)

        # TODO RIB_

        for item in ob.m3_projections:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                pb_matrix = get_pb_world_matrix(ob, pb, handle_to_bone)
                col = blgd.projector_color_normal if not pb_select[pb] else blgd.projector_color_select
                vec_min = mathutils.Vector((item.box_offset_x_left, item.box_offset_y_front, item.box_offset_z_top))
                vec_max = mathutils.Vector((item.box_offset_x_right, item.box_offset_y_back, item.box_offset_z_bottom))
                proj_matrix = mathutils.Matrix.LocRotScale(vec_max + vec_min, None, vec_max - vec_min)
                coords, indices = blgd.cube
                final_matrix = pb_matrix @ bone_to_inv_bind_scale_matrix[bone] @ proj_matrix
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for item in ob.m3_forces:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                pb_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                col = blgd.force_color_normal if not pb_select[pb] else blgd.force_color_select
                final_matrix = pb_matrix.copy()
                if item.shape == 'CUBE':
                    final_matrix @= mathutils.Matrix.LocRotScale(None, None, (item.width, item.length, item.height))
                    coords, indices = blgd.cube
                elif item.shape == 'CYLINDER':
                    final_matrix @= mathutils.Matrix.LocRotScale(None, None, (item.width, item.length, item.height))
                    coords, indices = blgd.cylinder
                elif item.shape == 'SPHERE':
                    final_matrix @= mathutils.Matrix.Scale(item.width, 4)
                    coords, indices = blgd.sphere
                elif item.shape == 'HEMISPHERE':
                    final_matrix @= mathutils.Matrix.Scale(item.width, 4)
                    coords, indices = blgd.hemisphere
                elif item.shape == 'CONEDOME':
                    coords, indices = blgd.init_cone_dome(item.width, item.height)

                final_matrix @= bone_to_inv_bind_scale_matrix[bone]
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for item in ob.m3_cameras:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                pb_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                col = blgd.camera_color_normal if not pb_select[pb] else blgd.camera_color_select
                final_matrix = pb_matrix @ mathutils.Matrix.LocRotScale(None, None, (item.field_of_view, item.field_of_view, item.focal_depth))
                coords, indices = blgd.camera
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        handle_to_physics_shape_data = {}

        for rigid_body in ob.m3_rigidbodies:
            bone = get_bone_from_handle(ob, rigid_body.bone, handle_to_bone)
            physics_shape = shared.m3_pointer_get(ob.m3_physicsshapes, rigid_body.physics_shape)
            if not bone or not physics_shape:
                continue

            pb = ob.pose.bones.get(bone.name)
            pb_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)

            physics_shape_data = handle_to_physics_shape_data.get(physics_shape.bl_handle)

            if not physics_shape_data:
                handle_to_physics_shape_data[physics_shape.bl_handle] = {}
                for ii, item in enumerate(physics_shape.volumes):
                    col = blgd.physics_color_normal if not pb_select[pb] or ii != physics_shape.volumes_index else blgd.physics_color_select
                    vol_matrix = None
                    if item.shape == 'CUBE':
                        vol_matrix = mathutils.Matrix.LocRotScale(None, None, (item.size[1], item.size[0], item.size[2]))
                        coords, indices = blgd.cube
                    elif item.shape == 'SPHERE':
                        vol_matrix = mathutils.Matrix.Scale(item.size[0], 4)
                        coords, indices = blgd.sphere
                    elif item.shape == 'CAPSULE':
                        coords, indices = blgd.init_capsule(item.size[0], item.size[1])
                    elif item.shape == 'CYLINDER':
                        vol_matrix = mathutils.Matrix.LocRotScale(None, None, (item.size[0], item.size[0], item.size[2]))
                        coords, indices = blgd.cylinder
                    elif item.shape == 'MESH' or item.shape == 'CONVEXHULL':
                        # TODO display actual convex hull of mesh if it is not convex when shape is CONVEXHULL
                        if not item.mesh_object:
                            continue
                        vol_matrix = rot_fix_matrix_transpose
                        coords = [vert.co for vert in item.mesh_object.data.vertices]
                        indices = [edge.vertices for edge in item.mesh_object.data.edges]

                    if vol_matrix:
                        vol_matrix @= mathutils.Matrix.LocRotScale(item.location, item.rotation, item.scale)
                    else:
                        vol_matrix = mathutils.Matrix.LocRotScale(item.location, item.rotation, item.scale)

                    handle_to_physics_shape_data[physics_shape.bl_handle][ii] = (coords, indices, vol_matrix)

                    final_matrix = pb_matrix @ bone_to_inv_bind_scale_matrix[bone] @ vol_matrix
                    coords = get_transformed_coords(coords, final_matrix)
                    batch_uni_polyline(coords, indices, col)
            else:
                for ii, item in physics_shape_data.items():
                    if not item:
                        continue
                    col = blgd.physics_color_normal if not pb_select[pb] or ii != shape.volumes_index else blgd.physics_color_select
                    final_matrix = pb_matrix @ bone_to_inv_bind_scale_matrix[bone] @ item[2]
                    coords = get_transformed_coords(item[0], final_matrix)
                    batch_uni_polyline(coords, item[1], col)

        for constraint_set in ob.m3_clothconstraintsets:
            # TODO only procede if the constraint set is used
            for item in constraint_set.constraints:
                bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
                if bone:
                    pb = ob.pose.bones.get(bone.name)
                    pb_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                    col = blgd.cloth_color_normal if not pb_select[pb] else blgd.cloth_color_select
                    final_matrix = pb_matrix @ bone_to_inv_bind_scale_matrix[bone] @ mathutils.Matrix.LocRotScale(item.location, item.rotation, item.scale)
                    coords, indices = blgd.init_capsule(item.radius, item.height)
                    coords = get_transformed_coords(coords, final_matrix)
                    batch_uni_polyline(coords, indices, col)

        for ii, item in enumerate(ob.m3_ikjoints):
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                bone_parent = bone
                for ii in range(0, item.joint_length):
                    if bone_parent.parent:
                        bone_parent = bone_parent.parent if bone_parent else bone_parent
                if bone_parent is not bone:
                    pbp = ob.pose.bones.get(bone_parent.name)
                    pb_world_m = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                    pbp_world_m = get_pb_world_matrix(ob, pbp, pb_to_world_matrix)
                    col = blgd.ik_color_normal if ii != ob.m3_ikjoints_index else blgd_ik_color_select
                    coords, indices = ((pb_world_m.translation, pbp_world_m.translation), (0, 1))
                    batch_uni_polyline(coords, indices, col)

        for item in ob.m3_shadowboxes:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                col = blgd.shbx_color_normal if not pb_select[pb] else blgd.shbx_color_select
                final_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                final_matrix @= mathutils.Matrix.LocRotScale(None, None, (item.width, item.length, item.height))
                coords, indices = blgd.cube
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for item in ob.m3_warps:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                col = blgd.warp_color_normal if not pb_select[pb] else blgd.warp_color_select
                final_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix) @ mathutils.Matrix.Scale(item.radius, 4)
                coords, indices = blgd.sphere
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)
    #
