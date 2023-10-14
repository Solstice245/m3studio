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
import os
from . import io_m3
from . import io_shared
from . import shared
from .m3_animations import ob_anim_data_set


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


def to_m3_vec3_uint8(bl_vec=None):
    m3_vec = io_m3.structures['Vector3As3uint8'].get_version(0).instance()
    if bl_vec:
        m3_vec.x = round((bl_vec[0] + 1) / 2 * 255)
        m3_vec.y = round((bl_vec[1] + 1) / 2 * 255)
        m3_vec.z = round((bl_vec[2] + 1) / 2 * 255)
    return m3_vec


def to_m3_vec4(bl_vec=None):
    m3_vec = io_m3.structures['VEC4'].get_version(0).instance()
    m3_vec.x, m3_vec.y, m3_vec.z, m3_vec.w = bl_vec or (0.0, 0.0, 0.0, 0.0)
    return m3_vec


def to_m3_vec4_quat(bl_vec=None):
    m3_vec = io_m3.structures['VEC4'].get_version(0).instance()
    m3_vec.w = bl_vec.w if bl_vec else 1.0
    m3_vec.x = bl_vec.x if bl_vec else 0.0
    m3_vec.y = bl_vec.y if bl_vec else 0.0
    m3_vec.z = bl_vec.z if bl_vec else 0.0
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


def bind_scale_to_matrix(vec3):
    return mathutils.Matrix.LocRotScale(None, None, vec3.yxz)


ANIM_VEC_DATA_SETTINGS = {
    'SD2V': {'length': 2, 'convert': to_m3_vec2, 'attr': ['x', 'y']},
    'SD3V': {'length': 3, 'convert': to_m3_vec3, 'attr': ['x', 'y', 'z']},
    'SDCC': {'length': 4, 'convert': to_m3_color, 'attr': ['r', 'g', 'b', 'a']},
}


def get_fcurve_anim_frames(fcurve, interpolation='LINEAR'):
    if fcurve is None or not len(fcurve.keyframe_points):
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
    return left  # slerp not working as intended right now  # TODO fix or optimize out


def quat_equal(val0, val1):
    dist = (val0.x - val1.x) ** 2 + (val0.y - val1.y) ** 2 + (val0.z - val1.z) ** 2 + (val0.w - val1.w) ** 2
    return dist < 0.0001 ** 2


def simplify_anim_data_with_interp(keys, vals, interp_func, equal_func):
    if len(vals) < 2:
        return keys, vals

    left_key, curr_key = keys[:2]
    left_val, curr_val = vals[:2]
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
    vals = ([], [], [])
    for bone, coords in bone_rest_bounds.items():
        matrix = bone_to_matrix_dict[bone]
        for co in coords:
            mat_co = matrix @ co
            vals[0].append(mat_co.x)
            vals[1].append(mat_co.y)
            vals[2].append(mat_co.z)

    return mathutils.Vector(min(val) for val in vals), mathutils.Vector(max(val) for val in vals)


class M3OutputProcessor:

    def __init__(self, exporter, bl, m3):
        self.exporter = exporter
        self.bl = bl
        self.m3 = m3
        self.version = m3.desc.version

    def collect_anim_data_single(self, field, anim_data_tag):
        type_ob = float if anim_data_tag == 'SDR3' else int
        head = getattr(self.bl, field + '_header')
        head.hex_id = head.hex_id  # set hex_id to itself to verify

        is_animated = False
        for action in self.exporter.action_to_anim_data:
            fcurve = action.fcurves.find(self.bl.path_from_id(field))
            frames = get_fcurve_anim_frames(fcurve)

            if not frames:
                continue

            is_animated = True

            values = [type_ob(fcurve.evaluate(frame)) for frame in frames]
            self.exporter.action_to_anim_data[action][anim_data_tag][int(head.hex_id, 16)] = (frames, values)

        return is_animated

    def collect_anim_data_vector(self, field, anim_data_tag):
        head = getattr(self.bl, field + '_header')
        head.hex_id = head.hex_id  # set hex_id to itself to verify

        is_animated = False
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

            is_animated = True

            values = []
            for frame in frames:
                vec_comps = []

                for ii, fcurve in enumerate(fcurves):
                    if fcurve is None:
                        vec_comps.append(getattr(anim_ref.default, vec_data_settings['attr'][ii]))
                    else:
                        vec_comps.append(fcurve.evaluate(frame))

                values.append(vec_data_settings['convert'](vec_comps))

            self.exporter.action_to_anim_data[action][anim_data_tag][int(head.hex_id, 16)] = (frames, values)

        return is_animated

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

    def anim_boolean_flag(self, field):
        head = getattr(self.bl, field + '_header')
        if self.collect_anim_data_single(field, 'SDFG'):
            interp = 0 if head.interpolation == 'CONSTANT' else 1 if head.interpolation == 'LINEAR' else -1
            setattr(self.m3, field, self.exporter.init_anim_ref_flag(getattr(self.bl, field), interp, head.flags, int(head.hex_id, 16)))
        else:
            setattr(self.m3, field, self.exporter.init_anim_ref_flag(getattr(self.bl, field), 0, 0, int(head.hex_id, 16)))

    def anim_int16(self, field):
        head = getattr(self.bl, field + '_header')
        if self.collect_anim_data_single(field, 'SDS6'):
            interp = 0 if head.interpolation == 'CONSTANT' else 1 if head.interpolation == 'LINEAR' else -1
            setattr(self.m3, field, self.exporter.init_anim_ref_int16(getattr(self.bl, field), interp, head.flags, int(head.hex_id, 16)))
        else:
            setattr(self.m3, field, self.exporter.init_anim_ref_int16(getattr(self.bl, field), 0, 0, int(head.hex_id, 16)))

    def anim_uint16(self, field):
        head = getattr(self.bl, field + '_header')
        if self.collect_anim_data_single(field, 'SDU6'):
            interp = 0 if head.interpolation == 'CONSTANT' else 1 if head.interpolation == 'LINEAR' else -1
            setattr(self.m3, field, self.exporter.init_anim_ref_uint16(getattr(self.bl, field), interp, head.flags, int(head.hex_id, 16)))
        else:
            setattr(self.m3, field, self.exporter.init_anim_ref_uint16(getattr(self.bl, field), 0, 0, int(head.hex_id, 16)))

    def anim_uint32(self, field):
        head = getattr(self.bl, field + '_header')
        # casting val to int because sometimes bools use this
        if self.collect_anim_data_single(field, 'SDU3'):
            interp = 0 if head.interpolation == 'CONSTANT' else 1 if head.interpolation == 'LINEAR' else -1
            setattr(self.m3, field, self.exporter.init_anim_ref_uint32(getattr(self.bl, field), interp, head.flags, int(head.hex_id, 16)))
        else:
            setattr(self.m3, field, self.exporter.init_anim_ref_uint32(getattr(self.bl, field), 0, 0, int(head.hex_id, 16)))

    def anim_float(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        head = getattr(self.bl, field + '_header')
        if self.collect_anim_data_single(field, 'SDR3'):
            interp = 0 if head.interpolation == 'CONSTANT' else 1 if head.interpolation == 'LINEAR' else -1
            setattr(self.m3, field, self.exporter.init_anim_ref_float(getattr(self.bl, field), interp, head.flags, int(head.hex_id, 16)))
        else:
            setattr(self.m3, field, self.exporter.init_anim_ref_float(getattr(self.bl, field), 0, 0, int(head.hex_id, 16)))

    def anim_vec2(self, field):
        head = getattr(self.bl, field + '_header')
        if self.collect_anim_data_vector(field, 'SD2V'):
            interp = 0 if head.interpolation == 'CONSTANT' else 1 if head.interpolation == 'LINEAR' else -1
            setattr(self.m3, field, self.exporter.init_anim_ref_vec2(getattr(self.bl, field), interp, head.flags, int(head.hex_id, 16)))
        else:
            setattr(self.m3, field, self.exporter.init_anim_ref_vec2(getattr(self.bl, field), 0, 0, int(head.hex_id, 16)))

    def anim_vec3(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        head = getattr(self.bl, field + '_header')
        if self.collect_anim_data_vector(field, 'SD3V'):
            interp = 0 if head.interpolation == 'CONSTANT' else 1 if head.interpolation == 'LINEAR' else -1
            setattr(self.m3, field, self.exporter.init_anim_ref_vec3(getattr(self.bl, field), interp, head.flags, int(head.hex_id, 16)))
        else:
            setattr(self.m3, field, self.exporter.init_anim_ref_vec3(getattr(self.bl, field), 0, 0, int(head.hex_id, 16)))

    def anim_color(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        head = getattr(self.bl, field + '_header')
        if self.collect_anim_data_vector(field, 'SDCC'):
            interp = 0 if head.interpolation == 'CONSTANT' else 1 if head.interpolation == 'LINEAR' else -1
            setattr(self.m3, field, self.exporter.init_anim_ref_color(getattr(self.bl, field), interp, head.flags, int(head.hex_id, 16)))
        else:
            setattr(self.m3, field, self.exporter.init_anim_ref_color(getattr(self.bl, field), 0, 0, int(head.hex_id, 16)))


class Exporter():

    def __init__(self, bl_op=None):
        self.bl_op = bl_op

    def m3_export(self, ob, filename):
        assert ob.type == 'ARMATURE'

        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if not ob.animation_data:
            ob.animation_data_create()

        self.ob = ob
        self.scene = bpy.context.scene
        self.m3 = io_m3.M3SectionList(init_header=True)

        self.anim_id_count = 0
        self.uv_count = 1
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
        self.stc_to_anim_group = {}  # only have 'full' or primary anims as keys

        # used to calculate exact positions of later sections in the section list
        self.stc_section = None  # defined in the sequence export
        self.stc_to_name_section = {}  # defined in the sequence export
        self.stg_last_indice_section = None  # defined in the sequence export

        # used for later reference such as setting region flags
        self.region_section = None  # defined in the mesh export code

        self.init_action = self.ob.animation_data.action
        self.init_frame = self.scene.frame_current

        self.warn_strings = []

        # TODO look for duplicate animation header ids and warn that they need to be resolved

        def valid_collections_and_requirements(collection):
            # TODO have second unexposed export custom prop for auto-culling such as invalid attachment point name
            export_items = []
            for item in collection:
                item_bones = set()
                if not item.m3_export:
                    continue
                if hasattr(item, 'bone'):
                    bone = shared.m3_pointer_get(ob.pose.bones, item.bone)
                    if bone:
                        item_bones.add(bone)
                    else:
                        self.warn_strings.append(f'{str(item)} has no bone assigned to it and will not be exported')
                        continue
                if hasattr(item, 'material'):
                    matref = shared.m3_pointer_get(ob.m3_materialrefs, item.material)
                    if matref:
                        self.export_required_material_references.add(matref)
                    else:
                        self.warn_strings.append(f'{str(item)} has no material assigned to it and will not be exported')
                        continue
                self.export_required_bones = self.export_required_bones.union(item_bones)
                export_items.append(item)
            return export_items

        self.export_sequences = []  # handled specially
        export_attachment_points = valid_collections_and_requirements(ob.m3_attachmentpoints)
        export_lights = valid_collections_and_requirements(ob.m3_lights)
        export_shadow_boxes = valid_collections_and_requirements(ob.m3_shadowboxes)
        export_cameras = valid_collections_and_requirements(ob.m3_cameras)
        export_material_references = []  # handled specially
        export_particle_systems = valid_collections_and_requirements(ob.m3_particlesystems)
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
        export_tmd_data = []  # handled specially

        self.vertex_color_mats = set()
        self.vertex_alpha_mats = set()

        for anim_group in ob.m3_animation_groups:
            # TODO all anim groups must have unique name.
            if not anim_group.m3_export:
                continue

            for anim in anim_group.animations:
                if anim.action:
                    self.export_sequences.append(anim_group)
                    break

        for system in export_particle_systems:
            self.vertex_color_mats.add(system.material.handle)
            if system.vertex_alpha:
                self.vertex_alpha_mats.add(system.material.handle)

        for ribbon in export_ribbons:
            self.vertex_color_mats.add(ribbon.material.handle)
            if ribbon.vertex_alpha:
                self.vertex_alpha_mats.add(ribbon.material.handle)

        for particle_copy in ob.m3_particlecopies:
            if not particle_copy.m3_export:
                continue
            particle_copy_bone = shared.m3_pointer_get(ob.pose.bones, particle_copy.bone)
            if len(particle_copy.systems) and particle_copy_bone and particle_copy.m3_export:
                self.export_required_bones.add(particle_copy_bone)
                export_particle_copies.append(particle_copy)

        for spline in ob.m3_ribbonsplines:
            export_spline_points = []
            for point in spline.points:
                point_bone = shared.m3_pointer_get(ob.pose.bones, point.bone)
                if point_bone:
                    self.export_required_bones.add(point_bone)
                    export_spline_points.append(point)
                else:
                    self.warn_strings.append(f'{str(point)} has no bone assigned to it and will not be exported')
            if len(export_spline_points):
                export_ribbon_splines.append(spline)

        self.physics_shapes_handle_to_shape = {}
        self.physics_shape_handle_to_volumes = {}
        physics_shape_used_bones = []
        for physics_body in ob.m3_rigidbodies:
            if not physics_body.m3_export:
                continue
            bone = shared.m3_pointer_get(ob.pose.bones, physics_body.bone)
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
                                    self.warn_strings.append(f'{str(volume)} is a mesh type volume, but no mesh object is assigned')
                            else:
                                valid_volumes.append(volume)
                        if len(valid_volumes):
                            self.physics_shape_handle_to_volumes[physics_shape.bl_handle] = valid_volumes
                            export_physics_bodies.append(physics_body)
                        else:
                            self.warn_strings.append(f'{str(physics_shape)} has a volume shape collection, but no shapes')
                else:
                    self.warn_strings.append(f'{str(physics_shape)} has no volume shape collection')
            else:
                self.warn_strings.append(f'{str(physics_shape)} has no corrosponding bone or the bone is already used by a physics body')

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
                        bone = shared.m3_pointer_get(ob.pose.bones, constraint.bone)
                        if constraint.m3_export and bone:
                            self.export_required_bones.add(bone)
                            valid_volumes.append(constraint)
                    if len(valid_volumes):
                        self.physics_cloth_constraint_handle_to_volumes[constraint_set.bl_handle] = valid_volumes

        self.ik_bones = []
        self.export_ik_joint_bones = []
        for ik_joint in ob.m3_ikjoints:
            if not ik_joint.m3_export:
                continue
            bone = shared.m3_pointer_get(ob.pose.bones, ik_joint.bone)
            if bone:
                bone_parent = bone

                for ii in range(0, ik_joint.joint_length):
                    if bone_parent.parent:
                        bone_parent = bone_parent.parent if bone_parent else bone_parent
                        self.ik_bones.append(bone_parent)
                    else:
                        self.warn_strings.append(f'{str(ik_joint)} joint length exceeds the length of the target bone\'s heirarchy')
                        # ???? warn if ik joints have any collisions?
                if bone_parent != bone:
                    export_ik_joints.append(ik_joint)
                    self.ik_bones.append(bone_parent)
                    self.export_ik_joint_bones.append([bone, bone_parent])
                    self.export_required_bones.add(bone)
                    self.export_required_bones.add(bone_parent)

        self.export_turret_parts = []

        group_id_to_part = {}
        for turret in ob.m3_turrets:
            if not turret.m3_export:
                continue
            turret_has_parts = False
            for part in turret.parts:
                part_bone = shared.m3_pointer_get(ob.pose.bones, part.bone)
                if part_bone:
                    turret_has_parts = True
                    self.export_required_bones.add(part_bone)
                    if part.main_part:
                        self.export_turret_parts.insert(0, part)
                        if not group_id_to_part[part.group_id]:
                            group_id_to_part[part.group_id] = part
                        else:
                            self.warn_strings.append(f'Turret group {part.group_id} has more than one main part, but it should have only one')
                    else:
                        self.export_turret_parts.append(part)
                else:
                    self.warn_strings.append(f'{str(part)} has no bone assigned to it and will not be exported')
            if turret_has_parts:
                export_turrets.append(turret)

        hittest_bone = shared.m3_pointer_get(ob.pose.bones, ob.m3_hittest_tight.bone)
        if hittest_bone:
            self.export_required_bones.add(hittest_bone)

        self.attachment_bones = []
        for attachment in export_attachment_points:
            attachment_point_bone = shared.m3_pointer_get(ob.pose.bones, attachment.bone)
            if attachment_point_bone:
                self.export_required_bones.add(attachment_point_bone)
                for volume in attachment.volumes:
                    export_attachment_volumes.append(volume)
                    self.attachment_bones.append(attachment_point_bone)
            else:
                self.warn_strings.append(f'{str(attachment)} has no valid bone assigned to it and will not be exported')

        for m3_tmd in ob.m3_tmd:
            if m3_tmd.m3_export:
                export_tmd_data.append(m3_tmd)

        self.export_regions = []
        self.ob_to_region_index = []

        mesh_matrefs = set()

        for child in ob.children:
            if child.type == 'MESH' and (child.m3_mesh_export or child in self.export_required_regions):
                me = child.data
                me.calc_loop_triangles()

                if len(me.loop_triangles) > 0:
                    valid_mesh_batches = 0
                    for mesh_batch in child.m3_mesh_batches:
                        matref = shared.m3_pointer_get(ob.m3_materialrefs, mesh_batch.material)
                        if matref:
                            self.export_required_material_references.add(matref)
                            mesh_matrefs.add(matref)
                            valid_mesh_batches += 1

                    if valid_mesh_batches == 0:
                        self.warn_strings.append(f'{str(child)} has no valid material assignments and will not be exported')
                        continue

                    skin_vertex_groups = 0
                    for vertex_group in child.vertex_groups:
                        group_bone = ob.data.bones.get(vertex_group.name)
                        if group_bone:
                            skin_vertex_groups += 1
                            self.export_required_bones.add(group_bone)
                            self.skinned_bones.append(group_bone)

                    if skin_vertex_groups == 0:
                        self.warn_strings.append(f'{str(child)} has no vertex groups skinned to a bone and will not be exported')
                        continue

                    self.export_regions.append(child)

                    for ii in range(valid_mesh_batches):
                        self.ob_to_region_index.append(child)

        materials_used_by_particle = set()
        materials_used_by_not_particle = set()

        for particle in export_particle_systems:
            matref = shared.m3_pointer_get(ob.m3_materialrefs, particle.material)
            materials_used_by_particle.add(matref)

        for handle in mesh_matrefs:
            materials_used_by_not_particle.add(handle)

        for item in export_ribbons + export_projections:
            matref = shared.m3_pointer_get(ob.m3_materialrefs, item.material)
            materials_used_by_not_particle.add(matref)

        def recurse_composite_materials(matref, force_color, force_alpha):
            if force_color:
                self.vertex_color_mats.add(matref.bl_handle)
            if force_alpha:
                self.vertex_alpha_mats.add(matref.bl_handle)
            if matref.mat_type == 'm3_materials_composite':
                mat = shared.m3_pointer_get(getattr(self.ob, matref.mat_type), matref.mat_handle)
                for section in mat.sections:
                    section_matref = shared.m3_pointer_get(ob.m3_materialrefs, section.material.handle)
                    if section_matref:
                        if matref in materials_used_by_particle:
                            materials_used_by_particle.add(section_matref)
                        if matref in materials_used_by_not_particle:
                            materials_used_by_not_particle.add(section_matref)
                        self.export_required_material_references.add(section_matref)
                        recurse_composite_materials(section_matref, matref.bl_handle in self.vertex_color_mats, matref.bl_handle in self.vertex_alpha_mats)

        for matref in self.export_required_material_references.copy():
            recurse_composite_materials(matref, matref.bl_handle in self.vertex_color_mats, matref.bl_handle in self.vertex_alpha_mats)

        # TODO exclude materials if their type cannot be exported in model version
        # TODO warning if layers have rtt channel in non-standard material

        for matref in self.export_required_material_references:
            mat = shared.m3_pointer_get(getattr(ob, matref.mat_type), matref.mat_handle)
            for layer_name in shared.material_type_to_layers[shared.material_collections.index(matref.mat_type)]:
                layer = shared.m3_pointer_get(self.ob.m3_materiallayers, getattr(mat, f'layer_{layer_name}'))

                if layer:
                    if layer.color_type == 'BITMAP' and layer.color_bitmap:
                        if layer.uv_source == 'UV3':
                            self.uv_count = 4
                        elif layer.uv_source == 'UV2' and self.uv_count < 3:
                            self.uv_count = 3
                        elif layer.uv_source == 'UV1' and self.uv_count < 2:
                            self.uv_count = 2

        for matref in materials_used_by_particle & materials_used_by_not_particle:
            mat = shared.m3_pointer_get(getattr(ob, matref.mat_type), matref.mat_handle)
            self.warn_strings.append(f'M3 Material "{mat.name}" being used by non-particles while being used by particles can break them')

        def export_bone_bool(bone):
            result = False
            if bone.m3_export_cull:
                result = True
            elif bone in self.export_required_bones:
                result = True

            # if result is True:
            #     db = ob.data.bones.get(bone.name)
            #     assert db.use_inherit_location and db.use_inherit_rotation and db.use_inherit_scale

            return result

        self.bones = []
        for bone in ob.pose.bones:
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
            billboard_bone = shared.m3_pointer_get(ob.pose.bones, billboard.bone)
            if billboard.m3_export and billboard_bone and billboard_bone in self.bones and billboard_bone not in self.billboard_bones:
                self.billboard_bones.append(billboard_bone)
                export_billboards.append(billboard)

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

        self.bone_name_indices = {bone.name: ii for ii, bone in enumerate(self.bones)}
        self.bone_to_correction_matrices = {}
        self.bone_to_iref = {}
        self.bone_to_abs_pose_matrix = {}
        self.bone_bound_vecs = None  # defined later

        self.matref_handle_indices = {}
        for matref in ob.m3_materialrefs:
            if matref in self.export_required_material_references:
                self.matref_handle_indices[matref.bl_handle] = len(self.matref_handle_indices.keys())
                export_material_references.append(matref)

        # make sure mesh objects are in their rest position
        for ob in self.export_regions:
            arm_mod = None
            for modifier in ob.modifiers:
                if modifier.type == 'ARMATURE':
                    if arm_mod:
                        self.warn_strings.append(f'{str(ob)} has more than one armature modifier')
                    arm_mod = modifier
                    if arm_mod.object != self.ob:
                        self.warn_strings.append(f'{str(ob)} has an armature modifier object which is not the parent armature object')
                    arm_mod.object = None

        self.depsgraph = bpy.context.evaluated_depsgraph_get()

        model_section = self.m3.section_for_reference(self.m3[0][0], 'model', version=self.ob.m3_model_version)
        model = model_section.content_add()

        model_name_section = self.m3.section_for_reference(model, 'model_name')
        model_name_section.content_from_string(os.path.basename(filename))

        self.bounds_min = mathutils.Vector((self.ob.m3_bounds.left, self.ob.m3_bounds.back, self.ob.m3_bounds.bottom))
        self.bounds_max = mathutils.Vector((self.ob.m3_bounds.right, self.ob.m3_bounds.front, self.ob.m3_bounds.top))
        model.boundings = to_m3_bnds((self.bounds_min, self.bounds_max))

        self.create_sequences(model, self.export_sequences)
        self.create_bones(model)
        self.create_division(model, self.export_regions, regn_version=self.ob.m3_mesh_version)
        self.create_attachment_points(model, export_attachment_points)  # TODO should exclude attachments with same bone as other attachments
        self.create_lights(model, export_lights)
        self.create_shadow_boxes(model, export_shadow_boxes)
        self.create_cameras(model, export_cameras)
        self.create_materials(model, export_material_references, material_versions)  # TODO test volume, volume noise and stb material types
        self.create_particle_systems(model, export_particle_systems, export_particle_copies, version=self.ob.m3_particlesystems_version)
        self.create_ribbons(model, export_ribbons, export_ribbon_splines, version=self.ob.m3_ribbons_version)
        self.create_projections(model, export_projections)
        self.create_forces(model, export_forces)
        self.create_warps(model, export_warps)
        # TODO PHSH 2/3 polygon shapes are buggy
        self.create_physics_bodies(model, export_physics_bodies, body_version=self.ob.m3_rigidbodies_version, shape_version=self.ob.m3_physicsshapes_version)
        self.create_physics_joints(model, export_physics_bodies, export_physics_joints)
        self.create_physics_cloths(model, export_physics_cloths, version=self.ob.m3_cloths_version)  # TODO simulation rigging
        self.create_ik_joints(model, export_ik_joints)
        self.create_turrets(model, export_turrets, part_version=self.ob.m3_turrets_part_version)
        self.create_irefs(model)
        self.create_hittests(model, export_hittests)
        self.create_attachment_volumes(model, export_attachment_volumes)
        self.create_billboards(model, export_billboards)
        # self.create_tmd_data(model, export_tmd_data)  # ! not supported in modern SC2 client

        self.finalize_anim_data(model)

        if len(self.warn_strings):
            warning = f'The following warnings were given during the M3 export operation of {self.ob.name}:\n' + '\n'.join(self.warn_strings)
            print(warning)  # not for debugging
            if self.bl_op:
                self.bl_op.report({"WARNING"}, warning)

        self.m3.validate()
        self.m3.resolve()
        self.m3.to_index()

        try:  # place armature back into the pose that it was before
            if self.ob.m3_animation_groups_index > -1:
                anim_group = self.ob.m3_animation_groups[self.ob.m3_animation_groups_index]
                anim = anim_group.animations[anim_group.animations_index]
                ob_anim_data_set(self.scene, self.ob, anim.action)
        except IndexError:  # pass if any index value is out of range
            pass

        self.ob.animation_data.action = self.init_action
        self.scene.frame_current = self.init_frame

        # animation data is exported much faster while no armature modifiers point to them.
        # keep this below anything handling animation data.
        for ob in self.export_regions:
            arm_mod = None
            for modifier in ob.modifiers:
                if modifier.type == 'ARMATURE':
                    arm_mod = modifier
                    arm_mod.object = self.ob

            # auto generate armature modifier if one does not already exist
            if arm_mod is None:
                arm_mod = ob.modifiers.new('Armature', 'ARMATURE')
                arm_mod.object = self.ob

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

        # TODO ensure animation group names are unique
        for anim_group in anim_groups:
            m3_seq = seq_section.content_add()
            m3_seq_name_section = self.m3.section_for_reference(m3_seq, 'name')
            m3_seq_name_section.content_from_string(anim_group.name)

            processor = M3OutputProcessor(self, anim_group, m3_seq)
            io_shared.io_anim_group(processor)

            m3_seq.anim_ms_start = to_m3_ms(anim_group.frame_start)
            m3_seq.anim_ms_end = to_m3_ms(anim_group.frame_end)

            m3_stg = stg_section.content_add()
            m3_seq_name_section.references.append(m3_stg.name)
            m3_stg_col_indices_section = self.m3.section_for_reference(m3_stg, 'stc_indices', pos=None)
            stg_indices_sections.append(m3_stg_col_indices_section)

            for anim in anim_group.animations:

                if not anim.action:
                    continue

                m3_stc = stc_section.content_add()
                m3_stc_name_section = self.m3.section_for_reference(m3_stc, 'name', pos=None)
                m3_stc_name_section.content_from_string(anim_group.name + '_' + anim.name)
                self.stc_to_name_section[m3_stc] = m3_stc_name_section
                stc_name_sections.append(m3_stc_name_section)
                self.stc_to_anim_group[m3_stc] = anim_group

                m3_stc.concurrent = int(anim.concurrent)
                m3_stc.priority = anim.priority
                m3_stc.sts_index = len(stc_section) - 1
                m3_stc.sts_index_fb = m3_stc.sts_index

                self.action_to_anim_data[anim.action] = {section_name: {} for section_name in ANIM_DATA_SECTION_NAMES}
                self.action_to_sdmb_user[anim.action] = False

                try:
                    self.action_to_stc[anim.action].append(m3_stc)
                except KeyError:
                    self.action_to_stc[anim.action] = [m3_stc]

                try:
                    self.action_frame_range[anim.action][0] = min(self.action_frame_range[anim.action][0], anim_group.frame_start)
                    self.action_frame_range[anim.action][1] = max(self.action_frame_range[anim.action][1], anim_group.frame_end)
                except KeyError:
                    self.action_frame_range[anim.action] = [anim_group.frame_start, anim_group.frame_end]

                m3_stg_col_indices_section.content_add(len(stc_section) - 1)

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

        for action, stc_list in self.action_to_stc.items():

            # do not calculate bounds if action which has no bone animation data, or there is no mesh data in general
            if self.action_to_sdmb_user.get(action) and len(self.export_regions):
                self.action_to_anim_data[action]['SDMB'][BNDS_ANIM_ID] = [[], []]
                bnds_data = self.action_to_anim_data[action]['SDMB'][BNDS_ANIM_ID]

                frame_list = list(self.action_abs_pose_matrices[action].keys())
                init_frame = frame_list.pop(0)

                prev_min, prev_max = bounding_vectors_from_bones(self.bone_bound_vecs, self.action_abs_pose_matrices[action][init_frame])

                bnds_data[0].append(init_frame)
                bnds_data[1].append(to_m3_bnds((prev_min, prev_max)))

                for frame in frame_list[0::3]:
                    bnds_min, bnds_max = bounding_vectors_from_bones(self.bone_bound_vecs, self.action_abs_pose_matrices[action][frame])
                    if (prev_min - bnds_min).length >= 0.03 or (prev_max - bnds_max).length >= 0.03:
                        bnds_data[0].append(frame)
                        bnds_data[1].append(to_m3_bnds((bnds_min, bnds_max)))
                        prev_min, prev_max = bnds_min, bnds_max

            section_pos = self.m3.index(self.stc_to_name_section[stc_list[-1]]) + 1

            stc_ids_section = {}

            for stc in stc_list:

                evnt_name_sections = []
                anim_group = self.stc_to_anim_group.get(stc)

                if anim_group:
                    self.action_to_anim_data[action]['SDEV'][EVNT_ANIM_ID] = [[], []]
                    evnt_data = self.action_to_anim_data[action]['SDEV'][EVNT_ANIM_ID]

                    if anim_group.simulate:
                        evnt_data[0].append(anim_group.simulate_frame)
                        evnt = io_m3.structures['EVNT'].get_version(0).instance()
                        evnt_name_section = self.m3.section_for_reference(evnt, 'name', pos=None)
                        evnt_name_section.content_from_string('Evt_Simulate')
                        evnt_data[1].append(evnt)
                        evnt_name_sections.append(evnt_name_section)
                        evnt.matrix = to_m3_matrix(mathutils.Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))))

                    evnt_data[0].append(anim_group.frame_end)
                    evnt = io_m3.structures['EVNT'].get_version(0).instance()
                    evnt_name_section = self.m3.section_for_reference(evnt, 'name', pos=None)
                    evnt_name_section.content_from_string('Evt_SeqEnd')
                    evnt_data[1].append(evnt)
                    evnt_name_sections.append(evnt_name_section)
                    evnt.matrix = to_m3_matrix(mathutils.Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))))

                ids_section = self.m3.section_for_reference(stc, 'anim_ids', pos=None)  # position later
                ids_sections.append(ids_section)
                stc_ids_section[stc] = ids_section
                refs_section = self.m3.section_for_reference(stc, 'anim_refs', pos=section_pos)
                section_pos += 1

                anim_fend = float('-inf')

                for data_type_ii, section_data_name in enumerate(ANIM_DATA_SECTION_NAMES):

                    if not len(self.action_to_anim_data[action][section_data_name]):
                        continue

                    action_data = self.action_to_anim_data[action][section_data_name]

                    for ii, id_num in enumerate(action_data):
                        anim_fend = min(max(anim_fend, action_data[id_num][0][-1]), anim_group.frame_end)

                for data_type_ii, section_data_name in enumerate(ANIM_DATA_SECTION_NAMES):

                    if not len(self.action_to_anim_data[action][section_data_name]):
                        continue

                    action_data = self.action_to_anim_data[action][section_data_name]
                    attr_name = section_data_name.lower()

                    data_section = self.m3.section_for_reference(stc, attr_name, pos=section_pos)
                    section_pos += 1

                    for ii, id_num in enumerate(action_data):
                        data_head = data_section.content_add()

                        ids_section.content_add(id_num)
                        refs_section.content_add((data_type_ii << 16) + ii)

                        data_head.fend = to_m3_ms(anim_fend)

                        frames_section = self.m3.section_for_reference(data_head, 'frames', pos=section_pos)
                        frames_section.content_add(*(to_m3_ms(frame) for frame in action_data[id_num][0]))
                        section_pos += 1

                        values_section = self.m3.section_for_reference(data_head, 'keys', pos=section_pos)
                        values_section.content_add(*action_data[id_num][1])
                        section_pos += 1

                        if section_data_name == 'SDEV':
                            data_head.flags = 1

                            for evnt_name_section in evnt_name_sections:
                                self.m3.insert(section_pos, evnt_name_section)
                                section_pos += 1

            for stc in stc_list:
                sts = sts_section.content_add()
                stc_ids_section[stc].references.append(sts.anim_ids)

        if self.action_to_stc:
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

        # place armature in the default pose so that bones are in their default pose
        ob_anim_data_set(self.scene, self.ob, None)
        self.scene.frame_set(0)

        bone_section = self.m3.section_for_reference(model, 'bones', version=1)
        m3_bone_defaults = {}

        bone_to_m3_bone = {}

        for pose_bone in self.bones:
            data_bone = self.ob.data.bones.get(pose_bone.name)
            m3_bone_parent = bone_to_m3_bone.get(pose_bone.parent, None) if pose_bone.parent else None
            m3_bone = bone_section.content_add()
            m3_bone_name_section = self.m3.section_for_reference(m3_bone, 'name')
            m3_bone_name_section.content_from_string(pose_bone.name)
            m3_bone.parent = self.bone_name_indices.get(pose_bone.parent.name) if pose_bone.parent else -1
            m3_bone.flags = 0
            m3_bone.bit_set('flags', 'real', True)  # TODO is not always true for blizzard models, figure out when this is applicable
            m3_bone.bit_set('flags', 'skinned', pose_bone in self.skinned_bones)
            m3_bone.bit_set('flags', 'ik', pose_bone in self.ik_bones)
            m3_bone.bit_set('flags', 'batch1', not pose_bone.m3_batching or m3_bone_parent.bit_get('flags', 'batch1') if m3_bone_parent else False)
            m3_bone.bit_set('flags', 'batch2', not pose_bone.m3_batching)

            # using set function of bone anim id prop to validate
            pose_bone.m3_location_hex_id = pose_bone.m3_location_hex_id

            m3_bone.location = self.init_anim_ref_vec3(anim_id=int(pose_bone.m3_location_hex_id, 16))
            m3_bone.rotation = self.init_anim_ref_quat(anim_id=int(pose_bone.m3_rotation_hex_id, 16))
            m3_bone.rotation.null.w = 1.0
            m3_bone.scale = self.init_anim_ref_vec3(anim_id=int(pose_bone.m3_scale_hex_id, 16))
            m3_bone.scale.null = to_m3_vec3((1.0, 1.0, 1.0))
            m3_bone.batching = self.init_anim_ref_uint32(pose_bone.m3_batching, anim_id=int(pose_bone.m3_batching_hex_id, 16))
            m3_bone.batching.null = 1

            bone_to_m3_bone[pose_bone] = m3_bone

            bone_local_inv_matrix = (data_bone.matrix_local @ io_shared.rot_fix_matrix_transpose).inverted()
            self.bone_to_iref[pose_bone] = bind_scale_to_matrix(pose_bone.m3_bind_scale) @ bone_local_inv_matrix

            bind_scale_inv = mathutils.Vector((1.0 / pose_bone.m3_bind_scale[ii] for ii in range(3)))
            bind_scale_inv_matrix = bind_scale_to_matrix(bind_scale_inv)

            if pose_bone.parent:
                parent_bind_matrix = bind_scale_to_matrix(pose_bone.parent.m3_bind_scale)
                left_correction_matrix = parent_bind_matrix @ io_shared.rot_fix_matrix @ data_bone.parent.matrix_local.inverted() @ data_bone.matrix_local
            else:
                left_correction_matrix = data_bone.matrix_local

            right_correction_matrix = io_shared.rot_fix_matrix_transpose @ bind_scale_inv_matrix

            self.bone_to_correction_matrices[pose_bone] = (left_correction_matrix, right_correction_matrix)

            pose_matrix = self.ob.convert_space(pose_bone=pose_bone, matrix=pose_bone.matrix, from_space='POSE', to_space='LOCAL')
            m3_pose_matrix = left_correction_matrix @ pose_matrix @ right_correction_matrix

            m3_bone_loc, m3_bone_rot, m3_bone_scl = m3_bone_defaults[m3_bone] = m3_pose_matrix.decompose()
            m3_bone.scale.default = to_m3_vec3(m3_bone_scl)
            m3_bone.rotation.default = to_m3_quat(m3_bone_rot)
            m3_bone.location.default = to_m3_vec3(m3_bone_loc)

            if pose_bone.parent:
                abs_pose_matrix = self.bone_to_abs_pose_matrix[pose_bone.parent] @ self.bone_to_iref[pose_bone.parent].inverted() @ m3_pose_matrix
            else:
                abs_pose_matrix = m3_pose_matrix

            self.bone_to_abs_pose_matrix[pose_bone] = abs_pose_matrix @ self.bone_to_iref[pose_bone]

        calc_actions = []
        for anim_group in self.export_sequences:
            for anim in anim_group.animations:
                if anim.action is None or anim.action in calc_actions:
                    continue
                calc_actions.append(anim.action)

                # setting scene properties is extremely slow
                # maximum optimization would keep calls to ob_anim_data_set and frame_set to an absolute minimum
                ob_anim_data_set(self.scene, self.ob, anim.action)

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

                    for pb in self.bones:
                        bone_to_pose_matrices[pb].append(self.ob.convert_space(pose_bone=pb, matrix=pb.matrix, from_space='POSE', to_space='LOCAL'))

                bone_m3_pose_matrices = {bone: [] for bone in self.bones}

                for pose_bone in self.bones:
                    data_bone = self.ob.data.bones.get(pose_bone.name)
                    m3_bone = bone_to_m3_bone[pose_bone]
                    left_correction_matrix, right_correction_matrix = self.bone_to_correction_matrices[pose_bone]

                    anim_locs = []
                    anim_rots = []
                    anim_scls = []

                    frame_start = self.action_frame_range[anim.action][0]

                    for pose_matrix in bone_to_pose_matrices[pose_bone]:
                        m3_pose_matrix = left_correction_matrix @ pose_matrix @ right_correction_matrix
                        # storing these and operating on them later if boundings are needed
                        bone_m3_pose_matrices[pose_bone].append(m3_pose_matrix)
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
                    m3_batching_fcurve = anim.action.fcurves.find(pose_bone.path_from_id('m3_batching'))
                    m3_batching_frames = get_fcurve_anim_frames(m3_batching_fcurve)

                    if m3_batching_frames:
                        m3_bone.bit_set('flags', 'batch1', True)
                        m3_bone.bit_set('flags', 'batch2', True)
                        m3_batching_values = [int(m3_batching_fcurve.evaluate(frame)) for frame in m3_batching_frames]
                        self.action_to_anim_data[anim.action]['SDFG'][m3_bone.batching.header.id] = (m3_batching_frames, m3_batching_values)

                # calculate absolute pose matrices only if needed for boundings
                if self.action_to_sdmb_user[anim.action]:
                    for bone in self.bones:
                        for jj, m3_pose_matrix in enumerate(bone_m3_pose_matrices[bone]):

                            if bone.parent is not None:
                                parent_abs_pose_matrix = frame_to_bone_abs_pose_matrix[jj + frame_start][bone.parent]
                                abs_bone_matrix = parent_abs_pose_matrix @ self.bone_to_iref[bone.parent].inverted() @ m3_pose_matrix
                            else:
                                abs_bone_matrix = m3_pose_matrix

                            frame_to_bone_abs_pose_matrix[jj + frame_start][bone] = abs_bone_matrix @ self.bone_to_iref[bone]

        # place armature in the default pose again so that default values of m3 properties are accessed properly
        ob_anim_data_set(self.scene, self.ob, None)
        self.scene.frame_set(0)

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

        model.skin_bone_count = max([self.bone_name_indices[bone.name] for bone in self.skinned_bones]) + 1
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

        bone_bounding_points = {bone: [] for bone in self.bones}

        for ob_index, ob in enumerate(mesh_objects):
            bm = bmesh.new(use_operators=True)
            bm.from_object(ob, self.depsgraph)
            bmesh.ops.transform(bm, matrix=ob.matrix_local, verts=bm.verts, use_shapekey=False)
            bmesh.ops.triangulate(bm, faces=bm.faces)

            layer_deform = bm.verts.layers.deform.verify()
            layer_color = bm.loops.layers.color.get('m3color')
            layer_alpha = bm.loops.layers.color.get('m3alpha')

            layers_uv = bm.loops.layers.uv.values()

            for ii in range(0, self.uv_count):
                custom_uv_name = getattr(ob, f'm3_mesh_uv{ii}')
                if custom_uv_name:
                    for uv_layer in layers_uv:
                        if custom_uv_name == uv_layer.name:
                            layers_uv[ii] = uv_layer
                            break

            layers_uv = layers_uv[0:self.uv_count]
            layer_tan = layers_uv[0]

            first_vertex_index = len(m3_vertices)
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

            no_deform_verts = 0

            for face in bm.faces:
                c1, c2, c3 = (L.vert.co for L in face.loops)
                u1, u2, u3 = (L[layer_tan].uv[0] for L in face.loops)
                v1, v2, v3 = (L[layer_tan].uv[1] for L in face.loops)
                d = (v2 - v1) * (u3 - u1) - (u2 - u1) * (v3 - v1)
                try:
                    tan = (((v3 - v1) * (c2 - c1) - (v2 - v1) * (c3 - c1)) / -d).normalized()
                except ZeroDivisionError:
                    tan = mathutils.Vector((0, 0, 0))

                for loop in face.loops:
                    co = loop.vert.co
                    m3_vert = m3_vertex_desc.instance()
                    m3_vert.pos = to_m3_vec3(co)

                    # only count groups which have a lookup match, sort by weight and then limit to a length of 4
                    deformations = []
                    for deformation in loop.vert[layer_deform].items():
                        lookup_ii = group_to_lookup_ii.get(deformation[0])
                        if lookup_ii is not None and deformation[1]:
                            deformations.append([lookup_ii, deformation[1]])
                            bone_bounding_points[self.bones[region_lookup[lookup_ii]]].append(co.copy())

                    deformations.sort(key=lambda x: x[1])
                    deformations = deformations[0:min(4, len(deformations))]

                    if not len(deformations):
                        no_deform_verts += 1

                    # normalize the weights
                    sum_weight = 0
                    for index, weight in deformations:
                        sum_weight += weight

                    remaining_weight = 255
                    for ii in range(len(deformations)):
                        lookup = deformations[ii][0]
                        weight = min(remaining_weight, round(deformations[ii][1] / sum_weight * 255))
                        remaining_weight = max(0, remaining_weight - weight)
                        if weight:
                            setattr(m3_vert, 'lookup' + str(ii), lookup)
                            setattr(m3_vert, 'weight' + str(ii), weight)

                    for ii in range(0, 4):
                        uv_layer = layers_uv[ii] if ii < len(layers_uv) else None
                        setattr(m3_vert, 'uv' + str(ii), to_m3_uv(loop[uv_layer].uv) if uv_layer else to_m3_uv((0, 0)))

                    if vertex_rgba:
                        try:
                            m3_vert.col = to_m3_color((*loop[layer_color][0:3], sum(loop[layer_alpha][0:3]) / 3))
                        except AttributeError:
                            m3_vert.col = to_m3_color((1, 1, 1, 1))

                    m3_vert.normal = to_m3_vec3_uint8(loop.vert.normal)
                    m3_vert.tan = to_m3_vec3_uint8(tan)
                    m3_vert.sign = 0 if d < 0 else 255

                    id_list = [
                        m3_vert.pos.x, m3_vert.pos.y, m3_vert.pos.z, m3_vert.lookup0, m3_vert.lookup1, m3_vert.lookup2, m3_vert.lookup3, m3_vert.sign,
                        m3_vert.weight0, m3_vert.weight1, m3_vert.weight2, m3_vert.weight3, m3_vert.normal.x, m3_vert.normal.y, m3_vert.normal.z,
                    ]

                    if vertex_rgba:
                        id_list.extend((m3_vert.col.r, m3_vert.col.g, m3_vert.col.b, m3_vert.col.a))

                    for ii in range(len(layers_uv)):
                        uv = getattr(m3_vert, 'uv' + str(ii))
                        id_list.extend((uv.x, uv.y))

                    id_tuple = tuple(id_list)
                    id_index = region_vert_id_to_vert.get(id_tuple)
                    if id_index is None:
                        id_index = region_vert_count
                        region_vert_id_to_vert[id_tuple] = id_index

                        vertex_lookups_used = max(vertex_lookups_used, len(deformations))

                        m3_vertex_desc.instance_validate(m3_vert, 'vertex')
                        region_vertices.append(m3_vert)
                        region_vert_count += 1

                    region_faces.append(id_index)

            if no_deform_verts:
                self.warn_strings.append(f'{str(ob)} has at least one vertex with no weight given to a valid bone and will not be exported')
                continue

            m3_vertices.extend(region_vertices)
            m3_lookup.extend(region_lookup)

            # TODO mesh flags for versions 4+
            for ii, batch in enumerate(ob.m3_mesh_batches):
                first_face_index = len(m3_faces)
                m3_faces.extend(region_faces)
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
                bone = shared.m3_pointer_get(self.ob.pose.bones, batch.bone)
                m3_batch = batch_section.content_add()
                m3_batch.material_reference_index = self.matref_handle_indices[batch.material.handle]
                m3_batch.region_index = len(region_section) - 1
                m3_batch.bone = self.bone_name_indices[bone.name] if bone else -1

        self.bone_bound_vecs = {}

        for bone in self.bones:
            if not bone_bounding_points[bone]:
                continue
            x_cos, y_cos, z_cos = zip(*bone_bounding_points[bone])
            vec_min = mathutils.Vector((min(x_cos), min(y_cos), min(z_cos)))
            vec_max = mathutils.Vector((max(x_cos), max(y_cos), max(z_cos)))
            self.bone_bound_vecs[bone] = (vec_min, vec_max)

        self.region_section = region_section

        msec_section = self.m3.section_for_reference(div, 'msec', version=1)
        msec = msec_section.content_add()
        msec.bounding = self.init_anim_ref_bnds(bounding_vectors_from_bones(self.bone_bound_vecs, self.bone_to_abs_pose_matrix))

        vertex_section.content_add(*list(m3_vertex_desc.instances_to_bytearray(m3_vertices)))
        face_section.content_add(*m3_faces)
        bone_lookup_section = self.m3.section_for_reference(model, 'bone_lookup')
        bone_lookup_section.content_add(*m3_lookup)

    def create_attachment_points(self, model, attachments):
        attachment_point_section = self.m3.section_for_reference(model, 'attachment_points', version=1)

        # manually add into section list *after* name sections are added to conform with original exporting conventions
        attachment_point_addon_section = self.m3.section_for_reference(model, 'attachment_points_addon', pos=None)

        for attachment in attachments:
            attachment_bone = shared.m3_pointer_get(self.ob.pose.bones, attachment.bone)

            m3_attachment = attachment_point_section.content_add()
            m3_attachment_name_section = self.m3.section_for_reference(m3_attachment, 'name')
            m3_attachment_name_section.content_from_string(attachment.name)
            m3_attachment.bone = self.bone_name_indices[attachment_bone.name]
            attachment_point_addon_section.content_add(0xffff)
        # add volumes later so that sections are in order of the modl data

        self.m3.append(attachment_point_addon_section)

    def create_lights(self, model, lights):
        light_section = self.m3.section_for_reference(model, 'lights', version=7)

        for light in lights:
            light_bone = shared.m3_pointer_get(self.ob.pose.bones, light.bone)

            m3_light = light_section.content_add()
            m3_light.bone = self.bone_name_indices[light_bone.name]
            processor = M3OutputProcessor(self, light, m3_light)
            io_shared.io_light(processor)

        # currently will never be a number below 0, not sure if this is correct
        for action, stc_list in self.action_to_stc.items():
            action_data = self.action_to_anim_data[action]['SDR3']
            for m3_light in light_section:
                m3_light.unknown148 = max(m3_light.unknown148, *action_data[m3_light.attenuation_far.header.id][1])

    def create_shadow_boxes(self, model, shadow_boxes):
        if int(self.ob.m3_model_version) < 21:
            return

        shadow_box_section = self.m3.section_for_reference(model, 'shadow_boxes', version=0)

        for shadow_box in shadow_boxes:
            shadow_box_bone = shared.m3_pointer_get(self.ob.pose.bones, shadow_box.bone)
            m3_shadow_box = shadow_box_section.content_add()
            m3_shadow_box.bone = self.bone_name_indices[shadow_box_bone.name]
            processor = M3OutputProcessor(self, shadow_box, m3_shadow_box)
            io_shared.io_shadow_box(processor)

    def create_cameras(self, model, cameras):
        camera_section = self.m3.section_for_reference(model, 'cameras', version=3)

        for camera in cameras:
            camera_bone = shared.m3_pointer_get(self.ob.pose.bones, camera.bone)
            m3_camera = camera_section.content_add()
            m3_camera_name_section = self.m3.section_for_reference(m3_camera, 'name')
            m3_camera_name_section.content_from_string(camera.name)
            m3_camera.bone = self.bone_name_indices[camera_bone.name]
            processor = M3OutputProcessor(self, camera, m3_camera)
            io_shared.io_camera(processor)

        cameras_addon_section = self.m3.section_for_reference(model, 'cameras_addon')
        cameras_addon_section.content_add(*(0xffff for camera in cameras))

    def create_materials(self, model, matrefs, versions):
        matref_section = self.m3.section_for_reference(model, 'material_references')

        layer_desc = io_m3.structures['LAYR'].get_version(self.ob.m3_materiallayers_version)
        # manually add into section list if referenced
        null_layer_section = io_m3.M3Section(desc=layer_desc, index_entry=None, references=[], content=[])
        null_layer_section.content_add()

        matrefs_typed = {ii: [] for ii in range(0, 13)}
        for matref in matrefs:
            m3_matref = matref_section.content_add()
            m3_matref.type = shared.material_collections.index(matref.mat_type)
            m3_matref.material_index = len(matrefs_typed[m3_matref.type])
            matrefs_typed[m3_matref.type].append(matref)

        handle_to_layer_section = {}
        for type_ii, matrefs in matrefs_typed.items():
            if not matrefs:
                continue
            mat_section = self.m3.section_for_reference(model, shared.material_type_to_model_reference[type_ii], version=versions[type_ii])
            mat_collection = getattr(self.ob, 'm3_' + shared.material_type_to_model_reference[type_ii])
            for matref in matrefs:
                mat = shared.m3_pointer_get(mat_collection, matref.mat_handle)
                m3_mat = mat_section.content_add()
                m3_mat_name_section = self.m3.section_for_reference(m3_mat, 'name')
                m3_mat_name_section.content_from_string(matref.name)
                processor = M3OutputProcessor(self, mat, m3_mat)
                io_shared.material_type_io_method[type_ii](processor)

                for layer_name in shared.material_type_to_layers[type_ii]:
                    layer_name_full = 'layer_' + layer_name

                    if not hasattr(m3_mat, layer_name_full):
                        continue

                    m3_layer_ref = getattr(m3_mat, layer_name_full)

                    layer = shared.m3_pointer_get(self.ob.m3_materiallayers, getattr(mat, layer_name_full))

                    if not layer or (layer.color_type == 'BITMAP' and not layer.color_bitmap):
                        null_layer_section.references.append(m3_layer_ref)
                    else:

                        if layer.video_channel != -1:
                            m3_mat.bit_set('rtt_channels_used', 'channel' + str(layer.video_channel), True)

                        if layer.bl_handle in handle_to_layer_section.keys():
                            handle_to_layer_section[layer.bl_handle].references.append(m3_layer_ref)
                        else:
                            layer_section = self.m3.section_for_reference(m3_mat, layer_name_full, version=self.ob.m3_materiallayers_version)
                            handle_to_layer_section[layer.bl_handle] = layer_section
                            m3_layer = layer_section.content_add()

                            if layer.color_type == 'BITMAP':
                                m3_layer_bitmap_section = self.m3.section_for_reference(m3_layer, 'color_bitmap')
                                m3_layer_bitmap_section.content_from_string(layer.color_bitmap)
                            else:
                                m3_layer.bit_set('flags', 'color', True)

                            processor = M3OutputProcessor(self, layer, m3_layer)
                            io_shared.io_material_layer(processor)

                            m3_layer.fresnel_max_offset = layer.fresnel_max - layer.fresnel_min

                            if int(self.ob.m3_materiallayers_version) >= 24:
                                m3_layer.uv_triplanar_scale.null = to_m3_vec3((1.0, 1.0, 1.0))

                            if int(self.ob.m3_materiallayers_version) >= 25:
                                m3_layer.fresnel_inverted_mask_x = 1 - layer.fresnel_mask[0]
                                m3_layer.fresnel_inverted_mask_y = 1 - layer.fresnel_mask[1]
                                m3_layer.fresnel_inverted_mask_z = 1 - layer.fresnel_mask[2]

                            m3_layer.bit_set('flags', 'particle_uv_flipbook', m3_layer.uv_source == 6)

                            if layer.color_bitmap.endswith('.ogg') and layer.color_type == 'BITMAP':
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
                            m3_layer.unknowna4ec0796 = self.init_anim_ref_uint32(0)
                            m3_layer.unknowna44bf452 = self.init_anim_ref_float(1.0)
                            m3_layer.unknowna44bf452.null = 1.0

                if type_ii == 1:  # standard material
                    m3_mat.bit_set('additional_flags', 'depth_blend_falloff', mat.depth_blend_falloff != 0.0)
                    m3_mat.bit_set('additional_flags', 'vertex_color', mat.vertex_color or matref.bl_handle in self.vertex_color_mats)
                    m3_mat.bit_set('additional_flags', 'vertex_alpha', mat.vertex_alpha or matref.bl_handle in self.vertex_alpha_mats)
                    if mat.parallax_height_header.flags == -1:
                        m3_mat.parallax_height.header.flags = 0x8
                elif type_ii == 3:  # composite material
                    valid_sections = []
                    for section in mat.sections:
                        matref = shared.m3_pointer_get(self.ob.m3_materialrefs, section.material.handle)
                        if matref:
                            valid_sections.append(section)
                    if len(valid_sections):
                        section_section = self.m3.section_for_reference(m3_mat, 'sections')
                        for section in valid_sections:
                            m3_section = section_section.content_add()
                            m3_section.material_reference_index = self.matref_handle_indices[section.material.handle]
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
        particle_system_section = self.m3.section_for_reference(model, 'particle_systems', version=version)

        for system in systems:
            system_bone = shared.m3_pointer_get(self.ob.pose.bones, system.bone)

            m3_system = particle_system_section.content_add()
            m3_system.bone = self.bone_name_indices[system_bone.name]
            m3_system.material_reference_index = self.matref_handle_indices[system.material.handle]

            processor = M3OutputProcessor(self, system, m3_system)
            io_shared.io_particle_system(processor)

            if system.tail_type == 'CLAMP':
                m3_system.bit_set('flags', 'tail_clamp', True)
            elif system.tail_type == 'FIX':
                m3_system.bit_set('flags', 'tail_fix', True)

            if system.emit_count_header.flags == -1:
                m3_system.emit_count.header.flags = 0x6

            trail_system = shared.m3_pointer_get(systems, system.trail_system)
            if trail_system:
                m3_system.trail_system = systems.index(trail_system)
                m3_system.bit_set('flags', 'use_trailing_particle', True)

            if int(version) >= 12:
                m3_system.local_forces_fb = m3_system.local_forces
                m3_system.world_forces_fb = m3_system.world_forces
                try:
                    m3_system.uv_flipbook_col_fraction = 1 / m3_system.uv_flipbook_cols
                    m3_system.uv_flipbook_row_fraction = 1 / m3_system.uv_flipbook_rows
                except ZeroDivisionError:
                    m3_system.uv_flipbook_col_fraction = float('inf')
                    m3_system.uv_flipbook_row_fraction = float('inf')

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
                m3_system.unknown18a90564.null = to_m3_vec2((1.0, 1.0))

                if m3_system.emit_shape == 7:
                    region_indices = set()
                    for mesh_pointer in system.emit_shape_meshes:
                        if mesh_pointer.bl_object in self.export_regions:
                            region_indices.add(self.ob_to_region_index.index(mesh_pointer.bl_object))
                    if len(region_indices):
                        region_indices_section = self.m3.section_for_reference(m3_system, 'emit_shape_regions')
                        region_indices_section.content_add(*region_indices)
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
            for ii, particle_copy in enumerate(copies):
                for pointer in particle_copy.systems:
                    if pointer.handle == system.bl_handle:
                        copy_indices.append(ii)

            if system.model_path:
                model_paths_section = self.m3.section_for_reference(m3_system, 'model_paths')
                model_path = model_paths_section.content_add()
                model_path_string_section = self.m3.section_for_reference(model_path, 'path')
                model_path_string_section.content_from_string(system.model_path)
                m3_system.bit_set('flags', 'model_particles', True)

            if len(copy_indices):
                copy_indices_section = self.m3.section_for_reference(m3_system, 'copy_indices')
                copy_indices_section.content_add(*copy_indices)

        if len(copies):
            particle_copy_section = self.m3.section_for_reference(model, 'particle_copies', version=0)
        for particle_copy in copies:
            particle_copy_bone = shared.m3_pointer_get(self.ob.pose.bones, particle_copy.bone)
            m3_copy = particle_copy_section.content_add()
            m3_copy.bone = self.bone_name_indices[particle_copy_bone.name]
            processor = M3OutputProcessor(self, particle_copy, m3_copy)
            io_shared.io_particle_copy(processor)

    def create_ribbons(self, model, ribbons, splines, version):
        ribbon_section = self.m3.section_for_reference(model, 'ribbons', version=version)

        handle_to_spline_sections = {}
        for ribbon in ribbons:
            ribbon_bone = shared.m3_pointer_get(self.ob.pose.bones, ribbon.bone)

            m3_ribbon = ribbon_section.content_add()
            m3_ribbon.bone = self.bone_name_indices[ribbon_bone.name]
            m3_ribbon.material_reference_index = self.matref_handle_indices[ribbon.material.handle]
            processor = M3OutputProcessor(self, ribbon, m3_ribbon)
            io_shared.io_ribbon(processor)

            m3_ribbon.unknown75e0b576 = self.init_anim_ref_float()
            m3_ribbon.unknownee00ae0a = self.init_anim_ref_float()
            m3_ribbon.unknown1686c0b7 = self.init_anim_ref_float()
            m3_ribbon.unknown9eba8df8 = self.init_anim_ref_float()

            m3_ribbon.color_base.null.a = 0xFF
            m3_ribbon.color_mid.null.a = 0xFF
            m3_ribbon.color_tip.null.a = 0xFF

            if ribbon.spline.handle not in handle_to_spline_sections.keys():
                spline = shared.m3_pointer_get(self.ob.m3_ribbonsplines, ribbon.spline)
                if spline in splines:
                    spline_section = self.m3.section_for_reference(m3_ribbon, 'spline', version=0)
                    handle_to_spline_sections[ribbon.spline.handle] = spline_section

                    for point in spline.points:
                        point_bone = shared.m3_pointer_get(self.ob.pose.bones, point.bone)
                        m3_point = spline_section.content_add()
                        m3_point.bone = self.bone_name_indices[point_bone.name]
                        processor = M3OutputProcessor(self, point, m3_point)
                        io_shared.io_ribbon_spline(processor)

                        m3_point.unknown3 = self.init_anim_ref_float(1.0)
                        m3_point.unknown4 = self.init_anim_ref_float(1.0)
            else:
                handle_to_spline_sections[ribbon.spline.handle].references.append(m3_ribbon.spline)

    def create_projections(self, model, projections):
        projection_section = self.m3.section_for_reference(model, 'projections', version=5)

        for projection in projections:
            projection_bone = shared.m3_pointer_get(self.ob.pose.bones, projection.bone)
            m3_projection = projection_section.content_add()
            m3_projection.bone = self.bone_name_indices[projection_bone.name]
            m3_projection.material_reference_index = self.matref_handle_indices[projection.material.handle]
            processor = M3OutputProcessor(self, projection, m3_projection)
            io_shared.io_projection(processor)

            m3_projection.unknown58ae2b94 = self.init_anim_ref_vec3()
            m3_projection.unknownf1f7110b = self.init_anim_ref_float()
            m3_projection.unknown2035f500 = self.init_anim_ref_float()
            m3_projection.unknown80d8189b = self.init_anim_ref_float()

    def create_forces(self, model, forces):
        force_section = self.m3.section_for_reference(model, 'forces', version=2)

        for force in forces:
            force_bone = shared.m3_pointer_get(self.ob.pose.bones, force.bone)
            m3_force = force_section.content_add()
            m3_force.bone = self.bone_name_indices[force_bone.name]
            processor = M3OutputProcessor(self, force, m3_force)
            io_shared.io_force(processor)

    def create_warps(self, model, warps):
        warp_section = self.m3.section_for_reference(model, 'warps', version=1)

        for warp in warps:
            warp_bone = shared.m3_pointer_get(self.ob.pose.bones, warp.bone)
            m3_warp = warp_section.content_add()
            m3_warp.bone = self.bone_name_indices[warp_bone.name]
            processor = M3OutputProcessor(self, warp, m3_warp)
            io_shared.io_warp(processor)

    def create_physics_bodies(self, model, physics_bodies, body_version, shape_version):
        physics_body_section = self.m3.section_for_reference(model, 'physics_rigidbodies', version=body_version)

        shape_to_section = {}
        for physics_body in physics_bodies:
            physics_body_bone = shared.m3_pointer_get(self.ob.pose.bones, physics_body.bone)

            m3_physics_body = physics_body_section.content_add()
            m3_physics_body.bone = self.bone_name_indices[physics_body_bone.name]
            processor = M3OutputProcessor(self, physics_body, m3_physics_body)
            io_shared.io_rigid_body(processor)

            if physics_body.physics_shape.handle in self.physics_shape_handle_to_volumes.keys():
                if not shape_to_section.get(physics_body.physics_shape.handle):
                    shape_section = self.m3.section_for_reference(m3_physics_body, 'physics_shape', version=shape_version)

                    for volume in self.physics_shape_handle_to_volumes[physics_body.physics_shape.handle]:
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
                    shape_section = self.shape_to_section[physics_body.physics_shape.handle]
                    shape_section.references.append(m3_physics_body.physics_shape)

    def create_physics_joints(self, model, physics_bodies, physics_joints):
        physics_joint_section = self.m3.section_for_reference(model, 'physics_joints', version=0)

        for physics_joint in physics_joints:
            body1 = shared.m3_pointer_get(physics_bodies, physics_joint.rigidbody1)
            body2 = shared.m3_pointer_get(physics_bodies, physics_joint.rigidbody2)
            bone1 = shared.m3_pointer_get(self.ob.pose.bones, body1.bone)
            bone2 = shared.m3_pointer_get(self.ob.pose.bones, body2.bone)

            # bone1_head = bone1.matrix_local.translation
            # bone1_vec = bone1.matrix_local.col[1].to_3d().normalized()

            # bone2_head = bone2.matrix_local.translation
            # bone2_vec = bone2.matrix_local.col[1].to_3d().normalized()

            # print(bone1_vec - bone2_vec)
            # print(bone2_vec - bone1_vec)
            # print()

            # # this produces the
            # print(bone2.matrix_local - bone1.matrix_local)
            # print(bone1.matrix_local - bone2.matrix_local)
            # print(bone2.matrix_local - bone1.matrix_local)
            # print(bone1.matrix_local @ bone2.matrix_local)
            # print(bone2.matrix_local @ bone1.matrix_local)
            # print()

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
        if int(self.ob.m3_model_version) < 28:
            return

        physics_cloth_section = self.m3.section_for_reference(model, 'physics_cloths', version=version)

        constraints_sections = {}
        for physics_cloth in physics_cloths:
            mesh_ob = physics_cloth.mesh_object
            sim_ob = physics_cloth.simulator_object

            regn_inf = self.region_section[self.ob_to_region_index.index(mesh_ob)]
            regn_sim = self.region_section[self.ob_to_region_index.index(sim_ob)]

            # set flags for regions used by the cloth behavior
            regn_inf.bit_set('flags', 'hidden', True)
            regn_inf.bit_set('flags', 'placeholder', True)
            regn_inf.bit_set('flags', 'cloth_influenced', True)

            regn_sim.bit_set('flags', 'hidden', True)
            regn_sim.bit_set('flags', 'cloth_simulated', True)

            m3_physics_cloth = physics_cloth_section.content_add()
            m3_physics_cloth.simulation_region_index = self.ob_to_region_index.index(sim_ob)

            processor = M3OutputProcessor(self, physics_cloth, m3_physics_cloth)
            io_shared.io_cloth(processor)

            skin_bones_section = self.m3.section_for_reference(m3_physics_cloth, 'skin_bones')
            skin_bones = set()
            vertex_simulated_section = self.m3.section_for_reference(m3_physics_cloth, 'vertex_simulated')
            vertex_simulated_list = []
            vertex_bones_section = self.m3.section_for_reference(m3_physics_cloth, 'vertex_bones')
            vertex_weights_section = self.m3.section_for_reference(m3_physics_cloth, 'vertex_weights')

            if physics_cloth.constraint_set.handle not in constraints_sections.keys():
                constraints_section = self.m3.section_for_reference(m3_physics_cloth, 'constraints', version=0)
                constraints_sections[physics_cloth.constraint_set.handle] = constraints_section
                for volume in self.physics_cloth_constraint_handle_to_volumes[physics_cloth.constraint_set.handle]:
                    volume_bone = shared.m3_pointer_get(self.ob.pose.bones, volume.bone)
                    db = self.ob.data.bones.get(volume_bone.name)
                    skin_bones.add(self.bone_name_indices[volume_bone.name])
                    m3_volume = constraints_section.content_add()
                    m3_volume.bone = self.bone_name_indices[volume_bone.name]
                    db_rot = db.matrix_local.to_euler('XYZ')
                    mat_loc = volume.location + db.head_local
                    mat_rot = mathutils.Euler(tuple(volume.rotation[ii] + db_rot[ii] for ii in range(3)))
                    m3_volume.matrix = to_m3_matrix(mathutils.Matrix.LocRotScale(mat_loc, mat_rot, volume.scale) @ io_shared.rot_fix_matrix)
                    m3_volume.height = volume.height
                    m3_volume.radius = volume.radius
            else:
                constraints_section = constraints_sections[physics_cloth.constraint_set.handle]
                constraints_section.references.append(m3_physics_cloth.constraints)

            influence_map_section = self.m3.section_for_reference(m3_physics_cloth, 'influence_map', version=0)
            m3_influence_map = influence_map_section.content_add()
            m3_influence_map.influenced_region_index = self.ob_to_region_index.index(mesh_ob)
            m3_influence_map.simulation_region_index = self.ob_to_region_index.index(sim_ob)

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

            skin_bones_section.content_add(*list(skin_bones))
            vertex_simulated_section.content_add(*vertex_simulated_list)

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
        ik_joint_section = self.m3.section_for_reference(model, 'ik_joints', version=0)

        for ik_joint, bones in zip(ik_joints, self.export_ik_joint_bones):
            m3_ik_joint = ik_joint_section.content_add()
            m3_ik_joint.bone_target = self.bone_name_indices[bones[0].name]
            m3_ik_joint.bone_base = self.bone_name_indices[bones[1].name]
            processor = M3OutputProcessor(self, ik_joint, m3_ik_joint)
            io_shared.io_ik(processor)

    def create_turrets(self, model, turrets, part_version):
        turret_part_section = self.m3.section_for_reference(model, 'turret_parts', version=part_version)
        turret_section = self.m3.section_for_reference(model, 'turrets', version=0)

        base_quat = mathutils.Quaternion((0.0, 0.0, -1.0), 1.5707961320877075)

        # sort parts by their bone index
        part_to_bone_index = {self.bone_name_indices[shared.m3_pointer_get(self.ob.pose.bones, part.bone).name]: part for part in self.export_turret_parts}
        turret_parts_index = []
        group_id_main_bone = {}

        for part in self.export_turret_parts:
            if part.main_part:
                group_id_main_bone[part.group_id] = shared.m3_pointer_get(self.ob.pose.bones, part.bone)

        for bone_index in sorted(list(part_to_bone_index.keys())):
            part = part_to_bone_index[bone_index]
            turret_parts_index.append(part)

            bone = shared.m3_pointer_get(self.ob.pose.bones, part.bone)
            m3_part = turret_part_section.content_add()
            m3_part.bone = self.bone_name_indices[bone.name]
            processor = M3OutputProcessor(self, part, m3_part)
            io_shared.io_turret_part(processor)

            forward_mat = mathutils.Euler(part.forward).to_quaternion().to_matrix().to_4x4()
            m3_part.matrix_forward.x = to_m3_vec4(forward_mat.col[0].yzxw)
            m3_part.matrix_forward.y = to_m3_vec4(forward_mat.col[1].yzxw)
            m3_part.matrix_forward.z = to_m3_vec4(forward_mat.col[2].yzxw)
            m3_part.matrix_forward.w = to_m3_vec4((0.0, 0.0, 0.0, 1.0))

            # m3_part.matrix_forward = to_m3_matrix(forward_mat)

            db = self.ob.data.bones.get(bone.name)

            if db.parent:
                upquat = to_m3_vec4_quat(db.matrix_local.to_quaternion().rotation_difference(db.parent.matrix_local.transposed().to_quaternion()))
            else:
                m3_part.quat_up0 = to_m3_vec4_quat(db.matrix_local.to_quaternion().rotation_difference(base_quat))

            # m3_part.quat_up1 = to_m3_vec4_quat()

            if group_id_main_bone.get(part.group_id) and not part.main_part:
                mdb = self.ob.data.bones.get(group_id_main_bone[part.group_id].name)
                m3_part.main_bone_offset = to_m3_vec3(db.matrix_local.translation - mdb.matrix_local.translation)
            else:
                m3_part.bit_set('flags', 'main_part', True)

        for turret in turrets:
            m3_turret = turret_section.content_add()
            m3_turret_part_index_section = self.m3.section_for_reference(m3_turret, 'parts')
            m3_turret_name_section = self.m3.section_for_reference(m3_turret, 'name')
            m3_turret_name_section.content_from_string(turret.name)

            for part in turret.parts:
                try:
                    m3_turret_part_index_section.content_add(turret_parts_index.index(part))
                except ValueError:
                    pass  # part is not in self.export_turret_parts

    def create_irefs(self, model):
        iref_section = self.m3.section_for_reference(model, 'bone_rests')

        for bone in self.bones:
            iref = iref_section.content_add()
            iref.matrix = to_m3_matrix(self.bone_to_iref[bone])

    def create_hittests(self, model, hittests):
        hittests_section = self.m3.section_for_reference(model, 'hittests', version=1)

        ht_tight = self.ob.m3_hittest_tight

        ht_tight_bone = shared.m3_pointer_get(self.ob.pose.bones, ht_tight.bone)

        if ht_tight_bone:
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
            hittest_bone = shared.m3_pointer_get(self.ob.pose.bones, hittest.bone)

            m3_hittest = hittests_section.content_add()
            m3_hittest.bone = self.bone_name_indices[hittest_bone.name]
            m3_hittest.shape = hittest.bl_rna.properties['shape'].enum_items.find(hittest.shape)

            m3_hittest.size0, m3_hittest.size1, m3_hittest.size2 = hittest.size
            m3_hittest.matrix = to_m3_matrix(mathutils.Matrix.LocRotScale(hittest.location, hittest.rotation, hittest.scale))

            if m3_hittest.shape == 4:
                self.get_basic_volume_object(hittest.mesh_object, m3_hittest)

    def create_attachment_volumes(self, model, volumes):
        attachment_volume_section = self.m3.section_for_reference(model, 'attachment_volumes', version=0)

        if int(self.ob.m3_model_version) >= 23:
            attachment_volume_addon0_section = self.m3.section_for_reference(model, 'attachment_volumes_addon0')
            attachment_volume_addon0_section.content_add(*(0 for volume in volumes))
            attachment_volume_addon1_section = self.m3.section_for_reference(model, 'attachment_volumes_addon1')
            attachment_volume_addon1_section.content_add(*(0 for volume in volumes))

        for volume, bone in zip(volumes, self.attachment_bones):
            m3_volume = attachment_volume_section.content_add()
            m3_volume.bone0 = self.bone_name_indices[bone.name]
            m3_volume.bone1 = self.bone_name_indices[bone.name]
            m3_volume.bone2 = self.bone_name_indices[bone.name]
            m3_volume.shape = volume.bl_rna.properties['shape'].enum_items.find(volume.shape)
            m3_volume.size0, m3_volume.size1, m3_volume.size2 = volume.size
            m3_volume.matrix = to_m3_matrix(mathutils.Matrix.LocRotScale(volume.location, volume.rotation, volume.scale))

            if m3_volume.shape == 4:
                self.get_basic_volume_object(volume.mesh_object, m3_volume)

    def create_billboards(self, model, billboards):
        billboard_section = self.m3.section_for_reference(model, 'billboards')

        for billboard, bone in zip(billboards, self.billboard_bones):
            m3_billboard = billboard_section.content_add()
            m3_billboard.bone = self.bone_name_indices[bone.name]
            processor = M3OutputProcessor(self, billboard, m3_billboard)
            io_shared.io_billboard(processor)

            m3_billboard.up = to_m3_quat(mathutils.Euler(billboard.up).to_quaternion())
            m3_billboard.forward = to_m3_quat(mathutils.Euler(billboard.forward).to_quaternion())

    def create_tmd_data(self, model, tmd_data):
        tmd_section = self.m3.section_for_reference(model, 'tmd_data', version=1)

        for tmd in tmd_data:
            m3_tmd = tmd_section.content_add()
            processor = M3OutputProcessor(self, tmd, m3_tmd)
            io_shared.io_tmd(processor)

            tmd_vec_section = self.m3.section_for_reference(m3_tmd, 'vectors')
            for vec_item in tmd.vectors:
                tmd_vec_section.content_add(to_m3_vec3(vec_item.vector))

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
            vert_section.content_add(*vert_data)
            face_section = self.m3.section_for_reference(m3, 'face_data')
            face_section.content_add(*face_data)
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
            plane_equation_data = []
            loop_data = []
            polygon_data = []

            loop_desc = io_m3.structures['DMSE'].get_version(0)

            polygon_medians = []

            for face in bm.faces:
                polygon_data.append(face.loops[0].index)
                loop_count = len(face.loops)
                for ii, loop in enumerate(face.loops):
                    next_loop = (ii + 1) if ii < loop_count - 1 else 0
                    m3_loop = loop_desc.instance()
                    m3_loop.unknown00 = 1
                    m3_loop.vertex = loop.vert.index
                    m3_loop.polygon = face.index
                    m3_loop.loop = face.loops[next_loop].index
                    loop_data.append(m3_loop)

                # calculating plane equation
                # simply taking first 3 verts since we assume that the face is planar
                v0 = face.verts[0].co
                v1 = face.verts[1].co
                v2 = face.verts[2].co

                a = v0 - v1
                b = v0 - v2

                r, s, t = a.cross(b)

                k = ((r * v0[0]) + (s * v0[1]) + (t * v0[2]))

                pe = mathutils.Vector((r, s, t, k))
                pen = pe.normalized()
                pen[3] = pe[3] * (pen[0] / pe[0])

                vec = face.calc_center_bounds()
                polygon_medians.append(vec)
                plane_equation_data.append(to_m3_vec4(pen))

            vert_section = self.m3.section_for_reference(m3, 'vertices')
            vert_section.content_add(*vert_data)
            plane_equation_section = self.m3.section_for_reference(m3, 'plane_equations')
            plane_equation_section.content_add(*plane_equation_data)
            loop_section = self.m3.section_for_reference(m3, 'loops')
            loop_section.content_add(*loop_data)
            polygon_section = self.m3.section_for_reference(m3, 'polygons')
            polygon_section.content_add(*polygon_data)

            m3.polygons_center = to_m3_vec3([(sum([poly_med[ii] for poly_med in polygon_medians]) / len(polygon_medians)) for ii in range(3)])
            m3.vertices_count = len(vert_section)
            m3.polygons_count = len(plane_equation_section)
            m3.loops_count = len(loop_section)

            self.mesh_to_physics_volume_sections[mesh_ob.name] = [vert_section, plane_equation_section, loop_section, polygon_section]
        else:
            vert_section, plane_equation_section, loop_section, polygon_section = self.mesh_to_physics_volume_sections[mesh_ob.name]
            vert_section.references.append(m3.vertices)
            plane_equation_section.references.append(m3.plane_equations)
            loop_section.references.append(m3.loops)
            polygon_section.references.append(m3.polygons)

    def init_anim_header(self, interpolation, flags, anim_id):
        anim_ref_header = io_m3.structures['AnimationReferenceHeader'].get_version(0).instance()
        anim_ref_header.id = anim_id
        anim_ref_header.interpolation = interpolation
        anim_ref_header.flags = flags
        return anim_ref_header

    def init_anim_ref_int16(self, val=0, interpolation=-1, flags=-1, anim_id=1):
        anim_ref = io_m3.structures['Int16AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(1 if interpolation == -1 else interpolation, 0x0 if flags == -1 else flags, anim_id)
        anim_ref.default = val
        anim_ref.null = 0
        return anim_ref

    def init_anim_ref_uint16(self, val=0, interpolation=-1, flags=-1, anim_id=1):
        anim_ref = io_m3.structures['UInt16AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(0 if interpolation == -1 else interpolation, 0x0 if flags == -1 else flags, anim_id)
        anim_ref.default = val
        anim_ref.null = 0
        return anim_ref

    def init_anim_ref_uint32(self, val=0, interpolation=-1, flags=-1, anim_id=1):
        anim_ref = io_m3.structures['UInt32AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(0 if interpolation == -1 else interpolation, 0x0 if flags == -1 else flags, anim_id)
        anim_ref.default = int(val)  # casting to int because sometimes bools use this
        anim_ref.null = 0
        return anim_ref

    def init_anim_ref_flag(self, val=0, interpolation=-1, flags=-1, anim_id=1):
        anim_ref = io_m3.structures['FlagAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(1 if interpolation == -1 else interpolation, 0x0 if flags == -1 else flags, anim_id)
        anim_ref.default = int(val)
        anim_ref.null = 0
        return anim_ref

    def init_anim_ref_float(self, val=0.0, interpolation=-1, flags=-1, anim_id=1):
        anim_ref = io_m3.structures['FloatAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(1 if interpolation == -1 else interpolation, 0x0 if flags == -1 else flags, anim_id)
        anim_ref.default = val
        anim_ref.null = 0.0
        return anim_ref

    def init_anim_ref_vec2(self, val=None, interpolation=-1, flags=-1, anim_id=1):
        anim_ref = io_m3.structures['Vector2AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(1 if interpolation == -1 else interpolation, 0x6 if flags == -1 else flags, anim_id)
        anim_ref.default = to_m3_vec2(val)
        anim_ref.null = to_m3_vec2()
        return anim_ref

    def init_anim_ref_vec3(self, val=None, interpolation=-1, flags=-1, anim_id=1):
        anim_ref = io_m3.structures['Vector3AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(1 if interpolation == -1 else interpolation, 0x6 if flags == -1 else flags, anim_id)
        anim_ref.default = to_m3_vec3(val)
        anim_ref.null = to_m3_vec3()
        return anim_ref

    def init_anim_ref_quat(self, val=None, interpolation=-1, flags=-1, anim_id=1):
        anim_ref = io_m3.structures['QuaternionAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(1 if interpolation == -1 else interpolation, 0x6 if flags == -1 else flags, anim_id)
        anim_ref.default = to_m3_quat(val)
        anim_ref.null = to_m3_quat()
        return anim_ref

    def init_anim_ref_color(self, val=None, interpolation=-1, flags=-1, anim_id=1):
        anim_ref = io_m3.structures['ColorAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(1 if interpolation == -1 else interpolation, 0x6 if flags == -1 else flags, anim_id)
        anim_ref.default = to_m3_color(val)
        anim_ref.null = to_m3_color()
        return anim_ref

    def init_anim_ref_bnds(self, val=None, interpolation=-1, flags=-1, anim_id=BNDS_ANIM_ID):
        anim_ref = io_m3.structures['BNDSAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(1 if interpolation == -1 else interpolation, 0x6 if flags == -1 else flags, anim_id)
        anim_ref.default = to_m3_bnds(val)
        anim_ref.null = to_m3_bnds()
        return anim_ref


def m3_export(ob, filename, bl_op=None):
    if not (filename.endswith('.m3') or filename.endswith('.m3a')):
        filename = filename.rsplit('.', 1)[0] + '.m3'
    print('m3_export', bl_op)
    exporter = Exporter(bl_op=bl_op)
    sections = exporter.m3_export(ob, filename,)
    io_m3.section_list_save(sections, filename)
