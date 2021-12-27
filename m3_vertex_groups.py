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

import bpy
import bmesh

# TODO Investigate possibility of using mesh data attributes instead of bmesh layers


def m3_get_vertex_sign(bm):
    return bm.faces.layers.int.get('m3_vertex_sign') or bm.faces.layers.int.new('m3_vertex_sign')


class SignPanel(bpy.types.Panel):
    bl_idname = 'DATA_PT_M3_VERTEXSIGN'
    bl_label = 'M3 Vertex Sign Group'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_mode = 'edit'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator('m3.vertex_sign_select', text='Select')
        col = layout.column_flow(columns=2)
        col.operator('m3.vertex_sign_set', text='Set To Selected')
        col.operator('m3.vertex_sign_invert', text='Invert Selected')
        col.operator('m3.vertex_sign_add', text='Add Selected')
        col.operator('m3.vertex_sign_remove', text='Remove Selected')


class SignOpSet(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_set'
    bl_label = 'Set faces'
    bl_description = 'Sets the selected faces to the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        mesh = context.object.data
        bm = bmesh.from_edit_mesh(mesh)

        group = m3_get_vertex_sign(bm)
        for face in bm.faces:
            face[group] = 1 if face.select else 0

        bmesh.update_edit_mesh(mesh)

        return {'FINISHED'}


class SignOpSelect(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_select'
    bl_label = 'Select faces'
    bl_description = 'Selects the assigned faces of the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        mesh = context.object.data
        bm = bmesh.from_edit_mesh(mesh)
        group = m3_get_vertex_sign(bm)
        for face in bm.faces:
            face.select = True if face[group] else face.select
        bmesh.update_edit_mesh(mesh)

        return {'FINISHED'}


class SignOpAdd(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_add'
    bl_label = 'Add faces'
    bl_description = 'Adds the selected faces to the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        mesh = context.object.data
        bm = bmesh.from_edit_mesh(mesh)

        group = m3_get_vertex_sign(bm)
        for face in bm.faces:
            face[group] = 1 if face.select else face[group]

        bmesh.update_edit_mesh(mesh)

        return {'FINISHED'}


class SignOpRemove(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_remove'
    bl_label = 'Remove faces'
    bl_description = 'Removes the selected faces from the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        mesh = context.object.data
        bm = bmesh.from_edit_mesh(mesh)

        group = m3_get_vertex_sign(bm)
        for face in bm.faces:
            face[group] = 0 if face.select else face[group]

        bmesh.update_edit_mesh(mesh)

        return {'FINISHED'}


class SignOpInvert(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_invert'
    bl_label = 'Invert faces'
    bl_description = 'Inverts the value of the sign inversion group for the selected faces.'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        mesh = context.object.data
        bm = bmesh.from_edit_mesh(mesh)

        group = m3_get_vertex_sign(bm)
        for face in bm.faces:
            face[group] = (1 if face[group] == 0 else 0) if face.select else face[group]

        bmesh.update_edit_mesh(mesh)

        return {'FINISHED'}


classes = (
    SignPanel,
    SignOpSet,
    SignOpSelect,
    SignOpAdd,
    SignOpRemove,
    SignOpInvert,
)
