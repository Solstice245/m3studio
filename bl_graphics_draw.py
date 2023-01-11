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


def get_bone_from_handle(ob, bone_handle, handle_bone_dict):
    bone_from_handle = handle_bone_dict.get(bone_handle, False)
    if bone_from_handle is False:
        bone_from_handle = shared.m3_pointer_get(ob.data.bones, bone_handle)
        handle_bone_dict[bone_handle] = bone_from_handle
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


def batch_uni_polyline(coords, indices, color, line_width=1.0):
    region = bpy.context.region
    uni_polyline_shader.uniform_float("lineWidth", line_width)
    uni_polyline_shader.uniform_float("viewportSize", (region.width, region.height))
    uni_polyline_shader.uniform_float('color', [*color] + [1])
    batch = batch_for_shader(uni_polyline_shader, 'LINES', {'pos': coords}, indices=indices)
    batch.draw(uni_polyline_shader)


# TODO cache batches rather than generating new ones on every execution?
# TODO cache pose bone world matrices outside of draw func?

# TODO options to filter generation of helper types
# TODO PAR_, RIB_, PROJ, PHRB, PHYJ, PHCC
def draw():

    if not bpy.context.space_data.overlay.show_overlays:
        return

    if bpy.context.space_data.shading.type == 'SOLID':
        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.depth_mask_set(True)
    elif bpy.context.space_data.shading.type == 'WIREFRAME':
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

        for attachment in ob.m3_attachmentpoints:
            bone = get_bone_from_handle(ob, attachment.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                pb_world_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                col = blgd.att_point_color_normal if not pb_select[pb] else blgd.att_point_color_select
                coords, indices = blgd.point
                coords = get_transformed_coords(coords, pb_world_matrix)
                batch_uni_polyline(coords, indices, col)

            for ii, vol in enumerate(attachment.volumes):
                vol_bone = get_bone_from_handle(ob, vol.bone, handle_to_bone)
                if vol_bone:
                    vol_pb = ob.pose.bones.get(bone.name)
                    vol_pb_world_matrix = get_pb_world_matrix(ob, vol_pb, pb_to_world_matrix)
                    vol_post_matrix = mathutils.Matrix.LocRotScale(vol.location, vol.rotation, vol.scale)
                    col = blgd.att_point_color_normal if not pb_select[pb] or ii != attachment.volumes_index else blgd.att_point_color_select
                    if vol.shape == 'CUBE':
                        vol_size_matrix = mathutils.Matrix.LocRotScale(None, None, vol.size)
                        final_matrix = vol_pb_world_matrix @ vol_size_matrix @ vol_post_matrix @ bone_to_inv_bind_scale_matrix[vol_bone]
                        coords, indices = blgd.cube
                    elif vol.shape == 'SPHERE':
                        vol_size_matrix = mathutils.Matrix.LocRotScale(None, None, [vol.size[0]] * 3)
                        final_matrix = vol_pb_world_matrix @ vol_size_matrix @ vol_post_matrix @ bone_to_inv_bind_scale_matrix[vol_bone]
                        coords, indices = blgd.sphere
                    elif vol.shape == 'CAPSULE':
                        final_matrix = vol_pb_world_matrix @ vol_post_matrix @ bone_to_inv_bind_scale_matrix[vol_bone]
                        coords, indices = blgd.init_capsule(vol.size[0], vol.size[1])
                    # TODO mesh/convex hull shapes

                    coords = get_transformed_coords(coords, final_matrix)
                    batch_uni_polyline(coords, indices, col)

        bone = get_bone_from_handle(ob, ob.m3_hittest_tight.bone, handle_to_bone)
        if bone:
            vol = ob.m3_hittest_tight
            pb = ob.pose.bones.get(bone.name)
            pb_world_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
            post_matrix = mathutils.Matrix.LocRotScale(vol.location, vol.rotation, vol.scale)
            col = blgd.hittest_color_normal if not pb_select[pb] else blgd.hittest_color_select
            if vol.shape == 'CUBE':
                size_matrix = mathutils.Matrix.LocRotScale(None, None, vol.size)
                final_matrix = pb_world_matrix @ size_matrix @ post_matrix @ bone_to_inv_bind_scale_matrix[bone]
                coords, indices = blgd.cube
            elif vol.shape == 'SPHERE':
                size_matrix = mathutils.Matrix.LocRotScale(None, None, [vol.size[0]] * 3)
                final_matrix = pb_world_matrix @ size_matrix @ post_matrix @ bone_to_inv_bind_scale_matrix[bone]
                coords, indices = blgd.sphere
            elif vol.shape == 'CAPSULE':
                final_matrix = pb_world_matrix @ post_matrix @ bone_to_inv_bind_scale_matrix[bone]
                coords, indices = blgd.init_capsule(vol.size[0], vol.size[1])
            # TODO mesh shapes

            coords = get_transformed_coords(coords, final_matrix)
            batch_uni_polyline(coords, indices, col)

        for vol in ob.m3_hittests:
            bone = get_bone_from_handle(ob, vol.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                col = blgd.hittest_color_normal if not pb_select[pb] else blgd.hittest_color_select
                final_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                if vol.shape == 'CUBE':
                    final_matrix @= mathutils.Matrix.LocRotScale(None, None, vol.size)
                    coords, indices = blgd.cube
                elif vol.shape == 'SPHERE':
                    final_matrix @= mathutils.Matrix.LocRotScale(None, None, [vol.size[0]] * 3)
                    coords, indices = blgd.sphere
                elif vol.shape == 'CAPSULE':
                    coords, indices = blgd.init_capsule(vol.size[0], vol.size[1])
                # TODO mesh shapes

                final_matrix @= mathutils.Matrix.LocRotScale(vol.location, vol.rotation, vol.scale) @ bone_to_inv_bind_scale_matrix[bone]
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        # TODO RIB_

        for light in ob.m3_lights:
            bone = get_bone_from_handle(ob, light.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                col = blgd.light_color_normal if not pb_select[pb] else blgd.light_color_select
                final_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                if light.shape == 'POINT':
                    final_matrix @= mathutils.Matrix.Scale(light.attenuation_far, 4)
                    coords, indices = blgd.sphere
                elif light.shape == 'SPOT':
                    final_matrix @= mathutils.Matrix.LocRotScale(None, None, (light.attenuation_far, light.attenuation_far, light.falloff))
                    coords, indices = blgd.cone

                final_matrix @= bone_to_inv_bind_scale_matrix[bone]
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for item in ob.m3_forces:
            bone = get_bone_from_handle(ob, item.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                col = blgd.force_color_normal if not pb_select[pb] else blgd.force_color_select
                final_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
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

        for cam in ob.m3_cameras:
            bone = get_bone_from_handle(ob, cam.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                col = blgd.camera_color_normal if not pb_select[pb] else blgd.camera_color_select
                final_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix)
                final_matrix @= mathutils.Matrix.LocRotScale(None, None, (cam.field_of_view, cam.field_of_view, cam.focal_depth))
                coords, indices = blgd.camera
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)

        for ii, ik in enumerate(ob.m3_ikjoints):
            bone = get_bone_from_handle(ob, ik.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                bone_parent = bone
                for ii in range(0, ik.joint_length):
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

        for warp in ob.m3_warps:
            bone = get_bone_from_handle(ob, warp.bone, handle_to_bone)
            if bone:
                pb = ob.pose.bones.get(bone.name)
                col = blgd.warp_color_normal if not pb_select[pb] else blgd.warp_color_select
                final_matrix = get_pb_world_matrix(ob, pb, pb_to_world_matrix) @ warp.radius
                coords, indices = blgd.sphere
                coords = get_transformed_coords(coords, final_matrix)
                batch_uni_polyline(coords, indices, col)
    #
