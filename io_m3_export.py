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
    m3_vec.w, m3_vec.x, m3_vec.y, m3_vec.z = bl_vec or (0.0, 0.0, 0.0, 0.0)
    return m3_vec


def to_m3_quat(bl_quat=None):
    m3_quat = io_m3.structures['QUAT'].get_version(0).instance()
    m3_quat.w, m3_quat.x, m3_quat.y, m3_quat.z = bl_quat or (0.0, 0.0, 0.0, 0.0)
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
        setattr(self.m3, field, to_m3_vec4(getattr(self.bl), field))

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
        self.vertex_group_names = set()

        export_regions = []
        for child in ob.children:
            if child.type == 'MESH' and child.m3_mesh_export:
                me = child.data
                me.calc_loop_triangles()

                if len(me.loop_triangles) > 0:
                    export_regions.append(child)

                    for vertex_group in child.vertex_groups:
                        self.vertex_group_names.add(vertex_group.name)

                    self.uv_count = max(self.uv_count, len(me.uv_layers))

        export_required_bones = []

        def get_valid_collection_items_and_bones(collection):
            # TODO have second unexposed export custom prop for auto-culling such as invalid attachment point name
            export_items = []
            for item in collection:
                if not item.m3_export:
                    continue
                item_bones = []
                if hasattr(item, 'bone'):
                    item_bones.append(shared.m3_pointer_get(ob.data.bones, item.bone))
                if hasattr(item, 'bone0'):
                    item_bones.append(shared.m3_pointer_get(ob.data.bones, item.bone0))
                if hasattr(item, 'bone1'):
                    item_bones.append(shared.m3_pointer_get(ob.data.bones, item.bone1))
                if hasattr(item, 'bone2'):
                    item_bones.append(shared.m3_pointer_get(ob.data.bones, item.bone2))
                export_required_bones.extend(item_bones)
                export_items.append(item)
            return export_items

        export_attachments = get_valid_collection_items_and_bones(ob.m3_attachmentpoints)
        export_particle_systems = get_valid_collection_items_and_bones(ob.m3_particle_systems)
        export_ribbons = get_valid_collection_items_and_bones(ob.m3_ribbons)

        def export_bone_bool(bone):
            result = False
            if not bone.m3_export_cull:
                result = True
            elif bone.name in self.vertex_group_names:
                result = True
            elif bone in export_required_bones:
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

        # TODO warning if meshes and particles have materials or layers in common

        self.bone_name_bones = {bone.name: bone for bone in self.bones}
        self.bone_name_indices = {bone.name: ii for ii, bone in enumerate(self.bones)}
        self.bone_name_correction_matrices = {}

        model_section = self.m3.section_for_reference(self.m3[0][0], 'model', version=ob.m3_model_version)
        model = model_section.content_add()

        model_name_section = self.m3.section_for_reference(model, 'model_name')
        model_name_section.content_from_bytes(os.path.basename(filename))

        self.create_bones(model)  # TODO needs correction matrices
        self.create_division(model, export_regions, regn_version=ob.m3_mesh_version)
        self.create_attachments(model, export_attachments)
        self.create_particle_systems(model, export_particle_systems, version=ob.m3_particle_systems_version)
        self.create_ribbons(model, export_ribbons, version=ob.m3_ribbons_version)
        self.create_irefs(model)  # TODO work on this, results are currently very incorrect

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
            m3_bone.bit_set('flags', 'skinned', bone.name in self.vertex_group_names)
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
            msec.header.id = BOUNDING_ANIM_ID

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
        region_section = self.m3.section_for_reference(div, 'regions', version=regn_version)
        batch_section = self.m3.section_for_reference(div, 'batches', version=1)

        bone_lookup_section = self.m3.section_for_reference(model, 'bone_lookup')

        m3_vertices = []
        m3_faces = []
        m3_lookup = []

        depsgraph = bpy.context.evaluated_depsgraph_get()

        for ob in mesh_objects:
            bm = bmesh.new(use_operators=True)
            bm.from_object(ob, depsgraph)
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

            matref_handles = []
            ob_matref_handles = set([matref.bl_handle for matref in ob.m3_mesh_material_refs])
            for ii, matref in enumerate(self.ob.m3_materialrefs):
                if matref.bl_handle in ob_matref_handles and matref.mat_handle not in matref_handles:
                    matref_handles.append(matref_handles)
                    batch = batch_section.content_add()
                    batch.region_index = len(region_section) - 1
                    batch.material_reference_index = ii

        vertex_section.content_from_bytes(m3_vertex_desc.instances_to_bytes(m3_vertices))
        face_section.content_iter_add(m3_faces)
        bone_lookup_section.content_iter_add(m3_lookup)

    def create_attachments(self, model, attachments):
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

    def create_particle_systems(self, model, systems, version):
        if not systems:
            return

        particle_system_section = self.m3.section_for_reference(model, 'particle_systems', version=version)

        for system in systems:
            system_bone = shared.m3_pointer_get(self.ob.data.bones, system.bone)

            m3_system = particle_system_section.content_add()
            m3_system.bone = self.bone_name_indices[system_bone.name]
            processor = M3OutputProcessor(self, system, m3_system)
            io_shared.io_particle_system(processor)

            # TODO material ref index
            # TODO copy indices
            # TODO trail particle index
            # TODO emission points
            # TODO emission regions

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

            if int(version) >= 22:
                m3_system.unknown8f507b52 = self.init_anim_ref_uint32()

    def create_ribbons(self, model, ribbons, version):
        if not ribbons:
            return

        ribbon_section = self.m3.section_for_reference(model, 'ribbons', version=version)

        for ribbon in ribbons:
            ribbon_bone = shared.m3_pointer_get(self.ob.data.bones, ribbon.bone)

            m3_ribbon = ribbon_section.content_add()
            m3_ribbon.bone = self.bone_name_indices[ribbon_bone.name]
            processor = M3OutputProcessor(self, ribbon, m3_ribbon)
            io_shared.io_ribbon(processor)

            # TODO material ref index
            # TODO ribbon spline section

            m3_ribbon.unknown75e0b576 = self.init_anim_ref_float()
            m3_ribbon.unknownee00ae0a = self.init_anim_ref_float()
            m3_ribbon.unknown1686c0b7 = self.init_anim_ref_float()
            m3_ribbon.unknown9eba8df8 = self.init_anim_ref_float()

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

    def new_anim_id(self):
        self.anim_id_count += 1  # increase first since we don't want to use 0
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
