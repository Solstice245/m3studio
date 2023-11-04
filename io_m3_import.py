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
import bmesh
import mathutils
from . import io_m3
from . import io_shared
from . import shared
from .m3_animations import set_default_value, ob_anim_data_set


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
        (m3_matrix.x.w, m3_matrix.y.w, m3_matrix.z.w, m3_matrix.w.w),
    ))


class M3InputProcessor:

    def __init__(self, importer, bl, m3):
        self.importer = importer
        self.bl = bl
        self.m3 = m3
        self.version = m3.desc.version

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

    def anim_boolean_flag(self, field):
        self.anim_integer(field)

    def anim_integer(self, field):
        anim_ref = getattr(self.m3, field)
        setattr(self.bl, field, anim_ref.default)
        key_fcurves(self.importer.stc_id_data, self.bl, field, anim_ref.header, (anim_ref.default,))

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
        key_fcurves(self.importer.stc_id_data, self.bl, field, anim_ref.header, (anim_ref.default,))

    def anim_vec2(self, field):
        anim_ref = getattr(self.m3, field)
        default = to_bl_vec2(anim_ref.default)
        setattr(self.bl, field, default)
        key_fcurves(self.importer.stc_id_data, self.bl, field, anim_ref.header, default)

    def anim_vec3(self, field, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        anim_ref = getattr(self.m3, field)
        default = to_bl_vec3(anim_ref.default)
        setattr(self.bl, field, default)
        key_fcurves(self.importer.stc_id_data, self.bl, field, anim_ref.header, default)

    def anim_color(self, field, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        anim_ref = getattr(self.m3, field)
        default = to_bl_color(anim_ref.default)
        setattr(self.bl, field, default)
        key_fcurves(self.importer.stc_id_data, self.bl, field, anim_ref.header, default)


def m3_key_collect_evnt(key_frames, key_values):
    pass  # handle these specially


def m3_key_collect_real(key_frames, key_values):
    ll = ([],)

    for key_frame, key_value in zip(key_frames, key_values):
        ll[0].extend((key_frame, key_value))

    return ll


def m3_key_collect_vec2(key_frames, key_values):
    ll = ([], [])

    for key_frame, key_value in zip(key_frames, key_values):
        ll[0].extend((key_frame, key_value.x))
        ll[1].extend((key_frame, key_value.y))

    return ll


def m3_key_collect_vec3(key_frames, key_values):
    ll = ([], [], [])

    for key_frame, key_value in zip(key_frames, key_values):
        ll[0].extend((key_frame, key_value.x))
        ll[1].extend((key_frame, key_value.y))
        ll[2].extend((key_frame, key_value.z))

    return ll


def m3_key_collect_quat(key_frames, key_values):
    ll = ([], [], [], [])

    for key_frame, key_value in zip(key_frames, key_values):
        ll[0].extend((key_frame, key_value.w))
        ll[1].extend((key_frame, key_value.x))
        ll[2].extend((key_frame, key_value.y))
        ll[3].extend((key_frame, key_value.z))

    return ll


def m3_key_collect_colo(key_frames, key_values):
    ll = ([], [], [], [])

    for key_frame, key_value in zip(key_frames, key_values):
        ll[0].append(key_frame)
        ll[0].append(key_value.r / 255)
        ll[1].append(key_frame)
        ll[1].append(key_value.g / 255)
        ll[2].append(key_frame)
        ll[2].append(key_value.b / 255)
        ll[3].append(key_frame)
        ll[3].append(key_value.a / 255)

    return ll


def m3_key_collect_sd08(key_frames, key_values):
    pass  # undefined


def m3_key_collect_bnds(key_frames, key_values):
    pass  # handle these specially


m3_key_type_collection_method = [
    m3_key_collect_evnt, m3_key_collect_vec2, m3_key_collect_vec3, m3_key_collect_quat, m3_key_collect_colo, m3_key_collect_real, m3_key_collect_sd08,
    m3_key_collect_real, m3_key_collect_real, m3_key_collect_real, m3_key_collect_real, m3_key_collect_real, m3_key_collect_bnds,
]


def key_fcurves(stc_dict, bl, field, header, default):

    if not hasattr(bl, field):
        return

    path = bl.path_from_id(field)

    for ii, val in enumerate(default):
        set_default_value(bl.id_data.m3_animations_default, path, ii, val)

    if type(header) == shared.M3AnimHeaderProp:
        anim_id_data = stc_dict.get(int(header.hex_id, 16))
    else:
        anim_id_data = stc_dict.get(header.id)

        bl_header = getattr(bl, field + '_header')
        bl_header.hex_id = hex(header.id)[2:]

        if not anim_id_data:
            bl_header.interpolation = 'AUTO'
            bl_header.flags = -1
            return

        bl_header.interpolation = 'LINEAR' if header.interpolation else 'CONSTANT'
        bl_header.flags = header.flags if header.flags else -1

    if not anim_id_data:
        return

    for action_name in anim_id_data.keys():
        anim_id_action_data = anim_id_data[action_name]
        points_len = len(anim_id_action_data[0]) // 2

        if type(header) == shared.M3AnimHeaderProp:
            interp_seq = [0 if header.interpolation == 'CONSTANT' else 1] * points_len  # TODO calculate AUTO based on field name
        else:
            interp_seq = [header.interpolation] * points_len

        key_sel_seq = [False] * points_len
        for index, index_data in enumerate(anim_id_action_data):
            fcurves = bpy.data.actions.get(action_name).fcurves
            fcurve = fcurves.new(path, index=index)
            fcurve.select = False
            fcurve.keyframe_points.add(points_len)
            fcurve.keyframe_points.foreach_set('co', index_data)
            fcurve.keyframe_points.foreach_set('interpolation', interp_seq)
            fcurve.keyframe_points.foreach_set('select_control_point', key_sel_seq)
            fcurve.keyframe_points.foreach_set('select_left_handle', key_sel_seq)
            fcurve.keyframe_points.foreach_set('select_right_handle', key_sel_seq)


def armature_object_new():
    scene = bpy.context.scene
    arm = bpy.data.armatures.new(name='Armature')
    ob = bpy.data.objects.new('Armature', arm)
    ob.location = scene.cursor.location
    scene.collection.objects.link(ob)

    return ob


class Importer:

    def __init__(self, bl_op=None):
        self.bl_op = bl_op
        self.warn_strings = []

    def report_warnings(self):
        if len(self.warn_strings):
            warning = f'The following warnings were given during the M3 import operation of {self.ob.name}:\n' + '\n'.join(self.warn_strings)
            print(warning)  # not for debugging
            if self.bl_op:
                self.bl_op.report({"WARNING"}, warning)
        self.warn_strings = []  # reset warnings

    def m3_import(self, filename, ob=None, opts=None):
        # TODO make fps an import option
        bpy.context.scene.render.fps = FRAME_RATE

        self.get_rig, self.get_anims, self.get_mesh, self.get_effects = opts if opts != None else [True] * 4

        self.m3 = io_m3.section_list_load(filename)
        self.m3_model = self.m3[self.m3[0][0].model][0]
        self.m3_division = self.m3[self.m3_model.divisions][0]

        self.m3_bl_ref = {}
        self.bl_ref_objects = []
        self.stc_id_data = {}
        self.final_bone_names = {}

        self.is_new_object = not ob
        self.ob = ob or armature_object_new()

        anims_len = len(self.ob.m3_animation_groups)
        matref_len = len(self.ob.m3_materialrefs)
        self.anim_index = lambda x: anims_len + x
        self.matref_index = lambda x: matref_len + x

        self.m3_struct_version_set_from_ref('m3_model_version', self.m3[0][0].model)

        if self.get_rig:
            if self.get_anims:
                self.create_animations()

            self.create_bones()
            self.create_attachments()
            self.create_hittests()
            self.create_rigid_bodies()
            self.create_rigid_body_joints()
            self.create_cameras()
            self.create_billboards()
            self.create_ik_joints()
            self.create_turrets()
            self.create_shadow_boxes()
            self.create_tmd()

        if self.get_rig and self.get_mesh:
            self.create_bounding()

        if self.get_mesh or self.get_effects:
            self.create_materials()

        if self.get_mesh:
            self.create_mesh()

        if self.get_mesh and self.get_rig:
            self.create_cloths()

        if self.get_effects:
            self.create_lights()
            self.create_particles()
            self.create_ribbons()
            self.create_projections()
            self.create_forces()
            self.create_warps()

        if self.is_new_object:
            ob_anim_data_set(bpy.context.scene, self.ob, None)
            bpy.context.view_layer.objects.active = self.ob
            self.ob.select_set(True)

        # lazy way to filter out materials unused by the imported data, but it works
        user_matref_index = self.ob.m3_materialrefs_index
        for ii in reversed(range(len(self.ob.m3_materialrefs))[matref_len:]):
            self.ob.m3_materialrefs_index = ii
            bpy.ops.m3.material_remove('INVOKE_DEFAULT', quiet=True)
        self.ob.m3_materialrefs_index = user_matref_index

    def m3a_import(self, filename, ob):

        def get_m3_id_props():
            hex_id_to_props = {}

            collections = [
                ob.m3_cameras, ob.m3_forces, ob.m3_lights, ob.m3_materiallayers, ob.m3_materials_standard, ob.m3_materials_displacement,
                ob.m3_materials_composite, ob.m3_materials_volume, ob.m3_materials_volumenoise, ob.m3_materials_reflection, ob.m3_materials_lensflare,
                ob.m3_particlesystems, ob.m3_particlecopies, ob.m3_projections, ob.m3_ribbons, ob.m3_ribbonsplines, ob.m3_shadowboxes, ob.m3_warps,
            ]

            def get_anim_ids(collection):
                for item in collection:
                    for key in type(item).__annotations__.keys():
                        prop = getattr(item, key)
                        if type(prop) == shared.M3AnimHeaderProp:
                            prop_path = prop.path_from_id()[:-7]  # removing the _header suffix
                            prop_id_int = int(prop.hex_id, 16)
                            try:
                                hex_id_to_props[prop_id_int].append(prop_path)
                            except KeyError:
                                hex_id_to_props[prop_id_int] = [prop_path]
                        elif str(type(prop)) == '<class \'bpy_prop_collection_idprop\'>':
                            get_anim_ids(prop)

            for collection in collections:
                get_anim_ids(collection)

            return hex_id_to_props

        # TODO make fps an import options
        bpy.context.scene.render.fps = FRAME_RATE
        ob_anim_data_set(bpy.context.scene, ob, None)

        self.is_new_object = False
        self.ob = ob
        self.m3 = io_m3.section_list_load(filename)
        self.m3_model = self.m3[self.m3[0][0].model][0]
        self.stc_id_data = {}

        anims_len = len(self.ob.m3_animation_groups)
        self.anim_index = lambda x: anims_len + x
        self.create_animations()

        m3_id_prop_paths = get_m3_id_props()

        for anim_id_data, paths in m3_id_prop_paths.items():
            rs = paths[0].rsplit('.', 1)
            prop = ob.path_resolve(paths[0])
            try:  # put prop in a tuple if it is not already
                key_fcurves(self.stc_id_data, ob.path_resolve(rs[0]), rs[1], ob.path_resolve(paths[0] + '_header'), prop)
            except TypeError:
                key_fcurves(self.stc_id_data, ob.path_resolve(rs[0]), rs[1], ob.path_resolve(paths[0] + '_header'), (prop,))

        bind_mats = {}
        for pb in ob.pose.bones:
            db = ob.data.bones.get(pb.name)

            # "exporting" bone matrix to get default bone pose in m3 terms
            bind_scale_inv = mathutils.Vector((1.0 / pb.m3_bind_scale[ii] for ii in range(3)))
            bind_scale_inv_matrix = mathutils.Matrix.LocRotScale(None, None, bind_scale_inv.yxz)

            if pb.parent:
                parent_bind_mat = mathutils.Matrix.LocRotScale(None, None, pb.parent.m3_bind_scale.yxz)
                left_out_mat = parent_bind_mat @ io_shared.rot_fix_matrix @ db.parent.matrix_local.inverted() @ db.matrix_local
            else:
                left_out_mat = db.matrix_local
            right_out_mat = io_shared.rot_fix_matrix_transpose @ bind_scale_inv_matrix
            pose_mat = ob.convert_space(pose_bone=pb, matrix=pb.matrix, from_space='LOCAL', to_space='POSE')

            defaults = (left_out_mat @ pose_mat @ right_out_mat).decompose()

            # now importing with the m3 defaults of the current pose
            rel_mat = db.matrix_local.inverted() if not pb.parent else (db.parent.matrix_local.inverted() @ db.matrix_local).inverted()
            bind_mat = bind_mats[pb] = mathutils.Matrix.LocRotScale(None, None, pb.m3_bind_scale.yxz)

            anim_ids = (int(pb.m3_location_hex_id, 16), int(pb.m3_rotation_hex_id, 16), int(pb.m3_scale_hex_id, 16), int(pb.m3_batching_hex_id, 16))

            left_in_mat = rel_mat if not pb.parent else rel_mat @ io_shared.rot_fix_matrix_transpose @ bind_mats[pb.parent].inverted()
            right_in_mat = bind_mat @ io_shared.rot_fix_matrix

            self.animate_pose_bone(anim_ids, defaults, pb, left_in_mat, right_in_mat)

    def m3_struct_version_set_from_ref(self, version_attr, ref):

        if ref.index and ref.entries:
            version_val = self.m3[ref].desc.version

            if not self.is_new_object:
                setattr(self.ob, version_attr, str(max(int(getattr(self.ob, version_attr)), version_val)))
            else:
                setattr(self.ob, version_attr, str(version_val))

    def m3_get_bone_name(self, bone_index):
        m3_bone_name = self.m3[self.m3[self.m3_model.bones][bone_index].name].content_to_string()
        final_bone_name = self.final_bone_names.get(m3_bone_name)
        return final_bone_name or m3_bone_name

    def animate_pose_bone(self, anim_ids, defaults, pose_bone, left_mat, right_mat):
        id_data_loc = self.stc_id_data.get(anim_ids[0], {})
        id_data_rot = self.stc_id_data.get(anim_ids[1], {})
        id_data_scl = self.stc_id_data.get(anim_ids[2], {})
        action_name_set = set().union(id_data_loc.keys(), id_data_rot.keys(), id_data_scl.keys())

        default_loc, default_rot, default_scl = defaults

        for action_name in action_name_set:
            anim_data_loc = id_data_loc.get(action_name, None)
            anim_data_rot = id_data_rot.get(action_name, None)
            anim_data_scl = id_data_scl.get(action_name, None)

            anim_data_loc_none = not anim_data_loc
            if anim_data_loc_none:
                anim_data_loc = [[0, default_loc.x], [0, default_loc.y], [0, default_loc.z]]

            anim_data_rot_none = not anim_data_rot
            if anim_data_rot_none:
                anim_data_rot = [[0, default_rot.w], [0, default_rot.x], [0, default_rot.y], [0, default_rot.z]]

            anim_data_scl_none = not anim_data_scl
            if anim_data_scl_none:
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
                points_len = len(index_data) // 2
                fcurve = fcurves.new(pose_bone.path_from_id('location'), index=index, action_group=pose_bone.name)
                fcurve.select = False
                fcurve.keyframe_points.add(points_len)
                fcurve.keyframe_points.foreach_set('co', index_data)
                fcurve.keyframe_points.foreach_set('interpolation', [1] * points_len)
                fcurve.keyframe_points.foreach_set('select_control_point', key_sel := [False] * points_len)
                fcurve.keyframe_points.foreach_set('select_left_handle', key_sel)
                fcurve.keyframe_points.foreach_set('select_right_handle', key_sel)
                fcurves_loc.append(fcurve)

            fcurves_rot = []
            for index, index_data in enumerate(anim_data_rot):
                points_len = len(index_data) // 2
                fcurve = fcurves.new(pose_bone.path_from_id('rotation_quaternion'), index=index, action_group=pose_bone.name)
                fcurve.select = False
                fcurve.keyframe_points.add(points_len)
                fcurve.keyframe_points.foreach_set('co', index_data)
                fcurve.keyframe_points.foreach_set('interpolation', [1] * points_len)
                fcurve.keyframe_points.foreach_set('select_control_point', key_sel := [False] * points_len)
                fcurve.keyframe_points.foreach_set('select_left_handle', key_sel)
                fcurve.keyframe_points.foreach_set('select_right_handle', key_sel)
                fcurves_rot.append(fcurve)

            fcurves_scl = []
            for index, index_data in enumerate(anim_data_scl):
                points_len = len(index_data) // 2
                fcurve = fcurves.new(pose_bone.path_from_id('scale'), index=index, action_group=pose_bone.name)
                fcurve.select = False
                fcurve.keyframe_points.add(points_len)
                fcurve.keyframe_points.foreach_set('co', index_data)
                fcurve.keyframe_points.foreach_set('interpolation', [1] * points_len)
                fcurve.keyframe_points.foreach_set('select_control_point', key_sel := [False] * points_len)
                fcurve.keyframe_points.foreach_set('select_left_handle', key_sel)
                fcurve.keyframe_points.foreach_set('select_right_handle', key_sel)
                fcurves_scl.append(fcurve)

            new_anim_data = [[], [], []]
            pre_rot = None
            for frame in sorted(list(anim_frames_set)):
                eval_loc = mathutils.Vector([fcurve.evaluate(frame) for fcurve in fcurves_loc])
                eval_rot = mathutils.Quaternion([fcurve.evaluate(frame) for fcurve in fcurves_rot])
                eval_scl = mathutils.Vector([fcurve.evaluate(frame) for fcurve in fcurves_scl])

                loc, rot, scl = (left_mat @ mathutils.Matrix.LocRotScale(eval_loc, eval_rot, eval_scl) @ right_mat).decompose()

                if pre_rot:
                    rot.make_compatible(pre_rot)
                pre_rot = rot

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

        # import bone batching flag
        id_data_render = self.stc_id_data.get(anim_ids[3], {})

        if id_data_render:
            for action_name in id_data_render.keys():
                action = bpy.data.actions.get(action_name)
                key_frame_points_len = len(id_data_render[action_name][0]) // 2

                fcurve = action.fcurves.new(pose_bone.path_from_id('m3_batching'), action_group=pose_bone.name)
                fcurve.select = False
                fcurve.keyframe_points.add(key_frame_points_len)
                fcurve.keyframe_points.foreach_set('co', id_data_render[action_name][0])
                fcurve.keyframe_points.foreach_set('interpolation', [0] * key_frame_points_len)

    def create_animations(self):
        ob = self.ob

        if self.is_new_object:
            ob.m3_animations_default = bpy.data.actions.new(ob.name + '_DEFAULTS')

        for m3_seq, m3_stg in zip(self.m3[self.m3_model.sequences], self.m3[self.m3_model.sequence_transformation_groups]):
            anim_group_name = self.m3[m3_seq.name].content_to_string()
            anim_group = shared.m3_item_add(ob.m3_animation_groups, anim_group_name)
            seq_processor = M3InputProcessor(self, anim_group, m3_seq)
            io_shared.io_anim_group(seq_processor)

            anim_group['frame_start'] = to_bl_frame(m3_seq.anim_ms_start)
            anim_group['frame_end'] = to_bl_frame(m3_seq.anim_ms_end)

            for m3_stc_index in self.m3[m3_stg.stc_indices]:
                m3_stc = self.m3[self.m3_model.sequence_transformation_collections][m3_stc_index]

                if not m3_stc.name.index:
                    continue

                anim_name = self.m3[m3_stc.name].content_to_string().replace(anim_group_name, '')[1:]
                anim = shared.m3_item_add(anim_group.animations, anim_name)
                anim['concurrent'] = m3_stc.concurrent
                anim['priority'] = m3_stc.priority
                anim['action'] = bpy.data.actions.new(f'{ob.name}_{anim_group.name}_{anim.name}')

                m3_key_type_collection_list = [
                    m3_stc.sdev, m3_stc.sd2v, m3_stc.sd3v, m3_stc.sd4q, m3_stc.sdcc, m3_stc.sdr3, m3_stc.sd08,
                    m3_stc.sds6, m3_stc.sdu6, m3_stc.sds3, m3_stc.sdu3, m3_stc.sdfg, m3_stc.sdmb,
                ]

                for stc_id, stc_ref in zip(self.m3[m3_stc.anim_ids], self.m3[m3_stc.anim_refs]):
                    anim_type = stc_ref >> 16
                    anim_index = stc_ref & 0xffff
                    m3_key_type_collection = m3_key_type_collection_list[anim_type]
                    m3_key_entries = self.m3[m3_key_type_collection][anim_index]

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

                    try:
                        self.stc_id_data[stc_id][anim.action.name] = m3_key_type_collection_method[anim_type](frames, keys)
                    except KeyError:
                        self.stc_id_data[stc_id] = {}
                        self.stc_id_data[stc_id][anim.action.name] = m3_key_type_collection_method[anim_type](frames, keys)

                    # consider making a dedicated property type and collection list for events
                    if m3_key_type_collection == m3_stc.sdev:
                        for ii, frame in enumerate(frames):
                            key = keys[ii]
                            event_name = self.m3[key.name].content_to_string()
                            if event_name == 'Evt_Simulate':
                                anim_group['simulate'] = True
                                anim_group['simulate_frame'] = frame

            anim_group['animations_index'] = 0

    def create_bones(self):

        def get_bone_tails(m3_bones, bone_heads, bone_vectors):
            child_bone_indices = [[] for ii in m3_bones]
            for bone_index, bone_entry in enumerate(m3_bones):
                if bone_entry.parent != -1:
                    child_bone_indices[bone_entry.parent].append(bone_index)

            tails = []

            for m3_bone, child_indices, head, vector in zip(m3_bones, child_bone_indices, bone_heads, bone_vectors):
                length = 0.1
                for child_index in child_indices:
                    head_to_child_head = bone_heads[child_index] - head
                    if head_to_child_head.length >= 0.01 and abs(head_to_child_head.angle(vector)) < 0.1:
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

        def get_edit_bones(m3_bones, bone_heads, bone_tails, bone_rolls):
            edit_bones = []
            for index, m3_bone in enumerate(m3_bones):
                m3_bone_name = self.m3[m3_bone.name].content_to_string()
                edit_bone = self.ob.data.edit_bones.new(m3_bone_name)
                self.final_bone_names[m3_bone_name] = edit_bone.name
                edit_bone.head = bone_heads[index]
                edit_bone.tail = bone_tails[index]
                edit_bone.roll = bone_rolls[index]
                edit_bone.select_tail = False

                if m3_bone.parent != -1:
                    parent_edit_bone = self.ob.data.edit_bones[m3_bone.parent]
                    edit_bone.parent = parent_edit_bone
                    parent_child_vector = parent_edit_bone.tail - edit_bone.head

                    if parent_child_vector.length < 0.000001:
                        edit_bone.use_connect = True
                edit_bones.append(edit_bone)

            return edit_bones

        def get_edit_bone_relations(m3_bones, edit_bones):
            rel_mats = []
            for m3_bone, edit_bone in zip(m3_bones, edit_bones):

                if m3_bone.parent != -1:
                    parent_edit_bone = self.ob.data.edit_bones.get(self.m3_get_bone_name(m3_bone.parent))
                    rel_mats.append((parent_edit_bone.matrix.inverted() @ edit_bone.matrix).inverted())
                else:
                    rel_mats.append(edit_bone.matrix.inverted())

            return rel_mats

        def adjust_pose_bones(m3_bones, edit_bone_relations, bind_scales, bind_matrices):
            for ii, m3_bone, rel_mat, bind_scl, bind_mat in zip(range(len(m3_bones)), m3_bones, edit_bone_relations, bind_scales, bind_matrices):

                if m3_bone.parent != -1:
                    bind_mat.transpose()

                left_mat = rel_mat if m3_bone.parent == -1 else rel_mat @ io_shared.rot_fix_matrix_transpose @ bind_matrices[m3_bone.parent].inverted()
                right_mat = bind_mat @ io_shared.rot_fix_matrix
                bone_mat_comp = to_bl_vec3(m3_bone.location.default), to_bl_quat(m3_bone.rotation.default), to_bl_vec3(m3_bone.scale.default)
                bone_mat = mathutils.Matrix.LocRotScale(*bone_mat_comp)
                pose_bone = self.ob.pose.bones.get(self.m3_get_bone_name(ii))
                pose_bone.matrix_basis = left_mat @ bone_mat @ right_mat
                pose_bone.bl_handle = shared.m3_handle_gen()
                pose_bone.m3_bind_scale = (bind_scl[1], bind_scl[0], bind_scl[2])

                bone_id_lock = self.ob.m3_bone_id_lockers.add()
                bone_id_lock.bone = pose_bone.bl_handle

                pose_bone.m3_batching = bool(m3_bone.batching.default)

                pose_bone.m3_location_hex_id = hex(m3_bone.location.header.id)[2:]
                pose_bone.m3_rotation_hex_id = hex(m3_bone.rotation.header.id)[2:]
                pose_bone.m3_scale_hex_id = hex(m3_bone.scale.header.id)[2:]
                pose_bone.m3_batching_hex_id = hex(m3_bone.batching.header.id)[2:]

                m3_anim_ids = (m3_bone.location.header.id, m3_bone.rotation.header.id, m3_bone.scale.header.id, m3_bone.batching.header.id)
                m3_defaults = (m3_bone.location.default, m3_bone.rotation.default, m3_bone.scale.default)

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
                set_default_value(self.ob.m3_animations_default, pose_bone.path_from_id('m3_batching'), 0, pose_bone.m3_batching)
                self.animate_pose_bone(m3_anim_ids, m3_defaults, pose_bone, left_mat, right_mat)

        bpy.context.view_layer.objects.active = self.ob

        bl_irefs = []
        bone_rests = []
        bind_scales = []
        bind_matrices = []
        bone_heads = []
        bone_vectors = []

        m3_bones = self.m3[self.m3_model.bones]

        for iref, m3_bone in zip(self.m3[self.m3_model.bone_rests], m3_bones):
            orig_mat = to_bl_matrix(iref.matrix)
            mat = orig_mat.copy()

            mat_scale = mat.to_scale()
            for ii in range(3):
                if mat_scale[ii] < 0:
                    mat[ii] = -mat[ii]

            bl_irefs.append(mat)
            bone_rests.append(mat.inverted() @ io_shared.rot_fix_matrix)
            bind_scales.append((orig_mat @ io_shared.rot_fix_matrix_transpose).to_scale().yxz)
            bone_heads.append(bone_rests[-1].translation)
            bone_vectors.append(bone_rests[-1].col[1].to_3d().normalized())

        bone_tails = get_bone_tails(m3_bones, bone_heads, bone_vectors)
        bone_rolls = get_bone_rolls(bone_rests, bone_heads, bone_tails)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        edit_bones = get_edit_bones(m3_bones, bone_heads, bone_tails, bone_rolls)
        edit_bone_relations = get_edit_bone_relations(m3_bones, edit_bones)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # this fixes the scale of bone rest matrices that use an unusual matrix form
        for ii, m3_bone in enumerate(m3_bones):
            db = self.ob.data.bones.get(self.m3[m3_bone.name].content_to_string())
            bone_local_inv_matrix = (db.matrix_local @ io_shared.rot_fix_matrix_transpose).inverted()
            iref = bl_irefs[ii]
            out_iref = mathutils.Matrix.LocRotScale(None, None, bind_scales[ii]) @ bone_local_inv_matrix

            # hacky solution for certain import problems, could cause problems elsewhere
            sub_x = abs(abs(sum(iref[0])) - abs(sum(out_iref[0]))) + 1
            sub_y = abs(abs(sum(iref[1])) - abs(sum(out_iref[1]))) + 1
            sub_z = abs(abs(sum(iref[2])) - abs(sum(out_iref[2]))) + 1

            div_x = sum(iref[0]) / sum(out_iref[0]) if (sum(iref[0]) and sum(out_iref[0])) else 1
            div_y = sum(iref[1]) / sum(out_iref[1]) if (sum(iref[1]) and sum(out_iref[1])) else 1
            div_z = sum(iref[2]) / sum(out_iref[2]) if (sum(iref[2]) and sum(out_iref[2])) else 1

            if abs(sum((sub_x, sub_y, sub_z))) < abs(sum((div_x, div_y, div_z))):
                bind_fac_x = abs(abs(sum(iref[0])) - abs(sum(out_iref[0]))) + 1
                bind_fac_y = abs(abs(sum(iref[1])) - abs(sum(out_iref[1]))) + 1
                bind_fac_z = abs(abs(sum(iref[2])) - abs(sum(out_iref[2]))) + 1
            else:
                bind_fac_x = abs(sum(iref[0]) / sum(out_iref[0])) if (sum(iref[0]) and sum(out_iref[0])) else 1
                bind_fac_y = abs(sum(iref[1]) / sum(out_iref[1])) if (sum(iref[1]) and sum(out_iref[1])) else 1
                bind_fac_z = abs(sum(iref[2]) / sum(out_iref[2])) if (sum(iref[2]) and sum(out_iref[2])) else 1

            bind_scales[ii][0] = bind_scales[ii][0] * bind_fac_x
            bind_scales[ii][1] = bind_scales[ii][1] * bind_fac_y
            bind_scales[ii][2] = bind_scales[ii][2] * bind_fac_z

            bind_matrices.append(mathutils.Matrix.LocRotScale(None, None, bind_scales[ii]))

        adjust_pose_bones(m3_bones, edit_bone_relations, bind_scales, bind_matrices)

    def create_materials(self):
        ob = self.ob

        standard_m3_version = self.m3[self.m3_model.materials_standard].desc.version
        standard_bl_version = int(self.ob.m3_materials_standard_version)

        if standard_m3_version > 16 and standard_bl_version <= 16:
            for mat in self.ob.m3_materials_standard:
                mat.geometry_visible = True
                self.warn_strings.append(f'Existing material {mat.name} "Geometry Visible" flag automatically checked, due to material version upgrade.')

        self.m3_struct_version_set_from_ref('m3_materials_standard_version', self.m3_model.materials_standard)

        standard_bl_version = int(self.ob.m3_materials_standard_version)

        if hasattr(self.m3_model, 'materials_reflection'):
            self.m3_struct_version_set_from_ref('m3_materials_reflection_version', self.m3_model.materials_reflection)

        layer_section_to_index = {}
        for m3_matref in self.m3[self.m3_model.material_references]:
            m3_mat = self.m3[getattr(self.m3_model, shared.material_type_to_model_reference[m3_matref.type])][m3_matref.material_index]

            matref = shared.m3_item_add(ob.m3_materialrefs, item_name=self.m3[m3_mat.name].content_to_string())
            mat_col = getattr(ob, 'm3_' + shared.material_type_to_model_reference[m3_matref.type])
            mat = shared.m3_item_add(mat_col, item_name=matref.name)

            processor = M3InputProcessor(self, mat, m3_mat)
            io_shared.material_type_io_method[m3_matref.type](processor)

            matref.mat_type = 'm3_' + shared.material_type_to_model_reference[m3_matref.type]
            matref.mat_handle = mat.bl_handle

            if m3_matref.type == 1:  # standard materials
                if standard_m3_version <= 16 and standard_bl_version > 16:
                    mat.geometry_visible = True
                    self.warn_strings.append(f'Imported material {matref.name} "Geometry Visible" flag automatically checked, due to material version upgrade.')
            if m3_matref.type == 3:  # composite materials
                for m3_section in self.m3[m3_mat.sections]:
                    section = shared.m3_item_add(mat.sections)
                    section.material.handle = ob.m3_materialrefs[self.matref_index(m3_section.material_reference_index)].bl_handle
                    processor = M3InputProcessor(self, section, m3_section)
                    io_shared.io_material_composite_section(processor)
            elif m3_matref.type == 11:  # lens flare materials
                for m3_starburst in self.m3[m3_mat.starbursts]:
                    starburst = shared.m3_item_add(mat.starbursts)
                    processor = M3InputProcessor(self, starburst, m3_starburst)
                    io_shared.io_starburst(processor)

            for layer_name in shared.material_type_to_layers[m3_matref.type]:
                m3_layer_field = getattr(m3_mat, 'layer_' + layer_name, None)
                if not m3_layer_field:
                    continue

                if m3_layer_field.index in layer_section_to_index.keys():
                    layer = ob.m3_materiallayers[layer_section_to_index[m3_layer_field.index]]
                    setattr(mat, 'layer_' + layer_name, layer.bl_handle)
                    continue

                m3_layer = self.m3[m3_layer_field][0]
                m3_layer_bitmap_str = self.m3[m3_layer.color_bitmap].content_to_string() if m3_layer.color_bitmap.index else ''
                if not m3_layer_bitmap_str and not m3_layer.bit_get('flags', 'color'):
                    continue

                self.m3_struct_version_set_from_ref('m3_materiallayers_version', m3_layer_field)

                layer = shared.m3_item_add(ob.m3_materiallayers, item_name=matref.name + '_' + layer_name)
                layer.color_bitmap = m3_layer_bitmap_str
                processor = M3InputProcessor(self, layer, m3_layer)
                io_shared.io_material_layer(processor)

                layer.color_type = 'COLOR' if m3_layer.bit_get('flags', 'color') else 'BITMAP'
                layer.fresnel_max = m3_layer.fresnel_min + m3_layer.fresnel_max_offset

                if m3_layer.desc.version >= 25:
                    layer.fresnel_mask[0] = 1.0 - m3_layer.fresnel_inverted_mask_x
                    layer.fresnel_mask[1] = 1.0 - m3_layer.fresnel_inverted_mask_y
                    layer.fresnel_mask[2] = 1.0 - m3_layer.fresnel_inverted_mask_z

                layer_section_to_index[m3_layer_field.index] = len(ob.m3_materiallayers) - 1
                setattr(mat, 'layer_' + layer_name, layer.bl_handle)

    def create_mesh(self):
        ob = self.ob

        if not (self.m3_division.regions.index and self.m3_division.regions.entries):
            return

        self.m3_struct_version_set_from_ref('m3_mesh_version', self.m3_division.regions)
        m3_vertices = self.m3[self.m3_model.vertices]

        if not self.m3_model.bit_get('vertex_flags', 'has_vertices'):
            if len(self.m3_model.vertices):
                raise Exception(f'Mesh claims to not have any vertices - expected buffer to be empty, but it isn\'t. size={len(m3_vertices)}')
            return

        v_colors = self.m3_model.bit_get('vertex_flags', 'has_vertex_colors')
        v_class = 'VertexFormat' + hex(self.m3_model.vertex_flags)
        if v_class not in io_m3.structures:
            raise Exception(f'{v_class} structure is undefined. Buffer size={len(m3_vertices)}')

        v_class_desc = io_m3.structures[v_class].get_version(0)
        v_count = len(m3_vertices) // v_class_desc.size
        m3_vertices = v_class_desc.instances(buffer=m3_vertices.raw_bytes, count=v_count)
        bone_lookup_full = self.m3[self.m3_model.bone_lookup]

        uv_props = []
        for uv_prop in ['uv0', 'uv1', 'uv2', 'uv3', 'uv4']:
            if v_class_desc.fields.get(uv_prop):
                uv_props.append(uv_prop)

        m3_faces = self.m3[self.m3_division.faces]
        m3_batches = self.m3[self.m3_division.batches]
        self.m3_bl_ref[self.m3_division.regions.index] = {}

        for region_ii, region in enumerate(self.m3[self.m3_division.regions]):
            region_batches = [batch for batch in m3_batches if batch.region_index == region_ii]

            if not region_batches:
                continue

            regn_m3_verts = m3_vertices[region.first_vertex_index:region.first_vertex_index + region.vertex_count]
            regn_m3_faces = m3_faces[region.first_face_index:region.first_face_index + region.face_count]
            regn_uv_multiply = getattr(region, 'uv_multiply', 16)
            regn_uv_offset = getattr(region, 'uv_offset', 0)

            if region.desc.version <= 2:
                for ii in range(len(regn_m3_faces)):
                    regn_m3_faces[ii] -= region.first_vertex_index

            regn_m3_vert_ids = {}
            regn_m3_vert_to_id = {}
            regn_m3_verts_new = []

            dups = 0
            for ii, v in enumerate(regn_m3_verts):
                id_tuple = (*to_bl_vec3(v.pos), *to_bl_vec3(v.normal), v.lookup0, v.lookup1, v.lookup2, v.lookup3, v.weight0, v.weight1, v.weight2, v.weight3)
                regn_m3_vert_to_id[ii] = id_tuple
                if regn_m3_vert_ids.get(id_tuple) is None:
                    regn_m3_vert_ids[id_tuple] = ii - dups
                    regn_m3_verts_new.append(v)
                else:
                    dups += 1

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

            for batch in region_batches:
                mesh_batch = shared.m3_item_add(mesh_ob.m3_mesh_batches)
                mesh_batch.material.handle = ob.m3_materialrefs[self.matref_index(batch.material_reference_index)].bl_handle

                if batch.bone != -1:
                    pose_bone_name = self.m3_get_bone_name(batch.bone)
                    pose_bone = ob.pose.bones.get(pose_bone_name)
                    mesh_batch.bone.handle = pose_bone.bl_handle if pose_bone else ''

            bm = bmesh.new(use_operators=True)

            layer_deform = bm.verts.layers.deform.new('m3lookup')
            layer_color = bm.loops.layers.color.new('m3color') if v_colors else None
            layer_alpha = bm.loops.layers.color.new('m3alpha') if v_colors else None

            for uv_prop in uv_props:
                bm.loops.layers.uv.new(uv_prop)

            vert_to_m3_vert = {}
            for m3_vert in regn_m3_verts_new:
                vert = bm.verts.new((m3_vert.pos.x, m3_vert.pos.y, m3_vert.pos.z))

                vert_to_m3_vert[vert] = m3_vert

                for ii in range(0, region.vertex_lookups_used):
                    weight = getattr(m3_vert, 'weight' + str(ii))
                    if weight:
                        lookup_index = getattr(m3_vert, 'lookup' + str(ii))
                        vertex_groups_used[lookup_index] = True
                        vert[layer_deform][lookup_index] = weight / 255

            bm.verts.ensure_lookup_table()

            for ii in range(0, len(regn_m3_faces), 3):

                try:
                    v0 = bm.verts[regn_m3_vert_ids.get(regn_m3_vert_to_id[regn_m3_faces[ii]])]
                    v1 = bm.verts[regn_m3_vert_ids.get(regn_m3_vert_to_id[regn_m3_faces[ii + 1]])]
                    v2 = bm.verts[regn_m3_vert_ids.get(regn_m3_vert_to_id[regn_m3_faces[ii + 2]])]
                    face = bm.faces.new((v0, v1, v2))
                    face.smooth = True

                    for jj in range(3):
                        m3v = regn_m3_verts[regn_m3_faces[ii + jj]]
                        loop = face.loops[jj]
                        for uv_prop in uv_props:
                            layer_uv = bm.loops.layers.uv.get(uv_prop)
                            loop[layer_uv].uv = to_bl_uv(getattr(m3v, uv_prop), regn_uv_multiply, regn_uv_offset)
                        if layer_color:
                            loop[layer_color] = (m3v.col.r / 255, m3v.col.g / 255, m3v.col.b / 255, 1)
                            loop[layer_alpha] = (m3v.col.a / 255, m3v.col.a / 255, m3v.col.a / 255, 1)
                except ValueError:
                    pass  # most likely to be duplicate or degenerate face

            bm.faces.ensure_lookup_table()

            def get_matching_edge(origin, target):
                for oedge in origin.link_edges:
                    for tedge in target.link_edges:
                        if len(set((tuple(oedge.verts[0].co), tuple(oedge.verts[1].co), tuple(tedge.verts[0].co), tuple(tedge.verts[1].co)))) == 2:
                            return not tedge.smooth  # return False if the edge is smooth
                return False

            doubles = bmesh.ops.find_doubles(bm, verts=bm.verts, dist=0.00001)['targetmap']
            for origin in list(doubles.keys()):
                target = doubles[origin]

                for edge in [*origin.link_edges, *target.link_edges]:
                    if len(edge.link_faces) == 1:
                        edge.smooth = False

            doubles_inverse = {}
            for key in doubles:
                try:
                    doubles_inverse[doubles[key]].append(key)
                except KeyError:
                    doubles_inverse[doubles[key]] = [key]

            point_lists = []
            for key in doubles:
                key_assigned = False
                for plist in point_lists:
                    if doubles[key] in plist:
                        plist.append(key)
                        key_assigned = True
                        break
                    elif doubles_inverse.get(key):
                        for val in doubles_inverse[key]:
                            if val in plist:
                                plist.append(key)
                                key_assigned = True
                                break
                if not key_assigned:
                    point_lists.append([key, doubles[key]])

            edge_match_dict = {}
            for plist in point_lists:
                for ii, origin in enumerate(plist):
                    plist.pop(ii)
                    edge_match_dict[origin] = {target: get_matching_edge(origin, target) for target in plist}
                    plist.insert(ii, origin)

            for origin in edge_match_dict:
                for target in edge_match_dict[origin]:
                    if not edge_match_dict[origin][target]:
                        if doubles.get(origin) == target and doubles.get(target) != origin:
                            common_keys = list(set(edge_match_dict[origin].keys()).intersection(edge_match_dict[target].keys()))
                            common_dict = {key: edge_match_dict[target][key] for key in common_keys}
                            if True not in common_dict.values():
                                doubles.pop(origin, None)
                        elif doubles.get(target) == origin and doubles.get(origin) != target:
                            common_keys = list(set(edge_match_dict[origin].keys()).intersection(edge_match_dict[target].keys()))
                            common_dict = {key: edge_match_dict[target][key] for key in common_keys}
                            if True not in common_dict.values():
                                doubles.pop(target, None)

            for origin in list(doubles.keys()):
                target = doubles[origin]

                m3v0 = vert_to_m3_vert[origin]
                m3v1 = vert_to_m3_vert[target]

                m3v0_lookup_id = (m3v0.lookup0, m3v0.lookup1, m3v0.lookup2, m3v0.lookup3, m3v0.weight0, m3v0.weight1, m3v0.weight2, m3v0.weight3)
                m3v1_lookup_id = (m3v1.lookup0, m3v1.lookup1, m3v1.lookup2, m3v1.lookup3, m3v1.weight0, m3v1.weight1, m3v1.weight2, m3v1.weight3)

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

    def create_attachments(self):
        ob = self.ob

        m3_volumes = self.m3[self.m3_model.attachment_volumes]

        for m3_point in self.m3[self.m3_model.attachment_points]:
            bone_name = self.m3_get_bone_name(m3_point.bone)
            pose_bone = ob.pose.bones.get(bone_name)
            point = shared.m3_item_add(ob.m3_attachmentpoints, item_name=self.m3[m3_point.name].content_to_string())
            point.bone.handle = pose_bone.bl_handle if pose_bone else ''

            for m3_volume in m3_volumes:
                if m3_volume.bone0 == m3_point.bone:
                    m3_vol_pose_bone_name = self.m3_get_bone_name(m3_volume.bone1)
                    m3_vol_pose_bone = ob.pose.bones.get(m3_vol_pose_bone_name)
                    vol = shared.m3_item_add(point.volumes, item_name='Volume')
                    vol.bone.handle = m3_vol_pose_bone.bl_handle if m3_vol_pose_bone else ''
                    vol.shape = vol.bl_rna.properties['shape'].enum_items[getattr(m3_volume, 'shape')].identifier
                    vol.size = (m3_volume.size0, m3_volume.size1, m3_volume.size2)
                    md = to_bl_matrix(m3_volume.matrix).decompose()
                    vol.location = md[0]
                    vol.rotation = md[1].to_euler('XYZ')
                    vol.scale = md[2]
                    vol.mesh_object = self.gen_basic_volume_object(f'{point.name}_{vol.name}', m3_volume.vertices, m3_volume.face_data)

    def create_lights(self):
        ob = self.ob

        for m3_light in self.m3[self.m3_model.lights]:
            pose_bone_name = self.m3_get_bone_name(m3_light.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            light = shared.m3_item_add(ob.m3_lights, item_name=pose_bone_name)
            light.bone.handle = pose_bone.bl_handle if pose_bone else ''
            processor = M3InputProcessor(self, light, m3_light)
            io_shared.io_light(processor)

    def create_shadow_boxes(self):
        if not hasattr(self.m3_model, 'shadow_boxes'):
            return

        ob = self.ob
        for m3_shadow_box in self.m3[self.m3_model.shadow_boxes]:
            pose_bone_name = self.m3_get_bone_name(m3_shadow_box.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            shadow_box = shared.m3_item_add(ob.m3_shadowboxes, item_name=pose_bone_name)
            shadow_box.bone.handle = pose_bone.bl_handle if pose_bone else ''
            processor = M3InputProcessor(self, shadow_box, m3_shadow_box)
            io_shared.io_shadow_box(processor)

    def create_cameras(self):
        ob = self.ob

        self.m3_struct_version_set_from_ref('m3_cameras_version', self.m3_model.cameras)

        for m3_camera in self.m3[self.m3_model.cameras]:
            pose_bone_name = self.m3_get_bone_name(m3_camera.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            camera = shared.m3_item_add(ob.m3_cameras, item_name=pose_bone_name)
            camera.bone.handle = pose_bone.bl_handle if pose_bone else ''
            processor = M3InputProcessor(self, camera, m3_camera)
            io_shared.io_camera(processor)

    def create_particles(self):
        ob = self.ob

        self.m3_struct_version_set_from_ref('m3_particlesystems_version', self.m3_model.particle_systems)

        m3_systems = self.m3[self.m3_model.particle_systems]
        m3_copies = self.m3[self.m3_model.particle_copies]

        for m3_copy in m3_copies:
            pose_bone_name = self.m3_get_bone_name(m3_copy.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            copy = shared.m3_item_add(ob.m3_particlecopies, item_name=pose_bone_name)
            copy.bone.handle = pose_bone.bl_handle if pose_bone else ''
            processor = M3InputProcessor(self, copy, m3_copy)
            io_shared.io_particle_copy(processor)

        system_handles = []
        prev_particles = len(ob.m3_particlesystems)

        for m3_system in m3_systems:
            pose_bone_name = self.m3_get_bone_name(m3_system.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            system = shared.m3_item_add(ob.m3_particlesystems, item_name=pose_bone_name)
            system_handles.append(system.bl_handle)
            system.bone.handle = pose_bone.bl_handle if pose_bone else ''
            system.material.handle = ob.m3_materialrefs[self.matref_index(m3_system.material_reference_index)].bl_handle

            processor = M3InputProcessor(self, system, m3_system)
            io_shared.io_particle_system(processor)

            if m3_system.bit_get('flags', 'tail_clamp'):
                system.tail_type = 'CLAMP'
            if m3_system.bit_get('flags', 'tail_fix'):
                system.tail_type = 'FIX'

            if m3_system.bit_get('flags', 'sort_distance'):
                system.sort_method = 'DISTANCE'
            elif m3_system.bit_get('flags', 'sort_height'):
                system.sort_method = 'HEIGHT'

            if m3_system.bit_get('flags', 'old_color_smooth'):
                system.old_color_smoothing = 'SMOOTH'
            elif m3_system.bit_get('flags', 'old_color_bezier'):
                system.old_color_smoothing = 'BEZIER'

            if m3_system.bit_get('flags', 'old_rotation_smooth'):
                system.old_rotation_smoothing = 'SMOOTH'
            elif m3_system.bit_get('flags', 'old_rotation_bezier'):
                system.old_rotation_smoothing = 'BEZIER'

            if m3_system.bit_get('flags', 'old_size_smooth'):
                system.old_size_smoothing = 'SMOOTH'
            elif m3_system.bit_get('flags', 'old_size_bezier'):
                system.old_size_smoothing = 'BEZIER'

            if hasattr(m3_system, 'emit_shape_regions'):
                for region_indice in self.m3[m3_system.emit_shape_regions]:
                    mesh_object_pointer = system.emit_shape_meshes.add()
                    try:
                        mesh_object_pointer.bl_object = self.m3_bl_ref.get(self.m3_division.regions.index)[region_indice]
                    except TypeError:  # for when get() returns None
                        self.warn_strings.append(f'No matching mesh found for particle system {system}. Unable to assign mesh shape emitter {region_indice}.')

            for m3_point in self.m3[m3_system.emit_shape_spline]:
                point = system.emit_shape_spline.add()
                processor = M3InputProcessor(self, point, m3_point)
                processor.anim_vec3('location')

            for m3_copy_index in self.m3[m3_system.copy_indices]:
                copy = ob.m3_particlecopies[-len(m3_copies) + m3_copy_index]
                system_pointer = copy.systems.add()
                system_pointer.handle = system.bl_handle

            m3_modelpaths = self.m3[m3_system.model_paths]
            if m3_modelpaths:  # it is only valid to have 1 path given
                system.model_path = self.m3[m3_modelpaths[0].path].content_to_string()

        for system, m3_system in zip(ob.m3_particlesystems[prev_particles:], m3_systems):
            system.collide_system.handle = system_handles[m3_system.collide_system] if m3_system.collide_system >= 0 else ''
            system.trail_system.handle = system_handles[m3_system.trail_system] if m3_system.trail_system >= 0 else ''

    def create_ribbons(self):
        ob = self.ob

        self.m3_struct_version_set_from_ref('m3_ribbons_version', self.m3_model.ribbons)

        for m3_ribbon in self.m3[self.m3_model.ribbons]:
            pose_bone_name = self.m3_get_bone_name(m3_ribbon.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            ribbon = shared.m3_item_add(ob.m3_ribbons, item_name=pose_bone_name)
            ribbon.bone.handle = pose_bone.bl_handle if pose_bone else ''
            ribbon.material.handle = ob.m3_materialrefs[self.matref_index(m3_ribbon.material_reference_index)].bl_handle
            processor = M3InputProcessor(self, ribbon, m3_ribbon)
            io_shared.io_ribbon(processor)

            if m3_ribbon.spline.index:
                for ref in self.bl_ref_objects:
                    if [m3_ribbon.spline.index] == ref['sections']:
                        ribbon.spline.handle = ref['ob'].bl_handle
                else:
                    m3_spline = self.m3[m3_ribbon.spline]
                    spline = shared.m3_item_add(ob.m3_ribbonsplines, item_name=ribbon.name + '_spline')
                    ribbon.spline.handle = spline.bl_handle
                    for m3_point in m3_spline:
                        pose_bone_name = self.m3_get_bone_name(m3_point.bone)
                        pose_bone = ob.pose.bones.get(pose_bone_name)
                        point = shared.m3_item_add(spline.points, item_name=pose_bone_name)
                        point.bone.handle = pose_bone.bl_handle if pose_bone else ''
                        processor = M3InputProcessor(self, point, m3_point)
                        io_shared.io_ribbon_spline(processor)
                    self.m3_bl_ref[m3_ribbon.spline.index] = spline

    def create_projections(self):
        ob = self.ob
        for m3_projection in self.m3[self.m3_model.projections]:
            pose_bone_name = self.m3_get_bone_name(m3_projection.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            projection = shared.m3_item_add(ob.m3_projections, item_name=pose_bone_name)
            projection.bone.handle = pose_bone.bl_handle if pose_bone else ''
            projection.material.handle = ob.m3_materialrefs[self.matref_index(m3_projection.material_reference_index)].bl_handle
            processor = M3InputProcessor(self, projection, m3_projection)
            io_shared.io_projection(processor)

    def create_forces(self):
        ob = self.ob

        self.m3_struct_version_set_from_ref('m3_forces_version', self.m3_model.forces)

        for m3_force in self.m3[self.m3_model.forces]:
            pose_bone_name = self.m3_get_bone_name(m3_force.bone)
            pose_bone = ob.data.bones.get(pose_bone_name)
            force = shared.m3_item_add(ob.m3_forces, item_name=pose_bone_name)
            force.bone.handle = pose_bone.bl_handle if pose_bone else ''
            processor = M3InputProcessor(self, force, m3_force)
            io_shared.io_force(processor)

    def create_warps(self):
        ob = self.ob
        for m3_warp in self.m3[self.m3_model.warps]:
            pose_bone_name = self.m3_get_bone_name(m3_warp.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            warp = shared.m3_item_add(ob.m3_warps, item_name=pose_bone_name)
            warp.bone.handle = pose_bone.bl_handle if pose_bone else ''
            processor = M3InputProcessor(self, warp, m3_warp)
            io_shared.io_warp(processor)

    def create_hittests(self):
        ob = self.ob

        m3_hittest_tight = self.m3_model.hittest_tight
        pose_bone_name = self.m3_get_bone_name(m3_hittest_tight.bone)
        pose_bone = ob.pose.bones.get(pose_bone_name)
        ob.m3_hittest_tight.bone.handle = pose_bone.bl_handle if pose_bone else ''
        ob.m3_hittest_tight.shape = ob.m3_hittest_tight.bl_rna.properties['shape'].enum_items[m3_hittest_tight.shape].identifier
        ob.m3_hittest_tight.size = (m3_hittest_tight.size0, m3_hittest_tight.size1, m3_hittest_tight.size2)
        md = to_bl_matrix(m3_hittest_tight.matrix).decompose()
        ob.m3_hittest_tight.location = md[0]
        ob.m3_hittest_tight.rotation = md[1].to_euler('XYZ')
        ob.m3_hittest_tight.scale = md[2]
        ob.m3_hittest_tight.mesh_object = self.gen_basic_volume_object(ob.m3_hittest_tight.name, m3_hittest_tight.vertices, m3_hittest_tight.face_data)

        for m3_hittest in self.m3[self.m3_model.hittests]:
            pose_bone_name = self.m3_get_bone_name(m3_hittest.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            hittest = shared.m3_item_add(ob.m3_hittests, item_name=pose_bone_name)
            hittest.bone.handle = pose_bone.bl_handle if pose_bone else ''
            hittest.shape = hittest.bl_rna.properties['shape'].enum_items[getattr(m3_hittest, 'shape')].identifier
            hittest.size = (m3_hittest.size0, m3_hittest.size1, m3_hittest.size2)
            md = to_bl_matrix(m3_hittest.matrix).decompose()
            hittest.location = md[0]
            hittest.rotation = md[1].to_euler('XYZ')
            hittest.scale = md[2]
            hittest.mesh_object = self.gen_basic_volume_object(hittest.name, m3_hittest.vertices, m3_hittest.face_data)

    def create_rigid_bodies(self):
        ob = self.ob

        self.m3_struct_version_set_from_ref('m3_rigidbodies_version', self.m3_model.physics_rigidbodies)

        for m3_rigidbody in self.m3[self.m3_model.physics_rigidbodies]:
            pose_bone_name = self.m3_get_bone_name(m3_rigidbody.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            rigidbody = shared.m3_item_add(ob.m3_rigidbodies, item_name=pose_bone_name)
            rigidbody.bone.handle = pose_bone.bl_handle if pose_bone else ''
            processor = M3InputProcessor(self, rigidbody, m3_rigidbody)
            io_shared.io_rigid_body(processor)

            physics_shape = self.m3_bl_ref.get(m3_rigidbody.physics_shape.index)
            if physics_shape:
                rigidbody.physics_shape.handle = physics_shape.bl_handle
            else:
                m3_physics_shape = self.m3[m3_rigidbody.physics_shape]

                physics_shape = shared.m3_item_add(ob.m3_physicsshapes, item_name=rigidbody.name + '_shape')
                rigidbody.physics_shape.handle = physics_shape.bl_handle
                for m3_volume in m3_physics_shape:
                    volume = shared.m3_item_add(physics_shape.volumes)
                    md = to_bl_matrix(m3_volume.matrix).decompose()
                    volume['location'] = md[0]
                    volume['rotation'] = md[1].to_euler('XYZ')
                    volume['scale'] = md[2]
                    volume.shape = volume.bl_rna.properties['shape'].enum_items[getattr(m3_volume, 'shape')].identifier
                    volume.size = (m3_volume.size0, m3_volume.size1, m3_volume.size2)

                    if m3_volume.desc.version == 1:
                        volume['mesh_object'] = self.gen_basic_volume_object(physics_shape.name, m3_volume.vertices, m3_volume.face_data)
                    else:
                        args = physics_shape.name, m3_volume.vertices, m3_volume.plane_equations, m3_volume.loops, m3_volume.polygons
                        volume['mesh_object'] = self.gen_rigidbody_volume_object(*args)

                self.m3_bl_ref[m3_rigidbody.physics_shape.index] = physics_shape

    def create_rigid_body_joints(self):
        ob = self.ob

        for m3_joint in self.m3[self.m3_model.physics_joints]:
            pose_bone1_name = self.m3_get_bone_name(m3_joint.bone1)
            pose_bone2_name = self.m3_get_bone_name(m3_joint.bone2)
            pose_bone1 = ob.pose.bones.get(pose_bone1_name)
            pose_bone2 = ob.pose.bones.get(pose_bone2_name)

            joint = shared.m3_item_add(ob.m3_physicsjoints, item_name=(pose_bone1.name if pose_bone1 else '') + '_joint')

            for rb in ob.m3_rigidbodies:
                if pose_bone1 and rb.bone == pose_bone1.bl_handle:
                    joint.rigidbody1.handle = rb.bl_handle
                if pose_bone2 and rb.bone == pose_bone2.bl_handle:
                    joint.rigidbody2.handle = rb.bl_handle

            processor = M3InputProcessor(self, joint, m3_joint)
            io_shared.io_rigid_body_joint(processor)

            md = to_bl_matrix(m3_joint.matrix1).decompose()
            joint.location1 = md[0]
            joint.rotation1 = md[1].to_euler('XYZ')
            md = to_bl_matrix(m3_joint.matrix2).decompose()
            joint.location2 = md[0]
            joint.rotation2 = md[1].to_euler('XYZ')

            matrix1 = mathutils.Matrix.LocRotScale(None, None, None)
            matrix1.col[0] = to_bl_vec4(m3_joint.matrix1.x).yzwx
            matrix1.col[1] = to_bl_vec4(m3_joint.matrix1.y).yzwx
            matrix1.col[2] = to_bl_vec4(m3_joint.matrix1.z).yzwx
            matrix2 = mathutils.Matrix.LocRotScale(None, None, None)
            matrix2.col[0] = to_bl_vec4(m3_joint.matrix2.x).yzwx
            matrix2.col[1] = to_bl_vec4(m3_joint.matrix2.y).yzwx
            matrix2.col[2] = to_bl_vec4(m3_joint.matrix2.z).yzwx

            # db1 = ob.data.bones.get(pose_bone1_name)
            # db2 = ob.data.bones.get(pose_bone2_name)
            # print(matrix1)
            # print(matrix2)
            # print(matrix1.to_euler())
            # print(matrix2.to_euler())
            # print(db1.head, db2.head)
            # print(db1.matrix_local.to_euler())
            # print(db2.matrix_local.to_euler())
            # print()
            # print()

    def create_cloths(self):
        if not hasattr(self.m3_model, 'physics_cloths'):
            return

        ob = self.ob

        self.m3_struct_version_set_from_ref('m3_cloths_version', self.m3_model.physics_cloths)

        for m3_cloth in self.m3[self.m3_model.physics_cloths]:
            cloth = shared.m3_item_add(ob.m3_cloths, item_name='Cloth')
            processor = M3InputProcessor(self, cloth, m3_cloth)
            io_shared.io_cloth(processor)

            if m3_cloth.constraints.index:
                for ref in self.bl_ref_objects:
                    if [m3_cloth.constraints.index] == ref['sections']:
                        cloth.constraint_set.handle = ref['ob'].bl_handle
                else:
                    m3_constraints = self.m3[m3_cloth.constraints]
                    constraint_set = shared.m3_item_add(ob.m3_clothconstraintsets, item_name=cloth.name + '_constraints')
                    cloth.constraint_set.handle = constraint_set.bl_handle
                    for m3_constraint in m3_constraints:
                        pose_bone_name = self.m3_get_bone_name(m3_constraint.bone)
                        pose_bone = ob.pose.bones.get(pose_bone_name)
                        constraint = shared.m3_item_add(constraint_set.constraints, item_name=pose_bone_name)
                        constraint.bone.handle = pose_bone.bl_handle if pose_bone else ''
                        constraint.height = m3_constraint.height
                        constraint.radius = m3_constraint.radius
                        md = (to_bl_matrix(m3_constraint.matrix) @ io_shared.rot_fix_matrix_transpose).decompose()
                        constraint.location = md[0] - mathutils.Vector(ob.data.bones.get(pose_bone_name).head_local)
                        constraint.rotation = md[1].rotation_difference(ob.data.bones.get(pose_bone_name).matrix_local.to_quaternion()).to_euler('XYZ')
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
            pose_bone_base_name = self.m3_get_bone_name(m3_ik.bone_base)
            pose_bone_target_name = self.m3_get_bone_name(m3_ik.bone_target)
            pose_bone_base = ob.pose.bones.get(pose_bone_base_name)
            pose_bone_target = ob.pose.bones.get(pose_bone_target_name)
            ik = shared.m3_item_add(ob.m3_ikjoints, item_name=pose_bone_target_name)
            ik.bone.handle = pose_bone_target.bl_handle if pose_bone_target else ''

            if pose_bone_base and pose_bone_target:
                joint_length = 0
                parent_pose_bone = pose_bone_target
                while parent_pose_bone and parent_pose_bone != pose_bone_base:
                    parent_pose_bone = parent_pose_bone.parent
                    joint_length += 1
                ik.joint_length = joint_length

            processor = M3InputProcessor(self, ik, m3_ik)
            io_shared.io_ik(processor)

    def create_turrets(self):
        ob = self.ob

        def to_m3_matrix(bl_matrix):

            def to_m3_vec4(bl_vec=None):
                m3_vec = io_m3.structures['VEC4'].get_version(0).instance()
                m3_vec.x, m3_vec.y, m3_vec.z, m3_vec.w = bl_vec or (0.0, 0.0, 0.0, 0.0)
                return m3_vec

            m3_matrix = io_m3.structures['Matrix44'].get_version(0).instance()
            m3_matrix.x = to_m3_vec4(bl_matrix.col[0])
            m3_matrix.y = to_m3_vec4(bl_matrix.col[1])
            m3_matrix.z = to_m3_vec4(bl_matrix.col[2])
            m3_matrix.w = to_m3_vec4(bl_matrix.col[3])
            return m3_matrix

        self.m3_struct_version_set_from_ref('m3_turrets_part_version', self.m3_model.turret_parts)

        for m3_turret in self.m3[self.m3_model.turrets]:
            turret = shared.m3_item_add(ob.m3_turrets, item_name=self.m3[m3_turret.name].content_to_string())
            for ii in self.m3[m3_turret.parts]:
                m3_part = self.m3[self.m3_model.turret_parts][ii]
                pose_bone_name = self.m3_get_bone_name(m3_part.bone)
                pose_bone = ob.pose.bones.get(pose_bone_name)
                part = shared.m3_item_add(turret.parts, item_name=pose_bone_name)
                part.bone.handle = pose_bone.bl_handle if pose_bone else ''
                processor = M3InputProcessor(self, part, m3_part)
                io_shared.io_turret_part(processor)

                part['main_part'] = m3_part.bit_get('flags', 'main_part')
                part['group_id'] = m3_part.group_id

                forward_matrix = mathutils.Matrix.LocRotScale(None, None, None)
                forward_matrix.col[0] = to_bl_vec4(m3_part.matrix_forward.x).wyzx
                forward_matrix.col[1] = to_bl_vec4(m3_part.matrix_forward.y).wyzx
                forward_matrix.col[2] = to_bl_vec4(m3_part.matrix_forward.z).wyzx
                part.forward = forward_matrix.to_euler()

                # test_matrix = to_bl_matrix(m3_part.matrix_forward)
                # db = self.ob.data.bones.get(pose_bone.name)
                # print(db.matrix_local.to_quaternion())
                # print(to_bl_quat(m3_part.quat_up0))
                # print()

    def create_billboards(self):
        ob = self.ob
        for m3_billboard in self.m3[self.m3_model.billboards]:
            pose_bone_name = self.m3_get_bone_name(m3_billboard.bone)
            pose_bone = ob.pose.bones.get(pose_bone_name)
            billboard = shared.m3_item_add(ob.m3_billboards, item_name=pose_bone_name)
            billboard.bone.handle = pose_bone.bl_handle if pose_bone else ''
            processor = M3InputProcessor(self, billboard, m3_billboard)
            io_shared.io_billboard(processor)

            billboard.up = to_bl_quat(m3_billboard.up).to_euler('XYZ')
            billboard.forward = to_bl_quat(m3_billboard.forward).to_euler('XYZ')

    def create_tmd(self):
        ob = self.ob
        for m3_tmd in self.m3[self.m3_model.tmd_data]:
            tmd = shared.m3_item_add(ob.m3_tmd, item_name='TMD')
            processor = M3InputProcessor(self, tmd, m3_tmd)
            io_shared.io_tmd(processor)

            for m3_vec in self.m3[m3_tmd.vectors]:
                vec_item = shared.m3_item_add(tmd.vectors, item_name='Vector')
                vec_item.vector = to_bl_vec3(m3_vec)

    def gen_basic_volume_object(self, name, m3_vert_ref, m3_face_ref):

        if not (m3_vert_ref.index and m3_vert_ref.entries and m3_face_ref.index and m3_face_ref.entries):
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

        me.vertices.add(round(len(bl_vert_data) / 3))
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

    def gen_rigidbody_volume_object(self, name, m3_vert_ref, m3_poly_related_ref, m3_loop_ref, m3_poly_ref):

        if not (m3_vert_ref.index and m3_vert_ref.entries and m3_loop_ref.index and m3_loop_ref.entries and m3_poly_ref.index and m3_poly_ref.entries):
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
            bl_vert_data.extend((v.x, v.y, v.z))

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

        me.vertices.add(len(bl_vert_data) // 3)
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


def m3_import(filename, ob=None, bl_op=None, opts=None):
    importer = Importer(bl_op)
    try:
        if ob and filename.endswith('.m3a'):
            importer.m3a_import(filename, ob)
        elif ob:
            importer.m3_import(filename, ob, opts=opts)
        else:
            importer.m3_import(filename, ob)
    finally:
        importer.report_warnings()
