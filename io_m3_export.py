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


def to_m3_vec2(bl_vec):
    m3_vec = io_m3.structures['VEC2'].get_version(0).instance()
    m3_vec.x, m3_vec.y = bl_vec
    return m3_vec


def to_m3_vec3(bl_vec):
    m3_vec = io_m3.structures['VEC3'].get_version(0).instance()
    m3_vec.x, m3_vec.y, m3_vec.z = bl_vec
    return m3_vec


def to_m3_vec3_f8(bl_vec):
    m3_vec = io_m3.structures['Vector3As3Fixed8'].get_version(0).instance()
    m3_vec.x = bl_vec[0]
    m3_vec.y = bl_vec[0]
    m3_vec.z = bl_vec[0]
    return m3_vec


def to_m3_vec4(bl_vec):
    m3_vec = io_m3.structures['VEC4'].get_version(0).instance()
    m3_vec.w, m3_vec.x, m3_vec.y, m3_vec.z = bl_vec
    return m3_vec


def to_m3_quat(bl_quat):
    m3_quat = io_m3.structures['QUAT'].get_version(0).instance()
    m3_quat.w, m3_quat.x, m3_quat.y, m3_quat.z = bl_quat
    return m3_quat


def to_m3_color(bl_col):
    m3_color = io_m3.structures['COL'].get_version(0).instance()
    m3_color.r = round(bl_col[0] * 255)
    m3_color.g = round(bl_col[1] * 255)
    m3_color.b = round(bl_col[2] * 255)
    m3_color.a = round(bl_col[3] * 255)
    return m3_color


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
        setattr(self.m3, field, False if getattr(self.bl, field) == 0 else True)

    def bit(self, field, name, since_version=None, till_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        if (till_version is not None) and (self.version > till_version):
            return
        self.m3.bit_set(field, name, getattr(self.bl, field))

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

    def string(self, field):
        setattr(self.m3, field, getattr(self.bl, field))

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


class Exporter:

    def m3_export(self, ob, filename):
        assert ob.type == 'ARMATURE'

        self.ob = ob
        self.offset = 0
        self.m3 = io_m3.SectionList(init_header=True)

        self.mesh_objects = []
        self.vertex_groups = set()
        self.uv_count = 0
        for child in self.ob.children:
            if child.type == 'MESH' and child.m3_mesh_export:
                me = child.data
                me.calc_loop_triangles()
                if len(me.loop_triangles) > 0:
                    self.mesh_objects.append(child)
                self.vertex_groups.union(ob.vertex_groups)
                self.uv_count = max(self.uv_count, len(me.uv_layers))

        self.bones = []
        for bone in ob.data.bones:
            if bone.name in [group.name for group in self.vertex_groups]:
                self.bones.append(bone)
            elif not bone.m3_export_cull:
                self.bones.append(bone)

        # TODO warning if meshes and particles have materials or layers in common

        self.bones_from_name = {bone.name: bone for bone in self.bones}
        self.bone_indices_from_name = {bone.name: ii for ii, bone in enumerate(self.bones)}

        model_section = self.m3.section_for_reference(self.m3[0][0], 'model', version=self.ob.m3_model_version)
        model = model_section.content_add()

        model_name_section = self.m3.section_for_reference(model, 'model_name')
        model_name_section.content_from_bytes(os.path.basename(filename))

        self.create_division(model)

        self.m3.resolve()
        self.m3.validate()
        self.m3.to_index()

        return self.m3

    def create_division(self, model):

        model.bit_set('flags', 'has_mesh', len(self.mesh_objects) > 0)

        if not len(self.mesh_objects):
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
        for ob in self.mesh_objects:
            me = ob.data

            for vertex_col in me.vertex_colors:
                if vertex_col.name == rgb_col or vertex_col.name == alpha_col:
                    vertex_rgba = True

        model.bit_set('vertex_flags', 'has_vertex_colors', vertex_rgba)

        m3_vertex_struct = io_m3.structures['VertexFormat' + hex(model.vertex_flags)].get_version(0)

        vertices_section = self.m3.section_for_reference(model, 'vertices')

        div_section = self.m3.section_for_reference(model, 'divisions', version=2)
        div = div_section.content_add()

        faces_section = self.m3.section_for_reference(div, 'faces')
        regions_section = self.m3.section_for_reference(div, 'regions', version=self.ob.m3_mesh_version)
        batches_section = self.m3.section_for_reference(div, 'batches', version=1)

        bone_lookup_section = self.m3.section_for_reference(model, 'bone_lookup')

        m3_vertices = []
        m3_faces = []
        m3_lookup = []

        depsgraph = bpy.context.evaluated_depsgraph_get()

        for ob in self.mesh_objects:
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
                    m3_vert = m3_vertex_struct.instance()

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

            region = regions_section.content_add()
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
                    batch = batches_section.content_add()
                    batch.region_index = len(regions_section) - 1
                    batch.material_reference_index = ii

        vertices_section.content_from_bytes(m3_vertex_struct.instances_to_bytes(m3_vertices))
        faces_section.content_iter_add(m3_faces)
        bone_lookup_section.content_iter_add(m3_lookup)


def m3_export(ob, filename):
    exporter = Exporter()
    sections = exporter.m3_export(ob, filename)
    io_m3.section_list_save(sections, filename)
