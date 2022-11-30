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
from timeit import timeit
from . import io_m3
from . import io_shared
from . import shared


BOUNDING_ANIM_ID = 0x1f9bd2
INT16_MIN = (-(1 << 15))
INT16_MAX = ((1 << 15) - 1)


def to_m3_uv(bl_uv):
    m3_uv = io_m3.structures['Vector2As2int16'].get_version(0).instance()
    m3_uv.x = sorted((INT16_MIN, round(bl_uv[0] * 255), INT16_MAX))[1]
    m3_uv.y = sorted((INT16_MIN, round(bl_uv[1] * 255), INT16_MAX))[1]
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
    m3_vec.x, m3_vec.y, m3_vec.z = bl_vec or (0, 0, 0)
    return m3_vec


def to_m3_vec4(bl_vec=None):
    m3_vec = io_m3.structures['VEC4'].get_version(0).instance()
    m3_vec.x, m3_vec.y, m3_vec.z, m3_vec.w = bl_vec or (0.0, 0.0, 0.0, 0.0)
    return m3_vec


def to_m3_quat(bl_quat=None):
    m3_quat = io_m3.structures['QUAT'].get_version(0).instance()
    m3_quat.x, m3_quat.y, m3_quat.z, m3_quat.w = bl_quat or (0.0, 0.0, 0.0, 0.0)
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


class M3OutputProcessor:

    def __init__(self, exporter, bl, m3):
        self.exporter = exporter
        self.bl = bl
        self.m3 = m3
        self.version = m3.struct_desc.struct_version

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
        setattr(self.m3, field, to_m3_vec3(getattr(self.bl), field))

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

    # def anim_single(self, field, ref_class, ref_flags, data_class, convert_method):
    #     setattr(self.m3, field, getattr(self.bl, field))

    def anim_boolean_based_on_SDU3(self, field):
        anim_ref = self.exporter.init_anim_ref_uint32()
        anim_ref.default = int(getattr(self.bl, field))
        setattr(self.m3, field, anim_ref)

    def anim_boolean_based_on_SDFG(self, field):
        anim_ref = self.exporter.init_anim_ref_uint32()
        anim_ref.default = int(getattr(self.bl, field))
        setattr(self.m3, field, anim_ref)

    def anim_int16(self, field):
        anim_ref = self.exporter.init_anim_ref_int16()
        anim_ref.default = getattr(self.bl, field)
        setattr(self.m3, field, anim_ref)

    def anim_uint16(self, field):
        anim_ref = self.exporter.init_anim_ref_uint16()
        anim_ref.default = getattr(self.bl, field)
        setattr(self.m3, field, anim_ref)

    def anim_uint32(self, field):
        anim_ref = self.exporter.init_anim_ref_uint32()
        anim_ref.default = int(getattr(self.bl, field))  # converting to int because sometimes bools use this
        setattr(self.m3, field, anim_ref)

    def anim_float(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        anim_ref = self.exporter.init_anim_ref_float()
        anim_ref.default = getattr(self.bl, field)
        setattr(self.m3, field, anim_ref)

    def anim_vec2(self, field):
        anim_ref = self.exporter.init_anim_ref_vec2()
        anim_ref.default = to_m3_vec2(getattr(self.bl, field))
        setattr(self.m3, field, anim_ref)

    def anim_vec3(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        anim_ref = self.exporter.init_anim_ref_vec3()
        anim_ref.default = to_m3_vec3(getattr(self.bl, field))
        setattr(self.m3, field, anim_ref)

    def anim_color(self, field, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        anim_ref = self.exporter.init_anim_ref_color()
        anim_ref.default = to_m3_color(getattr(self.bl, field))
        setattr(self.m3, field, anim_ref)


class Exporter:

    def m3_export(self, ob, filename):
        assert ob.type == 'ARMATURE'

        self.ob = ob
        self.m3 = io_m3.SectionList(init_header=True)

        self.anim_id_count = 0
        self.uv_count = 0
        self.skinned_bones = []
        self.mesh_to_basic_volume_sections = {}

        self.export_required_material_references = set()
        self.export_required_bones = set()

        self.export_regions = []
        for child in ob.children:
            if child.type == 'MESH' and child.m3_mesh_export:
                me = child.data
                me.calc_loop_triangles()

                if len(me.loop_triangles) > 0:
                    self.export_regions.append(child)

                    valid_mesh_material_refs = 0
                    for mesh_matref in child.m3_mesh_material_refs:
                        matref = shared.m3_pointer_get(ob.m3_materialrefs, mesh_matref.bl_handle)
                        if matref:
                            self.export_required_material_references.add(matref)
                            valid_mesh_material_refs += 1

                    assert valid_mesh_material_refs != 0
                    # TODO improve invalidation so that a list of all
                    # TODO warnings and exceptions can be made

                    for vertex_group in child.vertex_groups:
                        group_bone = ob.data.bones.get(vertex_group.name)
                        if group_bone:
                            self.export_required_bones.add(group_bone)
                            self.skinned_bones.append(group_bone)

                    self.uv_count = max(self.uv_count, len(me.uv_layers))

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
        export_ik_joints = []  # handled specially
        export_turrets = []  # handled specially
        export_hittests = valid_collections_and_requirements(ob.m3_hittests)
        export_attachment_volumes = []  # handled specially
        export_billboards = []  # handled specially

        def recurse_composite_materials(matref):
            if matref.mat_type == 'm3_materials_composite':
                mat = shared.m3_pointer_get(getattr(self.ob, matref.mat_type), matref.mat_handle)
                for section in mat.sections:
                    section_matref = shared.m3_pointer_get(ob.m3_materialrefs, section.matref)
                    if section_matref:
                        self.export_required_material_references.add(section_matref)
                        recurse_composite_materials(section_matref)

        for matref in self.export_required_material_references.copy():
            recurse_composite_materials(matref)

        for copy in ob.m3_particle_copies:
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

        self.export_ik_joint_bones = []
        for ik_joint in ob.m3_ikjoints:
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

        self.depsgraph = bpy.context.evaluated_depsgraph_get()

        # TODO warning if meshes and particles have materials or layers in common
        # TODO warning if layers have rtt channel collision, also only to be used in standard material

        self.bone_name_bones = {bone.name: bone for bone in self.bones}
        self.bone_name_indices = {bone.name: ii for ii, bone in enumerate(self.bones)}
        self.bone_name_correction_matrices = {}

        self.matref_handle_indices = {}
        for matref in ob.m3_materialrefs:
            if matref in self.export_required_material_references:
                self.matref_handle_indices[matref.bl_handle] = len(self.matref_handle_indices.keys())

        model_section = self.m3.section_for_reference(self.m3[0][0], 'model', version=ob.m3_model_version)
        model = model_section.content_add()

        model_name_section = self.m3.section_for_reference(model, 'model_name')
        model_name_section.content_from_bytes(os.path.basename(filename))

        self.bounds_min = to_m3_vec3((self.ob.m3_bounds.left, self.ob.m3_bounds.back, self.ob.m3_bounds.bottom))
        self.bounds_max = to_m3_vec3((self.ob.m3_bounds.right, self.ob.m3_bounds.front, self.ob.m3_bounds.top))
        self.bounds_radius = self.ob.m3_bounds.radius

        model.boundings = io_m3.structures['BNDS'].get_version(0).instance()
        model.boundings.min = self.bounds_min
        model.boundings.max = self.bounds_max
        model.boundings.radius = self.bounds_radius

        # TODO self.create_sequences(model)
        self.create_bones(model)  # TODO needs correction matrices
        self.create_division(model, self.export_regions, regn_version=ob.m3_mesh_version)  # TODO lookups are incorrect
        self.create_attachment_points(model, export_attachment_points)  # TODO should exclude attachments with same bone as other attachments
        self.create_lights(model, export_lights)
        self.create_shadow_boxes(model, export_shadow_boxes)
        self.create_cameras(model, export_cameras)
        self.create_materials(model, export_material_references, material_versions)  # TODO standard flags, and starbursts
        self.create_particle_systems(model, export_particle_systems, export_particle_copies, version=ob.m3_particle_systems_version)
        self.create_ribbons(model, export_ribbons, export_ribbon_splines, version=ob.m3_ribbons_version)
        self.create_projections(model, export_projections)
        self.create_forces(model, export_forces)
        self.create_warps(model, export_warps)
        # TODO self.create_physics_bodies(model, export_physics_bodies, version=ob.m3_rigid_bodies_version)  # TODO physics bodies bone should be exclusive
        # TODO self.create_physics_joints(model, export_physics_joints)
        # TODO self.create_physics_cloths(model, export_physics_cloths, version=ob.m3_physics_cloths_version)
        self.create_ik_joints(model, export_ik_joints)
        self.create_turrets(model, export_turrets, part_version=ob.m3_turrets_part_version)
        self.create_irefs(model)
        self.create_hittests(model, export_hittests)
        self.create_attachment_volumes(model, export_attachment_volumes)
        self.create_billboards(model, export_billboards)
        # ???? self.create_tmd_data(model, export_tmd_data)

        self.m3.resolve()
        self.m3.validate()
        self.m3.to_index()

        return self.m3

    def create_bones(self, model):
        if not self.bones:
            return

        bone_section = self.m3.section_for_reference(model, 'bones', version=1)

        for bone in self.bones:
            m3_bone = bone_section.content_add()
            m3_bone_name_section = self.m3.section_for_reference(m3_bone, 'name')
            m3_bone_name_section.content_from_bytes(bone.name)
            m3_bone.flags = 0
            m3_bone.bit_set('flags', 'real', True)
            m3_bone.bit_set('flags', 'skinned', bone in self.skinned_bones)
            m3_bone.location = self.init_anim_ref_vec3()
            m3_bone.rotation = self.init_anim_ref_quat()
            m3_bone.scale = self.init_anim_ref_vec3()
            m3_bone.ar1 = self.init_anim_ref_uint32(1)

            if bone.parent is not None:
                m3_bone.parent = self.bone_name_indices[bone.parent.name]
                # rel_rest_pose_matrix = bone.parent.matrix_local @ bone.matrix_local
            else:
                m3_bone.parent = -1
                # rel_rest_pose_matrix = bone.matrix_local

    def create_division(self, model, mesh_objects, regn_version):

        model.bit_set('flags', 'has_mesh', len(mesh_objects) > 0)

        if not len(mesh_objects):
            model.skin_bone_count = 0
            div_section = self.m3.section_for_reference(model, 'divisions', version=2)
            div = div_section.content_add()

            msec_section = self.m3.section_for_reference(div, 'msec', version=1)
            msec = msec_section.content_add()
            msec.header = io_m3.structures['BNDSAnimationReference'].get_version(0).instance()
            msec.header.interpolation = 1
            msec.header.flags = 0x0006
            msec.header.id = BOUNDING_ANIM_ID
            msec.default = io_m3.structures['BNDS'].get_version(0).instance()
            msec.default.min = self.bounds_min
            msec.default.max = self.bounds_max
            msec.default.max = self.bounds_radius

            return

        model.vertex_flags = 0x182007d

        model.bit_set('vertex_flags', 'use_uv0', self.uv_count > 0)
        model.bit_set('vertex_flags', 'use_uv1', self.uv_count > 1)
        model.bit_set('vertex_flags', 'use_uv2', self.uv_count > 2)
        model.bit_set('vertex_flags', 'use_uv3', self.uv_count > 3)
        model.bit_set('vertex_flags', 'use_uv4', self.uv_count > 4)

        rgb_col = 'm3color'
        alpha_col = 'm3alpha'

        vertex_rgba = False
        for ob in mesh_objects:
            me = ob.data

            for vertex_col in me.vertex_colors:
                if vertex_col.name == rgb_col or vertex_col.name == alpha_col:
                    vertex_rgba = True

        model.bit_set('vertex_flags', 'has_vertex_colors', vertex_rgba)

        m3_vertex_desc = io_m3.structures['VertexFormat' + hex(model.vertex_flags)].get_version(0)

        vertex_section = self.m3.section_for_reference(model, 'vertices')

        div_section = self.m3.section_for_reference(model, 'divisions', version=2)
        div = div_section.content_add()

        face_section = self.m3.section_for_reference(div, 'faces')

        msec_section = self.m3.section_for_reference(div, 'msec', version=1)
        msec = msec_section.content_add()
        msec.header = io_m3.structures['BNDSAnimationReference'].get_version(0).instance()
        msec.header.interpolation = 1
        msec.header.flags = 0x0006
        msec.header.id = BOUNDING_ANIM_ID
        msec.default = io_m3.structures['BNDS'].get_version(0).instance()
        msec.default.min = self.bounds_min
        msec.default.max = self.bounds_max
        msec.default.max = self.bounds_radius

        region_section = self.m3.section_for_reference(div, 'regions', version=regn_version)
        batch_section = self.m3.section_for_reference(div, 'batches', version=1)

        bone_lookup_section = self.m3.section_for_reference(model, 'bone_lookup')

        m3_vertices = []
        m3_faces = []
        m3_lookup = []

        for ob in mesh_objects:
            bm = bmesh.new(use_operators=True)
            bm.from_object(ob, self.depsgraph)
            bmesh.ops.triangulate(bm, faces=bm.faces)

            sign_layer = bm.faces.layers.int.get('m3sign') or bm.faces.layers.int.new('m3sign')
            color_layer = bm.loops.layers.color.get('m3color')
            alpha_layer = bm.loops.layers.color.get('m3alpha')
            deform_layer = bm.verts.layers.deform.get('m3lookup')

            first_vertex_index = len(m3_vertices)
            first_face_index = len(m3_faces)
            first_lookup_index = len(m3_lookup)
            vertex_lookups_used = 0

            region_vertices = []
            region_faces = []
            region_lookup = []

            vert_indices_used = set()

            for face in bm.faces:
                assert len(face.loops) == 3

                for loop in face.loops:

                    region_faces.append(loop.vert.index)

                    if loop.vert.index in vert_indices_used:
                        continue
                    else:
                        vert_indices_used.add(loop.vert.index)

                    vert = loop.vert
                    m3_vert = m3_vertex_desc.instance()

                    m3_vert.pos = to_m3_vec3(ob.matrix_local @ vert.co)

                    weight_lookup_pairs = vert[deform_layer].items()

                    sum_weight = 0
                    for index, weight in weight_lookup_pairs:
                        sum_weight += weight

                    round_weight_lookup_pairs = []
                    correct_sum_weight = 0
                    round_sum_weight = 0
                    for index, weight in weight_lookup_pairs:
                        weighted = 0
                        if weight:
                            weight += 1
                            if index not in region_lookup:
                                region_lookup.append(index)
                            correct_sum_weight += weight / sum_weight
                            new_round_weight = round(correct_sum_weight * 255)
                            round_weight_lookup_pairs.append((index, new_round_weight - round_sum_weight))
                            round_sum_weight = new_round_weight
                        if weighted >= 4:
                            break

                    for ii in range(0, min(4, len(weight_lookup_pairs))):
                        setattr(m3_vert, 'lookup' + str(ii), weight_lookup_pairs[ii][0])
                        setattr(m3_vert, 'weight' + str(ii), round(weight_lookup_pairs[ii][1] * 255))

                    # TODO handle static vertex here

                    vertex_lookups_used = max(vertex_lookups_used, len(round_weight_lookup_pairs))

                    uv_layers = bm.loops.layers.uv.values()
                    for ii in range(0, 4):
                        uv_layer = uv_layers[ii] if ii < len(uv_layers) else None
                        setattr(m3_vert, 'uv' + str(ii), to_m3_uv(loop[uv_layer].uv if uv_layer else (0, 0)))

                    m3_vert.normal = to_m3_vec3_f8(vert.normal)

                    if face[sign_layer] == 1:
                        m3_vert.sign = 1
                        m3_vert.tan = to_m3_vec3_f8(-loop.calc_tangent())
                    else:
                        m3_vert.sign = -1
                        m3_vert.tan = to_m3_vec3_f8(loop.calc_tangent())

                    if vertex_rgba:
                        r, g, b, a = (1, 1, 1, 1)
                        if color_layer:
                            r, g, b = loop[color_layer].color[0:3]
                        if alpha_layer:
                            bl_col = loop[color_layer].color
                            a = (bl_col[0] + bl_col[1] + bl_col[2]) / 3
                        m3_vert.color = to_m3_color((r, g, b, a))

                    region_vertices.append(m3_vert)

            m3_vertices.extend(region_vertices)
            m3_faces.extend(region_faces)
            m3_lookup.extend(region_lookup)  # TODO lookup values are wrong

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

            matref_handles = []
            ob_matref_handles = set([matref.bl_handle for matref in ob.m3_mesh_material_refs])
            for matref in self.ob.m3_materialrefs:
                if matref.bl_handle in ob_matref_handles and matref.mat_handle not in matref_handles:
                    matref_handles.append(matref_handles)
                    batch = batch_section.content_add()
                    batch.region_index = len(region_section) - 1
                    batch.material_reference_index = self.matref_handle_indices[matref.bl_handle]

        vertex_section.content_from_bytes(m3_vertex_desc.instances_to_bytes(m3_vertices))
        face_section.content_iter_add(m3_faces)
        bone_lookup_section.content_iter_add(m3_lookup)

    def create_attachment_points(self, model, attachments):
        if not attachments:
            return

        attachment_point_section = self.m3.section_for_reference(model, 'attachment_points', version=1)
        attachment_point_addon_section = self.m3.section_for_reference(model, 'attachment_points_addon')

        for attachment in attachments:
            attachment_bone = shared.m3_pointer_get(self.ob.data.bones, attachment.bone)

            m3_attachment = attachment_point_section.content_add()
            m3_attachment_name_section = self.m3.section_for_reference(m3_attachment, 'name')
            m3_attachment_name_section.content_from_bytes(('Ref_' if not attachment.name.startswith('Ref_') else '') + attachment.name)
            m3_attachment.bone = self.bone_name_indices[attachment_bone.name]
            attachment_point_addon_section.content_add(0xffff)
        # add volumes later so that sections are in order of the modl data

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
                                m3_layer.bit_set('flags', 'video')
                            else:
                                m3_layer.video_frame_rate = 0
                                m3_layer.video_frame_start = 0
                                m3_layer.video_frame_end = 0
                                m3_layer.video_mode = 0

                            m3_layer.unknownbc0c14e5 = self.init_anim_ref_uint32(0)
                            m3_layer.unknowne740df12 = self.init_anim_ref_float(0.0)
                            m3_layer.unknown39ade219 = self.init_anim_ref_uint16(0)
                            m3_layer.unknowna4ec0796 = self.init_anim_ref_uint32(0, interpolation=1)
                            m3_layer.unknowna44bf452 = self.init_anim_ref_float(1.0)

                # TODO manage flags of standard material, and lens flare starbursts.
                if type_ii == 3:  # composite material
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

            if bone.parent is not None:
                rel_rest_matrix = bone.parent.matrix_local @ bone.matrix_local
            else:
                rel_rest_matrix = bone.matrix_local

            bind_scale_matrix = mathutils.Matrix.LocRotScale(None, None, bone.m3_bind_scale)
            iref.matrix = to_m3_matrix(bind_scale_matrix @ rel_rest_matrix.inverted())

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
            self.mesh_to_basic_volume_sections[mesh_ob.name] = [vert_data, face_data]
        else:
            vert_section, face_section = self.mesh_to_basic_volume_sections[mesh_ob.name]
            vert_section.references.append(m3.vertices)
            face_section.references.append(m3.face_data)

    def new_anim_id(self):
        self.anim_id_count += 1  # increase first since we don't want to use 0
        if self.anim_id_count == BOUNDING_ANIM_ID:
            self.anim_id_count += 1
        return self.anim_id_count

    def init_anim_header(self, interpolation, anim_id=None):
        anim_ref_header = io_m3.structures['AnimationReferenceHeader'].get_version(0).instance()
        anim_ref_header.interpolation = interpolation
        anim_ref_header.flags = 0  # TODO make flags into param
        anim_ref_header.id = anim_id if anim_id is not None else self.new_anim_id()
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
        anim_ref.header = self.init_anim_header(interpolation=interpolation)
        anim_ref.default = to_m3_vec2(val)
        anim_ref.null = to_m3_vec2()
        return anim_ref

    def init_anim_ref_vec3(self, val=None, interpolation=1):
        anim_ref = io_m3.structures['Vector3AnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation)
        anim_ref.default = to_m3_vec3(val)
        anim_ref.null = to_m3_vec3()
        return anim_ref

    def init_anim_ref_quat(self, val=None, interpolation=1):
        anim_ref = io_m3.structures['QuaternionAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation)
        anim_ref.default = to_m3_quat(val)
        anim_ref.null = to_m3_quat()
        return anim_ref

    def init_anim_ref_color(self, val=None, interpolation=1):
        anim_ref = io_m3.structures['ColorAnimationReference'].get_version(0).instance()
        anim_ref.header = self.init_anim_header(interpolation=interpolation)
        anim_ref.default = to_m3_color(val)
        anim_ref.null = to_m3_color()
        return anim_ref


def m3_export(ob, filename):
    exporter = Exporter()
    sections = exporter.m3_export(ob, filename)
    io_m3.section_list_save(sections, filename)
