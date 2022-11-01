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
from . import io_m3
from . import io_shared
from . import shared


def to_bl_uv(m3_uv, uv_multiply, uv_offset):
    return (
        (m3_uv.x * (uv_multiply / 16.0) / 2048.0) + uv_offset,
        1 - ((m3_uv.y * (uv_multiply / 16.0) / 2048.0) + uv_offset)
    )


def to_bl_vec2(m3_vector):
    return mathutils.Vector((m3_vector.x, m3_vector.y))


def to_bl_vec3(m3_vector):
    return mathutils.Vector((m3_vector.x, m3_vector.y, m3_vector.z))


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

    def __init__(self, importer, ob, anim_path, bl, m3):
        self.importer = importer
        self.ob = ob
        self.anim_path = anim_path
        self.bl = bl
        self.m3 = m3
        self.version = m3.structureDescription.structureVersion

    def boolean(self, field, till_version=None):
        if (till_version is not None) and (self.version > till_version):
            return
        val = getattr(self.m3, field)
        setattr(self.bl, field, False if val == 0 else True)

    def bit(self, field, name, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        setattr(self.bl, name, self.m3.getNamedBit(field, name))

    def bit_enum(self, field, name, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        val = self.m3.getNamedBit(field, name)
        val = '0' if val is False else '1'
        setattr(self.bl, name, val)

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

    # with resolved references no longer used, this is only used by "tag" field
    def string(self, field):
        val = getattr(self.m3, field)
        setattr(self.bl, field, val if val else '')

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
        # self.importer.animate_integer(self.ob, self.anim_path, field, anim_ref)

    def anim_int16(self, field):
        self.anim_integer(field)

    def anim_uint16(self, field):
        self.anim_integer(field)

    def anim_uint8(self, field):
        self.anim_integer(field)

    def anim_uint32(self, field):
        self.anim_integer(field)

    def anim_float(self, field):
        anim_ref = getattr(self.m3, field)
        setattr(self.bl, field, anim_ref.default)
        # self.importer.float_key(self.bl, self.anim_path, field, anim_ref)

    def anim_vec2(self, field):
        anim_ref = getattr(self.m3, field)
        setattr(self.bl, field, to_bl_vec2(anim_ref.default))
        # self.importer.animate_vec2(self.bl, self.anim_path, anim_ref)

    def anim_vec3(self, field, since_version=None):
        if (since_version is not None) and (self.version < since_version):
            return
        anim_ref = getattr(self.m3, field)
        setattr(self.bl, field, to_bl_vec3(anim_ref.default))
        # self.importer.animate_vec3(self.bl, self.anim_path, anim_ref)

    def anim_color(self, field):
        anim_ref = getattr(self.m3, field)
        default = to_bl_color(anim_ref.default)
        # ! waiting to see when this fails
        setattr(self.bl, field, default)
        # # without alpha
        # if len(getattr(self.bl, field)) == 3:
        #     setattr(self.bl, field, [*default][:3])
        # else:
        #     setattr(self.bl, field, default)

        # self.importer.animate_color(self.bl, self.anim_path, anim_ref)

    def anim_boundings(self):
        anim_ref = self.m3
        anim_header = anim_ref.header
        anim_id = anim_header.id
        animPathMinBorder = self.anim_path + 'minBorder'
        animPathMaxBorder = self.anim_path + 'maxBorder'
        animPathRadius = self.anim_path + 'radius'
        default = anim_ref.default
        self.bl.minBorder = to_bl_vec3(default.minBorder)
        self.bl.maxBorder = to_bl_vec3(default.maxBorder)
        self.bl.radius = default.radius
        # self.importer.animate_boundings(self.bl, animPathMinBorder, animPathMaxBorder, animPathRadius, anim_id, self.bl.minBorder, self.bl.maxBorder, self.bl.radius)


matref_to_mattype = {
    1: ['materials_standard', io_shared.io_material_standard],
    2: ['materials_displacement', io_shared.io_material_displacement],
    3: ['materials_composite', io_shared.io_material_composite],
    4: ['materials_terrain', io_shared.io_material_terrain],
    5: ['materials_volume', io_shared.io_material_volume],
    7: ['materials_creep', io_shared.io_material_creep],
    8: ['materials_volumenoise', io_shared.io_material_volume_noise],
    9: ['materials_stb', io_shared.io_material_stb],
    10: ['materials_reflection', io_shared.io_material_reflection],
    11: ['materials_lensflare', io_shared.io_material_lens_flare],
    12: ['materials_buffer', io_shared.io_material_buffer],
}

mattype_layers = {
    1: ['diff', 'decal', 'spec', 'gloss', 'emis1', 'emis2', 'envi', 'envi_mask', 'alpha1', 'alpha2', 'norm',
        'height', 'light', 'ao', 'norm_blend1_mask', 'norm_blend2_mask', 'norm_blend1', 'norm_blend2'],
    2: ['normal', 'strength'],
    3: [],
    4: ['terrain'],
    5: ['color', 'unknown1', 'unknown2'],
    7: ['creep'],
    8: ['color', 'noise1', 'noise2'],
    9: ['diff', 'spec', 'normal'],
    10: ['normal', 'strength', 'blur'],
    11: ['color', 'unknown'],
    12: []
}


class Importer:

    def m3_get_ref(self, ref_field):
        return self.m3_ref_data[ref_field.index]['m3']

    def bl_get_ref(self, ref_field, fallback=False):
        bl = self.m3_ref_data[ref_field.index]['bl']
        return bl if not fallback or bl else self.m3_ref_data[ref_field.index]['m3']

    def m3_get_bone_name(self, bone_index):
        return self.final_bone_names[self.m3_get_ref(self.m3_bones[bone_index].name)]

    def m3_import(self, filename):
        self.m3 = io_m3.loadSections(filename)

        self.m3_ref_data = []
        for section in self.m3:
            self.m3_ref_data.append({'m3': section.content, 'bl': None})
        # 0 is used as index for null reference
        self.m3_ref_data[0] = {'m3': [], 'bl': None}
        self.bl_ref_objects = []
        self.rgn_objects = {}

        self.m3_model = self.m3_get_ref(self.m3[0].content[0].model)[0]
        self.m3_bones = self.m3_get_ref(self.m3_model.bones)
        self.m3_bone_rests = self.m3_get_ref(self.m3_model.bone_rests)

        self.sequence_stc_anim_id_set = {}
        self.final_bone_names = {}
        self.animations = []
        self.anim_id_to_long_map = {}

        self.ob = self.armature_object_new()
        self.create_bones()
        self.create_materials()
        # print('createMesh', timeit(lambda: self.create_mesh(), number=1))
        self.create_mesh()
        self.create_lights()
        self.create_particles()
        self.create_ribbons()
        self.create_hittests()
        self.create_attachments()
        self.create_cloths()
        bpy.context.view_layer.objects.active = self.ob

    def armature_object_new(self):
        scene = bpy.context.scene
        arm = bpy.data.armatures.new(name='Armature')
        ob = bpy.data.objects.new('Armature', arm)
        ob.location = scene.cursor.location
        scene.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)

        return ob

    def float_key(self, ob, path, anim_id, default):
        defaultAction = shared.getOrCreateDefaultActionFor(ob)
        shared.setDefaultValue(defaultAction, path, 0, default)

        self.addAnimIdData(animId, objectId=shared.animObjectIdScene, animPath=path)
        for action, timeValueMap in self.actionAndTimeValueMapPairsFor(animId):
            curve = action.fcurves.new(path, index=0)
            for frame, value in frameValuePairs(timeValueMap):
                insertLinearKeyFrame(curve, frame, value)

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

        def get_edit_bones(bone_heads, bone_tails, bone_rolls):
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            edit_bones = []
            for index, m3_bone in enumerate(self.m3_bones):
                m3_bone_name = self.m3[m3_bone.name.index].content
                edit_bone = self.ob.data.edit_bones.new(m3_bone_name)
                self.final_bone_names[m3_bone_name] = edit_bone.name
                edit_bone.bl_handle = shared.m3_handle_gen()
                edit_bone.head = bone_heads[index]
                edit_bone.tail = bone_tails[index]
                edit_bone.roll = bone_rolls[index]

                if m3_bone.parent != -1:
                    parent_edit_bone = self.ob.data.edit_bones[m3_bone.parent]
                    edit_bone.parent = parent_edit_bone
                    parent_child_vector = parent_edit_bone.tail - edit_bone.head

                    if parent_child_vector.length < 0.000001:
                        edit_bone.use_connect = True
                edit_bones.append(edit_bone)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            return edit_bones

        bone_rests = [to_bl_matrix(iref.matrix).inverted() @ io_shared.rot_fix_matrix for iref in self.m3_bone_rests]
        bone_heads = [matrix.translation for matrix in bone_rests]
        bone_vectors = [matrix.col[1].to_3d().normalized() for matrix in bone_rests]
        bone_tails = get_bone_tails(bone_heads, bone_vectors)
        bone_rolls = get_bone_rolls(bone_rests, bone_heads, bone_tails)
        get_edit_bones(bone_heads, bone_tails, bone_rolls)

    def create_materials(self):
        ob = self.ob

        for m3_matref in self.m3[self.m3_model.material_references.index].content:
            mattype_list = matref_to_mattype[m3_matref.type]
            m3_mat = self.m3_get_ref(getattr(self.m3_model, mattype_list[0]))[m3_matref.index]

            matref = shared.m3_item_new('m3_materialrefs', ob)
            mat_col = getattr(ob, 'm3_' + mattype_list[0])
            mat = shared.m3_item_new('m3_' + mattype_list[0], ob)
            mat.name = self.m3[m3_mat.name.index].content
            processor = M3InputProcessor(self, ob, 'm3_{}[{}]'.format(mattype_list[0], len(mat_col) - 1), mat, m3_mat)
            mattype_list[1](processor)

            matref.name = self.m3[m3_mat.name.index].content
            matref.mat_type = 'm3_' + matref_to_mattype[m3_matref.type][0]
            matref.mat_handle = mat.bl_handle

            shared.m3_msgbus_sub(mat, matref, 'name', 'name')

            for layer_name in mattype_layers[m3_matref.type]:
                m3_layer_field = getattr(m3_mat, 'layer_' + layer_name, None)
                if not m3_layer_field:
                    continue

                layer = self.bl_get_ref(m3_layer_field)
                if layer:
                    setattr(mat, 'layer_' + layer_name, layer.bl_handle)
                    continue

                m3_layer = self.m3_get_ref(m3_layer_field)[0]
                m3_layer_bitmap_str = self.m3[m3_layer.color_bitmap.index].content if m3_layer.color_bitmap.index else ''
                if not m3_layer_bitmap_str and not m3_layer.getNamedBit('flags', 'color'):
                    continue

                layer = shared.m3_item_new('m3_materiallayers', ob)
                layer.name = shared.m3_item_get_name('m3_materiallayers', mat.name + '_' + layer_name, ob)
                layer.color_bitmap = m3_layer_bitmap_str
                processor = M3InputProcessor(self, ob, 'm3_materiallayers[{}]'.format(len(ob.m3_materiallayers) - 1), layer, m3_layer)
                io_shared.io_material_layer(processor)

                layer.color_type = 'COLOR' if m3_layer.getNamedBit('flags', 'color') else 'BITMAP'
                layer.fresnel_max = m3_layer.fresnel_min + m3_layer.fresnel_max_offset

                if m3_layer.structureDescription.structureVersion >= 25:
                    layer.fresnel_mask[0] = 1.0 - m3_layer.fresnel_inverted_mask_x
                    layer.fresnel_mask[1] = 1.0 - m3_layer.fresnel_inverted_mask_y
                    layer.fresnel_mask[2] = 1.0 - m3_layer.fresnel_inverted_mask_z

                self.m3_ref_data[m3_layer_field.index]['bl'] = layer
                setattr(mat, 'layer_' + layer_name, layer.bl_handle)

    def create_mesh(self):
        ob = self.ob
        m3_vertices = self.m3_get_ref(self.m3_model.vertices)
        m3_divisions = self.m3_get_ref(self.m3_model.divisions)

        if not self.m3_model.getNamedBit('vertex_flags', 'has_vertices'):
            if len(self.m3_model.vertices):
                raise Exception('Mesh claims to not have any vertices - expected buffer to be empty, but it isn\'t. size=%d' % len(m3_vertices))
            return

        v_class = 'VertexFormat' + hex(self.m3_model.vertex_flags)
        if v_class not in io_m3.structures:
            raise Exception('Vertex flags %s can\'t be handled yet. bufferSize=%d' % (hex(self.m3_model.vertex_flags), len(m3_vertices)))

        v_class_desc = io_m3.structures[v_class].getVersion(0)
        v_count = len(m3_vertices) // v_class_desc.size
        m3_vertices = v_class_desc.createInstances(buffer=m3_vertices, count=v_count)
        bone_lookup_full = self.m3_get_ref(self.m3_model.bone_lookup)

        for division in m3_divisions:
            m3_objects = self.m3_get_ref(division.objects)
            m3_regions = self.m3_get_ref(division.regions)
            m3_faces = self.m3_get_ref(division.faces)
            for m3_ob in m3_objects:
                mesh = bpy.data.meshes.new('Mesh')
                mesh_ob = bpy.data.objects.new('Mesh', mesh)
                mesh_ob.parent = ob
                mesh_ob.m3_material_ref = ob.m3_materialrefs[m3_ob.material_reference_index].bl_handle
                bpy.context.scene.collection.objects.link(mesh_ob)

                modifier = mesh_ob.modifiers.new('EdgeSplit', 'EDGE_SPLIT')
                modifier.use_edge_angle = False

                modifier = mesh_ob.modifiers.new('Armature', 'ARMATURE')
                modifier.object = ob

                region = m3_regions[m3_ob.region_index]
                region_uv_multiply = getattr(region, 'uv_multiply', 16)
                region_uv_offset = getattr(region, 'uv_multiply', 0)
                region_vertex_range = range(region.first_vertex_index, region.first_vertex_index + region.vertex_count)

                faces_old = []
                vertex_index = region.first_face_index
                # some weirdness in REGNV2 from SC2 Beta
                if region.structureDescription.structureVersion <= 2:
                    while vertex_index + 2 <= region.first_face_index + region.face_count:
                        i0 = m3_faces[vertex_index]
                        i1 = m3_faces[vertex_index + 1]
                        i2 = m3_faces[vertex_index + 2]
                        faces_old.append((i0, i1, i2))
                        vertex_index += 3
                else:
                    while vertex_index + 2 <= region.first_face_index + region.face_count:
                        i0 = region.first_vertex_index + m3_faces[vertex_index]
                        i1 = region.first_vertex_index + m3_faces[vertex_index + 1]
                        i2 = region.first_vertex_index + m3_faces[vertex_index + 2]
                        faces_old.append((i0, i1, i2))
                        vertex_index += 3

                old_vertex_to_id_map = {}
                for ii in region_vertex_range:
                    v = m3_vertices[ii]
                    id_tuple = (v.pos.x, v.pos.y, v.pos.z, v.weight0, v.weight1, v.weight2, v.weight3,
                                v.bone0, v.bone1, v.bone2, v.bone3, v.normal.x, v.normal.y, v.normal.z)
                    old_vertex_to_id_map[ii] = id_tuple

                tris_old = []
                for face in faces_old:
                    t0 = old_vertex_to_id_map[face[0]]
                    t1 = old_vertex_to_id_map[face[1]]
                    t2 = old_vertex_to_id_map[face[2]]
                    if t0 != t1 and t0 != t2 and t1 != t2:
                        tris_old.append(face)

                next_new_vertex = 0
                old_vertex_to_new_vertex_map = {}
                new_vertex_to_old_vertex_map = {}
                vertex_id_new_map = {}

                region_vert_data = []

                for ii in region_vertex_range:
                    id_tuple = old_vertex_to_id_map[ii]
                    new_index = vertex_id_new_map.get(id_tuple)
                    if new_index is None:
                        new_index = next_new_vertex
                        next_new_vertex += 1
                        region_vert_data.append(m3_vertices[ii].pos.x)
                        region_vert_data.append(m3_vertices[ii].pos.y)
                        region_vert_data.append(m3_vertices[ii].pos.z)
                        vertex_id_new_map[id_tuple] = new_index
                    old_vertex_to_new_vertex_map[ii] = new_index
                    # store which old vertex indices were merged to a new one
                    old_vertex_indices = new_vertex_to_old_vertex_map.get(new_index)
                    if old_vertex_indices is None:
                        old_vertex_indices = set()
                        new_vertex_to_old_vertex_map[new_index] = old_vertex_indices
                    old_vertex_indices.add(ii)

                # since vertices got merged, the indices of the faces aren't correct anymore.
                # the old face indices however are still later required to figure out what UV coordinates a face has.
                region_face_data = []
                for face_old in tris_old:
                    i0 = old_vertex_to_new_vertex_map[face_old[0]]
                    i1 = old_vertex_to_new_vertex_map[face_old[1]]
                    i2 = old_vertex_to_new_vertex_map[face_old[2]]
                    if i0 != i1 and i1 != i2 and i0 != i2:
                        region_face_data.append(i0)
                        region_face_data.append(i1)
                        region_face_data.append(i2)

                region_tri_range = range(0, len(region_face_data), 3)

                mesh.vertices.add(len(region_vert_data) / 3)
                mesh.vertices.foreach_set('co', region_vert_data)
                mesh.loops.add(len(region_face_data))
                mesh.loops.foreach_set('vertex_index', region_face_data)
                mesh.polygons.add(len(region_tri_range))
                mesh.polygons.foreach_set('loop_start', [ii for ii in region_tri_range])
                mesh.polygons.foreach_set('loop_total', [3 for ii in region_tri_range])

                mesh.validate()
                mesh.update(calc_edges=True)

                bone_lookup = bone_lookup_full[region.first_bone_lookup_index:region.first_bone_lookup_index + region.bone_lookup_count]
                for lookup in bone_lookup:
                    mesh_ob.vertex_groups.new(name=self.final_bone_names[self.m3_get_ref(self.m3_bones[lookup].name)])

                vertex_groups_used = [False for g in mesh_ob.vertex_groups]

                bpy.context.view_layer.objects.active = mesh_ob
                bpy.ops.object.mode_set(mode='EDIT')

                bm = bmesh.from_edit_mesh(mesh)

                has_vertex_colors = self.m3_model.getNamedBit('vertex_flags', 'has_vertex_colors')
                color_layer = bm.loops.layers.color.new('m3color') if has_vertex_colors else None
                alpha_layer = bm.loops.layers.color.new('m3alpha') if has_vertex_colors else None
                deform_layer = bm.verts.layers.deform.new('m3lookup')
                sign_layer = bm.faces.layers.int.new('m3sign')
                uv_maps = []
                uv_layers = {}
                for uv_map in ['uv0', 'uv1', 'uv2', 'uv3', 'uv4']:
                    if v_class_desc.hasField(uv_map):
                        uv_layers[uv_map] = bm.loops.layers.uv.new(uv_map)
                        uv_maps.append(uv_map)

                for face in bm.faces:
                    old_indices = tris_old[face.index]
                    face.smooth = True

                    for loop_index, loop in enumerate(face.loops):
                        m3_vert = m3_vertices[old_indices[loop_index]]
                        for uv_map in uv_maps:
                            loop[uv_layers[uv_map]].uv = to_bl_uv(getattr(m3_vert, uv_map), region_uv_multiply, region_uv_offset)

                        if color_layer:
                            loop[color_layer] = (m3_vert.col.r / 255, m3_vert.col.g / 255, m3_vert.col.b / 255, 1)
                            loop[alpha_layer] = (m3_vert.col.a / 255, m3_vert.col.a / 255, m3_vert.col.a / 255, 1)

                    for vert_index, vert in enumerate(face.verts):
                        m3_vert = m3_vertices[old_indices[vert_index]]

                        for ii in range(0, 4):
                            weight = getattr(m3_vert, 'weight' + str(ii))
                            if weight:
                                vertex_groups_used[getattr(m3_vert, 'bone' + str(ii))] = True
                                vert[deform_layer][getattr(m3_vert, 'bone' + str(ii))] = weight / 255

                        face[sign_layer] = round(m3_vert.sign)

                for edge in bm.edges:
                    edge.smooth = len(edge.link_faces) > 1
                # perform destructive operations only after all uses of m3 vertex data
                bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)
                bmesh.ops.join_triangles(bm, faces=bm.faces, cmp_uvs=True, angle_face_threshold=1, angle_shape_threshold=1)

                bmesh.update_edit_mesh(mesh)
                bm.free()

                bpy.ops.object.mode_set(mode='OBJECT')

                for g, used in zip(mesh_ob.vertex_groups, vertex_groups_used):
                    if not used:
                        mesh_ob.vertex_groups.remove(g)

                self.rgn_objects[m3_ob.region_index] = mesh_ob

    def create_lights(self):
        ob = self.ob

        for m3_light in self.m3_get_ref(self.m3_model.lights):
            bone_name = self.m3_get_bone_name(m3_light.bone)
            bone = ob.data.bones[bone_name]
            light = shared.m3_item_new('m3_lights', ob)
            light.name = shared.m3_item_get_name('m3_lights', bone_name, ob)
            light.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, ob, 'm3_lights[{}]'.format(len(ob.m3_lights) - 1), light, m3_light)
            io_shared.io_light(processor)

    def create_particles(self):
        ob = self.ob

        for m3_particle in self.m3_get_ref(self.m3_model.particles):
            bone_name = self.m3_get_bone_name(m3_particle.bone)
            bone = ob.data.bones[bone_name]
            particle = shared.m3_item_new('m3_particles', ob)
            particle.name = shared.m3_item_get_name('m3_particles', bone_name, ob)
            particle.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, ob, 'm3_particles[{}]'.format(len(ob.m3_particles) - 1), particle, m3_particle)
            io_shared.io_particle_system(processor)

    def create_ribbons(self):
        ob = self.ob

        for m3_ribbon in self.m3_get_ref(self.m3_model.ribbons):
            bone_name = self.m3_get_bone_name(m3_ribbon.bone)
            bone = ob.data.bones[bone_name]
            ribbon = shared.m3_item_new('m3_ribbons', ob)
            ribbon.name = shared.m3_item_get_name('m3_ribbons', bone_name, obj=ob)
            ribbon.bone = bone.bl_handle if bone else ''
            processor = M3InputProcessor(self, ob, 'm3_ribbons[{}]'.format(len(ob.m3_ribbons) - 1), ribbon, m3_ribbon)
            io_shared.io_ribbon(processor)

            for m3_spline in m3_ribbon.splines:
                bone_name = m3_bones[m3_ribbon.bone].name
                bone = ob.data.bones[bone_name]
                spline = shared.m3_item_new('splines', ribbon)
                spline.name = shared.m3_item_get_name('splines', 'Spline', obj=ribbon)
                spline.bone = bone.bl_handle if bone else ''
                processor = M3InputProcessor(self, ob, 'm3_ribbons[{}].splines[{}]'.format(len(ob.m3_ribbons) - 1, len(ribbon.splines) - 1), spline, m3_spline)
                io_shared.io_ribbon_spline(processor)

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
        ob.m3_hittest_tight.mesh_object = self.generate_volume_object(ob.m3_hittest_tight.name, m3_hittest_tight.vertices, m3_hittest_tight.face_data)

        for m3_hittest in self.m3_get_ref(self.m3_model.hittests):
            bone_name = self.m3_get_bone_name(m3_hittest.bone)
            bone = ob.data.bones[bone_name]
            hittest = shared.m3_item_new('m3_hittests', ob)
            hittest.name = shared.m3_item_get_name('m3_hittests', bone_name, ob)
            hittest.bone = bone.bl_handle if bone else ''
            hittest.shape = hittest.bl_rna.properties['shape'].enum_items[getattr(m3_hittest, 'shape')].identifier
            hittest.size = (m3_hittest.size0, m3_hittest.size1, m3_hittest.size2)
            md = to_bl_matrix(m3_hittest.matrix).decompose()
            hittest.location = md[0]
            hittest.rotation = md[1].to_euler('XYZ')
            hittest.scale = md[2]
            hittest.mesh_object = self.generate_volume_object(hittest.name, m3_hittest.vertices, m3_hittest.face_data)

    def create_attachments(self):
        ob = self.ob

        bone_point = {}

        for m3_point in self.m3_get_ref(self.m3_model.attachment_points):
            bone_name = self.m3_get_bone_name(m3_point.bone)
            bone = ob.data.bones[bone_name]
            point = shared.m3_item_new('m3_attachmentpoints', ob)
            point.bone = bone.bl_handle if bone else ''
            point.name = self.m3_get_ref(m3_point.name)[4:]
            # print('point set', point.name)
            if not bone_point.get(bone_name) or bone_name.startswith('Vol'):
                bone_point[bone_name] = (point, len(getattr(ob, 'm3_attachmentpoints')) - 1)

        # print(bone_point)

        for m3_volume in self.m3_get_ref(self.m3_model.attachment_volumes):
            bone0_name = self.m3_get_bone_name(m3_volume.bone0)
            point, point_index = bone_point[bone0_name]
            bone1_name = self.m3_get_bone_name(m3_volume.bone1)
            bone1 = ob.data.bones[bone1_name]
            if not point:
                continue
            vol = shared.m3_item_new('m3_attachmentpoints[{}].volumes'.format(point_index), ob)
            vol.name = shared.m3_item_get_name('m3_attachmentpoints[{}].volumes'.format(point_index), 'Volume', ob)
            vol.bone = bone1.bl_handle if bone1 else ''
            vol.shape = vol.bl_rna.properties['shape'].enum_items[getattr(m3_volume, 'shape')].identifier
            vol.size = (m3_volume.size0, m3_volume.size1, m3_volume.size2)
            md = to_bl_matrix(m3_volume.matrix).decompose()
            vol.location = md[0]
            vol.rotation = md[1].to_euler('XYZ')
            vol.scale = md[2]
            # print('point', point, point.name)
            vol.mesh_object = self.generate_volume_object('{}_{}'.format(point.name, vol.name), m3_volume.vertices, m3_volume.face_data)

    def create_cloths(self):
        ob = self.ob

        for m3_cloth in self.m3_get_ref(self.m3_model.physics_cloths):
            cloth = shared.m3_item_new('m3_physicscloths', ob)
            cloth.name = shared.m3_item_get_name('m3_physicscloths', 'Cloth', ob)
            processor = M3InputProcessor(self, ob, 'm3_physicscloths[{}]'.format(len(ob.m3_physicscloths) - 1), cloth, m3_cloth)
            io_shared.io_cloth(processor)

            for m3_object_pair in self.m3_get_ref(m3_cloth.influence_map):
                object_pair = cloth.object_pairs.add()
                object_pair.mesh_object = self.rgn_objects[m3_object_pair.influenced_region_index]
                object_pair.simulator_object = self.rgn_objects[m3_object_pair.simulation_region_index]

    def generate_volume_object(self, name, m3_vert_ref, m3_face_ref):

        if not m3_vert_ref.index and not m3_face_ref.index:
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
        bpy.context.scene.collection.objects.link(me_ob)

        bl_vert_data = []
        for v in self.m3_get_ref(m3_vert_ref):
            bl_vert_data.append(v.x)
            bl_vert_data.append(v.y)
            bl_vert_data.append(v.z)

        m3_face_data = self.m3_get_ref(m3_face_ref)
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


def m3_import(filename):
    importer = Importer()
    importer.m3_import(filename)
