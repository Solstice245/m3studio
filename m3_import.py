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

from math import log
import bpy
import bmesh
import mathutils
from . import m3
from . import shared
from . import bl_enum


def m3BitToBl(m3, key, bit):
    if m3[key] == 0:
        return False
    bits = int(max(32, log(m3[key], 2) + 1))
    arr = [True if m3[key] & (1 << (bits - 1 - ii)) else False for ii in range(bits)]
    return arr[-(bit + 1)]


def m3ToBlBoolVec(m3, key, length):
    if m3[key] == 0:
        return length * [False]
    bits = int(max(32, log(m3[key], 2) + 1))
    arr = [True if m3[key] & (1 << (bits - 1 - ii)) else False for ii in range(bits)]
    return tuple(arr[:length][::-1])


def m3Anim1ToBl(m3, key):
    return m3[key]['initValue']


def m3AnimVec3ToBl(m3, key):
    m3InitValue = m3[key]['initValue']
    return (m3InitValue['x'], m3InitValue['y'], m3InitValue['z'])


def m3AnimColorToBl(m3, key):
    m3InitValue = m3[key]['initValue']
    return (m3InitValue['red'], m3InitValue['blue'], m3InitValue['green'], m3InitValue['alpha'])


def m3ToBlEnum(m3, key, enum):
    return enum[m3[key]][0]


def m3ToBlVec(m3, keys):
    return tuple(m3[key] for key in keys)


def m3AnimToBlVec(m3, keys):
    return tuple(m3[key]['initValue'] for key in keys)


def m3Matrix44ToBl(m3):
    return mathutils.Matrix((
        (m3['x']['x'], m3['y']['x'], m3['z']['x'], m3['w']['x']),
        (m3['x']['y'], m3['y']['y'], m3['z']['y'], m3['w']['y']),
        (m3['x']['z'], m3['y']['z'], m3['z']['z'], m3['w']['z']),
        (m3['x']['w'], m3['y']['w'], m3['z']['w'], m3['w']['w']),
    ))


class M3Import:

    def __init__(self, file):
        self.m3_index = m3.load_sections(file)

        self.m3_model = self.dict_from_ref(self.m3_index[0]['entries'][0]['model'])

        self.m3_bones = self.dict_from_ref(self.m3_model['entries'][0]['bones'])
        self.m3_bone_rests = self.dict_from_ref(self.m3_model['entries'][0]['boneRests'])

        self.m3_particle_systems = self.dict_from_ref(self.m3_model['entries'][0]['particles'])

        vertices = self.dict_from_ref(self.m3_model['entries'][0]['vertices'])
        self.vertex_struct = m3.load_struct('VertexFormat' + hex(self.m3_model['entries'][0]['vFlags']))
        buffer = bytes([vert['value'] for vert in vertices['entries']])
        size = int(self.vertex_struct['size'])

        self.m3_vertices = [m3.read_struct(self.vertex_struct, buffer[size * ii:size * ii + size]) for ii in range(int(len(buffer) / size))]

        self.m3_divisions = self.dict_from_ref(self.m3_model['entries'][0]['divisions'])

        self.create_armature()
        # self.create_particle_systems()
        self.create_mesh()

    def dict_from_ref(self, m3):
        return self.m3_index[m3['index']] if m3['index'] > 0 else {}

    def str_from_ref(self, m3):
        return ''.join([char['value'] for char in self.m3_index[m3['index']]['entries']]) if m3['index'] > 0 else ''

    def create_armature(self):
        self.armature = bpy.data.armatures.new('Armature')
        self.armatureOb = bpy.data.objects.new('Armature', self.armature)
        bpy.context.collection.objects.link(self.armatureOb)

        bpy.context.view_layer.objects.active = self.armatureOb
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        for m3Bone, m3BoneRest in zip(self.m3_bones['entries'], self.m3_bone_rests['entries']):
            matrix = m3Matrix44ToBl(m3BoneRest['matrix'])
            head = matrix.translation
            # # vector = matrix.col[1].to_3d().normalized()

            bone = self.armatureOb.data.edit_bones.new(self.str_from_ref(m3Bone['name']))
            bone.head = head
            bone.tail = (head[0], head[1] + 1, head[2])

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def create_mesh(self):
        mesh = bpy.data.meshes.new('Mesh')
        meshOb = bpy.data.objects.new('Mesh', mesh)
        bpy.context.collection.objects.link(meshOb)

        self.mesh = mesh
        self.meshOb = meshOb

        verts = [(vert['pos']['x'], vert['pos']['y'], vert['pos']['z']) for vert in self.m3_vertices]
        faces = []

        for m3Division in self.m3_divisions['entries']:
            m3_faces = self.dict_from_ref(m3Division['faces'])
            m3_regions = self.dict_from_ref(m3Division['regions'])
            m3_objects = self.dict_from_ref(m3Division['objects'])

            for m3_object in m3_objects['entries']:
                m3_region = m3_regions['entries'][m3_object['regionIndex']]
                first_vert = m3_region['firstVertexIndex']
                first_face = m3_region['firstFaceVertexIndexIndex']
                num_face = m3_region['numberOfFaceVertexIndices']

                ii = first_face
                while ii + 2 <= first_face + num_face:
                    faces.append((
                        first_vert + m3_faces['entries'][ii]['value'],
                        first_vert + m3_faces['entries'][ii + 1]['value'],
                        first_vert + m3_faces['entries'][ii + 2]['value']
                    ))
                    ii += 3

        mesh.from_pydata(verts, [], faces)

        coords = []
        for coord in ['uv0', 'uv1', 'uv2', 'uv3']:
            if self.vertex_struct['fields'].get(coord):
                mesh.uv_layers.new(name=coord)
                coords.append(coord)

        # Currently using separate layers for color and alpha even though
        # vertex color layers have an alpha channel because as of 3.0, Blender's
        # support for displaying actual vertex alphas is very poor.

        if self.vertex_struct['fields'].get('col'):
            color = mesh.vertex_colors.new(name='Col')
            alpha = mesh.vertex_colors.new(name='Alpha')

            for poly in mesh.polygons:
                for ii in range(3):
                    m3_vert = self.m3_vertices[poly.vertices[ii]]
                    for coord in coords:
                        mesh.uv_layers[coord].data[poly.loop_start + ii].uv = (
                            m3_vert[coord]['x'] * (m3_vert.get('uvwMult', 1) / 2048) + m3_vert.get('uvwOffset', 0),
                            1 - (m3_vert[coord]['y'] * (m3_vert.get('uvwMult', 1) / 2048)) + m3_vert.get('uvwOffset', 0)
                        )
                    color.data[poly.loop_start + ii].color = (m3_vert['col']['r'] / 255, m3_vert['col']['g'] / 255, m3_vert['col']['b'] / 255, 1)
                    alpha.data[poly.loop_start + ii].color = (m3_vert['col']['a'] / 255, m3_vert['col']['a'] / 255, m3_vert['col']['a'] / 255, 1)
        else:
            for poly in mesh.polygons:
                for ii in range(3):
                    m3_vert = self.m3_vertices[poly.vertices[ii]]
                    for coord in coords:
                        mesh.uv_layers[coord].data[poly.loop_start + ii].uv = (
                            m3_vert[coord]['x'] * (m3_vert.get('uvwMult', 1) / 2048) + m3_vert.get('uvwOffset', 0),
                            1 - (m3_vert[coord]['y'] * (m3_vert.get('uvwMult', 1) / 2048)) + m3_vert.get('uvwOffset', 0)
                        )

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.view_layers[0].objects.active = meshOb
        meshOb.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(mesh)
        group = bm.faces.layers.int.new('m3_vertex_sign')
        for face in bm.faces:
            for vert in face.verts:
                if self.m3_vertices[vert.index]['sign'] == 1.0:
                    face[group] = 1
                    break

        # Need to set mode back to object so that bmesh is cleared and does not interfere with the rest of the operations
        bpy.ops.object.mode_set(mode='OBJECT')

    def create_particle_systems(self):
        for m3_particle in self.m3_particle_systems['entries']:
            print(m3_particle)
            bone = self.armature.bones[m3_particle['bone']]
            particle = self.armature.m3_particles.add()
            particle.name = shared.collection_find_unused_name([self.armature.m3_particles], [], bone.name if bone.name else 'particle')
            particle.bone = bone.name
            particle.particle_type = bl_enum.particle_type[m3_particle['particle_type']][0]
            particle.length_width_ratio = m3_particle['length_width_ratio']
            particle.distance_limit = m3_particle['distance_limit']
            particle.lod_cut = bl_enum.lod[m3_particle['lod_cut']][0]
            particle.lod_reduce = bl_enum.lod[m3_particle['lod_reduce']][0]
            particle.emit_type = bl_enum.particle_emit_type[m3_particle['emit_type']][0]
            particle.emit_shape = bl_enum.particle_shape[m3_particle['emit_shape']][0]
            particle.emit_shape_cutout = bool(m3_particle['flags'][4])
            # particle.emit_shape_size # TODO
            # particle.emit_shape_size_cutout # TODO
            particle.emit_radius = m3_particle['emit_radius']
            particle.emit_radius_cutout = m3_particle['emit_radius_cutout']
            particle.emit_max = m3_particle['emit_max']
            particle.emit_rate = m3_particle['emit_rate']
            particle.emit_amount = m3_particle['emit_amount']
            particle.emit_speed = m3_particle['emit_speed']
            particle.emit_speed_random = m3_particle['emit_speed_random']
            particle.emit_speed_randomize = bool(m3_particle['flags'][0])  # TODO
            particle.friction = m3_particle['friction']
            particle.bounce = m3_particle['bounce']
            particle.wind_multiplier = m3_particle['wind_multiplier']
