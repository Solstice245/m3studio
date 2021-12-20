#!/usr/bin/python3
# -*- coding: utf-8 -*-

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


def m3ToBlEnum(m3, key, enumerator):
    return enumerator[m3[key]][0]


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

        # Currently using seperate layers for color and alpha even though
        # vertex color layers have an alpha channel because as of 3.0, Blender's
        # support for displaying actual vertex alphas is very poor.
        if self.vertex_struct['fields'].get('col'):
            color = mesh.vertex_colors.new(name='Col')
            alpha = mesh.vertex_colors.new(name='Alpha')

            for poly in mesh.polygons:
                for jj in range(3):
                    m3_vert = self.m3_vertices[poly.vertices[jj]]
                    print(m3_vert['col'])
                    for coord in coords:
                        mesh.uv_layers[coord].data[poly.loop_start + jj].uv = (
                            m3_vert[coord]['x'] * (m3_vert.get('uvwMult', 1) / 2048) + m3_vert.get('uvwOffset', 0),
                            1 - (m3_vert[coord]['y'] * (m3_vert.get('uvwMult', 1) / 2048)) + m3_vert.get('uvwOffset', 0)
                        )
                    color.data[poly.loop_start + jj].color = (m3_vert['col']['r'] / 255, m3_vert['col']['g'] / 255, m3_vert['col']['b'] / 255, 1)
                    alpha.data[poly.loop_start + jj].color = (m3_vert['col']['a'] / 255, m3_vert['col']['a'] / 255, m3_vert['col']['a'] / 255, 1)
        else:
            for poly in mesh.polygons:
                for jj in range(3):
                    m3_vert = self.m3_vertices[poly.vertices[jj]]
                    for coord in coords:
                        mesh.uv_layers[coord].data[poly.loop_start + jj].uv = (
                            m3_vert[coord]['x'] * (m3_vert.get('uvwMult', 1) / 2048) + m3_vert.get('uvwOffset', 0),
                            1 - (m3_vert[coord]['y'] * (m3_vert.get('uvwMult', 1) / 2048)) + m3_vert.get('uvwOffset', 0)
                        )

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.view_layers[0].objects.active = meshOb
        meshOb.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')

        # TODO Investigate possibility of using mesh data attributes to avoid having to use bmesh module

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
        pass
        # ! Outdated code below
        # for m3ParticleSystem in self.m3_particle_systems['entries']:
        #
        #     bone = self.armatureOb.data.bones[m3ParticleSystem['bone']]
        #     bone.m3BONEtype = 'PAR_'
        #
        #     if self.m3_particle_systems['version'] <= 12:
        #         bone.m3PAR_emitSpeedRandom = m3ParticleSystem['randomizeWithEmissionSpeed2'] > 0
        #         bone.m3PAR_lifespanRandom = m3ParticleSystem['randomizeWithLifespan2'] > 0
        #         # bone.m3PAR_massRandom = m3ParticleSystem['randomizeWithMass2'] > 0
        #         bone.m3PAR_flagTrailingEnabled = m3ParticleSystem['trailingEnabled'] > 0
        #
        #     if self.m3_particle_systems['version'] >= 17:
        #         bone.m3PAR_emitSpeedRandom = m3BitToBl(m3ParticleSystem, 'additionalFlags', 0)
        #         bone.m3PAR_lifespanRandom = m3BitToBl(m3ParticleSystem, 'additionalFlags', 1)
        #         bone.m3PAR_massRandom = m3BitToBl(m3ParticleSystem, 'additionalFlags', 2)
        #         bone.m3PAR_flagTrailingEnabled = m3BitToBl(m3ParticleSystem, 'additionalFlags', 3)
        #
        #         bone.m3PAR_colorHold = m3ParticleSystem['colorHoldTime']
        #         bone.m3PAR_alphaHold = m3ParticleSystem['alphaHoldTime']
        #         bone.m3PAR_rotationHold = m3ParticleSystem['rotationHoldTime']
        #         bone.m3PAR_sizeHold = m3ParticleSystem['sizeHoldTime']
        #         bone.m3PAR_colorSmooth = m3ToBlEnum(m3ParticleSystem, 'colorSmoothingType', enum.m3AnimSmoothType)
        #         bone.m3PAR_sizeSmooth = m3ToBlEnum(m3ParticleSystem, 'sizeSmoothingType', enum.m3AnimSmoothType)
        #         bone.m3PAR_rotationSmooth = m3ToBlEnum(m3ParticleSystem, 'rotationSmoothingType', enum.m3AnimSmoothType)
        #
        #     bone.m3PAR_type = m3ToBlEnum(m3ParticleSystem, 'particleType', enum.m3ParticleType)
        #     bone.m3PAR_lengthWidthRatio = m3ParticleSystem['lengthWidthRatio']
        #     bone.m3PAR_material = str(m3ParticleSystem['materialReferenceIndex'])
        #     bone.m3PAR_distanceLimit = m3ParticleSystem['killSphere']
        #     bone.m3PAR_lodCut = m3ToBlEnum(m3ParticleSystem, 'lodCut', enum.lod)
        #     bone.m3PAR_lodReduce = m3ToBlEnum(m3ParticleSystem, 'lodReduce', enum.lod)
        #     bone.m3PAR_emitMax = m3ParticleSystem['maxParticles']
        #     bone.m3PAR_emitRate = m3Anim1ToBl(m3ParticleSystem, 'emissionRate')
        #     bone.m3PAR_emitAmount = m3Anim1ToBl(m3ParticleSystem, 'partEmit')
        #     bone.m3PAR_emitArea = m3ToBlEnum(m3ParticleSystem, 'emissionAreaType', enum.m3ParticleEmitArea)
        #     bone.m3PAR_emitAreaSize = m3AnimVec3ToBl(m3ParticleSystem, 'emissionAreaSize')
        #     bone.m3PAR_emitAreaRadius = m3Anim1ToBl(m3ParticleSystem, 'emissionAreaRadius')
        #     bone.m3PAR_emitAreaSizeCutout = m3AnimVec3ToBl(m3ParticleSystem, 'emissionAreaCutoutSize')
        #     bone.m3PAR_emitAreaRadiusCutout = m3Anim1ToBl(m3ParticleSystem, 'emissionAreaCutoutRadius')
        #     bone.m3PAR_emitSpeed = m3Anim1ToBl(m3ParticleSystem, 'emissionSpeed1')
        #     bone.m3PAR_emitSpeedMax = m3Anim1ToBl(m3ParticleSystem, 'emissionSpeed2')
        #     bone.m3PAR_emitAngle = m3AnimToBlVec(m3ParticleSystem, ['emissionAngleX', 'emissionAngleY'])
        #     bone.m3PAR_emitSpread = m3AnimToBlVec(m3ParticleSystem, ['emissionSpreadX', 'emissionSpreadY'])
        #     bone.m3PAR_lifespan = m3Anim1ToBl(m3ParticleSystem, 'lifespan1')
        #     bone.m3PAR_lifespanMax = m3Anim1ToBl(m3ParticleSystem, 'lifespan2')
        #     bone.m3PAR_gravity = m3ParticleSystem['zAcceleration']
        #     bone.m3PAR_mass = m3ParticleSystem['mass']
        #     bone.m3PAR_massMax = m3ParticleSystem['mass2']
        #     bone.m3PAR_friction = m3ParticleSystem['friction']
        #     bone.m3PAR_bounce = m3ParticleSystem['bounce']
        #     bone.m3PAR_windMultiplier = m3ParticleSystem['windMultiplier']
        #     bone.m3PAR_initColor1 = m3AnimColorToBl(m3ParticleSystem, 'initialColor1')
        #     bone.m3PAR_middleColor1 = m3AnimColorToBl(m3ParticleSystem, 'middleColor1')
        #     bone.m3PAR_finalColor1 = m3AnimColorToBl(m3ParticleSystem, 'finalColor1')
        #     bone.m3PAR_colorRandom = m3ParticleSystem['randomizeWithColor2']
        #     bone.m3PAR_initColor2 = m3AnimColorToBl(m3ParticleSystem, 'initialColor2')
        #     bone.m3PAR_middleColor2 = m3AnimColorToBl(m3ParticleSystem, 'middleColor2')
        #     bone.m3PAR_finalColor2 = m3AnimColorToBl(m3ParticleSystem, 'finalColor2')
        #     bone.m3PAR_colorMiddle = m3ParticleSystem['colorAnimationMiddle']
        #     bone.m3PAR_alphaMiddle = m3ParticleSystem['alphaAnimationMiddle']
        #     bone.m3PAR_rotation1 = m3AnimVec3ToBl(m3ParticleSystem, 'rotationValues1')
        #     bone.m3PAR_rotationRandom = m3ParticleSystem['randomizeWithRotationValues2']
        #     bone.m3PAR_rotation2 = m3AnimVec3ToBl(m3ParticleSystem, 'rotationValues2')
        #     bone.m3PAR_rotationMiddle = m3ParticleSystem['rotationAnimationMiddle']
        #     bone.m3PAR_size1 = m3AnimVec3ToBl(m3ParticleSystem, 'particleSizes1')
        #     bone.m3PAR_sizeRandom = m3ParticleSystem['randomizeWithParticleSizes2']
        #     bone.m3PAR_size2 = m3AnimVec3ToBl(m3ParticleSystem, 'particleSizes2')
        #     bone.m3PAR_sizeMiddle = m3ParticleSystem['sizeAnimationMiddle']
        #     bone.m3PAR_noiseAmplitude = m3ParticleSystem['noiseAmplitude']
        #     bone.m3PAR_noiseFrequency = m3ParticleSystem['noiseFrequency']
        #     bone.m3PAR_noiseCohesion = m3ParticleSystem['noiseCohesion']
        #     bone.m3PAR_noiseEdge = m3ParticleSystem['noiseEdge']
        #     bone.m3PAR_trailParticleName = ''  # TODO Needs function for getting bone name from index, including -1
        #     bone.m3PAR_trailParticleChance = m3ParticleSystem['trailingParticlesChance']
        #     bone.m3PAR_trailParticleRate = m3Anim1ToBl(m3ParticleSystem, 'trailingParticlesRate')
        #     bone.m3PAR_flipbookCols = m3ParticleSystem['numberOfColumns']
        #     bone.m3PAR_flipbookRows = m3ParticleSystem['numberOfRows']
        #     bone.m3PAR_flipbookColWidth = m3ParticleSystem['columnWidth']
        #     bone.m3PAR_flipbookRowHeight = m3ParticleSystem['rowHeight']
        #     bone.m3PAR_phase1Start = m3ParticleSystem['phase1StartImageIndex']
        #     bone.m3PAR_phase1End = m3ParticleSystem['phase1EndImageIndex']
        #     bone.m3PAR_phase2Start = m3ParticleSystem['phase2StartImageIndex']
        #     bone.m3PAR_phase2End = m3ParticleSystem['phase2EndImageIndex']
        #     bone.m3PAR_phase1Length = m3ParticleSystem['relativePhase1Length']
        #     bone.m3PAR_localForces = m3ToBlBoolVec(m3ParticleSystem, 'localForceChannels', 16)
        #     bone.m3PAR_worldForces = m3ToBlBoolVec(m3ParticleSystem, 'worldForceChannels', 16)
        #     bone.m3PAR_flagSort = m3BitToBl(m3ParticleSystem, 'flags', 0)
        #     bone.m3PAR_flagCollideTerrain = m3BitToBl(m3ParticleSystem, 'flags', 1)
        #     bone.m3PAR_flagCollideObjects = m3BitToBl(m3ParticleSystem, 'flags', 2)
        #     bone.m3PAR_flagSpawnOnBounce = m3BitToBl(m3ParticleSystem, 'flags', 3)
        #     bone.m3PAR_flagInheritEmitArea = m3BitToBl(m3ParticleSystem, 'flags', 4)
        #     bone.m3PAR_flagInheritEmitParams = m3BitToBl(m3ParticleSystem, 'flags', 5)
        #     bone.m3PAR_flagInheritParentVel = m3BitToBl(m3ParticleSystem, 'flags', 6)
        #     bone.m3PAR_flagSortByZHeight = m3BitToBl(m3ParticleSystem, 'flags', 7)
        #     bone.m3PAR_flagReverseIteration = m3BitToBl(m3ParticleSystem, 'flags', 8)
        #     bone.m3PAR_flagRotationSmooth = m3BitToBl(m3ParticleSystem, 'flags', 9)
        #     bone.m3PAR_flagRotationSmoothBezier = m3BitToBl(m3ParticleSystem, 'flags', 10)
        #     bone.m3PAR_flagSizeSmooth = m3BitToBl(m3ParticleSystem, 'flags', 11)
        #     bone.m3PAR_flagSizeSmoothBezier = m3BitToBl(m3ParticleSystem, 'flags', 12)
        #     bone.m3PAR_flagColorSmooth = m3BitToBl(m3ParticleSystem, 'flags', 13)
        #     bone.m3PAR_flagColorSmoothBezier = m3BitToBl(m3ParticleSystem, 'flags', 14)
        #     bone.m3PAR_flagLitParts = m3BitToBl(m3ParticleSystem, 'flags', 15)
        #     bone.m3PAR_flagFlipbookStart = m3BitToBl(m3ParticleSystem, 'flags', 16)
        #     bone.m3PAR_flagMultiplyByGravity = m3BitToBl(m3ParticleSystem, 'flags', 17)
        #     bone.m3PAR_flagClampTailParts = m3BitToBl(m3ParticleSystem, 'flags', 18)
        #     bone.m3PAR_flagSpawnTrailingParts = m3BitToBl(m3ParticleSystem, 'flags', 19)
        #     bone.m3PAR_flagFixLengthTailParts = m3BitToBl(m3ParticleSystem, 'flags', 20)
        #     bone.m3PAR_flagUseVertexAlpha = m3BitToBl(m3ParticleSystem, 'flags', 21)
        #     bone.m3PAR_flagModelParts = m3BitToBl(m3ParticleSystem, 'flags', 22)
        #     bone.m3PAR_flagSwapYZOnModelParts = m3BitToBl(m3ParticleSystem, 'flags', 23)
        #     bone.m3PAR_flagScaleTimeByParent = m3BitToBl(m3ParticleSystem, 'flags', 24)
        #     bone.m3PAR_flagUseLocalTime = m3BitToBl(m3ParticleSystem, 'flags', 25)
        #     bone.m3PAR_flagSimulateOnInit = m3BitToBl(m3ParticleSystem, 'flags', 26)
        #     bone.m3PAR_flagCopy = m3BitToBl(m3ParticleSystem, 'flags', 27)
        #
        #     for m3ParticleCopy in self.dict_from_ref(m3ParticleSystem['copyIndices']):
        #         copyBone = self.armatureOb.data.bones[m3ParticleCopy['bone']]
        #
        #         copyBone.m3BONEtype = 'PARC'
        #
        #         copyBone.m3PARCsystem = bone.name
        #         copyBone.m3PARCemitRate = m3ParticleCopy['emissionRate']
        #         copyBone.m3PARCemitAmount = m3ParticleCopy['partEmit']
