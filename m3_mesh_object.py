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
from . import shared


class SignOpSelect(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_select'
    bl_label = 'Select faces'
    bl_description = 'Selects the assigned faces of the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_vertex_sign(bm)
            for face in bm.faces:
                face.select = True if face[group] else face.select

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpSet(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_set'
    bl_label = 'Set faces'
    bl_description = 'Sets the selected faces to the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_vertex_sign(bm)
            for face in bm.faces:
                face[group] = 1 if face.select else 0

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpAdd(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_add'
    bl_label = 'Add faces'
    bl_description = 'Adds the selected faces to the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_vertex_sign(bm)
            for face in bm.faces:
                face[group] = 1 if face.select else face[group]

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpRemove(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_remove'
    bl_label = 'Remove faces'
    bl_description = 'Removes the selected faces from the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_vertex_sign(bm)
            for face in bm.faces:
                face[group] = 0 if face.select else face[group]

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpInvert(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_invert'
    bl_label = 'Invert faces'
    bl_description = 'Inverts the value of the sign inversion group for the selected faces.'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_vertex_sign(bm)
            for face in bm.faces:
                face[group] = (1 if face[group] == 0 else 0) if face.select else face[group]

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


def bm_layer_vertex_sign(bm):
    return bm.faces.layers.int.get('m3sign') or bm.faces.layers.int.new('m3sign')


class ClothSimOpSelect(bpy.types.Operator):
    bl_idname = 'm3.cloth_sim_select'
    bl_label = 'Select vertices'
    bl_description = 'Selects the assigned vertices of the cloth simulation'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_cloth_sim(bm)
            for vert in bm.verts:
                vert.select = True if vert[group] else vert.select

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class ClothSimOpSet(bpy.types.Operator):
    bl_idname = 'm3.cloth_sim_set'
    bl_label = 'Set vertices'
    bl_description = 'Sets the selected vertices to the cloth simulation'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_cloth_sim(bm)
            for vert in bm.verts:
                vert[group] = 1 if vert.select else 0

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


def bm_layer_cloth_sim(bm):
    return bm.verts.layers.int.get('m3clothsim') or bm.verts.layers.int.new('m3clothsim')


class Panel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_GENERAL'
    bl_label = 'M3 Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_mode = 'edit'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        ob = context.object
        parent = ob.parent if ob.parent.type == 'ARMATURE' else None

        if parent:
            shared.draw_pointer_prop(layout.column(), parent.m3_materialrefs, ob, 'm3_material_ref', label='M3 Material', icon='MATERIAL')

        if ob.mode == 'EDIT':
            layout.separator()
            layout.label(text='M3 Vertex Normal Sign:')
            layout.operator('m3.vertex_sign_select', text='Select')
            col = layout.column_flow(columns=2)
            col.operator('m3.vertex_sign_set', text='Set To Selected')
            col.operator('m3.vertex_sign_invert', text='Invert Selected')
            col.operator('m3.vertex_sign_add', text='Add Selected')
            col.operator('m3.vertex_sign_remove', text='Remove Selected')

        mesh_cloth = None
        if parent:
            for cloth in parent.m3_cloths:
                if ob == cloth.simulator_object:
                    mesh_cloth = cloth
                    break

        if mesh_cloth and ob.mode == 'EDIT':
            layout.separator()
            layout.label(text='M3 Cloth Simulation Flag:')
            row = layout.row()
            row.operator('m3.cloth_sim_select', text='Select')
            row.operator('m3.cloth_sim_set', text='Set To Selected')


classes = (
    Panel,
    SignOpSelect,
    SignOpSet,
    SignOpAdd,
    SignOpRemove,
    SignOpInvert,
    ClothSimOpSelect,
    ClothSimOpSet,
)
