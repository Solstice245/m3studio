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

from timeit import timeit
import math
import bpy
import bmesh
import mathutils
from math import sqrt
from . import io_m3
from . import io_shared
from . import shared
from .io_shared import rot_fix_matrix, rot_fix_matrix_transpose
from .m3_animations import set_default_value


FRAME_RATE = 30


def to_bl_frame(m3_ms):
    return round(m3_ms / 1000 * FRAME_RATE)


def to_bl_uv(m3_uv, uv_multiply, uv_offset):
    return (
        m3_uv.x * uv_multiply / 32768 + uv_offset,
        -m3_uv.y * uv_multiply / 32768 - uv_offset + 1
    )


def to_bl_vec2(m3_vector):
    return mathutils.Vector((m3_vector.x, m3_vector.y))


def to_bl_vec3(m3_vector):
    return mathutils.Vector((m3_vector.x, m3_vector.y, m3_vector.z))


def to_bl_vec4(m3_vector):
    return mathutils.Vector((m3_vector.w, m3_vector.x, m3_vector.y, m3_vector.z))


def to_bl_quat(m3_vector):
    return mathutils.Quaternion((m3_vector.w, m3_vector.x, m3_vector.y, m3_vector.z))


def to_bl_color(m3_color):
    return mathutils.Vector((m3_color.r / 255, m3_color.g / 255, m3_color.b / 255, m3_color.a / 255))


def to_bl_matrix(m3_matrix):
    return mathutils.Matrix((
        (m3_matrix.x.x, m3_matrix.y.x, m3_matrix.z.x, m3_matrix.w.x),
        (m3_matrix.x.y, m3_matrix.y.y, m3_matrix.z.y, m3_matrix.w.y),
        (m3_matrix.x.z, m3_matrix.y.z, m3_matrix.z.z, m3_matrix.w.z),
        (m3_matrix.x.w, m3_matrix.y.w, m3_matrix.z.w, m3_matrix.w.w)
    ))


class M3InputProcessor:

    def __init__(self, importer, bl, m3):
        self.importer = importer
        self.bl = bl
        self.m3 = m3
        self.version = m3.struct_desc.struct_version

    def boolean(self, field, since_version=None, till_version=None):
        if (till_version is not None) and (self.version > till_version):
            return
        if (since_version is not None) and (self.version < since_version):
            return
        setattr(self.bl, field, False if getattr(self.m3, field) == 0 else True)

    def bit(self, field, name, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        setattr(self.bl, name, self.m3.bit_get(field, name))

    def bits_16(self, field):
        val = getattr(self.m3, field)
        vector = getattr(self.bl, field)
        for ii in range(0, 16):
            mask = 1 << ii
            vector[ii] = (mask & val) > 0

    def bits_32(self, field):
        val = getattr(self.m3, field)
        vector = getattr(self.bl, field)
        for ii in range(0, 32):
            mask = 1 << ii
            vector[ii] = (mask & val) > 0

    def integer(self, field, since_version=None, till_version=None):
        if (till_version is not None) and (self.version > till_version):
            return
        if (since_version is not None) and (self.version < since_version):
            return
        setattr(self.bl, field, getattr(self.m3, field))

    def float(self, field, since_version=None, till_version=None):
        if (till_version is not None) and (self.version > till_version):
            return
        if (since_version is not None) and (self.version < since_version):
            return
        setattr(self.bl, field, getattr(self.m3, field))

    def vec3(self, field, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        setattr(self.bl, field, to_bl_vec3(getattr(self.m3, field)))

    def vec4(self, field, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        setattr(self.bl, field, to_bl_vec4(getattr(self.m3, field)))

    def color(self, field, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        setattr(self.bl, field, to_bl_color(getattr(self.m3, field)))

    def enum(self, field, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if getattr(self.m3, field) == 0xFFFFFFFF:
            return
        value = self.bl.bl_rna.properties[field].enum_items[getattr(self.m3, field)].identifier
        setattr(self.bl, field, value)

    def anim_boolean_based_on_SDU3(self, field):
        self.anim_integer(field)

    def anim_boolean_based_on_SDFG(self, field):
        self.anim_integer(field)

    def anim_integer(self, field):
        anim_ref = getattr(self.m3, field)
        setattr(self.bl, field, anim_ref.default)
        self.importer.key_base(self.bl, field, anim_ref)

    def anim_int16(self, field):
        self.anim_integer(field)

    def anim_uint16(self, field):
        self.anim_integer(field)

    def anim_uint32(self, field):
        self.anim_integer(field)

    def anim_float(self, field, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        anim_ref = getattr(self.m3, field)
        setattr(self.bl, field, anim_ref.default)
        self.importer.key_base(self.bl, field, anim_ref)

    def anim_vec2(self, field):
        anim_ref = getattr(self.m3, field)
        default = to_bl_vec2(anim_ref.default)
        setattr(self.bl, field, default)
        self.importer.key_vec(self.bl, field, anim_ref, default)

    def anim_vec3(self, field, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        anim_ref = getattr(self.m3, field)
        default = to_bl_vec3(anim_ref.default)
        setattr(self.bl, field, default)
        self.importer.key_vec(self.bl, field, anim_ref, default)

    def anim_color(self, field, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        anim_ref = getattr(self.m3, field)
        default = to_bl_color(anim_ref.default)
        # ! waiting to see when this fails
        setattr(self.bl, field, default)
        # # without alpha
        # if len(getattr(self.bl, field)) == 3:
        #     setattr(self.bl, field, [*default][:3])
        # else:
        #     setattr(self.bl, field, default)

        self.importer.key_vec(self.bl, field, anim_ref, default)


def m3_key_collect_evnt(key_frames, key_values):
    pass  # handle these specially


def m3_key_collect_vec2(key_frames, key_values):
    ll = [[], []]

    for key_frame, key_value in zip(key_frames, key_values):
        ll[0].append(key_frame)
        ll[0].append(key_value.x)
        ll[1].append(key_frame)
        ll[1].append(key_value.y)

    return ll


def m3_key_collect_vec3(key_frames, key_values):
    ll = [[], [], []]

    for key_frame, key_value in zip(key_frames, key_values):
        ll[0].append(key_frame)
        ll[0].append(key_value.x)
        ll[1].append(key_frame)
        ll[1].append(key_value.y)
        ll[2].append(key_frame)
        ll[2].append(key_value.z)

    return ll


def m3_key_collect_quat(key_frames, key_values):
    ll = [[], [], [], []]

    for key_frame, key_value in zip(key_frames, key_values):
        ll[0].append(key_frame)
        ll[0].append(key_value.w)
        ll[1].append(key_frame)
        ll[1].append(key_value.x)
        ll[2].append(key_frame)
        ll[2].append(key_value.y)
        ll[3].append(key_frame)
        ll[3].append(key_value.z)

    return ll


def m3_key_collect_colo(key_frames, key_values):
    ll = [[], [], [], []]

    for key_frame, key_value in zip(key_frames, key_values):
        ll[0].append(key_frame)
        ll[0].append(key_value.r)
        ll[1].append(key_frame)
        ll[1].append(key_value.g)
        ll[2].append(key_frame)
        ll[2].append(key_value.b)
        ll[3].append(key_frame)
        ll[3].append(key_value.a)

    return ll


def m3_key_collect_real(key_frames, key_values):
    ll = []

    for key_frame, key_value in zip(key_frames, key_values):
        ll.append(key_frame)
        ll.append(key_value)

    return ll


def m3_key_collect_sd08(key_frames, key_values):
    pass  # undefined


def m3_key_collect_sd11(key_frames, key_values):
    pass  # undefined


def m3_key_collect_bnds(key_frames, key_values):
    pass  # handle these specially


m3_key_type_collection_method = [
    m3_key_collect_evnt, m3_key_collect_vec2, m3_key_collect_vec3, m3_key_collect_quat, m3_key_collect_colo, m3_key_collect_real, m3_key_collect_sd08,
    m3_key_collect_real, m3_key_collect_real, m3_key_collect_sd11, m3_key_collect_real, m3_key_collect_real, m3_key_collect_bnds,
]


class Importer:

    def m3_get_bone_name(self, bone_index):
        return self.final_bone_names[self.m3[self.m3_bones[bone_index].name].content]

    def m3_import(self, filename):
        # TODO make fps an import option
        bpy.context.scene.render.fps = FRAME_RATE

        self.m3 = io_m3.section_list_load(filename)

        self.m3_bl_ref = {}
        self.bl_ref_objects = []

        self.m3_model = self.m3[self.m3[0][0].model][0]
        self.m3_division = self.m3[self.m3_model.divisions][0]
        self.m3_bones = self.m3[self.m3_model.bones]

        self.stc_id_data = {}
        self.final_bone_names = {}

        self.ob = self.armature_object_new()
        self.create_animations()
        self.create_bones()
        self.create_materials()
        self.create_mesh()  # TODO mesh import options
        self.create_bounding()
        self.create_attachments()
        self.create_lights()
        self.create_shadow_boxes()
        self.create_cameras()
        self.create_particles()
        self.create_ribbons()
        self.create_projections()
        self.create_forces()
        self.create_warps()
        self.create_hittests()
        self.create_rigid_bodies()
        self.create_rigid_body_joints()
        self.create_cloths()
        self.create_ik_joints()
        self.create_turrets()
        self.create_billboards()

        self.ob.m3_model_version = str(self.m3_model.struct_desc.struct_version)

        bpy.context.view_layer.objects.active = self.ob
        self.ob.select_set(True)

    def armature_object_new(self):
        scene = bpy.context.scene
        arm = bpy.data.armatures.new(name='Armature')
        ob = bpy.data.objects.new('Armature', arm)
        ob.location = scene.cursor.location
        scene.collection.objects.link(ob)

        return ob

    def key_base(self, bl, field, ref):

        if not hasattr(bl, field):
            return

        path = bl.path_from_id(field)
        set_default_value(bl.id_data.m3_animations_default, path, 0, ref.default)
        anim_id_data = self.stc_id_data.get(ref.header.id)

        if not anim_id_data:
            return

        for action_name in anim_id_data.keys():
            anim_id_action_data = anim_id_data[action_name]
            fcurves = bpy.data.actions.get(action_name).fcurves
            fcurve = fcurves.new(path, index=0)
            fcurve.keyframe_points.add(len(anim_id_action_data) / 2)
            fcurve.keyframe_points.foreach_set('co', anim_id_action_data)

    def key_vec(self, bl, field, ref, default):

        if not hasattr(bl, field):
            return

        path = bl.path_from_id(field)

        for ii, val in enumerate(default):
            set_default_value(bl.id_data.m3_animations_default, path, ii, val)

        anim_id_data = self.stc_id_data.get(ref.header.id)

        if not anim_id_data:
            return

        for action_name in anim_id_data.keys():
            anim_id_action_data = anim_id_data[action_name]
            for index, index_data in enumerate(anim_id_action_data):
                fcurves = bpy.data.actions.get(action_name).fcurves
                fcurve = fcurves.new(path, index=index)
                fcurve.keyframe_points.add(len(index_data) / 2)
                fcurve.keyframe_points.foreach_set('co', index_data)

    def create_animations(self):
        ob = self.ob

        ob.m3_animations_default = bpy.data.actions.new(ob.name + '_DEFAULTS')

        for m3_anim_group in self.m3[self.m3_model.sequences]:
            anim_group_name = self.m3[m3_anim_group.name].content
            anim_group = shared.m3_item_add(ob.m3_animation_groups, anim_group_name)
            processor = M3InputProcessor(self, anim_group, m3_anim_group)
            io_shared.io_anim_group(processor)

            anim_group['frame_start'] = to_bl_frame(m3_anim_group.anim_ms_start)
            anim_group['frame_end'] = to_bl_frame(m3_anim_group.anim_ms_end)

        m3_stcs = self.m3[self.m3_model.sequence_transformation_collections]
        for m3_anim in m3_stcs:
            anim_name = self.m3[m3_anim.name].content
            anim = shared.m3_item_add(ob.m3_animations, anim_name)
            anim['runs_concurrent'] = m3_anim.runs_concurrent
            anim['priority'] = m3_anim.priority
            anim['action'] = bpy.data.actions.new(ob.name + '_' + anim_name)

            m3_key_type_collection_list = [
                m3_anim.sdev, m3_anim.sd2v, m3_anim.sd3v, m3_anim.sd4q, m3_anim.sdcc, m3_anim.sdr3, m3_anim.sd08,
                m3_anim.sds6, m3_anim.sdu6, m3_anim.sd11, m3_anim.sdu3, m3_anim.sdfg, m3_anim.sdmb,
            ]

            for stc_id, stc_ref in zip(self.m3[m3_anim.anim_ids], self.m3[m3_anim.anim_refs]):
                anim_type = stc_ref >> 16
                anim_index = stc_ref & 0xffff
                m3_key_type_collection = m3_key_type_collection_list[anim_type]
                m3_key_entries = self.m3[m3_key_type_collection][anim_index]

                if not self.stc_id_data.get(stc_id):
                    self.stc_id_data[stc_id] = {}

                frames = []
                ignored_indices = []
                for ii, ms in enumerate(self.m3[m3_key_entries.frames]):
                    frame = to_bl_frame(ms)
                    if frame not in frames:
                        frames.append(frame)
                    else:
                        ignored_indices.append(ii)

                m3_keys = self.m3[m3_key_entries.keys]
                keys = [m3_keys[ii] for ii in range(len(m3_keys)) if ii not in ignored_indices]

                self.stc_id_data[stc_id][anim.action.name] = m3_key_type_collection_method[anim_type](frames, keys)

                # consider making a dedicated property type and collection list for events
                if m3_key_type_collection == m3_anim.sdev:
                    for ii, frame in enumerate(frames):
                        key = keys[ii]
                        event_name = self.m3[key.name].content
                        if event_name == 'Evt_Simulate':
                            anim['simulate'] = True
                            anim['simulate_frame'] = frame

        m3_stgs = self.m3[self.m3_model.sequence_transformation_groups]
        for ii, m3_stc_group in enumerate(m3_stgs):
            m3_stc_indices = self.m3[m3_stc_group.stc_indices]
            for stc_index in m3_stc_indices:
                anim_group = ob.m3_animation_groups[-len(m3_stgs) + ii]
                anim_index = anim_group.animations.add()
                anim_index.bl_handle = ob.m3_animations[-len(m3_stcs) + stc_index].bl_handle

    def create_bones(self):

        def get_bone_tails(bone_heads, bone_vectors):
            child_bone_indices = [[] for ii in self.m3_bones]
            for bone_index, bone_entry in enumerate(self.m3_bones):
                if bone_entry.parent != -1:
                    child_bone_indices[bone_entry.parent].append(bone_index)

            tails = []

            for m3_bone, child_indices, head, vector in zip(self.m3_bones, child_bone_indices, bone_heads, bone_vectors):
                length = 0.1
                for child_index in child_indices:
                    head_to_child_head = bone_heads[child_index] - head
                    if head_to_child_head.length >= 0.0001 and abs(head_to_child_head.angle(vector)) < 0.1:
                        length = head_to_child_head.length
                tail_offset = length * vector
                tail = head + tail_offset
                while (tail - head).length == 0:
                    tail_offset *= 2
                    tail = head + tail_offset
                tails.append(tail)

            return tails

        def get_bone_rolls(bone_rests, bone_heads, bone_tails):
            rolls = []
            for iref, head, tail in zip(bone_rests, bone_heads, bone_tails):
                v = (tail - head).normalized()
                target = mathutils.Vector((0, 1, 0))
                axis = target.cross(v)
                if axis.dot(axis) > 0.000001:
                    axis.normalize()
                    theta = target.angle(v)
                    b_matrix = mathutils.Matrix.Rotation(theta, 3, axis)
                else:
                    sign = 1 if target.dot(v) > 0 else -1

                    b_matrix = mathutils.Matrix((
                        (sign, 0, 0),
                        (0, sign, 0),
                        (0, 0, 1),
                    ))

                rot_matrix = mathutils.Matrix.Rotation(0, 3, v) @ b_matrix
                rot_matrix = rot_matrix.to_4x4()
                rot_matrix.translation = head

                matrix33 = rot_matrix.to_3x3()

                z_x = matrix33.col[2].angle(iref.col[0].to_3d())
                z_z = matrix33.col[2].angle(iref.col[2].to_3d())

                roll_angle = z_z if z_x > math.pi / 2 else -z_z

                rolls.append(roll_angle)

            return rolls

        def get_edit_bones(bone_heads, bone_tails, bone_rolls, bind_scales):
            edit_bones = []
            for index, m3_bone in enumerate(self.m3_bones):
                m3_bone_name = self.m3[m3_bone.name.index].content
                edit_bone = self.ob.data.edit_bones.new(m3_bone_name)
                self.final_bone_names[m3_bone_name] = edit_bone.name
                edit_bone.bl_handle = shared.m3_handle_gen()
                edit_bone.head = bone_heads[index]
                edit_bone.tail = bone_tails[index]
                edit_bone.roll = bone_rolls[index]
                edit_bone.m3_bind_scale = (bind_scales[index][1], bind_scales[index][0], bind_scales[index][2])

                if m3_bone.parent != -1:
                    parent_edit_bone = self.ob.data.edit_bones[m3_bone.parent]
                    edit_bone.parent = parent_edit_bone
                    parent_child_vector = parent_edit_bone.tail - edit_bone.head

                    if parent_child_vector.length < 0.000001:
                        edit_bone.use_connect = True
                edit_bones.append(edit_bone)

            return edit_bones

        def get_edit_bone_relations(edit_bones):
            rel_mats = []
            for m3_bone, edit_bone in zip(self.m3_bones, edit_bones):
                if m3_bone.parent != -1:
                    parent_edit_bone = self.ob.data.edit_bones.get(self.m3_get_bone_name(m3_bone.parent))
                    rel_mats.append((parent_edit_bone.matrix.inverted() @ edit_bone.matrix).inverted())
                else:
                    rel_mats.append(edit_bone.matrix.inverted())

            return rel_mats

        def adjust_pose_bones(edit_bone_relations, bind_matrices):
            for ii, m3_bone, rel_mat, bind_mat in zip(range(len(self.m3_bones)), self.m3_bones, edit_bone_relations, bind_matrices):
                # TODO current problems:
                # TODO seems to get wrong scale values with non 1.0 values on both scale and bind scale values
                # TODO if scales are negative, rotation and location values are out of whack as well
                left_mat = rel_mat if m3_bone.parent == -1 else rel_mat @ rot_fix_matrix_transpose @ bind_matrices[m3_bone.parent].inverted()
                right_mat = bind_mat @ rot_fix_matrix
                bone_mat_comp = to_bl_vec3(m3_bone.location.default), to_bl_quat(m3_bone.rotation.default), to_bl_vec3(m3_bone.scale.default)
                bone_mat = mathutils.Matrix.LocRotScale(*bone_mat_comp)
                pose_bone = self.ob.pose.bones.get(self.m3_get_bone_name(ii))
                pose_bone.matrix_basis = left_mat @ bone_mat @ right_mat
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('location'), 0, pose_bone.location[0])
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('location'), 1, pose_bone.location[1])
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('location'), 2, pose_bone.location[2])
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('rotation_quaternion'), 0, pose_bone.rotation_quaternion[0])
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('rotation_quaternion'), 1, pose_bone.rotation_quaternion[1])
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('rotation_quaternion'), 2, pose_bone.rotation_quaternion[2])
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('rotation_quaternion'), 3, pose_bone.rotation_quaternion[3])
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('scale'), 0, pose_bone.scale[0])
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('scale'), 1, pose_bone.scale[1])
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('scale'), 2, pose_bone.scale[2])
                animate_pose_bone(m3_bone, pose_bone, left_mat, right_mat)

        def animate_pose_bone(m3_bone, pose_bone, left_mat, right_mat):
            id_data_loc = self.stc_id_data.get(m3_bone.location.header.id, {})
            id_data_rot = self.stc_id_data.get(m3_bone.rotation.header.id, {})
            id_data_scl = self.stc_id_data.get(m3_bone.scale.header.id, {})
            action_name_set = set().union(id_data_loc.keys(), id_data_rot.keys(), id_data_scl.keys())

            default_loc = m3_bone.location.default
            default_rot = m3_bone.rotation.default
            default_scl = m3_bone.scale.default

            for action_name in action_name_set:
                anim_data_loc = id_data_loc.get(action_name, None)
                anim_data_rot = id_data_rot.get(action_name, None)
                anim_data_scl = id_data_scl.get(action_name, None)

                anim_data_loc_none = not anim_data_loc
                if anim_data_loc_none:
                    anim_data_loc_none = True
                    anim_data_loc = [[0, default_loc.x], [0, default_loc.y], [0, default_loc.z]]

                anim_data_rot_none = not anim_data_rot
                if anim_data_rot_none:
                    anim_data_rot_none = True
                    anim_data_rot = [[0, default_rot.w], [0, default_rot.x], [0, default_rot.y], [0, default_rot.z]]

                anim_data_scl_none = not anim_data_scl
                if anim_data_scl_none:
                    anim_data_scl_none = True
                    anim_data_scl = [[0, default_scl.x], [0, default_scl.y], [0, default_scl.z]]

                anim_frames = [anim_data_loc[0][::2], anim_data_rot[0][::2], anim_data_scl[0][::2]]
                anim_frames_set = set().union(*anim_frames)

                if not anim_frames_set:
                    return

                # we put in original data first so that we can evaluate the fcurves.
                # blender interpolates the data we need to apply the correction matrices for us.
                # * can we interpolate based on interpolation of m3 anim header?
                fcurves = bpy.data.actions.get(action_name).fcurves
                # store fcurve references so that we don't have to find them later
                fcurves_loc = []
                for index, index_data in enumerate(anim_data_loc):
                    fcurve = fcurves.new(pose_bone.path_from_id('location'), index=index, action_group=pose_bone.name)
                    fcurve.keyframe_points.add(len(index_data) / 2)
                    fcurve.keyframe_points.foreach_set('co', index_data)
                    fcurve.keyframe_points.foreach_set('interpolation', [1] * int(len(index_data) / 2))
                    fcurves_loc.append(fcurve)

                fcurves_rot = []
                for index, index_data in enumerate(anim_data_rot):
                    fcurve = fcurves.new(pose_bone.path_from_id('rotation_quaternion'), index=index, action_group=pose_bone.name)
                    fcurve.keyframe_points.add(len(index_data) / 2)
                    fcurve.keyframe_points.foreach_set('co', index_data)
                    fcurve.keyframe_points.foreach_set('interpolation', [1] * int(len(index_data) / 2))
                    fcurves_rot.append(fcurve)

                fcurves_scl = []
                for index, index_data in enumerate(anim_data_scl):
                    fcurve = fcurves.new(pose_bone.path_from_id('scale'), index=index, action_group=pose_bone.name)
                    fcurve.keyframe_points.add(len(index_data) / 2)
                    fcurve.keyframe_points.foreach_set('co', index_data)
                    fcurve.keyframe_points.foreach_set('interpolation', [1] * int(len(index_data) / 2))
                    fcurves_scl.append(fcurve)

                new_anim_data = [[], [], []]
                for frame in sorted(list(anim_frames_set)):
                    eval_loc = mathutils.Vector([fcurve.evaluate(frame) for fcurve in fcurves_loc])
                    eval_rot = mathutils.Quaternion([fcurve.evaluate(frame) for fcurve in fcurves_rot])
                    eval_scl = mathutils.Vector([fcurve.evaluate(frame) for fcurve in fcurves_scl])

                    loc, rot, scl = (left_mat @ mathutils.Matrix.LocRotScale(eval_loc, eval_rot, eval_scl) @ right_mat).decompose()

                    if frame in anim_frames[0]:
                        new_anim_data[0].append(loc)

                    if frame in anim_frames[1]:
                        new_anim_data[1].append(rot)

                    if frame in anim_frames[2]:
                        new_anim_data[2].append(scl)

                # second pass animation data, after evaluation
                new_anim_data_loc = m3_key_collect_vec3(anim_frames[0], new_anim_data[0])
                new_anim_data_rot = m3_key_collect_quat(anim_frames[1], new_anim_data[1])
                new_anim_data_scl = m3_key_collect_vec3(anim_frames[2], new_anim_data[2])

                for index, index_data in enumerate(new_anim_data_loc):
                    fcurve = fcurves_loc[index]
                    if anim_data_loc_none:
                        fcurves.remove(fcurve)
                    else:
                        fcurve.keyframe_points.foreach_set('co', index_data)

                for index, index_data in enumerate(new_anim_data_rot):
                    fcurve = fcurves_rot[index]
                    if anim_data_rot_none:
                        fcurves.remove(fcurve)
                    else:
                        fcurve.keyframe_points.foreach_set('co', index_data)

                for index, index_data in enumerate(new_anim_data_scl):
                    fcurve = fcurves_scl[index]
                    if anim_data_scl_none:
                        fcurves.remove(fcurve)
                    else:
                        fcurve.keyframe_points.foreach_set('co', index_data)

        m3_bone_rests = self.m3[self.m3_model.bone_rests]

        bpy.context.view_layer.objects.active = self.ob
        bone_rests = [to_bl_matrix(iref.matrix).inverted() @ io_shared.rot_fix_matrix for iref in m3_bone_rests]
        bone_heads = [matrix.translation for matrix in bone_rests]
        bone_vectors = [matrix.col[1].to_3d().normalized() for matrix in bone_rests]
        bone_tails = get_bone_tails(bone_heads, bone_vectors)
        bone_rolls = get_bone_rolls(bone_rests, bone_heads, bone_tails)
        bind_scales = [to_bl_matrix(iref.matrix).decompose()[2] for iref in m3_bone_rests]
        bind_matrices = [mathutils.Matrix.LocRotScale(mathutils.Vector(), mathutils.Quaternion(), scl) for scl in bind_scales]
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        edit_bones = get_edit_bones(bone_heads, bone_tails, bone_rolls, bind_scales)
        edit_bone_relations = get_edit_bone_relations(edit_bones)
        bpy.ops.object.mode_set(mode='POSE')
        adjust_pose_bones(edit_bone_relations, bind_matrices)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def create_materials(self):
        ob = self.ob

        if self.m3_model.materials_standard.index:
            ob.m3_materials_standard_version = str(self.m3[self.m3_model.materials_standard.index].struct_desc.struct_version)

        if hasattr(self.m3_model, 'materials_reflection'):
            if self.m3_model.materials_reflection.index:
                ob.m3_materials_reflection_version = str(self.m3[self.m3_model.materials_reflection].struct_desc.struct_version)

        layer_section_to_index = {}
        for m3_matref in self.m3[self.m3_model.material_references]:
            m3_mat = self.m3[getattr(self.m3_model, io_shared.material_type_to_model_reference[m3_matref.type])][m3_matref.material_index]

            matref = shared.m3_item_add(ob.m3_materialrefs, item_name=self.m3[m3_mat.name].content)
            mat_col = getattr(ob, 'm3_' + io_shared.material_type_to_model_reference[m3_matref.type])
            mat = shared.m3_item_add(mat_col, item_name=matref.name)

            processor = M3InputProcessor(self, mat, m3_mat)
            io_shared.material_type_io_method[m3_matref.type](processor)

            matref.mat_type = 'm3_' + io_shared.material_type_to_model_reference[m3_matref.type]
            matref.mat_handle = mat.bl_handle

            shared.m3_msgbus_sub(mat, matref, 'name', 'name')

            if m3_matref.type == 3:
                for m3_section in self.m3[m3_mat.sections]:
                    section = shared.m3_item_add(mat.sections)
                    section.matref = ob.m3_materialrefs[m3_section.material_reference_index].bl_handle
                    processor = M3InputProcessor(self, section, m3_section)
                    io_shared.io_material_composite_section(processor)
            elif m3_matref.type == 11:
                for m3_starburst in self.m3[m3_mat.starbursts]:
                    starburst = shared.m3_item_add(mat.starbursts)
                    processor = M3InputProcessor(self, starburst, m3_starburst)
                    io_shared.io_starburst(processor)

            for layer_name in io_shared.material_type_to_layers[m3_matref.type]:
                m3_layer_field = getattr(m3_mat, 'layer_' + layer_name, None)
                if not m3_layer_field:
                    continue

                if m3_layer_field.index in layer_section_to_index.keys():
                    layer = ob.m3_materiallayers[layer_section_to_index[m3_layer_field.index]]
                    setattr(mat, 'layer_' + layer_name, layer.bl_handle)
                    continue

                m3_layer = self.m3[m3_layer_field][0]
                m3_layer_bitmap_str = self.m3[m3_layer.color_bitmap.index].content if m3_layer.color_bitmap.index else ''
                if not m3_layer_bitmap_str and not m3_layer.bit_get('flags', 'color'):
                    continue

                ob.m3_materiallayers_version = str(self.m3[m3_layer_field].struct_desc.struct_version)

                layer = shared.m3_item_add(ob.m3_materiallayers, item_name=mat.name + '_' + layer_name)
                layer.color_bitmap = m3_layer_bitmap_str
                processor = M3InputProcessor(self, layer, m3_layer)
                io_shared.io_material_layer(processor)

                layer.color_type = 'COLOR' if m3_layer.bit_get('flags', 'color') else 'BITMAP'
                layer.fresnel_max = m3_layer.fresnel_min + m3_layer.fresnel_max_offset

                if m3_layer.struct_desc.struct_version >= 25:
                    layer.fresnel_mask[0] = 1.0 - m3_layer.fresnel_inverted_mask_x
                    layer.fresnel_mask[1] = 1.0 - m3_layer.fresnel_inverted_mask_y
                    layer.fresnel_mask[2] = 1.0 - m3_layer.fresnel_inverted_mask_z

                layer_section_to_index[m3_layer_field.index] = len(ob.m3_materiallayers) - 1
                setattr(mat, 'layer_' + layer_name, layer.bl_handle)

    def create_mesh(self):
        ob = self.ob

        if not self.m3_division.regions.index:
            return

        ob.m3_mesh_version = str(self.m3[self.m3_division.regions].struct_desc.struct_version)
        m3_vertices = self.m3[self.m3_model.vertices]

        if not self.m3_model.bit_get('vertex_flags', 'has_vertices'):
            if len(self.m3_model.vertices):
                raise Exception('Mesh claims to not have any vertices - expected buffer to be empty, but it isn\'t. size=%d' % len(m3_vertices))
            return

        v_colors = self.m3_model.bit_get('vertex_flags', 'has_vertex_colors')
        v_class = 'VertexFormat' + hex(self.m3_model.vertex_flags)
        if v_class not in io_m3.structures:
            raise Exception('Vertex flags %s can\'t be handled yet. bufferSize=%d' % (hex(self.m3_model.vertex_flags), len(m3_vertices)))

        v_class_desc = io_m3.structures[v_class].get_version(0)
        v_count = len(m3_vertices) // v_class_desc.size
        m3_vertices = v_class_desc.instances(buffer=m3_vertices.content, count=v_count)
        bone_lookup_full = self.m3[self.m3_model.bone_lookup]

        uv_props = []
        for uv_prop in ['uv0', 'uv1', 'uv2', 'uv3', 'uv4']:
            if v_class_desc.fields.get(uv_prop):
                uv_props.append(uv_prop)

        m3_faces = self.m3[self.m3_division.faces]
        m3_batches = self.m3[self.m3_division.batches]
        self.m3_bl_ref[self.m3_division.regions.index] = {}

        for region_ii, region in enumerate(self.m3[self.m3_division.regions]):
            region_matref_indices = [batch.material_reference_index for batch in m3_batches if batch.region_index == region_ii]

            if not region_matref_indices:
                continue

            regn_m3_verts = m3_vertices[region.first_vertex_index:region.first_vertex_index + region.vertex_count]
            regn_m3_faces = m3_faces[region.first_face_index:region.first_face_index + region.face_count]
            regn_uv_multiply = getattr(region, 'uv_multiply', 16)
            regn_uv_offset = getattr(region, 'uv_offset', 0)

            if region.struct_desc.struct_version <= 2:
                for ii in range(len(regn_m3_faces)):
                    regn_m3_faces[ii] -= region.first_vertex_index

            regn_m3_vert_ids = {}
            regn_m3_vert_to_id = {}
            regn_m3_verts_new = []
            regn_m3_faces_new = []

            dups = 0
            for ii, v in enumerate(regn_m3_verts):
                id_tuple = (*to_bl_vec3(v.pos), *to_bl_vec3(v.normal), v.lookup0, v.lookup1, v.lookup2, v.lookup3, v.weight0, v.weight1, v.weight2, v.weight3)
                regn_m3_vert_to_id[ii] = id_tuple
                if regn_m3_vert_ids.get(id_tuple) is None:
                    regn_m3_vert_ids[id_tuple] = ii - dups
                    regn_m3_verts_new.append(v)
                else:
                    dups += 1

            for ii in range(len(regn_m3_faces)):
                regn_m3_faces_new.append(regn_m3_vert_ids.get(regn_m3_vert_to_id[regn_m3_faces[ii]]))

            mesh = bpy.data.meshes.new('Mesh')
            mesh_ob = bpy.data.objects.new('Mesh', mesh)
            mesh_ob.parent = ob

            bpy.context.scene.collection.objects.link(mesh_ob)

            modifier = mesh_ob.modifiers.new('EdgeSplit', 'EDGE_SPLIT')
            modifier.use_edge_angle = False

            modifier = mesh_ob.modifiers.new('Armature', 'ARMATURE')
            modifier.object = ob

            bone_lookup = bone_lookup_full[region.first_bone_lookup_index:region.first_bone_lookup_index + region.bone_lookup_count]
            for lookup in bone_lookup:
                mesh_ob.vertex_groups.new(name=self.m3_get_bone_name(lookup))

            vertex_groups_used = [False for g in mesh_ob.vertex_groups]

            bm = bmesh.new(use_operators=True)

            layer_sign = bm.verts.layers.int.new('m3sign')
            layer_deform = bm.verts.layers.deform.new('m3lookup')
            layer_color = bm.loops.layers.color.new('m3color') if v_colors else None
            layer_alpha = bm.loops.layers.color.new('m3alpha') if v_colors else None

            for uv_prop in uv_props:
                bm.loops.layers.uv.new(uv_prop)

            for m3_vert in regn_m3_verts_new:
                vert = bm.verts.new((m3_vert.pos.x, m3_vert.pos.y, m3_vert.pos.z))
                vert[layer_sign] = 1 if round(m3_vert.sign) > 0 else 0

                for ii in range(0, region.vertex_lookups_used):
                    weight = getattr(m3_vert, 'weight' + str(ii))
                    if weight:
                        lookup_index = getattr(m3_vert, 'lookup' + str(ii))
                        vertex_groups_used[lookup_index] = True
                        vert[layer_deform][lookup_index] = weight / 255

            bm.verts.ensure_lookup_table()

            for ii in range(0, len(regn_m3_faces), 3):
                face = bm.faces.new((bm.verts[regn_m3_faces_new[ii]], bm.verts[regn_m3_faces_new[ii + 1]], bm.verts[regn_m3_faces_new[ii + 2]]))
                face.smooth = True

                for jj in range(3):
                    m3v = regn_m3_verts[regn_m3_faces[ii + jj]]
                    loop = face.loops[jj]
                    for uv_prop in uv_props:
                        layer_uv = bm.loops.layers.uv.get(uv_prop)
                        loop[layer_uv].uv = to_bl_uv(getattr(m3v, uv_prop), regn_uv_multiply, regn_uv_offset)
                    if layer_color:
                        loop[layer_color] = (m3_vert.col.r / 255, m3_vert.col.g / 255, m3_vert.col.b / 255, 1)
                        loop[layer_alpha] = (m3_vert.col.a / 255, m3_vert.col.a / 255, m3_vert.col.a / 255, 1)

            bm.faces.ensure_lookup_table()

            doubles = bmesh.ops.find_doubles(bm, verts=bm.verts, dist=0.00001)['targetmap']
            for origin in list(doubles.keys()):
                target = doubles[origin]

                m3v0 = regn_m3_verts[origin.index]
                m3v1 = regn_m3_verts[target.index]

                m3v0_lookup_id = (m3v0.lookup0, m3v0.lookup1, m3v0.lookup2, m3v0.lookup3, m3v0.weight0, m3v0.weight1, m3v0.weight2, m3v0.weight3)
                m3v1_lookup_id = (m3v1.lookup0, m3v1.lookup1, m3v1.lookup2, m3v1.lookup3, m3v1.weight0, m3v1.weight1, m3v1.weight2, m3v1.weight3)

                for edge in [*origin.link_edges, *target.link_edges]:
                    if len(edge.link_faces) == 1:
                        edge.smooth = False

                if m3v0_lookup_id != m3v1_lookup_id:
                    del doubles[origin]
            bmesh.ops.weld_verts(bm, targetmap=doubles)

            bm.to_mesh(mesh)

            for g, used in zip(mesh_ob.vertex_groups, vertex_groups_used):
                if not used:
                    mesh_ob.vertex_groups.remove(g)

            self.m3_bl_ref[self.m3_division.regions.index][region_ii] = mesh_ob

    def create_bounding(self):
        ob = self.ob
        bounds = ob.m3_bounds
        bounds.left, bounds.back, bounds.bottom = to_bl_vec3(self.m3_model.boundings.min)
        bounds.right, bounds.front, bounds.top = to_bl_vec3(self.m3_model.boundings.max)
        bounds.radius = self.m3_model.boundings.radius
        # TODO animate boundings?

    def create_attachments(self):
        ob = self.ob

        m3_volumes = self.m3[self.m3_model.attachment_volumes]

        for m3_point in self.m3[self.m3_model.attachment_points]:
            bone_name = self.m3_get_bone_name(m3_point.bone)
            bone = ob.data.bones[bone_name]
            point = shared.m3_item_add(ob.m3_attachmentpoints, item_name=self.m3[m3_point.name].content[4:])
            point.bone = bone.bl_handle if bone else ''

            for m3_volume in m3_volumes:
                if m3_volume.bone0 == m3_point.bone:
                    m3_vol_bone_name = self.m3_get_bone_name(m3_volume.bone1)
                    m3_vol_bone = ob.data.bones[m3_vol_bone_name]
                    vol = shared.m3_item_add(point.volumes, item_name='Volume')
                    vol.bone = m3_vol_bone.bl_handle if m3_vol_bone else ''
                    vol.shape = vol.bl_rna.properties['shape'].enum_items[getattr(m3_volume, 'shape')].identifier
                    vol.size = (m3_volume.size0, m3_volume.size1, m3_volume.size2)
                    md = to_bl_matrix(m3_volume.matrix).decompose()
                    vol.location = md[0]
                    vol.rotation = md[1].to_euler('XYZ')
                    vol.scale = md[2]
                    vol.mesh_object = self.generate_basic_volume_object('{}_{}'.format(point.name, vol.name), m3_volume.vertices, m3_volume.face_data)

    def create_lights(self):
        ob = self.ob

        for m3_light in self.m3[self.m3_model.lights]:
            bone_name = self.m3_get_bone_name(m3_light.bone)
            bone = ob.data.bones[bone_name]
            light = shared.m3_item_add(ob.m3_lights, item_name=bone_name)
            light.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, light, m3_light)
            io_shared.io_light(processor)

    def create_shadow_boxes(self):
        if not hasattr(self.m3_model, 'shadow_boxes'):
            return

        ob = self.ob
        for m3_shadow_box in self.m3[self.m3_model.shadow_boxes]:
            bone_name = self.m3_get_bone_name(m3_shadow_box.bone)
            bone = ob.data.bones[bone_name]
            shadow_box = shared.m3_item_add(ob.m3_shadowboxes, item_name=bone_name)
            shadow_box.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, shadow_box, m3_shadow_box)
            io_shared.io_shadow_box(processor)

    def create_cameras(self):
        ob = self.ob

        if self.m3_model.cameras.index:
            ob.m3_cameras_version = str(self.m3[self.m3_model.cameras].struct_desc.struct_version)

        for m3_camera in self.m3[self.m3_model.cameras]:
            bone_name = self.m3_get_bone_name(m3_camera.bone)
            bone = ob.data.bones[bone_name]
            camera = shared.m3_item_add(ob.m3_cameras, item_name=bone_name)
            camera.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, camera, m3_camera)
            io_shared.io_camera(processor)

    def create_particles(self):
        ob = self.ob

        if self.m3_model.particle_systems.index:
            ob.m3_particle_systems_version = str(self.m3[self.m3_model.particle_systems].struct_desc.struct_version)

        m3_systems = self.m3[self.m3_model.particle_systems]
        m3_copies = self.m3[self.m3_model.particle_copies]

        for m3_copy in m3_copies:
            bone_name = self.m3_get_bone_name(m3_copy.bone)
            bone = ob.data.bones[bone_name]
            copy = shared.m3_item_add(ob.m3_particle_copies, item_name=bone_name)
            copy.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, copy, m3_copy)
            io_shared.io_particle_copy(processor)

        for m3_system in m3_systems:
            bone_name = self.m3_get_bone_name(m3_system.bone)
            bone = ob.data.bones[bone_name]
            system = shared.m3_item_add(ob.m3_particle_systems, item_name=bone_name)
            system.bone = bone.bl_handle if bone else ''
            system.material = ob.m3_materialrefs[m3_system.material_reference_index].bl_handle
            processor = M3InputProcessor(self, system, m3_system)
            io_shared.io_particle_system(processor)

            if hasattr(m3_system, 'emit_shape_regions'):
                for region_indice in self.m3[m3_system.emit_shape_regions]:
                    mesh_object_pointer = system.emit_shape_meshes.add()
                    mesh_object_pointer.bl_object = self.m3_bl_ref.get(self.m3_division.regions.index)[region_indice]

            for m3_point in self.m3[m3_system.emit_shape_spline]:
                point = system.emit_shape_spline.add()
                processor = M3InputProcessor(self, point, m3_point)
                processor.anim_vec3('location')

            for m3_copy_index in self.m3[m3_system.copy_indices]:
                copy = ob.m3_particle_copies[-len(m3_copies) + m3_copy_index]
                system_user = copy.systems.add()
                system_user.bl_handle = system.bl_handle

    def create_ribbons(self):
        ob = self.ob

        if self.m3_model.ribbons.index:
            ob.m3_ribbons_version = str(self.m3[self.m3_model.ribbons].struct_desc.struct_version)

        for m3_ribbon in self.m3[self.m3_model.ribbons]:
            bone_name = self.m3_get_bone_name(m3_ribbon.bone)
            bone = ob.data.bones[bone_name]
            ribbon = shared.m3_item_add(ob.m3_ribbons, item_name=bone_name)
            ribbon.bone = bone.bl_handle if bone else ''
            ribbon.material = ob.m3_materialrefs[m3_ribbon.material_reference_index].bl_handle
            processor = M3InputProcessor(self, ribbon, m3_ribbon)
            io_shared.io_ribbon(processor)

            if m3_ribbon.spline.index:
                for ref in self.bl_ref_objects:
                    if [m3_ribbon.spline.index] == ref['sections']:
                        ribbon.spline = ref['ob'].bl_handle
                else:
                    m3_spline = self.m3[m3_ribbon.spline]
                    spline = shared.m3_item_add(ob.m3_ribbonsplines, item_name=ribbon.name + '_spline')
                    ribbon.spline = spline.bl_handle
                    for m3_point in m3_spline:
                        bone_name = self.m3_get_bone_name(m3_point.bone)
                        bone = ob.data.bones[bone_name]
                        point = shared.m3_item_add(spline.points, item_name=bone_name)
                        point.bone = bone.bl_handle if bone else ''
                    self.m3_bl_ref[m3_ribbon.spline.index] = spline

    def create_projections(self):
        ob = self.ob
        for m3_projection in self.m3[self.m3_model.projections]:
            bone_name = self.m3_get_bone_name(m3_projection.bone)
            bone = ob.data.bones[bone_name]
            projection = shared.m3_item_add(ob.m3_projections, item_name=bone_name)
            projection.bone = bone.bl_handle if bone else ''
            projection.material = ob.m3_materialrefs[m3_projection.material_reference_index].bl_handle
            processor = M3InputProcessor(self, projection, m3_projection)
            io_shared.io_projection(processor)

    def create_forces(self):
        ob = self.ob
        for m3_force in self.m3[self.m3_model.forces]:
            bone_name = self.m3_get_bone_name(m3_force.bone)
            bone = ob.data.bones[bone_name]
            force = shared.m3_item_add(ob.m3_forces, item_name=bone_name)
            force.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, force, m3_force)
            io_shared.io_force(processor)

    def create_warps(self):
        ob = self.ob
        for m3_warp in self.m3[self.m3_model.warps]:
            bone_name = self.m3_get_bone_name(m3_warp.bone)
            bone = ob.data.bones[bone_name]
            warp = shared.m3_item_add(ob.m3_warps, item_name=bone_name)
            warp.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, warp, m3_warp)
            io_shared.io_warp(processor)

    def create_hittests(self):
        ob = self.ob

        m3_hittest_tight = self.m3_model.hittest_tight
        bone_name = self.m3_get_bone_name(m3_hittest_tight.bone)
        bone = ob.data.bones[bone_name]
        ob.m3_hittest_tight.bone = bone.bl_handle if bone else ''
        ob.m3_hittest_tight.shape = ob.m3_hittest_tight.bl_rna.properties['shape'].enum_items[m3_hittest_tight.shape].identifier
        ob.m3_hittest_tight.size = (m3_hittest_tight.size0, m3_hittest_tight.size1, m3_hittest_tight.size2)
        md = to_bl_matrix(m3_hittest_tight.matrix).decompose()
        ob.m3_hittest_tight.location = md[0]
        ob.m3_hittest_tight.rotation = md[1].to_euler('XYZ')
        ob.m3_hittest_tight.scale = md[2]
        ob.m3_hittest_tight.mesh_object = self.generate_basic_volume_object(ob.m3_hittest_tight.name, m3_hittest_tight.vertices, m3_hittest_tight.face_data)

        for m3_hittest in self.m3[self.m3_model.hittests]:
            bone_name = self.m3_get_bone_name(m3_hittest.bone)
            bone = ob.data.bones[bone_name]
            hittest = shared.m3_item_add(ob.m3_hittests, item_name=bone_name)
            hittest.bone = bone.bl_handle if bone else ''
            hittest.shape = hittest.bl_rna.properties['shape'].enum_items[getattr(m3_hittest, 'shape')].identifier
            hittest.size = (m3_hittest.size0, m3_hittest.size1, m3_hittest.size2)
            md = to_bl_matrix(m3_hittest.matrix).decompose()
            hittest.location = md[0]
            hittest.rotation = md[1].to_euler('XYZ')
            hittest.scale = md[2]
            hittest.mesh_object = self.generate_basic_volume_object(hittest.name, m3_hittest.vertices, m3_hittest.face_data)

    def create_rigid_bodies(self):
        ob = self.ob

        if self.m3_model.physics_rigidbodies.index:
            ob.m3_rigidbodies_version = str(self.m3[self.m3_model.physics_rigidbodies].struct_desc.struct_version)

        for m3_rigidbody in self.m3[self.m3_model.physics_rigidbodies]:
            bone_name = self.m3_get_bone_name(m3_rigidbody.bone)
            bone = ob.data.bones[bone_name]
            rigidbody = shared.m3_item_add(ob.m3_rigidbodies, item_name=bone_name)
            rigidbody.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, rigidbody, m3_rigidbody)
            io_shared.io_rigid_body(processor)

            physics_shape = self.m3_bl_ref.get(m3_rigidbody.physics_shape.index)
            if physics_shape:
                rigidbody.physics_shape = physics_shape.bl_handle
            else:
                m3_physics_shape = self.m3[m3_rigidbody.physics_shape]

                physics_shape = shared.m3_item_add(ob.m3_physicsshapes, item_name=rigidbody.name + '_shape')
                rigidbody.physics_shape = physics_shape.bl_handle
                for m3_volume in m3_physics_shape:
                    volume = shared.m3_item_add(physics_shape.volumes)
                    md = to_bl_matrix(m3_volume.matrix).decompose()
                    volume['location'] = md[0]
                    volume['rotation'] = md[1].to_euler('XYZ')
                    volume['scale'] = md[2]
                    volume.shape = volume.bl_rna.properties['shape'].enum_items[getattr(m3_volume, 'shape')].identifier
                    volume.size = (m3_volume.size0, m3_volume.size1, m3_volume.size2)

                    if m3_volume.struct_desc.struct_version == 1:
                        volume['mesh_object'] = self.generate_basic_volume_object(physics_shape.name, m3_volume.vertices, m3_volume.face_data)
                    else:
                        args = (physics_shape.name, m3_volume.vertices, m3_volume.polygons_related, m3_volume.loops, m3_volume.polygons)
                        volume['mesh_object'] = self.generate_rigidbody_volume_object(*args)

                self.m3_bl_ref[m3_rigidbody.physics_shape.index] = physics_shape

    def create_rigid_body_joints(self):
        ob = self.ob

        for m3_joint in self.m3[self.m3_model.physics_joints]:
            bone1_name = self.m3_get_bone_name(m3_joint.bone1)
            bone2_name = self.m3_get_bone_name(m3_joint.bone2)
            bone1 = ob.data.bones[bone1_name]
            bone2 = ob.data.bones[bone2_name]

            joint = shared.m3_item_add(ob.m3_physicsjoints, item_name=(bone1.name if bone1 else '') + '_joint')

            for rb in ob.m3_rigidbodies:
                if bone1 and rb.bone == bone1.bl_handle:
                    joint.rigidbody1 = rb.bl_handle
                if bone2 and rb.bone == bone2.bl_handle:
                    joint.rigidbody2 = rb.bl_handle

            processor = M3InputProcessor(self, joint, m3_joint)
            io_shared.io_rigid_body_joint(processor)

            md = to_bl_matrix(m3_joint.matrix1).decompose()
            joint.location1 = md[0]
            joint.rotation1 = md[1].to_euler('XYZ')
            md = to_bl_matrix(m3_joint.matrix2).decompose()
            joint.location2 = md[0]
            joint.rotation2 = md[1].to_euler('XYZ')

    def create_cloths(self):
        if not hasattr(self.m3_model, 'physics_cloths'):
            return

        ob = self.ob

        if self.m3_model.physics_cloths.index:
            ob.m3_cloths_version = str(self.m3[self.m3_model.physics_cloths].struct_desc.struct_version)

        for m3_cloth in self.m3[self.m3_model.physics_cloths]:
            cloth = shared.m3_item_add(ob.m3_cloths, item_name='Cloth')
            processor = M3InputProcessor(self, cloth, m3_cloth)
            io_shared.io_cloth(processor)

            if m3_cloth.constraints.index:
                for ref in self.bl_ref_objects:
                    if [m3_cloth.constraints.index] == ref['sections']:
                        cloth.constraint_set = ref['ob'].bl_handle
                else:
                    m3_constraints = self.m3[m3_cloth.constraints]
                    constraint_set = shared.m3_item_add(ob.m3_clothconstraintsets, item_name=cloth.name + '_constraints')
                    cloth.constraint_set = constraint_set.bl_handle
                    for m3_constraint in m3_constraints:
                        bone_name = self.m3_get_bone_name(m3_constraint.bone)
                        bone = ob.data.bones[bone_name]
                        constraint = shared.m3_item_add(constraint_set.constraints, item_name=bone_name)
                        constraint.bone = bone.bl_handle if bone else ''
                        constraint.height = m3_constraint.height
                        constraint.radius = m3_constraint.radius
                        md = to_bl_matrix(m3_constraint.matrix).decompose()
                        constraint.location = md[0]
                        constraint.rotation = md[1].to_euler('XYZ')
                        constraint.scale = md[2]
                    self.m3_bl_ref[m3_cloth.constraints.index] = constraint_set

            m3_cloth_objects = self.m3[m3_cloth.influence_map][0]
            cloth.mesh_object = self.m3_bl_ref.get(self.m3_division.regions.index)[m3_cloth_objects.influenced_region_index]
            cloth.simulator_object = self.m3_bl_ref.get(self.m3_division.regions.index)[m3_cloth_objects.simulation_region_index]

            # because create_mesh() can perform destructive operations, cloth vertex data can possibly become corrupted.
            # if problems occur it may be necessary to make the new/old vertex data maps accessible outside of the create_mesh() function.
            if not cloth.simulator_object:
                continue

            cloth_vertex_sim = self.m3[m3_cloth.vertex_simulated]

            bpy.context.view_layer.objects.active = cloth.simulator_object
            bpy.ops.object.mode_set(mode='EDIT')
            me = cloth.simulator_object.data
            bm = bmesh.from_edit_mesh(me)

            layer = bm.verts.layers.int.get('m3clothsim') or bm.verts.layers.int.new('m3clothsim')
            for vert in bm.verts:
                vert[layer] = cloth_vertex_sim[vert.index]

            bmesh.update_edit_mesh(me)
            bpy.ops.object.mode_set(mode='OBJECT')

    def create_ik_joints(self):
        ob = self.ob
        for m3_ik in self.m3[self.m3_model.ik_joints]:
            bone_base_name = self.m3_get_bone_name(m3_ik.bone_base)
            bone_target_name = self.m3_get_bone_name(m3_ik.bone_target)
            bone_base = ob.data.bones[bone_base_name]
            bone_target = ob.data.bones[bone_target_name]
            ik = shared.m3_item_add(ob.m3_ikjoints, item_name=bone_target_name)
            ik.bone = bone_target.bl_handle if bone_target else ''

            if bone_base and bone_target:
                joint_length = 0
                parent_bone = bone_target
                while parent_bone and parent_bone != bone_base:
                    parent_bone = parent_bone.parent
                    joint_length += 1
                ik.joint_length = joint_length

            processor = M3InputProcessor(self, ik, m3_ik)
            io_shared.io_ik(processor)

    def create_turrets(self):
        ob = self.ob

        if self.m3_model.turret_parts.index:
            ob.m3_turrets_part_version = str(self.m3[self.m3_model.turret_parts].struct_desc.struct_version)

        for m3_turret in self.m3[self.m3_model.turrets]:
            turret = shared.m3_item_add(ob.m3_turrets, item_name=self.m3[m3_turret.name].content)
            for ii in self.m3[m3_turret.parts].content:
                m3_part = self.m3[self.m3_model.turret_parts][ii]
                bone_name = self.m3_get_bone_name(m3_part.bone)
                bone = ob.data.bones[bone_name]
                part = shared.m3_item_add(turret.parts, item_name=bone_name)
                part.bone = bone.bl_handle if bone else ''
                processor = M3InputProcessor(self, part, m3_part)
                io_shared.io_turret_part(processor)

                if self.m3[self.m3_model.turret_parts].struct_desc.struct_version < 4:
                    part.matrix = to_bl_matrix(m3_part.matrix)

    def create_billboards(self):
        ob = self.ob
        for m3_billboard in self.m3[self.m3_model.billboards]:
            bone_name = self.m3_get_bone_name(m3_billboard.bone)
            bone = ob.data.bones[bone_name]
            billboard = shared.m3_item_add(ob.m3_billboards, item_name=bone_name)
            billboard.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, billboard, m3_billboard)
            io_shared.io_billboard(processor)

    def generate_basic_volume_object(self, name, m3_vert_ref, m3_face_ref):

        if not m3_vert_ref.index or not m3_face_ref.index:
            return

        for ref in self.bl_ref_objects:
            if [m3_vert_ref.index, m3_face_ref.index] == ref['sections']:
                return ref['ob']

        me = bpy.data.meshes.new(name)
        me_ob = bpy.data.objects.new(me.name, me)
        me_ob.display_type = 'WIRE'
        me_ob.parent = self.ob
        me_ob.hide_viewport = True
        me_ob.hide_render = True
        me_ob.m3_mesh_export = False
        bpy.context.scene.collection.objects.link(me_ob)

        bl_vert_data = []
        for v in self.m3[m3_vert_ref]:
            bl_vert_data.append(v.x)
            bl_vert_data.append(v.y)
            bl_vert_data.append(v.z)

        m3_face_data = self.m3[m3_face_ref].content
        bl_tri_range = range(0, len(m3_face_data), 3)

        me.vertices.add(len(bl_vert_data) / 3)
        me.vertices.foreach_set('co', bl_vert_data)
        me.loops.add(len(m3_face_data))
        me.loops.foreach_set('vertex_index', m3_face_data)
        me.polygons.add(len(bl_tri_range))
        me.polygons.foreach_set('loop_start', [ii for ii in bl_tri_range])
        me.polygons.foreach_set('loop_total', [3 for ii in bl_tri_range])

        me.validate()
        me.update(calc_edges=True)

        self.bl_ref_objects.append({'sections': [m3_vert_ref.index, m3_face_ref.index], 'ob': me_ob})

        return me_ob

    def generate_rigidbody_volume_object(self, name, m3_vert_ref, m3_poly_related_ref, m3_loop_ref, m3_poly_ref):

        if not m3_vert_ref.index or not m3_loop_ref.index or not m3_poly_ref.index:
            return

        for ref in self.bl_ref_objects:
            if [m3_vert_ref.index, m3_loop_ref.index, m3_poly_ref] == ref['sections']:
                return ref['ob']

        me = bpy.data.meshes.new(name)
        me_ob = bpy.data.objects.new(me.name, me)
        me_ob.display_type = 'WIRE'
        me_ob.parent = self.ob
        me_ob.hide_viewport = True
        me_ob.hide_render = True
        me_ob.m3_mesh_export = False
        bpy.context.scene.collection.objects.link(me_ob)

        bl_vert_data = []
        for v in self.m3[m3_vert_ref]:
            bl_vert_data.append(v.x)
            bl_vert_data.append(v.y)
            bl_vert_data.append(v.z)

        bl_loop_data = self.m3[m3_loop_ref].content
        bl_poly_data = self.m3[m3_poly_ref].content

        loop_indices = {ii: [] for ii in bl_poly_data}
        bl_loop_data_ordered = []
        for ii in bl_poly_data:
            loop_index = ii
            while loop_index not in loop_indices[ii]:
                loop_indices[ii].append(loop_index)
                bl_loop_data_ordered.append(bl_loop_data[loop_index].vertex)
                loop_index = bl_loop_data[loop_index].loop

        bl_loop_start_ordered = []
        num = 0
        for ii in loop_indices:
            bl_loop_start_ordered.append(num)
            num += len(loop_indices[ii])

        me.vertices.add(len(bl_vert_data) / 3)
        me.vertices.foreach_set('co', bl_vert_data)
        me.loops.add(len(bl_loop_data))
        me.loops.foreach_set('vertex_index', [ii for ii in bl_loop_data_ordered])
        me.polygons.add(len(bl_poly_data))
        me.polygons.foreach_set('loop_start', [ii for ii in bl_loop_start_ordered])
        me.polygons.foreach_set('loop_total', [len(loop_indices[ii]) for ii in bl_poly_data])

        me.validate()
        me.update(calc_edges=True)

        self.bl_ref_objects.append({'sections': [m3_vert_ref.index, m3_loop_ref.index, m3_poly_ref], 'ob': me_ob})

        return me_ob


def m3_import(filename):
    importer = Importer()
    importer.m3_import(filename)
