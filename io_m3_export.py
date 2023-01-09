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
import bmesh
import mathutils
import math
import os
from . import io_m3
from . import io_shared
from . import shared
from .m3_animations import anim_set


ANIM_DATA_SECTION_NAMES = ('SDEV', 'SD2V', 'SD3V', 'SD4Q', 'SDCC', 'SDR3', 'SD08', 'SDS6', 'SDU6', 'SDS3', 'SDU3', 'SDFG', 'SDMB')
BNDS_ANIM_ID = 0x001f9bd2
EVNT_ANIM_ID = 0x65bd3215
INT16_MIN = (-(1 << 15))
INT16_MAX = ((1 << 15) - 1)


def to_m3_ms(bl_frame):
    # TODO 30 is the desired scene frame rate, but more options could be accounted for
    return round(bl_frame / 30 * 1000)


def to_m3_uv(bl_uv):
    m3_uv = io_m3.structures['Vector2As2int16'].get_version(0).instance()
    m3_uv.x = sorted((INT16_MIN, round(bl_uv[0] * 2048), INT16_MAX))[1]
    m3_uv.y = (sorted((INT16_MIN, round((-bl_uv[1] + 1.0) * 2048), INT16_MAX))[1])
    return m3_uv


def to_m3_vec2(bl_vec=None):
    m3_vec = io_m3.structures['VEC2'].get_version(0).instance()
    m3_vec.x, m3_vec.y = bl_vec or (0.0, 0.0)
    return m3_vec


def to_m3_vec3(bl_vec=None):
    m3_vec = io_m3.structures['VEC3'].get_version(0).instance()
    m3_vec.x, m3_vec.y, m3_vec.z = bl_vec or (0.0, 0.0, 0.0)
    return m3_vec


def to_m3_vec3_f8(bl_vec=None):
    m3_vec = io_m3.structures['Vector3As3Fixed8'].get_version(0).instance()
    m3_vec.x, m3_vec.y, m3_vec.z = bl_vec or (0.0, 0.0, 0.0)
    return m3_vec


def to_m3_vec4(bl_vec=None):
    m3_vec = io_m3.structures['VEC4'].get_version(0).instance()
    m3_vec.x, m3_vec.y, m3_vec.z, m3_vec.w = bl_vec or (0.0, 0.0, 0.0, 0.0)
    return m3_vec


def to_m3_quat(bl_quat=None):
    m3_quat = io_m3.structures['QUAT'].get_version(0).instance()
    m3_quat.w, m3_quat.x, m3_quat.y, m3_quat.z = bl_quat or (1.0, 0.0, 0.0, 0.0)
    return m3_quat


def to_m3_color(bl_col=None):
    m3_color = io_m3.structures['COL'].get_version(0).instance()
    if bl_col is None:
        m3_color.r, m3_color.g, m3_color.b, m3_color.a = (0, 0, 0, 0xff)
    else:
        m3_color.r = round(bl_col[0] * 255)
        m3_color.g = round(bl_col[1] * 255)
        m3_color.b = round(bl_col[2] * 255)
        m3_color.a = round(bl_col[3] * 255)
    return m3_color


def to_m3_matrix(bl_matrix):
    m3_matrix = io_m3.structures['Matrix44'].get_version(0).instance()
    m3_matrix.x = to_m3_vec4(bl_matrix.col[0])
    m3_matrix.y = to_m3_vec4(bl_matrix.col[1])
    m3_matrix.z = to_m3_vec4(bl_matrix.col[2])
    m3_matrix.w = to_m3_vec4(bl_matrix.col[3])
    return m3_matrix


def to_m3_bnds(bl_vecs=None):
    m3_bnds = io_m3.structures['BNDS'].get_version(0).instance()
    if bl_vecs is not None:
        m3_bnds.min = to_m3_vec3(bl_vecs[0])
        m3_bnds.max = to_m3_vec3(bl_vecs[1])
        m3_bnds.radius = (bl_vecs[1] - bl_vecs[0]).length / 2
    return m3_bnds


ANIM_VEC_DATA_SETTINGS = {
    'SD2V': {'length': 2, 'convert': to_m3_vec2, 'attr': ['x', 'y']},
    'SD3V': {'length': 3, 'convert': to_m3_vec3, 'attr': ['x', 'y', 'z']},
    'SDCC': {'length': 4, 'convert': to_m3_color, 'attr': ['r', 'g', 'b', 'a']},
}


def get_fcurve_anim_frames(fcurve, interpolation='LINEAR'):
    if fcurve is None:
        return

    frames = []

    last_interp = interpolation
    last_frame = round(fcurve.keyframe_points[0].co.x)
    for point in fcurve.keyframe_points:
        frame = round(point.co.x)
        if last_interp != interpolation and last_interp != 'CONSTANT':
            for f in range(last_frame, frame):
                frames.append(f)
        last_interp = point.interpolation
        last_frame = round(point.co.x)
        frames.append(frame)

    return frames


def sqr(val):
    return val * val


def quats_compatibility(quats):
    if len(quats) < 2:
        return

    prev_quat = quats[0]
    for quat in quats[1:]:
        quat.make_compatible(prev_quat)
        prev_quat = quat


def float_interp(left, right, factor):
    return left * (1 - factor) + right * factor


def float_equal(val0, val1):
    return abs(val0 - val1) < 0.0001


def vec_interp(left, right, factor):
    return left.lerp(right, factor)


def vec_equal(val0, val1):
    return (val0 - val1).length < 0.0001


def quat_interp(left, right, factor):
    return left.slerp(right, factor)


def quat_equal(val0, val1):
    dist = sqr(val0.x - val1.x) + sqr(val0.y - val1.y) + sqr(val0.z - val1.z) + sqr(val0.w - val1.w)
    return dist < sqr(0.0001)


def simplify_anim_data_with_interp(keys, vals, interp_func, equal_func):
    if len(vals) < 2:
        return keys, vals

    left_key, curr_key = keys[0:2]
    left_val, curr_val = vals[0:2]
    new_keys = [left_key]
    new_vals = [left_val]

    for right_key, right_val in zip(keys[2:], vals[2:]):
        interpolated_val = interp_func(left_val, right_val, (curr_key - left_key) / (right_key - left_key))
        if equal_func(interpolated_val, curr_val):
            # ignore current value since since it matches the given interpolation
            pass
        else:
            new_keys.append(curr_key)
            new_vals.append(curr_val)
            left_key = curr_key
            left_val = curr_val
        curr_key = right_key
        curr_val = right_val

    new_keys.append(keys[-1])
    new_vals.append(vals[-1])

    return new_keys, new_vals


def vec_list_contains_not_only(vec_list, vec):
    for v in vec_list:
        if not vec_equal(v, vec):
            return True
    return False


def quat_list_contains_not_only(quat_list, quat):
    for q in quat_list:
        if not quat_equal(q, quat):
            return True
    return False


def bounding_vectors_from_bones(bone_rest_bounds, bone_to_matrix_dict):
    vec_min = mathutils.Vector((float('inf'), float('inf'), float('inf')))
    vec_max = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))

    for bone, bounding_cos in bone_rest_bounds.items():
        matrix = bone_to_matrix_dict[bone]
        bone_vec_min = mathutils.Vector((float('inf'), float('inf'), float('inf')))
        bone_vec_max = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))
        for co in bounding_cos:
            mat_co = matrix @ co
            for ii in range(3):
                bone_vec_min[ii] = min(bone_vec_min[ii], mat_co[ii])
                bone_vec_max[ii] = max(bone_vec_max[ii], mat_co[ii])
        for ii in range(3):
            if not math.isinf(bone_vec_min[0]):
                vec_min[ii] = min(vec_min[ii], bone_vec_min[ii])
                vec_max[ii] = max(vec_max[ii], bone_vec_max[ii])

    return vec_min, vec_max


class M3OutputProcessor:

    def __init__(self, exporter, bl, m3):
        self.exporter = exporter
        self.bl = bl
        self.m3 = m3
        self.version = m3.struct_desc.struct_version

    def collect_anim_data_single(self, field, anim_ref, anim_data_tag):
        for action in self.exporter.action_to_anim_data:
            fcurve = action.fcurves.find(self.bl.path_from_id(field))
            frames = get_fcurve_anim_frames(fcurve)

            if not frames:
                continue

            values = [int(fcurve.evaluate(frame)) for frame in frames]
            self.exporter.action_to_anim_data[action][anim_data_tag][anim_ref.header.id] = (frames, values)

    def collect_anim_data_vector(self, field, anim_ref, anim_data_tag):
        vec_data_settings = ANIM_VEC_DATA_SETTINGS[anim_data_tag]
        for action in self.exporter.action_to_anim_data:
            animated = False
            fcurves = []
            for ii in range(vec_data_settings['length']):
                fcurve = action.fcurves.find(self.bl.path_from_id(field), index=ii)

                if fcurve:
                    fcurves.append(fcurve)
                    animated = True
                else:
                    fcurves.append(None)

            if not animated:
                continue

            frames = []
            for fcurve in fcurves:
                if fcurve is None:
                    continue

                fcurve_frames = get_fcurve_anim_frames(fcurve)
                if fcurve_frames is not None:
                    frames.extend(fcurve_frames)

            frames = sorted(list(set(frames)))

            if not frames:
                continue

            values = []
            for frame in frames:
                vec_comps = []

                for ii, fcurve in enumerate(fcurves):
                    if fcurve is None:
                        vec_comps.append(getattr(anim_ref.default, vec_data_settings['attr'][ii]))
                    else:
                        vec_comps.append(fcurve.evaluate(frame))

                values.append(vec_data_settings['convert'](vec_comps))

            self.exporter.action_to_anim_data[action][anim_data_tag][anim_ref.header.id] = (frames, values)

    def boolean(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        setattr(self.m3, field, int(getattr(self.bl, field)))

    def bit(self, field, name, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        self.m3.bit_set(field, name, getattr(self.bl, name))

    def bits_16(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        vector = getattr(self.bl, field)
        val = 0
        for ii in range(0, 16):
            if vector[ii]:
                val |= 1 << ii
        setattr(self.m3, field, val)

    def bits_32(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        vector = getattr(self.bl, field)
        val = 0
        for ii in range(0, 32):
            if vector[ii]:
                val |= 1 << ii
        setattr(self.m3, field, val)

    def integer(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        setattr(self.m3, field, getattr(self.bl, field))

    def float(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        setattr(self.m3, field, getattr(self.bl, field))

    def vec3(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        setattr(self.m3, field, to_m3_vec3(getattr(self.bl, field)))

    def vec4(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        setattr(self.m3, field, to_m3_vec4(getattr(self.bl, field)))

    def color(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        setattr(self.m3, field, to_m3_color(getattr(self.bl, field)))

    def enum(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        bl_val = getattr(self.bl, field)
        for ii, item in enumerate(self.bl.bl_rna.properties[field].enum_items):
            if item.identifier == bl_val:
                setattr(self.m3, field, ii)
                break

    def anim_boolean_based_on_SDU3(self, field):
        anim_ref = self.exporter.init_anim_ref_uint32()
        anim_ref.default = int(getattr(self.bl, field))
        setattr(self.m3, field, anim_ref)
        self.collect_anim_data_single(field, anim_ref, 'SDU3')

    def anim_boolean_based_on_SDFG(self, field):
        anim_ref = self.exporter.init_anim_ref_uint32()
        anim_ref.default = int(getattr(self.bl, field))
        setattr(self.m3, field, anim_ref)
        self.collect_anim_data_single(field, anim_ref, 'SDFG')

    def anim_int16(self, field):
        anim_ref = self.exporter.init_anim_ref_int16()
        anim_ref.default = getattr(self.bl, field)
        setattr(self.m3, field, anim_ref)
        self.collect_anim_data_single(field, anim_ref, 'SDS6')

    def anim_uint16(self, field):
        anim_ref = self.exporter.init_anim_ref_uint16()
        anim_ref.default = getattr(self.bl, field)
        setattr(self.m3, field, anim_ref)
        self.collect_anim_data_single(field, anim_ref, 'SDU6')

    def anim_uint32(self, field):
        anim_ref = self.exporter.init_anim_ref_uint32()
        anim_ref.default = int(getattr(self.bl, field))  # casting to int because sometimes bools use this
        setattr(self.m3, field, anim_ref)
        self.collect_anim_data_single(field, anim_ref, 'SDU3')

    def anim_float(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        anim_ref = self.exporter.init_anim_ref_float()
        anim_ref.default = getattr(self.bl, field)
        setattr(self.m3, field, anim_ref)
        self.collect_anim_data_single(field, anim_ref, 'SDR3')

    def anim_vec2(self, field):
        anim_ref = self.exporter.init_anim_ref_vec2()
        anim_ref.default = to_m3_vec2(getattr(self.bl, field))
        setattr(self.m3, field, anim_ref)
        self.collect_anim_data_vector(field, anim_ref, 'SD2V')

    def anim_vec3(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        anim_ref = self.exporter.init_anim_ref_vec3()
        anim_ref.default = to_m3_vec3(getattr(self.bl, field))
        setattr(self.m3, field, anim_ref)
        self.collect_anim_data_vector(field, anim_ref, 'SD3V')

    def anim_color(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        anim_ref = self.exporter.init_anim_ref_color()
        anim_ref.default = to_m3_color(getattr(self.bl, field))
        setattr(self.m3, field, anim_ref)
        self.collect_anim_data_vector(field, anim_ref, 'SDCC')


class Exporter:

    def m3_export(self, ob, filename):
        assert ob.type == 'ARMATURE'

        self.ob = ob
        self.view_layer = bpy.context.view_layer
        self.scene = bpy.context.scene
        self.m3 = io_m3.SectionList(init_header=True)

        self.view_layer.objects.active = self.ob
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.anim_id_count = 0
        self.uv_count = 0
        self.skinned_bones = []
        self.mesh_to_basic_volume_sections = {}
        self.mesh_to_physics_volume_sections = {}

        self.export_required_regions = set()
        self.export_required_material_references = set()
        self.export_required_bones = set()

        self.exported_anims = []
        self.action_frame_range = {}
        self.action_to_anim_data = {}
        self.action_to_sdmb_user = {}
        self.action_abs_pose_matrices = {}
        self.action_to_stc = {}

        # used to calculate exact positions of later sections in the section list
        self.stc_section = None  # defined in the sequence export
        self.stc_to_name_section = {}  # defined in the sequence export
        self.stg_last_indice_section = None  # defined in the sequence export

        # used for later reference such as setting region flags
        self.region_section = None  # defined in the mesh export code

        def valid_collections_and_requirements(collection):
            # TODO have second unexposed export custom prop for auto-culling such as invalid attachment point name
            export_items = []
            for item in collection:
                item_bones = set()
                if not item.m3_export:
                    continue
                if hasattr(item, 'bone'):
                    bone = shared.m3_pointer_get(ob.data.bones, item.bone)
                    if bone:
                        item_bones.add(bone)
                    else:
                        continue  # TODO warn items without valid bone that need one
                if hasattr(item, 'material'):
                    matref = shared.m3_pointer_get(ob.m3_materialrefs, item.material)
                    if matref:
                        self.export_required_material_references.add(matref)
                    else:
                        continue  # TODO warn items without valid material reference that need one
                self.export_required_bones = self.export_required_bones.union(item_bones)
                export_items.append(item)
            return export_items

        export_sequences = []  # handled specially
        export_attachment_points = valid_collections_and_requirements(ob.m3_attachmentpoints)
        export_lights = valid_collections_and_requirements(ob.m3_lights)
        export_shadow_boxes = valid_collections_and_requirements(ob.m3_shadowboxes)
        export_cameras = valid_collections_and_requirements(ob.m3_cameras)
        export_material_references = valid_collections_and_requirements(ob.m3_materialrefs)
        export_particle_systems = valid_collections_and_requirements(ob.m3_particle_systems)
        export_particle_copies = []  # handled specially
        export_ribbons = valid_collections_and_requirements(ob.m3_ribbons)
        export_ribbon_splines = []  # handled specially
        export_projections = valid_collections_and_requirements(ob.m3_projections)
        export_forces = valid_collections_and_requirements(ob.m3_forces)
        export_warps = valid_collections_and_requirements(ob.m3_warps)
        export_physics_bodies = []  # handled specially
        export_physics_joints = []  # handled specially
        export_physics_cloths = []  # handled specially
        export_ik_joints = []  # handled specially
        export_turrets = []  # handled specially
        export_hittests = valid_collections_and_requirements(ob.m3_hittests)
        export_attachment_volumes = []  # handled specially
        export_billboards = []  # handled specially

        self.vertex_color_mats = set()
        self.vertex_alpha_mats = set()

        for anim_group in ob.m3_animation_groups:
            # TODO all anim groups must have unique name.
            # TODO anim groups must have at least one anim.
            if anim_group.m3_export:
                export_sequences.append(anim_group)

        for system in export_particle_systems:
            self.vertex_color_mats.add(system.material)
            if system.vertex_alpha:
                self.vertex_alpha_mats.add(system.material)

        for ribbon in export_ribbons:
            self.vertex_color_mats.add(ribbon.material)
            if ribbon.vertex_alpha:
                self.vertex_alpha_mats.add(ribbon.material)

        def recurse_composite_materials(matref, force_color, force_alpha):
            if force_color:
                self.vertex_color_mats.add(matref.bl_handle)
            if force_alpha:
                self.vertex_alpha_mats.add(matref.bl_handle)
            if matref.mat_type == 'm3_materials_composite':
                mat = shared.m3_pointer_get(getattr(self.ob, matref.mat_type), matref.mat_handle)
                for section in mat.sections:
                    section_matref = shared.m3_pointer_get(ob.m3_materialrefs, section.matref)
                    if section_matref:
                        self.export_required_material_references.add(section_matref)
                        recurse_composite_materials(section_matref, matref.bl_handle in self.vertex_color_mats, matref.bl_handle in self.vertex_alpha_mats)

        for matref in self.export_required_material_references.copy():
            recurse_composite_materials(matref, matref.bl_handle in self.vertex_color_mats, matref.bl_handle in self.vertex_alpha_mats)

        # TODO exclude materials if their type cannot be exported in model version

        for copy in ob.m3_particle_copies:
            if not copy.m3_export:
                continue
            copy_bone = shared.m3_pointer_get(ob.data.bones, copy.bone)
            if len(copy.systems) and copy_bone and copy.m3_export:
                self.export_required_bones.add(copy_bone)
                export_particle_copies.append(copy)

        for spline in ob.m3_ribbonsplines:
            export_spline_points = []
            for point in spline.points:
                point_bone = shared.m3_pointer_get(ob.data.bones, point.bone)
                if point_bone:
                    self.export_required_bones.add(point_bone)
                    export_spline_points.append(point)
                else:
                    pass  # TODO warning that spline point has no valid bone
            if len(export_spline_points):
                export_ribbon_splines.append(spline)

        self.physics_shapes_handle_to_shape = {}
        self.physics_shape_handle_to_volumes = {}
        physics_shape_used_bones = []
        for physics_body in ob.m3_rigidbodies:
            if not physics_body.m3_export:
                continue
            bone = shared.m3_pointer_get(ob.data.bones, physics_body.bone)
            if bone and bone not in physics_shape_used_bones:
                physics_shape_used_bones.append(bone)
                physics_shape = shared.m3_pointer_get(ob.m3_physicsshapes, physics_body.physics_shape)
                if physics_shape:
                    if physics_shape.bl_handle not in self.physics_shape_handle_to_volumes.keys():
                        valid_volumes = []
                        for volume in physics_shape.volumes:
                            if volume.shape == 'MESH' or volume.shape == 'CONVEXHULL':
                                if volume.mesh_object:
                                    valid_volumes.append(volume)
                                    # TODO warning if mesh type volume has no mesh object
                            else:
                                valid_volumes.append(volume)
                        if len(valid_volumes):
                            self.physics_shape_handle_to_volumes[physics_shape.bl_handle] = valid_volumes
                            export_physics_bodies.append(physics_body)
                        else:
                            pass  # TODO warning that physics body shape has no valid volumes
                else:
                    pass  # TODO warning that physics body has no shape
            else:
                pass  # TODO warning that physics body has no valid bone or bone is already used

        for physics_joint in ob.m3_physicsjoints:
            if not physics_joint.m3_export:
                continue
            body1 = shared.m3_pointer_get(export_physics_bodies, physics_joint.rigidbody1)
            body2 = shared.m3_pointer_get(export_physics_bodies, physics_joint.rigidbody2)
            if body1 and body2:
                export_physics_joints.append(physics_joint)

        self.physics_cloth_constraint_handle_to_volumes = {}
        # TODO assert that any given object is only used once in physics cloths.
        # TODO assert that the objects vertex group name sets match.
        for physics_cloth in ob.m3_cloths:
            if physics_cloth.m3_export:
                if physics_cloth.mesh_object and physics_cloth.simulator_object:
                    self.export_required_regions.add(physics_cloth.mesh_object)
                    self.export_required_regions.add(physics_cloth.simulator_object)
                    export_physics_cloths.append(physics_cloth)

                    constraint_set = shared.m3_pointer_get(ob.m3_clothconstraintsets, physics_cloth.constraint_set)
                    valid_volumes = []
                    for constraint in constraint_set.constraints:
                        bone = shared.m3_pointer_get(ob.data.bones, constraint.bone)
                        if constraint.m3_export and bone:
                            self.export_required_bones.add(bone)
                            valid_volumes.append(constraint)
                    if len(valid_volumes):
                        self.physics_cloth_constraint_handle_to_volumes[constraint_set.bl_handle] = valid_volumes

        self.export_ik_joint_bones = []
        for ik_joint in ob.m3_ikjoints:
            if not ik_joint.m3_export:
                continue
            bone = shared.m3_pointer_get(ob.data.bones, ik_joint.bone)
            if bone:
                bone_parent = bone
                for ii in range(0, ik_joint.joint_length):
                    if bone_parent.parent:
                        bone_parent = bone_parent.parent if bone_parent else bone_parent
                    else:
                        pass  # TODO warning that joint length is invalid
                        # ???? warn if ik joints have any collisions?
                if bone_parent != bone:
                    export_ik_joints.append(ik_joint)
                    self.export_ik_joint_bones.append([bone, bone_parent])
                    self.export_required_bones.add(bone)
                    self.export_required_bones.add(bone_parent)

        self.export_turret_data = []
        # TODO assert that for each group ID, only one main bone exists
        for turret in ob.m3_turrets:
            if not turret.m3_export:
                continue
            turret_parts = []
            for part in turret.parts:
                part_bone = shared.m3_pointer_get(ob.data.bones, part.bone)
                if part_bone:  # TODO warning if parts have invalid bones
                    self.export_required_bones.add(part_bone)
                    turret_parts.append([part, part_bone])
            export_turrets.append(turret)
            self.export_turret_data.append(turret_parts)

        # TODO warning if hittest bone is none
        hittest_bone = shared.m3_pointer_get(ob.data.bones, ob.m3_hittest_tight.bone)
        if hittest_bone:
            self.export_required_bones.add(hittest_bone)

        self.attachment_bones = []
        for attachment in export_attachment_points:
            attachment_point_bone = shared.m3_pointer_get(ob.data.bones, attachment.bone)
            for volume in attachment.volumes:
                volume_bone = shared.m3_pointer_get(ob.data.bones, volume.bone)
                if volume_bone:
                    self.export_required_bones.add(volume_bone)
                    export_attachment_volumes.append(volume)
                    self.attachment_bones.append([attachment_point_bone, volume_bone])

        self.export_regions = []
        for child in ob.children:
            if child.type == 'MESH' and (child.m3_mesh_export or child in self.export_required_regions):
                me = child.data
                me.calc_loop_triangles()

                if len(me.loop_triangles) > 0:
                    self.export_regions.append(child)

                    valid_mesh_batches = 0
                    for mesh_batch in child.m3_mesh_batches:
                        matref = shared.m3_pointer_get(ob.m3_materialrefs, mesh_batch.material)
                        if matref:
                            self.export_required_material_references.add(matref)
                            valid_mesh_batches += 1

                    assert valid_mesh_batches != 0
                    # TODO improve invalidation so that a list of all warnings and exceptions can be made

                    for vertex_group in child.vertex_groups:
                        group_bone = ob.data.bones.get(vertex_group.name)
                        if group_bone:
                            self.export_required_bones.add(group_bone)
                            self.skinned_bones.append(group_bone)

                    self.uv_count = max(self.uv_count, len(me.uv_layers))

        def export_bone_bool(bone):
            result = False
            if not bone.m3_export_cull:
                result = True
            elif bone in self.export_required_bones:
                result = True

            if result is True:
                assert bone.use_inherit_rotation and bone.use_inherit_scale

            return result

        self.bones = []
        # TODO see if this can be optimized. all these loops will be expensive for large skeletons.
        for bone in ob.data.bones:
            if export_bone_bool(bone):
                self.bones.append(bone)
                continue

            for child_bone in bone.children_recursive:
                if export_bone_bool(child_bone):
                    self.bones.append(bone)
                    break

        self.billboard_bones = []
        # billboards will not require bones, instead the billboard will be culled if the bone is not required
        for billboard in ob.m3_billboards:
            billboard_bone = shared.m3_pointer_get(ob.data.bones, billboard.bone)
            if billboard.m3_export and billboard_bone and billboard_bone in self.bones and billboard_bone not in billboard_bones:
                self.billboard_bones.append(billboard_bone)
                export_billboards.append[billboard]

        material_versions = {
            1: ob.m3_materials_standard_version,
            2: 4,
            3: 2,
            4: 0,
            5: 0,
            7: 0,
            8: 0,
            9: 0,
            10: ob.m3_materials_reflection_version,
            11: 3,
            12: 1,
        }

        # TODO warning if meshes and particles have materials or layers in common
        # TODO warning if layers have rtt channel collision, also only to be used in standard material

        self.bone_name_indices = {bone.name: ii for ii, bone in enumerate(self.bones)}
        self.bone_to_correction_matrices = {}
        self.bone_to_iref = {}
        self.bone_to_inv_iref = {}
        self.bone_to_abs_pose_matrix = {}
        self.bone_bounding_cos = None  # defined later

        self.matref_handle_indices = {}
        for matref in ob.m3_materialrefs:
            if matref in self.export_required_material_references:
                self.matref_handle_indices[matref.bl_handle] = len(self.matref_handle_indices.keys())

        # place armature in the default pose so that bones are in their default pose
        anim_set(None, self.scene, self.view_layer, self.ob)
        self.scene.frame_set(0)
        # self.view_layer.update()

        self.depsgraph = bpy.context.evaluated_depsgraph_get()

        model_section = self.m3.section_for_reference(self.m3[0][0], 'model', version=ob.m3_model_version)
        model = model_section.content_add()

        model_name_section = self.m3.section_for_reference(model, 'model_name')
        model_name_section.content_from_bytes(os.path.basename(filename))

        self.bounds_min = mathutils.Vector((self.ob.m3_bounds.left, self.ob.m3_bounds.back, self.ob.m3_bounds.bottom))
        self.bounds_max = mathutils.Vector((self.ob.m3_bounds.right, self.ob.m3_bounds.front, self.ob.m3_bounds.top))
        model.boundings = to_m3_bnds((self.bounds_min, self.bounds_max))

        self.create_sequences(model, export_sequences)
        self.create_bones(model)
        self.create_division(model, self.export_regions, regn_version=ob.m3_mesh_version)  # TODO create dummy region if 1 and only region has multiple batches
        self.create_attachment_points(model, export_attachment_points)  # TODO should exclude attachments with same bone as other attachments
        self.create_lights(model, export_lights)
        self.create_shadow_boxes(model, export_shadow_boxes)
        self.create_cameras(model, export_cameras)
        self.create_materials(model, export_material_references, material_versions)  # TODO test volume, volume noise and stb material types
        self.create_particle_systems(model, export_particle_systems, export_particle_copies, version=ob.m3_particle_systems_version)
        self.create_ribbons(model, export_ribbons, export_ribbon_splines, version=ob.m3_ribbons_version)
        self.create_projections(model, export_projections)
        self.create_forces(model, export_forces)
        self.create_warps(model, export_warps)
        self.create_physics_bodies(model, export_physics_bodies, body_version=ob.m3_rigidbodies_version, shape_version=ob.m3_physicsshapes_version)
        self.create_physics_joints(model, export_physics_joints)
        self.create_physics_cloths(model, export_physics_cloths, version=ob.m3_cloths_version)  # TODO simulation rigging
        self.create_ik_joints(model, export_ik_joints)
        self.create_turrets(model, export_turrets, part_version=ob.m3_turrets_part_version)
        self.create_irefs(model)
        self.create_hittests(model, export_hittests)
        self.create_attachment_volumes(model, export_attachment_volumes)
        self.create_billboards(model, export_billboards)
        # ???? self.create_tmd_data(model, export_tmd_data)

        self.finalize_anim_data(model)  # TODO EVNT export

        self.m3.resolve()
        self.m3.validate()
        self.m3.to_index()

        # place armature back into the pose that it was before
        # TODO account for the possibility that the user turned off the auto action selection
        anim_set(self.ob.m3_animations[self.ob.m3_animations_index], self.scene, self.view_layer, self.ob)

        return self.m3

    def create_sequences(self, model, anim_groups):
        if not anim_groups:
            return

        seq_section = self.m3.section_for_reference(model, 'sequences', version=2)
        stc_section = self.m3.section_for_reference(model, 'sequence_transformation_collections', version=4, pos=None)
        self.stc_section = stc_section
        stc_name_sections = []
        stg_section = self.m3.section_for_reference(model, 'sequence_transformation_groups', version=0, pos=None)
        stg_indices_sections = []

        for anim_group in anim_groups:
            m3_seq = seq_section.content_add()
            m3_seq_name_section = self.m3.section_for_reference(m3_seq, 'name')
            m3_seq_name_section.content_from_bytes(anim_group.name)

            processor = M3OutputProcessor(self, anim_group, m3_seq)
            io_shared.io_anim_group(processor)

            m3_seq.anim_ms_start = to_m3_ms(anim_group.frame_start)
            m3_seq.anim_ms_end = to_m3_ms(anim_group.frame_end)

            m3_stg = stg_section.content_add()
            m3_seq_name_section.references.append(m3_stg.name)
            m3_stg_col_indices_section = self.m3.section_for_reference(m3_stg, 'stc_indices', pos=None)
            stg_indices_sections.append(m3_stg_col_indices_section)

            for anim in anim_group.animations:
                anim = shared.m3_pointer_get(self.ob.m3_animations, anim.bl_handle)
                if anim not in self.exported_anims:
                    # TODO ensure stc names are unique
                    self.exported_anims.append(anim)

                    m3_stc = stc_section.content_add()
                    m3_stc_name_section = self.m3.section_for_reference(m3_stc, 'name', pos=None)
                    m3_stc_name_section.content_from_bytes(anim.name)
                    self.stc_to_name_section[m3_stc] = m3_stc_name_section
                    stc_name_sections.append(m3_stc_name_section)

                    m3_stc.concurrent = int(anim.concurrent)
                    m3_stc.priority = anim.priority

                    self.action_to_anim_data[anim.action] = {section_name: {} for section_name in ANIM_DATA_SECTION_NAMES}
                    self.action_to_sdmb_user[anim.action] = False

                    if not self.action_to_stc.get(anim.action):
                        self.action_to_stc[anim.action] = [m3_stc]
                    else:
                        self.action_to_stc[anim.action].append(m3_stc)

                    if not self.action_frame_range.get(anim.action):
                        self.action_frame_range[anim.action] = [anim_group.frame_start, anim_group.frame_end]
                    else:
                        self.action_frame_range[anim.action][0] = min(self.action_frame_range[anim.action][0], anim_group.frame_start)
                        self.action_frame_range[anim.action][1] = max(self.action_frame_range[anim.action][1], anim_group.frame_end)

                m3_stg_col_indices_section.content_add(self.exported_anims.index(anim))

        # used to position other sections
        self.stg_last_indice_section = stg_indices_sections[-1]

        self.m3.append(stc_section)

        for stc_name_section in stc_name_sections:
            self.m3.append(stc_name_section)

        self.m3.append(stg_section)

        for stg_indices_section in stg_indices_sections:
            self.m3.append(stg_indices_section)

    def finalize_anim_data(self, model):
        sts_section = self.m3.section_for_reference(model, 'sts', pos=None)  # position later
        ids_sections = []  # for collecting anim_id sections to position later

        # do not calculate bounds if action which has no bone animation data
        for action, user in self.action_to_sdmb_user.items():
            if not user:
                continue

            self.action_to_anim_data[action]['SDMB'][BNDS_ANIM_ID] = [[], []]
            bnds_data = self.action_to_anim_data[action]['SDMB'][BNDS_ANIM_ID]

            frame_list = list(self.action_abs_pose_matrices[action].keys())
            init_frame = frame_list.pop(0)

            prev_min, prev_max = bounding_vectors_from_bones(self.bone_bounding_cos, self.action_abs_pose_matrices[action][init_frame])

            bnds_data[0].append(init_frame)
            bnds_data[1].append(to_m3_bnds((prev_min, prev_max)))

            for frame in frame_list[0::2]:
                bnds_min, bnds_max = bounding_vectors_from_bones(self.bone_bounding_cos, self.action_abs_pose_matrices[action][frame])
                if (prev_min - bnds_min).length >= 0.025 or (prev_max - bnds_max).length >= 0.025:
                    bnds_data[0].append(frame)
                    bnds_data[1].append(to_m3_bnds((bnds_min, bnds_max)))
                    prev_min, prev_max = bnds_min, bnds_max

        for action, stc_list in self.action_to_stc.items():

            data_names_with_data = 0
            for section_data_name in ANIM_DATA_SECTION_NAMES:
                if len(self.action_to_anim_data[action][section_data_name]):
                    data_names_with_data += 1

            if not data_names_with_data:
                continue

            section_pos = self.m3.index(self.stc_to_name_section[stc_list[-1]]) + 1

            ids_section = self.m3.section_for_reference(stc_list[0], 'anim_ids', pos=None)  # position later
            ids_sections.append(ids_section)
            refs_section = self.m3.section_for_reference(stc_list[0], 'anim_refs', pos=section_pos)
            section_pos += 1

            for data_type_ii, section_data_name in enumerate(ANIM_DATA_SECTION_NAMES):

                if not len(self.action_to_anim_data[action][section_data_name]):
                    continue

                action_data = self.action_to_anim_data[action][section_data_name]
                attr_name = section_data_name.lower()

                data_section = self.m3.section_for_reference(stc_list[0], attr_name, pos=section_pos)
                section_pos += 1

                for ii, id_num in enumerate(action_data):
                    data_head = data_section.content_add()

                    ids_section.content_add(id_num)
                    refs_section.content_add((data_type_ii << 16) + ii)

                    if section_data_name == 'SDEV':
                        data_head.flags = 1

                    data_head.fend = to_m3_ms(action_data[id_num][0][-1])

                    frames_section = self.m3.section_for_reference(data_head, 'frames', pos=section_pos)
                    frames_section.content_iter_add([to_m3_ms(frame) for frame in action_data[id_num][0]])
                    section_pos += 1

                    values_section = self.m3.section_for_reference(data_head, 'keys', pos=section_pos)
                    values_section.content_iter_add(action_data[id_num][1])
                    section_pos += 1

                if len(stc_list) > 1:
                    for stc in stc_list[1:]:
                        data_section.references.append(getattr(stc, attr_name))

            if len(stc_list) > 1:
                ids_section.references.append(getattr(stc, 'anim_ids'))
                refs_section.references.append(getattr(stc, 'anim_refs'))

            for stc in stc_list:
                sts = sts_section.content_add()
                ids_section.references.append(getattr(sts, 'anim_ids'))

        # offseting the position the given amount assuming model unknown reference is unused
        section_pos = self.m3.index(self.stg_last_indice_section) + 1
        self.m3.insert(section_pos, sts_section)
        section_pos += 1
        for ids_section in ids_sections:
            self.m3.insert(section_pos, ids_section)
            section_pos += 1

    def create_bones(self, model):
        if not self.bones:
            return

        bone_section = self.m3.section_for_reference(model, 'bones', version=1)
        m3_bone_defaults = {}

        for bone in self.bones:
            pose_bone = self.ob.pose.bones.get(bone.name)
            m3_bone = bone_section.content_add()
            m3_bone_name_section = self.m3.section_for_reference(m3_bone, 'name')
            m3_bone_name_section.content_from_bytes(bone.name)
            m3_bone.flags = 0
            m3_bone.bit_set('flags', 'real', True)
            m3_bone.bit_set('flags', 'skinned', bone in self.skinned_bones)
            m3_bone.bit_set('flags', 'unknown0x4000', not pose_bone.m3_batching)
            m3_bone.bit_set('flags', 'unknown0x8000', not pose_bone.m3_batching)
            m3_bone.location = self.init_anim_ref_vec3()
            m3_bone.rotation = self.init_anim_ref_quat()
            m3_bone.rotation.null.w = 1.0
            m3_bone.scale = self.init_anim_ref_vec3()
            m3_bone.scale.null = to_m3_vec3((1.0, 1.0, 1.0))
            m3_bone.batching = self.init_anim_ref_uint32(int(pose_bone.m3_batching))
            m3_bone.batching.null = 1

            bone_matrix_local = bone.matrix_local.copy()
            rest_matrix = bone_matrix_local @ io_shared.rot_fix_matrix_transpose
            rest_matrix = io_shared.bind_scale_to_matrix(bone.m3_bind_scale) @ rest_matrix.inverted()
            self.bone_to_iref[bone] = rest_matrix
            self.bone_to_inv_iref[bone] = bone_matrix_local.inverted()

            bind_scale_inv = mathutils.Vector((1.0 / bone.m3_bind_scale[ii] for ii in range(3)))
            bind_scale_inv_matrix = io_shared.bind_scale_to_matrix(bind_scale_inv)

            if bone.parent is not None:
                m3_bone.parent = self.bone_name_indices[bone.parent.name]
                parent_bind_matrix = io_shared.bind_scale_to_matrix(bone.parent.m3_bind_scale)
                parent_inv_iref = self.bone_to_inv_iref[bone.parent]
                left_correction_matrix = parent_bind_matrix @ io_shared.rot_fix_matrix @ parent_inv_iref @ bone.matrix_local
            else:
                m3_bone.parent = -1
                left_correction_matrix = bone.matrix_local

            right_correction_matrix = io_shared.rot_fix_matrix_transpose @ bind_scale_inv_matrix

            self.bone_to_correction_matrices[bone] = (left_correction_matrix, right_correction_matrix)

            pose_bone = self.ob.pose.bones[bone.name]
            pose_matrix = self.ob.convert_space(pose_bone=pose_bone, matrix=pose_bone.matrix, from_space='POSE', to_space='LOCAL')

            m3_pose_matrix = left_correction_matrix @ pose_matrix @ right_correction_matrix

            m3_bone_loc, m3_bone_rot, m3_bone_scl = m3_bone_defaults[m3_bone] = m3_pose_matrix.decompose()
            m3_bone.scale.default = to_m3_vec3(m3_bone_scl)
            m3_bone.rotation.default = to_m3_quat(m3_bone_rot)
            m3_bone.location.default = to_m3_vec3(m3_bone_loc)

            if bone.parent is not None:
                abs_pose_matrix = self.bone_to_abs_pose_matrix[bone.parent] @ self.bone_to_inv_iref[bone.parent].inverted() @ m3_pose_matrix
            else:
                abs_pose_matrix = m3_pose_matrix

            self.bone_to_abs_pose_matrix[bone] = abs_pose_matrix @ rest_matrix

        calc_actions = []
        for anim in self.exported_anims:
            if anim.action in calc_actions:
                continue
            calc_actions.append(anim.action)

            # setting scene properties is extremely slow
            # maximum optimization would keep calls to anim_set and frame_set to an absolute minimum
            anim_set(anim, self.scene, self.view_layer, self.ob)

            # jog animation frame so that complicated pose calculations are completed before proceeding
            # TODO make an export option to step through a given number of previous frames to allow completion of timed calculations (ie wigglebone)
            self.scene.frame_set(0)

            frames_range = range(self.action_frame_range[anim.action][0], self.action_frame_range[anim.action][1] + 1)
            frames = list(frames_range)

            bone_to_pose_matrices = {bone: [] for bone in self.bones}
            frame_to_bone_abs_pose_matrix = {frame: {} for frame in frames}
            self.action_abs_pose_matrices[anim.action] = frame_to_bone_abs_pose_matrix

            for frame in frames:
                self.scene.frame_set(frame)

                for bone in self.bones:
                    pose_bone = self.ob.pose.bones[bone.name]
                    bone_to_pose_matrices[bone].append(self.ob.convert_space(pose_bone=pose_bone, matrix=pose_bone.matrix, from_space='POSE', to_space='LOCAL'))

            bone_m3_pose_matrices = {bone: [] for bone in self.bones}

            for ii, bone in enumerate(self.bones):
                m3_bone = bone_section[ii]
                left_correction_matrix, right_correction_matrix = self.bone_to_correction_matrices[bone]

                anim_locs = []
                anim_rots = []
                anim_scls = []

                frame_start = self.action_frame_range[anim.action][0]

                for pose_matrix in bone_to_pose_matrices[bone]:
                    m3_pose_matrix = left_correction_matrix @ pose_matrix @ right_correction_matrix
                    # storing these and operating on them later if boundings are needed
                    bone_m3_pose_matrices[bone].append(m3_pose_matrix)
                    m3_pose = m3_pose_matrix.decompose()
                    anim_locs.append(m3_pose[0])
                    anim_rots.append(m3_pose[1])
                    anim_scls.append(m3_pose[2])

                if vec_list_contains_not_only(anim_locs, m3_bone_defaults[m3_bone][0]):
                    keys, values = simplify_anim_data_with_interp(frames, anim_locs, vec_interp, vec_equal)
                    self.action_to_anim_data[anim.action]['SD3V'][m3_bone.location.header.id] = (keys, [to_m3_vec3(val) for val in values])
                    self.action_to_sdmb_user[anim.action] = True
                    m3_bone.bit_set('flags', 'animated', True)

                if quat_list_contains_not_only(anim_rots, m3_bone_defaults[m3_bone][1]):
                    quats_compatibility(anim_rots)
                    keys, values = simplify_anim_data_with_interp(frames, anim_rots, quat_interp, quat_equal)
                    self.action_to_anim_data[anim.action]['SD4Q'][m3_bone.rotation.header.id] = (keys, [to_m3_quat(val) for val in values])
                    self.action_to_sdmb_user[anim.action] = True
                    m3_bone.bit_set('flags', 'animated', True)

                if vec_list_contains_not_only(anim_scls, m3_bone_defaults[m3_bone][2]):
                    keys, values = simplify_anim_data_with_interp(frames, anim_scls, vec_interp, vec_equal)
                    self.action_to_anim_data[anim.action]['SD3V'][m3_bone.scale.header.id] = (keys, [to_m3_vec3(val) for val in values])
                    self.action_to_sdmb_user[anim.action] = True
                    m3_bone.bit_set('flags', 'animated', True)

                # export animated batching property
                pose_bone = self.ob.pose.bones.get(bone.name)
                m3_batching_fcurve = anim.action.fcurves.find(pose_bone.path_from_id('m3_batching'))
                m3_batching_frames = get_fcurve_anim_frames(m3_batching_fcurve)

                if m3_batching_frames:
                    m3_bone.bit_set('flags', 'unknown0x4000', True)
                    m3_bone.bit_set('flags', 'unknown0x8000', True)
                    m3_batching_values = [int(m3_batching_fcurve.evaluate(frame)) for frame in m3_batching_frames]
                    self.action_to_anim_data[anim.action]['SDFG'][m3_bone.batching.header.id] = (m3_batching_frames, m3_batching_values)

            # calculate absolute pose matrices only if needed for boundings
            if self.action_to_sdmb_user[anim.action]:
                for bone in self.bones:
                    for jj, m3_pose_matrix in enumerate(bone_m3_pose_matrices[bone]):
                        if bone.parent is not None:
                            parent_abs_pose_matrix = frame_to_bone_abs_pose_matrix[jj + frame_start][bone.parent]
                            abs_bone_matrix = parent_abs_pose_matrix @ self.bone_to_inv_iref[bone.parent].inverted() @ m3_pose_matrix
                        else:
                            abs_bone_matrix = m3_pose_matrix @ self.bone_to_inv_iref[bone].inverted()

                        frame_to_bone_abs_pose_matrix[jj + frame_start][bone] = abs_bone_matrix

    def create_division(self, model, mesh_objects, regn_version):

        model.bit_set('flags', 'has_mesh', len(mesh_objects) > 0)

        if not len(mesh_objects):
            model.skin_bone_count = 0
            div_section = self.m3.section_for_reference(model, 'divisions', version=2)
            div = div_section.content_add()

            msec_section = self.m3.section_for_reference(div, 'msec', version=1)
            msec = msec_section.content_add()
            msec.bounding = self.init_anim_ref_bnds((self.bounds_min, self.bounds_max))
            return

        model.skin_bone_count = sorted([self.bone_name_indices[bone.name] for bone in self.skinned_bones])[-1] + 1
        model.vertex_flags = 0x182007d

        model.bit_set('vertex_flags', 'use_uv0', self.uv_count > 1)
        model.bit_set('vertex_flags', 'use_uv1', self.uv_count > 2)
        model.bit_set('vertex_flags', 'use_uv2', self.uv_count > 3)
        model.bit_set('vertex_flags', 'use_uv3', self.uv_count > 4)

        vertex_rgba = False
        for ob in mesh_objects:
            me = ob.data

            for vertex_col in me.vertex_colors:
                if vertex_col.name in ['m3color', 'm3alpha']:
                    vertex_rgba = True

        model.bit_set('vertex_flags', 'has_vertex_colors', vertex_rgba)

        m3_vertex_desc = io_m3.structures['VertexFormat' + hex(model.vertex_flags)].get_version(0)

        vertex_section = self.m3.section_for_reference(model, 'vertices')

        div_section = self.m3.section_for_reference(model, 'divisions', version=2)
        div = div_section.content_add()

        face_section = self.m3.section_for_reference(div, 'faces')

        region_section = self.m3.section_for_reference(div, 'regions', version=regn_version)
        batch_section = self.m3.section_for_reference(div, 'batches', version=1)

        m3_vertices = []
        m3_faces = []
        m3_lookup = []

        bone_boundings = {bone: [*(float('inf'),) * 3, *(-float('inf'),) * 3] for bone in self.bones}

        for ob in mesh_objects:
            bm = bmesh.new(use_operators=True)
            bm.from_object(ob, self.depsgraph)
            bmesh.ops.triangulate(bm, faces=bm.faces)

            export_rgba = False

            layer_deform = bm.verts.layers.deform.get('m3lookup')
            layer_color = bm.loops.layers.color.get('m3color')
            layer_alpha = bm.loops.layers.color.get('m3alpha')
            layers_uv = bm.loops.layers.uv.values()
            layer_tan = layers_uv[0]
            layer_sign = bm.faces.layers.int.get('m3sign') or bm.verts.layers.int.new('m3sign')

            first_vertex_index = len(m3_vertices)
            first_face_index = len(m3_faces)
            first_lookup_index = len(m3_lookup)
            vertex_lookups_used = 0

            region_vertices = []
            region_faces = []
            region_lookup = []
            group_to_lookup_ii = {}
            for ii, group in enumerate(ob.vertex_groups):
                if self.bone_name_indices.get(group.name) is not None:
                    group_to_lookup_ii[ii] = len(region_lookup)
                    region_lookup.append(self.bone_name_indices[group.name])

            region_vert_id_to_vert = {}
            region_vert_count = 0

            for face in bm.faces:
                l0, l1, l2 = ((L.vert.co, L[layer_tan].uv[1]) for L in face.loops)
                tan = ((l2[1] - l0[1]) * (l1[0] - l0[0]) - (l1[1] - l0[1]) * (l2[0] - l0[0])).normalized()

                for loop in face.loops:
                    co = ob.matrix_local @ loop.vert.co
                    m3_vert = m3_vertex_desc.instance()
                    m3_vert.pos = to_m3_vec3(co)

                    # only count groups which have a lookup match, sort by weight and then limit to a length of 4
                    deformations = []
                    for deformation in loop.vert[layer_deform].items():
                        lookup_ii = group_to_lookup_ii.get(deformation[0])
                        if lookup_ii is not None and deformation[1]:
                            deformations.append([lookup_ii, deformation[1]])

                            bbl = bone_boundings[self.bones[region_lookup[lookup_ii]]]
                            for ii in range(3):
                                bbl[ii] = min(bbl[ii], co[ii])
                                bbl[ii + 3] = max(bbl[ii + 3], co[ii])

                    deformations.sort(key=lambda x: x[1])
                    deformations = deformations[0:max(4, len(deformations))]

                    if len(deformations):
                        # normalize the weights
                        sum_weight = 0
                        for index, weight in deformations:
                            sum_weight += weight

                        for ii in range(len(deformations)):
                            lookup, weight = deformations[ii]
                            setattr(m3_vert, 'lookup' + str(ii), lookup)
                            setattr(m3_vert, 'weight' + str(ii), round(weight / sum_weight * 255))

                    for ii in range(0, 4):
                        uv_layer = layers_uv[ii] if ii < len(layers_uv) else None
                        setattr(m3_vert, 'uv' + str(ii), to_m3_uv(loop[uv_layer].uv) if uv_layer else (0, 0))

                    if export_rgba:
                        m3_vert.col = to_bl_color((*loop[layer_color][0:3], (loop[layer_alpha][0] + loop[layer_alpha][1] + loop[layer_alpha][2]) / 3))

                    m3_vert.normal = to_m3_vec3_f8(loop.vert.normal)

                    if face[layer_sign] == 1:
                        m3_vert.sign = 1.0
                        m3_vert.tan = to_m3_vec3_f8(-tan)
                    else:
                        m3_vert.sign = -1.0
                        m3_vert.tan = to_m3_vec3_f8(tan)

                    id_list = [
                        m3_vert.pos.x, m3_vert.pos.y, m3_vert.pos.z, m3_vert.lookup0, m3_vert.lookup1, m3_vert.lookup2, m3_vert.lookup3, m3_vert.sign,
                        m3_vert.weight0, m3_vert.weight1, m3_vert.weight2, m3_vert.weight3, m3_vert.normal.x, m3_vert.normal.y, m3_vert.normal.z,
                    ]

                    if export_rgba:
                        id_list.extend((m3_vert.col.r, m3_vert.col.g, m3_vert.col.b, m3_vert.col.a))

                    for ii in range(len(layers_uv)):
                        uv = getattr(m3_vert, 'uv' + str(ii))
                        id_list.extend((uv.x, uv.y))

                    id_tuple = tuple(id_list)
                    id_index = region_vert_id_to_vert.get(id_tuple)
                    if id_index is None:
                        id_index = region_vert_count
                        region_vert_id_to_vert[id_tuple] = id_index

                        # TODO handle static vertex here

                        vertex_lookups_used = max(vertex_lookups_used, len(deformations))

                        m3_vertex_desc.instance_validate(m3_vert, 'vertex')
                        region_vertices.append(m3_vert)
                        region_vert_count += 1

                    region_faces.append(id_index)

            m3_vertices.extend(region_vertices)
            m3_faces.extend(region_faces)
            m3_lookup.extend(region_lookup)

            # TODO mesh flags for versions 4+
            region = region_section.content_add()
            region.first_vertex_index = first_vertex_index
            region.vertex_count = len(region_vertices)
            region.first_face_index = first_face_index
            region.face_count = len(region_faces)
            region.bone_count = len(region_lookup)
            region.first_bone_lookup_index = first_lookup_index
            region.bone_lookup_count = len(region_lookup)
            region.vertex_lookups_used = vertex_lookups_used
            region.root_bone = region_lookup[0]

            for batch in ob.m3_mesh_batches:
                m3_batch = batch_section.content_add()
                m3_batch.region_index = len(region_section) - 1
                m3_batch.material_reference_index = self.matref_handle_indices[batch.material]

                bone = shared.m3_pointer_get(self.ob.data.bones, batch.bone)
                m3_batch.bone = self.bone_name_indices[bone.name] if bone else -1

        self.bone_bounding_cos = {bone: [] for bone in self.bones}

        for bone, arr in bone_boundings.items():
            self.bone_bounding_cos[bone].append(mathutils.Vector((arr[0], arr[1], arr[2])))
            self.bone_bounding_cos[bone].append(mathutils.Vector((arr[0], arr[4], arr[2])))
            self.bone_bounding_cos[bone].append(mathutils.Vector((arr[0], arr[4], arr[5])))
            self.bone_bounding_cos[bone].append(mathutils.Vector((arr[0], arr[1], arr[5])))
            self.bone_bounding_cos[bone].append(mathutils.Vector((arr[3], arr[4], arr[2])))
            self.bone_bounding_cos[bone].append(mathutils.Vector((arr[3], arr[1], arr[2])))
            self.bone_bounding_cos[bone].append(mathutils.Vector((arr[3], arr[4], arr[5])))
            self.bone_bounding_cos[bone].append(mathutils.Vector((arr[3], arr[1], arr[5])))

        self.region_section = region_section

        msec_section = self.m3.section_for_reference(div, 'msec', version=1)
        msec = msec_section.content_add()
        msec.bounding = self.init_anim_ref_bnds(bounding_vectors_from_bones(self.bone_bounding_cos, self.bone_to_abs_pose_matrix))

        vertex_section.content_from_bytes(m3_vertex_desc.instances_to_bytes(m3_vertices))
        face_section.content_iter_add(m3_faces)
        bone_lookup_section = self.m3.section_for_reference(model, 'bone_lookup')
        bone_lookup_section.content_iter_add(m3_lookup)

    def create_attachment_points(self, model, attachments):
        if not attachments:
            return

        attachment_point_section = self.m3.section_for_reference(model, 'attachment_points', version=1)

        # manually add into section list *after* name sections are added to conform with original exporting conventions
        attachment_point_addon_section = self.m3.section_for_reference(model, 'attachment_points_addon', pos=None)

        for attachment in attachments:
            attachment_bone = shared.m3_pointer_get(self.ob.data.bones, attachment.bone)

            m3_attachment = attachment_point_section.content_add()
            m3_attachment_name_section = self.m3.section_for_reference(m3_attachment, 'name')
            m3_attachment_name_section.content_from_bytes(('Ref_' if not attachment.name.startswith('Ref_') else '') + attachment.name)
            m3_attachment.bone = self.bone_name_indices[attachment_bone.name]
            attachment_point_addon_section.content_add(0xffff)
        # add volumes later so that sections are in order of the modl data

        self.m3.append(attachment_point_addon_section)

    def create_lights(self, model, lights):
        if not lights:
            return

        light_section = self.m3.section_for_reference(model, 'lights', version=7)

        for light in lights:
            light_bone = shared.m3_pointer_get(self.ob.data.bones, light.bone)

            m3_light = light_section.content_add()
            m3_light.bone = self.bone_name_indices[light_bone.name]
            processor = M3OutputProcessor(self, light, m3_light)
            io_shared.io_light(processor)

    def create_shadow_boxes(self, model, shadow_boxes):
        if not shadow_boxes and int(self.ob.m3_model_version) >= 21:
            return

        shadow_box_section = self.m3.section_for_reference(model, 'shadow_boxes', version=3)

        for shadow_box in shadow_boxes:
            shadow_box_bone = shared.m3_pointer_get(self.ob.data.bones, shadow_box.bone)
            m3_shadow_box = shadow_box_section.content_add()
            m3_shadow_box.bone = self.bone_name_indices[shadow_box_bone.name]
            processor = M3OutputProcessor(self, shadow_box, m3_shadow_box)
            io_shared.io_shadow_box(processor)

    def create_cameras(self, model, cameras):
        if not cameras:
            return

        camera_section = self.m3.section_for_reference(model, 'cameras', version=3)

        for camera in cameras:
            camera_bone = shared.m3_pointer_get(self.ob.data.bones, camera.bone)
            m3_camera = camera_section.content_add()
            m3_camera_name_section = self.m3.section_for_reference(m3_camera, 'name')
            m3_camera_name_section.content_from_bytes(camera.name)
            m3_camera.bone = self.bone_name_indices[camera_bone.name]
            processor = M3OutputProcessor(self, camera, m3_camera)
            io_shared.io_camera(processor)

        cameras_addon_section = self.m3.section_for_reference(model, 'camera_addons')
        cameras_addon_section.content_iter_add([0xffff for camera in cameras])

    def create_materials(self, model, matrefs, versions):
        if not matrefs:
            return

        matref_section = self.m3.section_for_reference(model, 'material_references')

        layer_desc = io_m3.structures['LAYR'].get_version(self.ob.m3_materiallayers_version)
        # manually add into section list if referenced
        null_layer_section = io_m3.Section(index_entry=None, struct_desc=layer_desc, references=[], content=[])
        null_layer_section.content_add()

        matrefs_typed = {ii: [] for ii in range(0, 13)}
        for matref in matrefs:
            m3_matref = matref_section.content_add()
            m3_matref.type = io_shared.material_collections.index(matref.mat_type)
            m3_matref.material_index = len(matrefs_typed[m3_matref.type])
            matrefs_typed[m3_matref.type].append(matref)

        handle_to_layer_section = {}
        for type_ii, matrefs in matrefs_typed.items():
            if not matrefs:
                continue
            mat_section = self.m3.section_for_reference(model, io_shared.material_type_to_model_reference[type_ii], version=versions[type_ii])
            mat_collection = getattr(self.ob, 'm3_' + io_shared.material_type_to_model_reference[type_ii])
            for matref in matrefs:
                mat = shared.m3_pointer_get(mat_collection, matref.mat_handle)
                m3_mat = mat_section.content_add()
                m3_mat_name_section = self.m3.section_for_reference(m3_mat, 'name')
                m3_mat_name_section.content_from_bytes(matref.name)
                processor = M3OutputProcessor(self, mat, m3_mat)
                io_shared.material_type_io_method[type_ii](processor)

                for layer_name in io_shared.material_type_to_layers[type_ii]:
                    layer_name_full = 'layer_' + layer_name
                    mat_layer_handle = getattr(mat, layer_name_full)

                    if not hasattr(m3_mat, layer_name_full):
                        continue

                    m3_layer_ref = getattr(m3_mat, layer_name_full)

                    layer = shared.m3_pointer_get(self.ob.m3_materiallayers, getattr(mat, layer_name_full))

                    if not layer or (layer.color_type == 'BITMAP' and not layer.color_bitmap):
                        null_layer_section.references.append(m3_layer_ref)
                    else:

                        if layer.video_channel != 'NONE':
                            # TODO warn if rtt channel collision (assigning to true while already true)
                            m3_mat.bit_set('rtt_channels_used', 'channel' + layer.video_channel, True)

                        if mat_layer_handle in handle_to_layer_section.keys():
                            handle_to_layer_section[mat_layer_handle].references.append(m3_layer_ref)
                        else:
                            layer_section = self.m3.section_for_reference(m3_mat, layer_name_full, version=self.ob.m3_materiallayers_version)
                            m3_layer = layer_section.content_add()
                            m3_layer_bitmap_section = self.m3.section_for_reference(m3_layer, 'color_bitmap')
                            m3_layer_bitmap_section.content_from_bytes(layer.color_bitmap)
                            processor = M3OutputProcessor(self, layer, m3_layer)
                            io_shared.io_material_layer(processor)

                            m3_layer.fresnel_max_offset = layer.fresnel_max - layer.fresnel_min

                            if int(self.ob.m3_materiallayers_version) >= 25:
                                m3_layer.fresnel_inverted_mask_x = 1 - layer.fresnel_mask[0]
                                m3_layer.fresnel_inverted_mask_y = 1 - layer.fresnel_mask[1]
                                m3_layer.fresnel_inverted_mask_z = 1 - layer.fresnel_mask[2]

                            m3_layer.bit_set('flags', 'particle_uv_flipbook', m3_layer.uv_source == 6)

                            if layer.color_bitmap.endswith('.ogg'):
                                m3_layer.bit_set('flags', 'video', True)
                            else:
                                m3_layer.video_frame_rate = 0
                                m3_layer.video_frame_start = 0
                                m3_layer.video_frame_end = 0
                                m3_layer.video_mode = 0

                            m3_layer.color_brightness.null = 1.0
                            m3_layer.color_multiply.null = 1.0
                            m3_layer.color_value.null.a = 0
                            m3_layer.uv_tiling.null.x = 1.0
                            m3_layer.uv_tiling.null.y = 1.0

                            if m3_layer.video_channel == 7:  # 7 is the bl enum index for none
                                m3_layer.video_channel = -1

                            m3_layer.unknownbc0c14e5 = self.init_anim_ref_uint32(0)
                            m3_layer.unknowne740df12 = self.init_anim_ref_float(0.0)
                            m3_layer.unknown39ade219 = self.init_anim_ref_uint16(0)
                            m3_layer.unknowna4ec0796 = self.init_anim_ref_uint32(0, interpolation=1)
                            m3_layer.unknowna44bf452 = self.init_anim_ref_float(1.0)
                            m3_layer.unknowna44bf452.null = 1.0

                            m3_layer.video_play.interpolation = 1
                            m3_layer.video_restart.interpolation = 1
                            m3_layer.uv_flipbook_frame.interpolation = 1

                if type_ii == 1:  # standard material
                    m3_mat.bit_set('additional_flags', 'depth_blend_falloff', mat.depth_blend_falloff != 0.0)
                    m3_mat.bit_set('additional_flags', 'vertex_color', mat.vertex_color or matref.bl_handle in self.vertex_color_mats)
                    m3_mat.bit_set('additional_flags', 'vertex_alpha', mat.vertex_alpha or matref.bl_handle in self.vertex_alpha_mats)
                    m3_mat.bit_set('additional_flags', 'unknown0x200', True)
                elif type_ii == 3:  # composite material
                    valid_sections = []
                    for section in mat.sections:
                        matref = shared.m3_pointer_get(self.ob.m3_materialrefs, section.matref)
                        if matref:
                            valid_sections.append(section)
                    if len(valid_sections):
                        section_section = self.m3.section_for_reference(m3_mat, 'sections')
                        for section in valid_sections:
                            m3_section = section_section.content_add()
                            m3_section.material_reference_index = self.matref_handle_indices[section.matref]
                            processor = M3OutputProcessor(self, section, m3_section)
                            processor.anim_float('alpha_factor')
                elif type_ii == 11:  # lens flare material
                    if len(mat.starbursts):
                        starburst_section = self.m3.section_for_reference(m3_mat, 'starbursts', version=2)
                        for starburst in mat.starbursts:
                            m3_starburst = starburst_section.content_add()
                            processor = M3OutputProcessor(self, starburst, m3_starburst)
                            io_shared.io_starburst(processor)

        if len(null_layer_section.references):
            self.m3.append(null_layer_section)
            m3_layer = null_layer_section[0]
            m3_layer.color_brightness.null = 1.0
            m3_layer.color_multiply.null = 1.0
            m3_layer.color_value.null.a = 0
            m3_layer.uv_tiling.null.x = 1.0
            m3_layer.uv_tiling.null.y = 1.0
            m3_layer.unknownbc0c14e5 = self.init_anim_ref_uint32(0)
            m3_layer.unknowne740df12 = self.init_anim_ref_float(0.0)
            m3_layer.unknown39ade219 = self.init_anim_ref_uint16(0)
            m3_layer.unknowna4ec0796 = self.init_anim_ref_uint32(0, interpolation=1)
            m3_layer.unknowna44bf452 = self.init_anim_ref_float(1.0)
            m3_layer.unknowna44bf452.null = 1.0

    def create_particle_systems(self, model, systems, copies, version):
        if not systems:
            return

        particle_system_section = self.m3.section_for_reference(model, 'particle_systems', version=version)

        for system in systems:
            system_bone = shared.m3_pointer_get(self.ob.data.bones, system.bone)

            m3_system = particle_system_section.content_add()
            m3_system.bone = self.bone_name_indices[system_bone.name]
            m3_system.material_reference_index = self.matref_handle_indices[system.material]

            processor = M3OutputProcessor(self, system, m3_system)
            io_shared.io_particle_system(processor)

            trail_particle = shared.m3_pointer_get(systems, system.trail_particle)
            if trail_particle:
                m3_system.trail_particle = systems.index(trail_particle)

            m3_system.unknowne0bd54c8 = self.init_anim_ref_float()
            m3_system.unknowna2d44d80 = self.init_anim_ref_float()
            m3_system.unknownf8e2b3d0 = self.init_anim_ref_float()
            m3_system.unknown54f4ae30 = self.init_anim_ref_float()
            m3_system.unknown5f54fb02 = self.init_anim_ref_float()
            m3_system.unknown84d843d6 = self.init_anim_ref_float()
            m3_system.unknown9cb3dd18 = self.init_anim_ref_float()
            m3_system.unknown2e01be90 = self.init_anim_ref_float()
            m3_system.unknownf6193fc0 = self.init_anim_ref_float()
            m3_system.unknowna5e2260a = self.init_anim_ref_float()
            m3_system.unknown485f7eea = self.init_anim_ref_float()
            m3_system.unknown34b6f141 = self.init_anim_ref_float()
            m3_system.unknown89cdf966 = self.init_anim_ref_float()
            m3_system.unknown4eefdfc1 = self.init_anim_ref_float()
            m3_system.unknownab37a1d5 = self.init_anim_ref_float()
            m3_system.unknownbef7f4d3 = self.init_anim_ref_float()
            m3_system.unknownb2dbf2f3 = self.init_anim_ref_float()
            m3_system.unknown3c76d64c = self.init_anim_ref_float()
            m3_system.unknownbc151e17 = self.init_anim_ref_float()
            m3_system.unknown21ca0cea = self.init_anim_ref_float()
            m3_system.unknown1e97145f = self.init_anim_ref_float(1.0)

            if int(version) >= 17:
                m3_system.unknown22856fde = self.init_anim_ref_float()
                m3_system.unknownb35ad6e1 = self.init_anim_ref_vec2()
                m3_system.unknown686e5943 = self.init_anim_ref_vec3()
                m3_system.unknown18a90564 = self.init_anim_ref_vec2((1.0, 1.0))

                if m3_system.emit_shape == 7:
                    region_indices = set()
                    for mesh_pointer in system.emit_shape_meshes:
                        if mesh_pointer.bl_object in self.export_regions:
                            region_indices.add(self.export_regions.index(mesh_pointer.bl_object))
                    if len(region_indices):
                        region_indices_section = self.m3.section_for_reference(m3_system, 'emit_shape_regions')
                        region_indices_section.content_iter_add(region_indices)
            else:
                if m3_system.emit_shape >= 7:
                    m3_system.shape = 0  # region emission invalid if version is below 17

            if int(version) >= 22:
                m3_system.unknown8f507b52 = self.init_anim_ref_uint32()

            if m3_system.emit_shape == 6:
                if len(system.emit_shape_spline):
                    system_spline_section = self.m3.section_for_reference(m3_system, 'emit_shape_spline')
                    for point in system.emit_shape_spline:
                        m3_point = system_spline_section.content_add()
                        processor = M3OutputProcessor(self, point, m3_point)
                        processor.anim_vec3('location')

            copy_indices = []
            for ii, copy in enumerate(copies):
                for system_handle in copy.systems:
                    if system_handle.bl_handle == system.bl_handle:
                        copy_indices.append(ii)

            if len(copy_indices):
                copy_indices_section = self.m3.section_for_reference(m3_system, 'copy_indices')
                copy_indices_section.content_iter_add(copy_indices)

        if len(copies):
            particle_copy_section = self.m3.section_for_reference(model, 'particle_copies', version=0)
        for copy in copies:
            copy_bone = shared.m3_pointer_get(self.ob.data.bones, copy.bone)
            m3_copy = particle_copy_section.content_add()
            m3_copy.bone = self.bone_name_indices[copy_bone.name]
            processor = M3OutputProcessor(self, copy, m3_copy)
            io_shared.io_particle_copy(processor)

    def create_ribbons(self, model, ribbons, splines, version):
        if not ribbons:
            return

        ribbon_section = self.m3.section_for_reference(model, 'ribbons', version=version)

        handle_to_spline_sections = {}
        for ribbon in ribbons:
            ribbon_bone = shared.m3_pointer_get(self.ob.data.bones, ribbon.bone)

            m3_ribbon = ribbon_section.content_add()
            m3_ribbon.bone = self.bone_name_indices[ribbon_bone.name]
            m3_ribbon.material_reference_index = self.matref_handle_indices[ribbon.material]
            processor = M3OutputProcessor(self, ribbon, m3_ribbon)
            io_shared.io_ribbon(processor)

            m3_ribbon.unknown75e0b576 = self.init_anim_ref_float()
            m3_ribbon.unknownee00ae0a = self.init_anim_ref_float()
            m3_ribbon.unknown1686c0b7 = self.init_anim_ref_float()
            m3_ribbon.unknown9eba8df8 = self.init_anim_ref_float()

            if ribbon.spline not in handle_to_spline_sections.keys():
                spline = shared.m3_pointer_get(self.ob.m3_ribbonsplines, ribbon.spline)
                if spline in splines:
                    spline_section = self.m3.section_for_reference(m3_ribbon, 'spline', version=0)
                    handle_to_spline_sections[ribbon.spline] = spline_section

                    for point in splines[splines.index(spline)].points:
                        point_bone = shared.m3_pointer_get(self.ob.data.bones, point.bone)

                        if not point_bone:
                            continue

                        m3_point = spline_section.content_add()
                        m3_point.bone = self.bone_name_indices[point_bone.name]
                        processor = M3OutputProcessor(self, point, m3_point)
                        io_shared.io_ribbon_spline(processor)

                        m3_point.unknown3 = self.init_anim_ref_float(1.0)
                        m3_point.unknown4 = self.init_anim_ref_float(1.0)
            else:
                handle_to_spline_sections[ribbon.spline].references.append(m3_ribbon.spline)

    def create_projections(self, model, projections):
        if not projections:
            return

        projection_section = self.m3.section_for_reference(model, 'projections', version=5)

        for projection in projections:
            projection_bone = shared.m3_pointer_get(self.ob.data.bones, projection.bone)
            m3_projection = projection_section.content_add()
            m3_projection.bone = self.bone_name_indices[projection_bone.name]
            m3_projection.material_reference_index = self.matref_handle_indices[projection.material]
            processor = M3OutputProcessor(self, projection, m3_projection)
            io_shared.io_projection(processor)

            m3_projection.unknown58ae2b94 = self.init_anim_ref_vec3()
            m3_projection.unknownf1f7110b = self.init_anim_ref_float()
            m3_projection.unknown2035f500 = self.init_anim_ref_float()
            m3_projection.unknown80d8189b = self.init_anim_ref_float()

    def create_forces(self, model, forces):
        if not forces:
            return

        force_section = self.m3.section_for_reference(model, 'forces', version=2)

        for force in forces:
            force_bone = shared.m3_pointer_get(self.ob.data.bones, force.bone)
            m3_force = force_section.content_add()
            m3_force.bone = self.bone_name_indices[force_bone.name]
            processor = M3OutputProcessor(self, force, m3_force)
            io_shared.io_force(processor)

    def create_warps(self, model, warps):
        if not warps:
            return

        warp_section = self.m3.section_for_reference(model, 'warps', version=1)

        for warp in warps:
            warp_bone = shared.m3_pointer_get(self.ob.data.bones, warp.bone)
            m3_warp = warp_section.content_add()
            m3_warp.bone = self.bone_name_indices[warp_bone.name]
            processor = M3OutputProcessor(self, warp, m3_warp)
            io_shared.io_warp(processor)

    def create_physics_bodies(self, model, physics_bodies, body_version, shape_version):
        if not physics_bodies:
            return

        physics_body_section = self.m3.section_for_reference(model, 'physics_rigidbodies', version=body_version)

        shape_to_section = {}
        for physics_body in physics_bodies:
            physics_body_bone = shared.m3_pointer_get(self.ob.data.bones, physics_body.bone)

            m3_physics_body = physics_body_section.content_add()
            m3_physics_body.bone = self.bone_name_indices[physics_body_bone.name]
            processor = M3OutputProcessor(self, physics_body, m3_physics_body)
            io_shared.io_rigid_body(processor)

            if physics_body.physics_shape in self.physics_shape_handle_to_volumes.keys():
                if not shape_to_section.get(physics_body.physics_shape):
                    shape_section = self.m3.section_for_reference(m3_physics_body, 'physics_shape', version=shape_version)

                    for volume in self.physics_shape_handle_to_volumes[physics_body.physics_shape]:
                        m3_volume = shape_section.content_add()
                        m3_volume.shape = volume.bl_rna.properties['shape'].enum_items.find(volume.shape)
                        m3_volume.size0, m3_volume.size1, m3_volume.size2 = volume.size
                        m3_volume.matrix = to_m3_matrix(mathutils.Matrix.LocRotScale(volume.location, volume.rotation, volume.scale))

                        if m3_volume.shape >= 4:
                            if int(shape_version) == 1:
                                if m3_volume.shape == 4:
                                    m3_volume.shape = 5  # TODO temporary solution while convex hull research is still needed
                                self.get_basic_volume_object(volume.mesh_object, m3_volume)
                            else:
                                self.get_physics_volume_object(volume.mesh_object, m3_volume)
                else:
                    shape_section = self.shape_to_section[physics_body.physics_shape]
                    shape_section.references.append(m3_physics_body.physics_shape)

    def create_physics_joints(self, model, physics_joints):
        if not physics_joints:
            return

        physics_joint_section = self.m3.section_for_reference(model, 'physics_joints', version=0)

        for physics_joint in physics_joints:
            body1 = shared.m3_pointer_get(export_physics_bodies, physics_joint.rigidbody1)
            body2 = shared.m3_pointer_get(export_physics_bodies, physics_joint.rigidbody2)
            bone1 = shared.m3_pointer_get(self.ob.data.bones, body1.bone)
            bone2 = shared.m3_pointer_get(self.ob.data.bones, body2.bone)
            m3_physics_joint = physics_joint_section.content_add()
            m3_physics_joint.bone1 = self.bone_name_indices[bone1.name]
            m3_physics_joint.bone2 = self.bone_name_indices[bone2.name]
            # TODO make algorithm which calculates the appropriate matrices rather than exposing to the UI.
            # TODO they seem to have a specific relation to how the bone rest matrices differ.
            m3_physics_joint.matrix1 = to_m3_matrix(mathutils.Matrix.LocRotScale(physics_joint.location1, physics_joint.rotation1, (1.0, 1.0, 1.0)))
            m3_physics_joint.matrix2 = to_m3_matrix(mathutils.Matrix.LocRotScale(physics_joint.location2, physics_joint.rotation2, (1.0, 1.0, 1.0)))
            processor = M3OutputProcessor(self, physics_joint, m3_physics_joint)
            io_shared.io_rigid_body_joint(processor)

    def create_physics_cloths(self, model, physics_cloths, version):
        if not physics_cloths or int(self.ob.m3_model_version) < 28:
            return

        physics_cloth_section = self.m3.section_for_reference(model, 'physics_cloths', version=version)

        constraints_sections = {}
        for physics_cloth in physics_cloths:
            mesh_ob = physics_cloth.mesh_object
            sim_ob = physics_cloth.simulator_object

            regn_inf = self.region_section[self.export_regions.index(mesh_ob)]
            regn_sim = self.region_section[self.export_regions.index(sim_ob)]

            # set flags for regions used by the cloth behavior
            regn_inf.bit_set('flags', 'hidden', True)
            regn_inf.bit_set('flags', 'placeholder', True)
            regn_inf.bit_set('flags', 'cloth_influenced', True)

            regn_sim.bit_set('flags', 'hidden', True)
            regn_sim.bit_set('flags', 'cloth_simulated', True)

            m3_physics_cloth = physics_cloth_section.content_add()
            m3_physics_cloth.simulation_region_index = self.export_regions.index(sim_ob)

            processor = M3OutputProcessor(self, physics_cloth, m3_physics_cloth)
            io_shared.io_cloth(processor)

            skin_bones_section = self.m3.section_for_reference(m3_physics_cloth, 'skin_bones')
            skin_bones = set()
            vertex_simulated_section = self.m3.section_for_reference(m3_physics_cloth, 'vertex_simulated')
            vertex_simulated_list = []
            vertex_bones_section = self.m3.section_for_reference(m3_physics_cloth, 'vertex_bones')
            vertex_weights_section = self.m3.section_for_reference(m3_physics_cloth, 'vertex_weights')

            if physics_cloth.constraint_set not in constraints_sections.keys():
                constraints_section = self.m3.section_for_reference(m3_physics_cloth, 'constraints', version=0)
                constraints_sections[physics_cloth.constraint_set] = constraints_section
                for volume in self.physics_cloth_constraint_handle_to_volumes[physics_cloth.constraint_set]:
                    volume_bone = shared.m3_pointer_get(self.ob.data.bones, volume.bone)
                    skin_bones.add(self.bone_name_indices[volume_bone.name])
                    m3_volume = constraints_section.content_add()
                    m3_volume.bone = self.bone_name_indices[volume_bone.name]
                    m3_volume.matrix = to_m3_matrix(mathutils.Matrix.LocRotScale(volume.location, volume.rotation, volume.scale))
                    m3_volume.height = volume.height
                    m3_volume.radius = volume.radius
            else:
                constraints_section = constraints_sections[physics_cloth.constraint_set]
                constraints_section.references.append(m3_physics_cloth.constraints)

            influence_map_section = self.m3.section_for_reference(m3_physics_cloth, 'influence_map', version=0)
            m3_influence_map = influence_map_section.content_add()
            m3_influence_map.influenced_region_index = self.export_regions.index(mesh_ob)
            m3_influence_map.simulation_region_index = self.export_regions.index(sim_ob)

            sim_group_names = [group.name for group in sim_ob.vertex_groups]
            sim_group_verts = {group.name: [] for group in sim_ob.vertex_groups}

            sim_bm = bmesh.new()
            sim_bm.from_object(sim_ob, self.depsgraph)

            layer_deform = sim_bm.verts.layers.deform.get('m3lookup')
            layer_clothsim = sim_bm.verts.layers.int.get('m3clothsim') or sim_bm.verts.layers.int.new('m3clothsim')

            for vert in sim_bm.verts:
                bone_weight_pairs = vert[layer_deform].items()
                vertex_bones = 0
                vertex_weights = 0
                # assume that weights are already normalized
                for index, weight in bone_weight_pairs:
                    weighted = 0
                    if weight:
                        bone_index = self.bone_name_indices[sim_group_names[index]]
                        vertex_bones |= bone_index << (weighted * 8)
                        vertex_weights |= round(weight * 255) << (weighted * 8)
                        skin_bones.add(bone_index)
                        sim_group_verts[sim_group_names[index]].append(vert)
                        weighted += 1
                    if weighted >= 4:
                        break

                vertex_simulated_list.append(vert[layer_clothsim])
                vertex_bones_section.content_add(vertex_bones)
                vertex_weights_section.content_add(vertex_weights)

            skin_bones_section.content_iter_add(list(skin_bones))
            vertex_simulated_section.content_from_bytes(vertex_simulated_list)

            simulation_vertex_lookups_section = self.m3.section_for_reference(m3_influence_map, 'simulation_vert_lookups')
            simulation_vertex_weights_section = self.m3.section_for_reference(m3_influence_map, 'simulation_vert_weights')

            mesh_bm = bmesh.new()
            mesh_bm.from_object(mesh_ob, self.depsgraph)

            mesh_group_names = [group.name for group in mesh_ob.vertex_groups]
            mesh_group_to_sim_group_verts = {ii: sim_group_verts[mesh_group_names[ii]] for ii in range(len(mesh_ob.vertex_groups))}

            for vert in mesh_bm.verts:
                layer_deform = mesh_bm.verts.layers.deform.get('m3lookup')
                group_weight_pairs = vert[layer_deform].items()

                sim_verts = 0
                sim_weights = 0
                weighted = 0
                # used_sim_verts = []
                for index, weight in group_weight_pairs:
                    #  there should be always be sim verts. if not, some user error likely has occurred
                    if weight:
                        distance_sim_verts = []
                        for sim_vert in mesh_group_to_sim_group_verts[index]:
                            # if sim_vert not in used_sim_verts:
                            distance_sim_verts.append([(vert.co - sim_vert.co).length, sim_vert])
                            # used_sim_verts.append(sim_vert)
                        distance_sim_verts.sort()
                        sim_verts |= distance_sim_verts[0][1].index << (weighted * 16)
                        sim_weights |= round(weight * 255) << (weighted * 8)
                        weighted += 1
                    if weighted >= 4:
                        break

                simulation_vertex_lookups_section.content_add(sim_verts)
                simulation_vertex_weights_section.content_add(sim_weights)

    def create_ik_joints(self, model, ik_joints):
        if not ik_joints:
            return

        ik_joint_section = self.m3.section_for_reference(model, 'ik_joints', version=0)

        for ik_joint, bones in zip(ik_joints, self.export_ik_joint_bones):
            m3_ik_joint = ik_joint_section.content_add()
            m3_ik_joint.bone_target = self.bone_name_indices[bones[0].name]
            m3_ik_joint.bone_base = self.bone_name_indices[bones[1].name]
            processor = M3OutputProcessor(self, ik_joint, m3_ik_joint)
            io_shared.io_ik(processor)

    def create_turrets(self, model, turrets, part_version):
        if not turrets:
            return

        turret_part_section = self.m3.section_for_reference(model, 'turret_parts', version=part_version)
        turret_section = self.m3.section_for_reference(model, 'turrets', version=0)

        part_index = 0
        for turret, turret_data in zip(turrets, self.export_turret_data):
            m3_turret = turret_section.content_add()
            m3_turret_part_index_section = self.m3.section_for_reference(m3_turret, 'parts')
            m3_turret_name_section = self.m3.section_for_reference(m3_turret, 'name')
            m3_turret_name_section.content_from_bytes(turret.name)

            # TODO transfer matrix if part_version == 1
            for part, bone in turret_data:
                m3_part = turret_part_section.content_add()
                m3_part.bone = self.bone_name_indices[bone.name]
                processor = M3OutputProcessor(self, part, m3_part)
                io_shared.io_turret_part(processor)

                m3_turret_part_index_section.content_add(part_index)
                part_index += 1

    def create_irefs(self, model):
        if not self.bones:
            return

        iref_section = self.m3.section_for_reference(model, 'bone_rests')

        for bone in self.bones:
            iref = iref_section.content_add()
            iref.matrix = to_m3_matrix(self.bone_to_iref[bone])

    def create_hittests(self, model, hittests):
        if not hittests:
            return

        hittests_section = self.m3.section_for_reference(model, 'hittests', version=1)

        ht_tight = self.ob.m3_hittest_tight
        ht_tight_bone = shared.m3_pointer_get(self.ob.data.bones, ht_tight.bone)

        m3_ht_tight = model.hittest_tight
        m3_ht_tight.bone = self.bone_name_indices[ht_tight_bone.name]

        for ii, item in enumerate(ht_tight.bl_rna.properties['shape'].enum_items):
            if item.identifier == ht_tight.shape:
                m3_ht_tight.shape = ii
                break

        m3_ht_tight.size0, m3_ht_tight.size1, m3_ht_tight.size2 = ht_tight.size
        m3_ht_tight.matrix = to_m3_matrix(mathutils.Matrix.LocRotScale(ht_tight.location, ht_tight.rotation, ht_tight.scale))

        if m3_ht_tight.shape == 4:
            self.get_basic_volume_object(ht_tight.mesh_object, m3_ht_tight)

        for hittest in hittests:
            hittest_bone = shared.m3_pointer_get(self.ob.data.bones, hittest.bone)

            m3_hittest = hittests_section.content_add()
            m3_hittest.bone = self.bone_name_indices[hittest_bone.name]
            m3_hittest.shape = hittest.bl_rna.properties['shape'].enum_items.find(hittest.shape)

            m3_hittest.size0, m3_hittest.size1, m3_hittest.size2 = hittest.size
            m3_hittest.matrix = to_m3_matrix(mathutils.Matrix.LocRotScale(hittest.location, hittest.rotation, hittest.scale))

            if m3_hittest.shape == 4:
                self.get_basic_volume_object(hittest.mesh_object, m3_hittest)

    def create_attachment_volumes(self, model, volumes):
        if not volumes:
            return

        attachment_volume_section = self.m3.section_for_reference(model, 'attachment_volumes', version=0)

        if int(self.ob.m3_model_version) >= 23:
            attachment_volume_addon0_section = self.m3.section_for_reference(model, 'attachment_volumes_addon0')
            attachment_volume_addon0_section.content_iter_add([0 for volume in volumes])
            attachment_volume_addon1_section = self.m3.section_for_reference(model, 'attachment_volumes_addon1')
            attachment_volume_addon1_section.content_iter_add([0 for volume in volumes])

        for volume, bones in zip(volumes, self.attachment_bones):
            m3_volume = attachment_volume_section.content_add()
            m3_volume.bone0 = self.bone_name_indices[bones[0].name]
            m3_volume.bone1 = self.bone_name_indices[bones[1].name]
            m3_volume.bone2 = self.bone_name_indices[bones[0].name]
            m3_volume.shape = volume.bl_rna.properties['shape'].enum_items.find(volume.shape)
            m3_volume.size0, m3_volume.size1, m3_volume.size2 = volume.size
            m3_volume.matrix = to_m3_matrix(mathutils.Matrix.LocRotScale(volume.location, volume.rotation, volume.scale))

            if m3_volume.shape == 4:
                self.get_basic_volume_object(volume.mesh_object, m3_volume)

    def create_billboards(self, model, billboards):
        if not billboards:
            return

        billboard_section = self.m3.section_for_reference(model, 'billboards')

        for billboard, bone in zip(billboards, self.billboard_bones):
            m3_billboard = billboard_section.content_add()
            m3_billboard.bone = self.bone_name_indices[bone.name]
            processor = M3OutputProcessor(self, billboard, m3_billboard)
            io_shared.io_billboard(processor)

    def get_basic_volume_object(self, mesh_ob, m3):
        if mesh_ob.name not in self.mesh_to_basic_volume_sections.keys():
            bm = bmesh.new(use_operators=True)
            bm.from_object(mesh_ob, self.depsgraph)
            bmesh.ops.triangulate(bm, faces=bm.faces)

            vert_data = [to_m3_vec3(vert.co) for vert in bm.verts]
            face_data = []

            for face in bm.faces:
                for vert in face.verts:
                    face_data.append(vert.index)

            vert_section = self.m3.section_for_reference(m3, 'vertices')
            vert_section.content_iter_add(vert_data)
            face_section = self.m3.section_for_reference(m3, 'face_data')
            face_section.content_iter_add(face_data)
            self.mesh_to_basic_volume_sections[mesh_ob.name] = [vert_section, face_section]
        else:
            vert_section, face_section = self.mesh_to_basic_volume_sections[mesh_ob.name]
            vert_section.references.append(m3.vertices)
            face_section.references.append(m3.face_data)

    def get_physics_volume_object(self, mesh_ob, m3):
        if mesh_ob.name not in self.mesh_to_physics_volume_sections.keys():
            bm = bmesh.new()
            bm.from_object(mesh_ob, self.depsgraph)

            vert_data = [to_m3_vec3(vert.co) for vert in bm.verts]
            polygon_related_data = []
            loop_data = []
            polygon_data = []

            loop_desc = io_m3.structures['DMSE'].get_version(0)

            for face in bm.faces:
                polygon_data.append(face.loops[0].index)
                loop_count = len(face.loops)
                for ii, loop in enumerate(face.loops):
                    next_loop = (ii + 1) if ii < loop_count - 1 else 0
                    m3_loop = loop_desc.instance()
                    m3_loop.vertex = loop.vert.index
                    m3_loop.polygon = face.index
                    m3_loop.loop = face.loops[next_loop].index
                    loop_data.append(m3_loop)

                # TODO try to figure out what data is actually appropriate here
                polygon_related_data.append(to_m3_vec4((0.0, 0.0, 0.0, 1.0)))

            vert_section = self.m3.section_for_reference(m3, 'vertices')
            vert_section.content_iter_add(vert_data)
            polygon_related_section = self.m3.section_for_reference(m3, 'polygons_related')
            polygon_related_section.content_iter_add(polygon_related_data)
            loop_section = self.m3.section_for_reference(m3, 'loops')
            loop_section.content_iter_add(loop_data)
            polygon_section = self.m3.section_for_reference(m3, 'polygons')
            polygon_section.content_from_bytes(polygon_data)
            self.mesh_to_physics_volume_sections[mesh_ob.name] = [vert_section, polygon_related_section, loop_section, polygon_section]
        else:
            vert_section, polygon_related_section, loop_section, polygon_section = self.mesh_to_physics_volume_sections[mesh_ob.name]
            vert_section.references.append(m3.vertices)
            # polygon_related_section.references.append(m3.polygons_related)
            loop_section.references.append(m3.loops)
            polygon_section.references.append(m3.polygons)

    def new_anim_id(self):
        self.anim_id_count += 1  # increase first since we don't want to use 0
        if self.anim_id_count == BNDS_ANIM_ID:
            self.anim_id_count += 1
        return self.anim_id_count

    def init_anim_header(self, interpolation, flags=0, anim_id=None):
        anim_ref_header = io_m3.structures['AnimationReferenceHeader'].get_version(0).instance()
        anim_ref_header.interpolation = interpolation
        anim_ref_header.flags = flags
        anim_ref_header.id = anim_id if anim_id else self.new_anim_id()
        return anim_ref_header

    def init_anim_ref_int16(self, val=0, interpolation=1):
        anim_ref = io_m3.structures['Int16AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation)
        anim_ref.default = val
        anim_ref.null = 0
        return anim_ref

    def init_anim_ref_uint16(self, val=0, interpolation=0):
        anim_ref = io_m3.structures['UInt16AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation)
        anim_ref.default = val
        anim_ref.null = 0
        return anim_ref

    def init_anim_ref_uint32(self, val=0, interpolation=0):
        anim_ref = io_m3.structures['UInt32AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation)
        anim_ref.default = val
        anim_ref.null = 0
        return anim_ref

    def init_anim_ref_flag(self, val=0, interpolation=1):
        anim_ref = io_m3.structures['FlagAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation)
        anim_ref.default = val
        anim_ref.null = 0
        return anim_ref

    def init_anim_ref_float(self, val=0.0, null_is_init=False, interpolation=1):
        anim_ref = io_m3.structures['FloatAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation)
        anim_ref.default = val
        anim_ref.null = 0.0
        return anim_ref

    def init_anim_ref_vec2(self, val=None, interpolation=1):
        anim_ref = io_m3.structures['Vector2AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation, flags=0x6)
        anim_ref.default = to_m3_vec2(val)
        anim_ref.null = to_m3_vec2()
        return anim_ref

    def init_anim_ref_vec3(self, val=None, interpolation=1):
        anim_ref = io_m3.structures['Vector3AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation, flags=0x6)
        anim_ref.default = to_m3_vec3(val)
        anim_ref.null = to_m3_vec3()
        return anim_ref

    def init_anim_ref_quat(self, val=None, interpolation=1):
        anim_ref = io_m3.structures['QuaternionAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation, flags=0x6)
        anim_ref.default = to_m3_quat(val)
        anim_ref.null = to_m3_quat()
        return anim_ref

    def init_anim_ref_color(self, val=None, interpolation=1):
        anim_ref = io_m3.structures['ColorAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation, flags=0x6)
        anim_ref.default = to_m3_color(val)
        anim_ref.null = to_m3_color()
        return anim_ref

    def init_anim_ref_bnds(self, val=None, interpolation=1):
        anim_ref = io_m3.structures['BNDSAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation, flags=0x6, anim_id=BNDS_ANIM_ID)
        anim_ref.default = to_m3_bnds(val)
        anim_ref.null = to_m3_bnds()
        return anim_ref


def m3_export(ob, filename):
    exporter = Exporter()
    sections = exporter.m3_export(ob, filename)
    io_m3.section_list_save(sections, filename)
