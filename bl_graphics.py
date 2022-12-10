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
import gpu
from gpu_extras.batch import batch_for_shader
from . import shared


uniform_shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')


def batch_uniform_color_line(color, coords):
    uniform_shader.uniform_float('color', color)
    batch = batch_for_shader(uniform_shader, 'LINES', {'pos': coords})
    batch.draw(uniform_shader)


def draw():
    if not bpy.context.space_data.overlay.show_overlays:
        return

    ob = bpy.context.object
    if ob.type == 'ARMATURE':
        if ob.mode == 'POSE':
            for ik in ob.m3_ikjoints:
                bone = shared.m3_pointer_get(ob.data.bones, ik.bone)
                pb = ob.pose.bones.get(bone.name)
                if bone:
                    bone_parent = bone
                    for ii in range(0, ik.joint_length):
                        if bone_parent.parent:
                            bone_parent = bone_parent.parent if bone_parent else bone_parent
                    if bone_parent is not bone:
                        pbp = ob.pose.bones.get(bone_parent.name)
                        world_bone_m = ob.matrix_world @ pb.matrix
                        world_bone_parent_m = ob.matrix_world @ pbp.matrix
                        batch_uniform_color_line((0, 0, 0, 1), [world_bone_m.translation, world_bone_parent_m.translation])
    #
